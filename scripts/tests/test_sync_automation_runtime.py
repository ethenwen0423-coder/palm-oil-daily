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

    def test_dirty_generated_worktree_is_preserved_while_source_fast_forwards(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, runtime, actor = self.make_repositories(Path(temporary))
            (runtime / "data" / "generated.json").write_text('{"version": 2}\n')
            (runtime / "data" / "new.json").write_text('{"new": true}\n')
            (actor / "source.txt").write_text("source-v2\n")
            git(actor, "add", "--", "source.txt")
            git(actor, "commit", "-m", "source update")
            git(actor, "push", "origin", "main")

            result = self.invoke(runtime)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["action"], "fast_forwarded")
            self.assertEqual(
                payload["preserved_worktree_paths"],
                ["data/generated.json", "data/new.json"],
            )
            self.assertEqual((runtime / "source.txt").read_text(), "source-v2\n")
            self.assertEqual(
                (runtime / "data" / "generated.json").read_text(),
                '{"version": 2}\n',
            )
            self.assertEqual(
                (runtime / "data" / "new.json").read_text(),
                '{"new": true}\n',
            )
            self.assertEqual(git(runtime, "stash", "list"), "")

    def test_dirty_source_worktree_is_rejected_without_stashing_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, runtime, _ = self.make_repositories(Path(temporary))
            (runtime / "source.txt").write_text("unsafe\n")

            result = self.invoke(runtime)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("source.txt", payload["reason"])
            self.assertEqual((runtime / "source.txt").read_text(), "unsafe\n")
            self.assertEqual(git(runtime, "stash", "list"), "")

    def test_dirty_generated_overlap_is_restored_without_fast_forward(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, runtime, actor = self.make_repositories(Path(temporary))
            local_head = git(runtime, "rev-parse", "HEAD")
            (runtime / "data" / "generated.json").write_text('{"local": true}\n')
            (actor / "data" / "generated.json").write_text('{"remote": true}\n')
            git(actor, "add", "--", "data/generated.json")
            git(actor, "commit", "-m", "remote data update")
            git(actor, "push", "origin", "main")

            result = self.invoke(runtime)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("overlaps upstream changes", payload["reason"])
            self.assertEqual(git(runtime, "rev-parse", "HEAD"), local_head)
            self.assertEqual(
                (runtime / "data" / "generated.json").read_text(),
                '{"local": true}\n',
            )
            self.assertEqual(git(runtime, "stash", "list"), "")


if __name__ == "__main__":
    unittest.main()
