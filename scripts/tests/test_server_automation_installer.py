import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "server" / "install_automation.sh"
AUDIT = ROOT / "server" / "audit_runtime.py"
REQUIREMENTS = ROOT / "server" / "requirements-market.txt"


class ServerAutomationInstallerTests(unittest.TestCase):
    def test_installer_shell_syntax_and_fail_closed_apply_contract(self):
        result = subprocess.run(
            ["bash", "-n", str(INSTALLER)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = INSTALLER.read_text(encoding="utf-8")
        self.assertIn('MODE="${1:---dry-run}"', script)
        self.assertIn('"--apply must run as root"', script)
        self.assertIn("server/sync_live_data.py", script)
        self.assertIn("compose.automation.yaml", script)
        self.assertIn("$LIVE_DATA_ROOT:/site/data:ro", script)
        self.assertIn('python3 -m venv --clear "$VENV_ROOT"', script)
        self.assertIn('"$VENV_ROOT/bin/python" -m pip --version', script)
        self.assertIn("systemd-analyze verify", script)
        self.assertIn("systemctl enable --now palm-oil-market-collector.timer", script)
        self.assertNotIn("systemctl enable --now palm-oil-ai-brief.timer", script)
        self.assertIn("AI service units installed but timer intentionally left disabled", script)

    def test_systemd_units_share_lock_and_only_write_scoped_runtime_paths(self):
        installer = INSTALLER.read_text(encoding="utf-8")
        market = (ROOT / "server" / "run_market_collector.py").read_text(
            encoding="utf-8"
        )
        ai = (ROOT / "server" / "run_ai_brief.py").read_text(encoding="utf-8")
        updater = (ROOT / "server" / "update-site.sh").read_text(encoding="utf-8")
        self.assertIn('state_root / "automation.lock"', market)
        self.assertIn('state_root / "automation.lock"', ai)
        self.assertIn('"$STATE_ROOT/automation.lock"', updater)
        self.assertIn("ProtectSystem=strict", installer)
        self.assertIn(
            "ReadWritePaths=$LIVE_DATA_ROOT $STATE_ROOT "
            "$MARKET_RUNTIME_ROOT $AI_RUNTIME_ROOT",
            installer,
        )
        self.assertIn("OnCalendar=*-*-* *:0/10:00", installer)

    def test_market_dependencies_are_pinned_to_the_verified_runtime(self):
        lines = {
            line.strip()
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        self.assertEqual(
            lines,
            {
                "akshare==1.18.45",
                "numpy==2.4.3",
                "pandas==3.0.1",
                "requests==2.32.5",
            },
        )

    def test_runtime_audit_probes_the_server_venv_when_present(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("server_audit_installer_test", AUDIT)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        version, modules = module.probe_python_modules(Path(sys.executable))
        self.assertTrue(version)
        self.assertEqual(set(modules), set(module.REQUIRED_PYTHON_MODULES))


if __name__ == "__main__":
    unittest.main()
