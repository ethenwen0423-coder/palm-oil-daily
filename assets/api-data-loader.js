(function (global) {
  "use strict";

  const DEFAULT_TIMEOUT_MS = 5000;
  const MIN_POLL_INTERVAL_MS = 15000;

  function versionedSource(source, cacheBust) {
    if (!cacheBust) return source;
    const separator = source.includes("?") ? "&" : "?";
    return `${source}${separator}v=${encodeURIComponent(cacheBust)}`;
  }

  function loadScript(source, cacheBust, kind) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = versionedSource(source, cacheBust);
      script.async = false;
      script.dataset.apiDataLoader = kind;
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener(
        "error",
        () => reject(new Error(`无法加载脚本：${source}`)),
        { once: true },
      );
      document.body.appendChild(script);
    });
  }

  function validPayload(payload) {
    return Boolean(payload) && typeof payload === "object";
  }

  async function fetchJson(endpoint, timeoutMs) {
    if (typeof global.fetch !== "function") {
      throw new Error("当前浏览器不支持 Fetch API");
    }

    const controller = typeof global.AbortController === "function"
      ? new global.AbortController()
      : null;
    const timer = controller
      ? global.setTimeout(() => controller.abort(), timeoutMs)
      : null;

    try {
      const response = await global.fetch(endpoint, {
        cache: "no-store",
        credentials: "same-origin",
        headers: { Accept: "application/json" },
        signal: controller?.signal,
      });
      if (!response.ok) {
        throw new Error(`API 返回 HTTP ${response.status}`);
      }
      const payload = await response.json();
      if (!validPayload(payload)) {
        throw new Error("API 返回的数据结构无效");
      }
      return payload;
    } finally {
      if (timer) global.clearTimeout(timer);
    }
  }

  function updateState(state) {
    global.PALM_OIL_DATA_LOAD_STATE = Object.freeze({ ...state });
    document.documentElement.dataset.marketDataSource = state.source || "error";
    document.documentElement.dataset.marketDataStatus = state.status;
    document.dispatchEvent(new CustomEvent("palm-oil:data-load-state", { detail: state }));
  }

  function payloadFingerprint(payload) {
    try {
      return JSON.stringify(payload);
    } catch (_error) {
      return "";
    }
  }

  function scheduleRefresh(options, initialPayload, initialSource) {
    const interval = Number(options.pollIntervalMs);
    if (!Number.isFinite(interval) || interval < MIN_POLL_INTERVAL_MS) return;

    let fingerprint = payloadFingerprint(initialPayload);
    global.setInterval(async () => {
      if (document.visibilityState === "hidden") return;
      try {
        const payload = await fetchJson(options.endpoint, options.timeoutMs);
        const nextFingerprint = payloadFingerprint(payload);
        if (initialSource !== "api" || nextFingerprint !== fingerprint) {
          global[options.globalName] = payload;
          fingerprint = nextFingerprint;
          updateState({
            status: "updating",
            source: "api",
            endpoint: options.endpoint,
            globalName: options.globalName,
          });
          document.dispatchEvent(
            new CustomEvent("palm-oil:data-updated", {
              detail: { endpoint: options.endpoint, globalName: options.globalName },
            }),
          );
          global.location.reload();
        }
      } catch (error) {
        updateState({
          status: "ready",
          source: initialSource,
          endpoint: options.endpoint,
          globalName: options.globalName,
          lastRefreshError: String(error.message || error),
        });
      }
    }, interval);
  }

  async function boot(options) {
    const {
      endpoint,
      globalName,
      fallbackSrc,
      consumerSrc,
      cacheBust = Date.now(),
      timeoutMs = DEFAULT_TIMEOUT_MS,
      pollIntervalMs = 0,
    } = options || {};

    if (!endpoint || !globalName || !fallbackSrc || !consumerSrc) {
      throw new Error("行情数据加载配置不完整");
    }

    updateState({ status: "loading", source: "", endpoint, globalName });

    let source = "api";
    let apiError = null;
    try {
      global[globalName] = await fetchJson(endpoint, timeoutMs);
    } catch (error) {
      source = "static";
      apiError = error;
      await loadScript(fallbackSrc, cacheBust, "fallback");
      const fallbackData = global[globalName];
      if (!validPayload(fallbackData)) {
        throw new Error(`静态回退数据未提供 ${globalName}`);
      }
    }

    const state = {
      status: "rendering",
      source,
      endpoint,
      globalName,
      apiError: apiError ? String(apiError.message || apiError) : "",
    };
    updateState(state);
    await loadScript(consumerSrc, cacheBust, "consumer");
    const readyState = { ...state, status: "ready" };
    updateState(readyState);
    scheduleRefresh(
      { endpoint, globalName, timeoutMs, pollIntervalMs },
      global[globalName],
      source,
    );
    return readyState;
  }

  global.PalmOilDataLoader = Object.freeze({
    boot(options) {
      return boot(options).catch((error) => {
        updateState({
          status: "error",
          source: "error",
          endpoint: options?.endpoint || "",
          globalName: options?.globalName || "",
          error: String(error.message || error),
        });
        global.console?.error("动态数据加载失败", error);
        return null;
      });
    },
  });
})(window);
