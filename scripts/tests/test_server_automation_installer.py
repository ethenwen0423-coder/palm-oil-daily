import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "server" / "install_automation.sh"
AUDIT = ROOT / "server" / "audit_runtime.py"
REQUIREMENTS = ROOT / "server" / "requirements-market.txt"
AI_ENABLEMENT = ROOT / "server" / "enable_ai_automation.sh"


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
        self.assertIn('PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-private}"', script)
        self.assertIn('"--apply must run as root"', script)
        self.assertIn("server/sync_live_data.py", script)
        self.assertIn("server/enable_ai_automation.sh", script)
        self.assertIn("compose.automation.yaml", script)
        self.assertIn("$LIVE_DATA_ROOT:/site/data:ro", script)
        self.assertIn('python3 -m venv --clear "$VENV_ROOT"', script)
        self.assertIn('"$VENV_ROOT/bin/python" -m pip --version', script)
        self.assertIn("systemd-analyze verify", script)
        self.assertIn("systemctl enable --now palm-oil-market-collector.timer", script)
        self.assertIn("systemctl enable --now palm-oil-supply-demand.timer", script)
        self.assertIn("systemctl start palm-oil-supply-demand.service", script)
        self.assertNotIn("systemctl enable --now palm-oil-ai-brief.timer", script)
        self.assertIn("AI service units installed but timer intentionally left disabled", script)
        self.assertIn('if [[ "$PUBLIC_ACCESS_MODE" == "private" ]]', script)
        self.assertIn('stop web || true', script)
        self.assertIn('up -d --no-deps api', script)
        self.assertIn('--access-mode "$PUBLIC_ACCESS_MODE"', script)
        self.assertIn("Environment=CODEX_HOME=$STATE_ROOT/home/.codex", script)

    def test_systemd_units_share_lock_and_only_write_scoped_runtime_paths(self):
        installer = INSTALLER.read_text(encoding="utf-8")
        market = (ROOT / "server" / "run_market_collector.py").read_text(
            encoding="utf-8"
        )
        supply = (ROOT / "server" / "run_supply_demand.py").read_text(
            encoding="utf-8"
        )
        ai = (ROOT / "server" / "run_ai_brief.py").read_text(encoding="utf-8")
        updater = (ROOT / "server" / "update-site.sh").read_text(encoding="utf-8")
        self.assertIn('state_root / "automation.lock"', market)
        self.assertIn('state_root / "automation.lock"', supply)
        self.assertIn('state_root / "automation.lock"', ai)
        self.assertIn('"$STATE_ROOT/automation.lock"', updater)
        self.assertIn("ProtectSystem=strict", installer)
        self.assertIn(
            "ReadWritePaths=$LIVE_DATA_ROOT $STATE_ROOT "
            "$MARKET_RUNTIME_ROOT $AI_RUNTIME_ROOT",
            installer,
        )
        self.assertIn(
            "Environment=PATH=$VENV_ROOT/bin:/usr/local/sbin:/usr/local/bin:"
            "/usr/sbin:/usr/bin:/sbin:/bin",
            installer,
        )
        self.assertIn('"*-*-* *:0/10:00"', installer)
        self.assertIn('"*-*-* *:02/10:00"', installer)
        self.assertIn('"*-*-* 09:20:00 Asia/Shanghai"', installer)
        self.assertIn('PUBLIC_ACCESS_MODE="${PALM_OIL_PUBLIC_ACCESS_MODE:-private}"', updater)
        self.assertIn('compose exec -T api python3 -c', updater)
        self.assertIn('compose stop web || true', updater)

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

    def test_ai_timer_enablement_requires_login_and_real_generation(self):
        result = subprocess.run(
            ["bash", "-n", str(AI_ENABLEMENT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        script = AI_ENABLEMENT.read_text(encoding="utf-8")
        self.assertIn("login --device-auth", script)
        self.assertIn("login status", script)
        self.assertIn("systemctl disable --now palm-oil-ai-brief.timer", script)
        self.assertIn("run_ai_brief.py", script)
        self.assertIn(".server-ai-ready.json", script)
        self.assertIn("systemctl enable --now palm-oil-ai-brief.timer", script)
        self.assertNotIn("--mock-response", script)

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
