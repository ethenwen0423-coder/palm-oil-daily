import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sync_automation_runtime.py"


def run(*arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(arguments),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def git(cwd: Path, *arguments: str) -> str:
    result = run("git", *arguments, cwd=cwd)
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


class AutomationRuntimeSyncTests(unittest.TestCase):
    def make_repositories(self, base: Path) -> tuple[Path, Path, Path]:
        origin = base / "origin.git"
        seed = base / "seed"
        runtime = base / "runtime"
        actor = base / "actor"
        git(base, "init", "--bare", "--initial-branch=main", str(origin))
        git(base, "clone", str(origin), str(seed))
        for repository in (seed,):
            git(repository, "config", "user.name", "Automation Test")
            git(repository, "config", "user.email", "automation@example.com")
        (seed / "data").mkdir()
        (seed / "data" / "generated.json").write_text('{"version": 1}\n')
        (seed / "source.txt").write_text("source-v1\n")
        git(seed, "add", "--", "data/generated.json", "source.txt")
        git(seed, "commit", "-m", "seed")
        git(seed, "push", "origin", "main")
        git(base, "clone", str(origin), str(runtime))
        git(base, "clone", str(origin), str(actor))
        for repository in (runtime, actor):
            git(repository, "config", "user.name", "Automation Test")
            git(repository, "config", "user.email", "automation@example.com")
        return origin, runtime, actor

    def invoke(self, runtime: Path) -> subprocess.CompletedProcess[str]:
        return run(
            "python3",
            str(SCRIPT),
            "--root",
            str(runtime),
            "--attempts",
            "1",
            cwd=ROOT,
        )

    def test_diverged_generated_commit_is_rebased_and_pushed(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, runtime, actor = self.make_repositories(Path(temporary))
            (runtime / "data" / "generated.json").write_text('{"version": 2}\n')
            git(runtime, "add", "--", "data/generated.json")
            git(runtime, "commit", "-m", "generated data")
            (actor / "source.txt").write_text("source-v2\n")
            git(actor, "add", "--", "source.txt")
            git(actor, "commit", "-m", "source update")
            git(actor, "push", "origin", "main")

            result = self.invoke(runtime)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["action"], "rebased_and_pushed")
            self.assertEqual((runtime / "source.txt").read_text(), "source-v2\n")
            self.assertEqual(
                (runtime / "data" / "generated.json").read_text(),
                '{"version": 2}\n',
            )
            git(runtime, "fetch", "origin", "main")
            self.assertEqual(
                git(runtime, "rev-parse", "HEAD"),
                git(runtime, "rev-parse", "origin/main"),
            )

    def test_diverged_source_commit_is_rejected_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, runtime, actor = self.make_repositories(Path(temporary))
            (runtime / "local-source.py").write_text("unsafe = True\n")
            git(runtime, "add", "--", "local-source.py")
            git(runtime, "commit", "-m", "local source")
            local_head = git(runtime, "rev-parse", "HEAD")
            (actor / "source.txt").write_text("source-v2\n")
            git(actor, "add", "--", "source.txt")
            git(actor, "commit", "-m", "source update")
            git(actor, "push", "origin", "main")

            result = self.invoke(runtime)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("local-source.py", payload["reason"])
            self.assertEqual(git(runtime, "rev-parse", "HEAD"), local_head)
            self.assertFalse((runtime / ".git" / "rebase-merge").exists())


if __name__ == "__main__":
    unittest.main()
