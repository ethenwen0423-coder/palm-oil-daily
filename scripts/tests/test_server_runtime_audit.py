import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "audit_runtime.py"
SPEC = importlib.util.spec_from_file_location("palm_server_runtime_audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)


class ServerRuntimeAuditTests(unittest.TestCase):
    def test_private_mode_listener_probe_ignores_loopback_only(self):
        output = "\n".join(
            (
                "LISTEN 0 4096 127.0.0.1:80 0.0.0.0:*",
                "LISTEN 0 4096 0.0.0.0:443 0.0.0.0:*",
                "LISTEN 0 4096 [::1]:443 [::]:*",
            )
        )
        completed = subprocess.CompletedProcess(["ss"], 0, output, "")
        with mock.patch.object(AUDIT.shutil, "which", return_value="/usr/bin/ss"), mock.patch.object(
            AUDIT, "run", return_value=completed
        ):
            listeners = AUDIT.public_web_listeners()
        self.assertEqual(listeners, ["0.0.0.0:443"])

    def test_remote_host_never_returns_embedded_credentials(self):
        self.assertEqual(
            AUDIT.remote_host("https://user:secret@example.com/org/repo.git"),
            "example.com",
        )
        self.assertEqual(
            AUDIT.remote_host("git@github.com:owner/repo.git"),
            "github.com",
        )

    def test_credential_inventory_exposes_booleans_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            deploy_root = Path(temporary)
            with mock.patch.dict(
                os.environ,
                {
                    "OPENAI_API_KEY": "super-secret-openai",
                    "GITHUB_TOKEN": "super-secret-github",
                },
            ):
                with mock.patch.object(AUDIT, "run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        ["codex", "login", "status"], 0, "Logged in", ""
                    )
                    with mock.patch.object(
                        AUDIT.shutil,
                        "which",
                        return_value="/usr/bin/codex",
                    ):
                        payload = AUDIT.credential_capabilities(
                            deploy_root,
                            deploy_root / "state",
                        )
        rendered = json.dumps(payload, sort_keys=True)
        self.assertTrue(payload["openai_api_key_present"])
        self.assertTrue(payload["github_token_present"])
        self.assertTrue(payload["codex_cli_authenticated"])
        self.assertNotIn("super-secret", rendered)

    def test_cli_is_read_only_and_returns_valid_json_when_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site_root = base / "site"
            deploy_root = base / "deploy"
            site_root.mkdir()
            deploy_root.mkdir()
            before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--site-root",
                    str(site_root),
                    "--deploy-root",
                    str(deploy_root),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["status"], "blocked")
        self.assertTrue(payload["read_only"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
