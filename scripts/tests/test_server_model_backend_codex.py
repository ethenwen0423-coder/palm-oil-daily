from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "model_backend.py"
SPEC = importlib.util.spec_from_file_location("server_model_backend_codex_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ServerModelBackendCodexTests(unittest.TestCase):
    def test_codex_provider_uses_chatgpt_auth_and_structured_read_only_exec(self):
        calls: list[tuple[list[str], dict[str, str]]] = []

        def fake_run(command, **kwargs):
            environment = kwargs.get("env", {})
            calls.append((list(command), dict(environment)))
            if command[1:3] == ["login", "status"]:
                return subprocess.CompletedProcess(
                    command, 0, "Logged in using ChatGPT\n", ""
                )
            output_index = command.index("--output-last-message") + 1
            Path(command[output_index]).write_text(
                json.dumps({"status": "ready"}), encoding="utf-8"
            )
            return subprocess.CompletedProcess(command, 0, "", "")

        environment = {
            "PALM_OIL_AI_PROVIDER": "codex",
            "OPENAI_API_KEY": "must-not-reach-codex",
            "CODEX_API_KEY": "must-not-reach-codex",
            "PATH": os.environ.get("PATH", ""),
        }
        with mock.patch.dict(os.environ, environment, clear=True), mock.patch.object(
            MODULE, "_codex_binary", return_value="/usr/local/bin/codex"
        ), mock.patch.object(MODULE.subprocess, "run", side_effect=fake_run):
            output, backend = MODULE.request_json(
                schema={"type": "object"},
                schema_name="test",
                prompt="Only analyze the supplied evidence.",
                timeout=30,
            )

        self.assertEqual(output, {"status": "ready"})
        self.assertEqual(backend, "codex-chatgpt-cli")
        exec_command, exec_environment = calls[1]
        self.assertIn("--ephemeral", exec_command)
        self.assertIn("--output-schema", exec_command)
        self.assertIn("read-only", exec_command)
        self.assertIn("--ignore-user-config", exec_command)
        self.assertNotIn("OPENAI_API_KEY", exec_environment)
        self.assertNotIn("CODEX_API_KEY", exec_environment)
        self.assertEqual(exec_environment["HOME"], "/srv/palm-oil-daily/state/home")
        self.assertEqual(
            exec_environment["CODEX_HOME"], "/srv/palm-oil-daily/state/home/.codex"
        )
        self.assertEqual(
            exec_environment["XDG_CACHE_HOME"], "/srv/palm-oil-daily/state/cache"
        )

    def test_codex_environment_uses_configured_server_state_root(self):
        with mock.patch.dict(
            os.environ,
            {"PALM_OIL_SERVER_STATE_ROOT": "/var/lib/palm-oil-state"},
            clear=True,
        ):
            environment = MODULE._codex_environment()

        self.assertEqual(environment["HOME"], "/var/lib/palm-oil-state/home")
        self.assertEqual(
            environment["CODEX_HOME"], "/var/lib/palm-oil-state/home/.codex"
        )
        self.assertEqual(
            environment["XDG_CACHE_HOME"], "/var/lib/palm-oil-state/cache"
        )

    def test_codex_provider_rejects_api_key_login(self):
        completed = subprocess.CompletedProcess(
            ["codex", "login", "status"], 0, "Logged in using an API key", ""
        )
        with mock.patch.dict(
            os.environ, {"PALM_OIL_AI_PROVIDER": "codex"}, clear=True
        ), mock.patch.object(
            MODULE, "_codex_binary", return_value="/usr/local/bin/codex"
        ), mock.patch.object(MODULE.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(
                MODULE.ModelBackendError, "ChatGPT subscription access"
            ):
                MODULE.resolve_config(require_key=True)


if __name__ == "__main__":
    unittest.main()
