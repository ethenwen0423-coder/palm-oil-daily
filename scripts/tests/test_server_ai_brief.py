import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "server" / "run_ai_brief.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("server_ai_brief_test", SCRIPT)


def valid_brief() -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "ready",
        "source_fingerprint": "fingerprint",
        "source_snapshot": {"quant-model-signals": "2026-07-31 00:25"},
        "fixed_logic": ["otc_structure_library", "quant_model_rules"],
        "key_moves": [{"source": "quant-model-signals"}],
    }


class ServerAiBriefTests(unittest.TestCase):
    def test_validate_brief_requires_dynamic_quant_evidence_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "brief.json"
            path.write_text(json.dumps(valid_brief()), encoding="utf-8")
            self.assertEqual(
                RUNNER.validate_brief(path)["source_fingerprint"],
                "fingerprint",
            )
            payload = valid_brief()
            payload["source_snapshot"] = {}
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                RUNNER.AiBriefRunnerError,
                "dynamic quant-model output",
            ):
                RUNNER.validate_brief(path)

    def test_dry_run_with_mock_backend_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            site = base / "site"
            runtime = base / "runtime"
            live = base / "live"
            state = base / "state"
            mock_response = base / "model.json"
            site.mkdir()
            mock_response.write_text("{}\n", encoding="utf-8")
            before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--site-root",
                    str(site),
                    "--runtime-root",
                    str(runtime),
                    "--live-data-root",
                    str(live),
                    "--state-root",
                    str(state),
                    "--mock-response",
                    str(mock_response),
                    "--dry-run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["backend"], "mock")
        self.assertTrue(payload["first_generation_required"])
        self.assertEqual(before, after)

    def test_first_server_generation_is_forced_before_ai_ownership(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('state_root / "automation.lock"', script)
        self.assertIn('command.append("--force")', script)
        self.assertIn("sync_module.sync_ai(", script)
        self.assertLess(
            script.index('command.append("--force")'),
            script.index("sync_module.sync_ai("),
        )


if __name__ == "__main__":
    unittest.main()
