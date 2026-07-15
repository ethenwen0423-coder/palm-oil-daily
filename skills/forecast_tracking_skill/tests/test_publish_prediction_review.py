import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "publish_prediction_review.sh"


class PublishPredictionReviewTest(unittest.TestCase):
    date = "2026-07-14"

    def fixture(self, **overrides: str) -> tuple[Path, Path, dict[str, str]]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "scripts").mkdir()
        shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
        fake_bin = root / "fake-bin"
        fake_bin.mkdir()
        log = root / "git.log"
        state = root / "staged.state"
        fake_git = fake_bin / "git"
        fake_git.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import os
                import pathlib
                import sys

                args = sys.argv[1:]
                pathlib.Path(os.environ["FAKE_GIT_LOG"]).open("a", encoding="utf-8").write(" ".join(args) + "\\n")

                def emit(raw: str) -> None:
                    if raw:
                        sys.stdout.buffer.write(b"\\0".join(item.encode() for item in raw.split("|")) + b"\\0")

                joined = " ".join(args)
                state = pathlib.Path(os.environ["FAKE_GIT_STATE"])
                if args[:1] == ["diff"] and "--cached --name-only -z" in joined:
                    emit(os.environ.get("FAKE_STAGED_AFTER" if state.exists() else "FAKE_OUTSIDE_STAGED", ""))
                    raise SystemExit(0)
                if "status --porcelain=v1 -z" in joined:
                    emit(os.environ.get("FAKE_STATUS_ENTRIES", ""))
                    raise SystemExit(0)
                if args[:1] == ["add"]:
                    state.touch()
                    raise SystemExit(int(os.environ.get("FAKE_ADD_EXIT", "0")))
                if args[:1] == ["commit"]:
                    raise SystemExit(int(os.environ.get("FAKE_COMMIT_EXIT", "0")))
                if args[:1] == ["push"]:
                    raise SystemExit(int(os.environ.get("FAKE_PUSH_EXIT", "0")))
                if args == ["branch", "--show-current"]:
                    print(os.environ.get("FAKE_BRANCH", "main"))
                    raise SystemExit(0)
                if args == ["rev-parse", "HEAD"]:
                    print(os.environ.get("FAKE_SHA", "0123456789abcdef"))
                    raise SystemExit(0)
                raise SystemExit(99)
                """
            ),
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
        env = {
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "FAKE_GIT_LOG": str(log),
            "FAKE_GIT_STATE": str(state),
            **overrides,
        }
        return root, log, env

    def run_script(self, root: Path, env: dict[str, str], *arguments: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            ["bash", f"scripts/{SCRIPT.name}", *arguments],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_dry_run_performs_no_git_write(self) -> None:
        candidate = f"data/forecast/evaluated/{self.date}.json"
        root, log, env = self.fixture(FAKE_STATUS_ENTRIES=f"?? {candidate}")
        result, payload = self.run_script(root, env, "--dry-run", "--date", self.date)
        calls = log.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["candidate_files"], [candidate])
        self.assertFalse(payload["git_write_operations_performed"])
        self.assertNotIn("add --", calls)
        self.assertNotIn("commit", calls)
        self.assertNotIn("push", calls)

    def test_publish_requires_both_publish_and_confirmation(self) -> None:
        for arguments in (
            ("--publish", "--date", self.date),
            ("--dry-run", "--confirm-persistence-reviewed", "--date", self.date),
            ("--confirm-persistence-reviewed", "--date", self.date),
        ):
            with self.subTest(arguments=arguments):
                root, log, env = self.fixture()
                result, payload = self.run_script(root, env, *arguments)
                calls = log.read_text(encoding="utf-8") if log.exists() else ""
                if arguments[0] == "--dry-run":
                    self.assertEqual(result.returncode, 0)
                else:
                    self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("add --", calls)
                self.assertNotIn("commit", calls)
                self.assertNotIn("push", calls)
                if arguments[0] == "--publish":
                    self.assertEqual(payload["stage"], "confirmation")

    def test_allowlisted_publish_stages_commits_and_pushes_current_branch(self) -> None:
        candidate = f"data/forecast/evaluated/{self.date}.json"
        root, log, env = self.fixture(
            FAKE_STATUS_ENTRIES=f"?? {candidate}",
            FAKE_STAGED_AFTER=candidate,
            FAKE_BRANCH="feature/review",
            FAKE_SHA="abc123",
        )
        result, payload = self.run_script(
            root,
            env,
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            self.date,
        )
        calls = log.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"add -- {candidate}", calls)
        self.assertIn(f"commit -m Update prediction review {self.date}", calls)
        self.assertIn("push origin feature/review", calls)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["commit_sha"], "abc123")
        self.assertEqual(payload["branch"], "feature/review")
        self.assertEqual(payload["committed_files"], [candidate])
        self.assertEqual(payload["push_status"], "ok")

    def test_non_allowlisted_staged_file_blocks_before_git_write(self) -> None:
        outside = f"reports/{self.date}.md"
        root, log, env = self.fixture(FAKE_OUTSIDE_STAGED=outside)
        result, payload = self.run_script(
            root,
            env,
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            self.date,
        )
        calls = log.read_text(encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["stage"], "preflight")
        self.assertIn(outside, payload["non_allowlisted_staged_files"])
        self.assertNotIn("add --", calls)
        self.assertNotIn("commit", calls)
        self.assertNotIn("push", calls)

    def test_no_data_changes_is_noop(self) -> None:
        root, log, env = self.fixture()
        result, payload = self.run_script(
            root,
            env,
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            self.date,
        )
        calls = log.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "noop")
        self.assertEqual(payload["reason"], "no prediction-review data changes")
        self.assertNotIn("add --", calls)
        self.assertNotIn("commit", calls)
        self.assertNotIn("push", calls)

    def test_allowlisted_retention_deletion_is_committed(self) -> None:
        deleted = "data/review/daily/2026-01-05.json"
        root, log, env = self.fixture(
            FAKE_STATUS_ENTRIES=f" D {deleted}",
            FAKE_STAGED_AFTER=deleted,
        )
        result, payload = self.run_script(
            root,
            env,
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            self.date,
        )
        calls = log.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"add -- {deleted}", calls)
        self.assertEqual(payload["committed_files"], [deleted])

    def test_generation_feedback_is_allowlisted(self) -> None:
        candidate = "data/forecast/feedback/latest.json"
        root, log, env = self.fixture(
            FAKE_STATUS_ENTRIES=f"?? {candidate}",
            FAKE_STAGED_AFTER=candidate,
        )
        result, payload = self.run_script(
            root,
            env,
            "--publish",
            "--confirm-persistence-reviewed",
            "--date",
            self.date,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["committed_files"], [candidate])


if __name__ == "__main__":
    unittest.main()
