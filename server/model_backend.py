#!/usr/bin/env python3
"""Small, dependency-free structured-output client for unattended AI jobs."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROVIDERS = {
    "codex": {
        "style": "codex-cli",
        "endpoint": "",
        "model": "gpt-5.6-terra",
        "key_names": (),
    },
    "openai": {
        "style": "responses",
        "endpoint": "https://api.openai.com/v1/responses",
        "model": "gpt-5.2",
        "key_names": ("PALM_OIL_AI_API_KEY", "OPENAI_API_KEY"),
    },
    "custom": {
        "style": "chat-completions",
        "endpoint": "",
        "model": "",
        "key_names": ("PALM_OIL_AI_API_KEY",),
    },
}


class ModelBackendError(RuntimeError):
    """Raised when the configured model backend cannot return valid JSON."""


def provider_name() -> str:
    configured = os.environ.get("PALM_OIL_AI_PROVIDER", "").strip().lower()
    if configured:
        return configured
    return "openai"


def _provider_defaults() -> dict[str, Any]:
    provider = provider_name()
    defaults = PROVIDERS.get(provider)
    if defaults is None:
        raise ModelBackendError(f"unsupported AI provider: {provider}")
    return defaults


def resolve_api_key() -> str:
    defaults = _provider_defaults()
    for name in defaults["key_names"]:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise ModelBackendError(f"{provider_name()} API key is not configured")


def _codex_environment() -> dict[str, str]:
    environment = dict(os.environ)
    # A Codex-provider run must never silently fall back to usage-based API auth.
    for name in (
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "PALM_OIL_AI_API_KEY",
        "DEEPSEEK_API_KEY",
    ):
        environment.pop(name, None)
    return environment


def _codex_binary() -> str:
    configured = os.environ.get("CODEX_BIN", "").strip()
    executable = configured if configured and os.access(configured, os.X_OK) else ""
    executable = executable or shutil.which("codex") or ""
    if not executable:
        raise ModelBackendError("official Codex CLI is not installed")
    return executable


def _codex_chatgpt_authenticated(executable: str) -> bool:
    try:
        completed = subprocess.run(
            [executable, "login", "status"],
            env=_codex_environment(),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    status = f"{completed.stdout}\n{completed.stderr}".lower()
    return completed.returncode == 0 and "chatgpt" in status


def backend_configured() -> bool:
    try:
        resolve_config(require_key=True)
    except ModelBackendError:
        return False
    return True


def resolve_config(*, require_key: bool = True) -> dict[str, str]:
    provider = provider_name()
    defaults = _provider_defaults()
    style = os.environ.get("PALM_OIL_AI_API_STYLE", defaults["style"]).strip()
    endpoint = os.environ.get("PALM_OIL_AI_ENDPOINT", defaults["endpoint"]).strip()
    model = os.environ.get("PALM_OIL_AI_MODEL", defaults["model"]).strip()
    if style not in {"responses", "chat-completions", "codex-cli"}:
        raise ModelBackendError(f"unsupported AI API style: {style}")
    if style != "codex-cli" and not endpoint.startswith("https://"):
        raise ModelBackendError("AI endpoint must use HTTPS")
    if not model:
        raise ModelBackendError("AI model is not configured")
    api_key = ""
    codex_bin = ""
    if style == "codex-cli":
        codex_bin = _codex_binary()
        if require_key and not _codex_chatgpt_authenticated(codex_bin):
            raise ModelBackendError(
                "Codex CLI is not authenticated with ChatGPT subscription access"
            )
    elif require_key:
        api_key = resolve_api_key()
    return {
        "provider": provider,
        "style": style,
        "endpoint": endpoint,
        "model": model,
        "api_key": api_key,
        "codex_bin": codex_bin,
        "backend": (
            "codex-chatgpt-cli" if style == "codex-cli" else f"{provider}-{style}"
        ),
    }


def _request_codex(
    *,
    config: dict[str, str],
    schema: dict[str, Any],
    prompt: str,
    timeout: int,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="palm-oil-codex.") as temporary:
        work_root = Path(temporary)
        schema_path = work_root / "schema.json"
        output_path = work_root / "result.json"
        schema_path.write_text(
            json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        command = [
            config["codex_bin"],
            "exec",
            "-",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "--model",
            config["model"],
            "--cd",
            str(work_root),
        ]
        for feature in (
            "apps",
            "browser_use",
            "computer_use",
            "image_generation",
            "multi_agent",
            "plugins",
            "shell_tool",
        ):
            command.extend(["--disable", feature])
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                env=_codex_environment(),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ModelBackendError("Codex subscription task timed out") from exc
        except OSError as exc:
            raise ModelBackendError("Codex subscription task could not start") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "unknown error").strip()
            raise ModelBackendError(
                "Codex subscription task failed: " + detail[-600:]
            )
        try:
            output = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ModelBackendError("Codex did not return valid structured JSON") from exc
    if not isinstance(output, dict):
        raise ModelBackendError("Codex output must be a JSON object")
    return output


def _responses_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    fragments: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if isinstance(part, dict) and part.get("type") == "output_text":
                value = part.get("text")
                if isinstance(value, str):
                    fragments.append(value)
    text = "".join(fragments).strip()
    if not text:
        raise ModelBackendError("model did not return structured text")
    return text


def _chat_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ModelBackendError("model did not return a chat completion")
    first = choices[0]
    message = first.get("message") if isinstance(first, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ModelBackendError("model returned empty structured text")
    return content.strip()


def request_json(
    *,
    schema: dict[str, Any],
    schema_name: str,
    prompt: str,
    timeout: int,
    verbosity: str = "medium",
    model: str | None = None,
) -> tuple[dict[str, Any], str]:
    config = resolve_config(require_key=True)
    if model:
        config["model"] = model.strip()
    if config["style"] == "codex-cli":
        return (
            _request_codex(
                config=config,
                schema=schema,
                prompt=prompt,
                timeout=timeout,
            ),
            config["backend"],
        )
    if config["style"] == "responses":
        body: dict[str, Any] = {
            "model": config["model"],
            "input": prompt,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
                "verbosity": verbosity,
            },
        }
    else:
        schema_prompt = (
            f"{prompt}\n\nOUTPUT_JSON_SCHEMA（只能输出符合此结构的 JSON 对象）：\n"
            + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        )
        body = {
            "model": config["model"],
            "messages": [{"role": "user", "content": schema_prompt}],
            "response_format": {"type": "json_object"},
            "max_tokens": int(os.environ.get("PALM_OIL_AI_MAX_TOKENS", "8192")),
        }
    request = urllib.request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ModelBackendError(
            f"{config['provider']} API request failed (HTTP {exc.code})"
        ) from exc
    except (OSError, TimeoutError) as exc:
        raise ModelBackendError(
            f"{config['provider']} API request timed out or network failed"
        ) from exc
    try:
        response_payload = json.loads(raw)
        text = (
            _responses_text(response_payload)
            if config["style"] == "responses"
            else _chat_text(response_payload)
        )
        output = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ModelBackendError("model did not return valid JSON") from exc
    if not isinstance(output, dict):
        raise ModelBackendError("model output must be a JSON object")
    return output, config["backend"]
