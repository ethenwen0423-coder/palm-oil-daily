#!/usr/bin/env python3
"""Safely reconcile a clean automation runtime with origin/main.

Automation runtimes may have local generated-data commits when source changes
land on origin/main. This helper preserves and rebases only generated outputs;
it refuses to rewrite or publish local source-code commits.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ALLOWED_LOCAL_PREFIXES = (
    "data/",
    "downloads/",
    "miniprogram/data/",
    "reports/",
)


class SyncError(RuntimeError):
    """Raised when the runtime cannot be reconciled without losing work."""


def git(
    root: Path,
    *arguments: str,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SyncError(f"git command failed to start: {arguments[0]}: {exc}") from exc


def git_output(root: Path, *arguments: str) -> str:
    result = git(root, *arguments)
    if result.returncode != 0:
        raise SyncError(
            result.stderr.strip()
            or result.stdout.strip()
            or f"git command failed: {' '.join(arguments)}"
        )
    return result.stdout.strip()


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return git(root, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def validate_runtime(root: Path, branch: str) -> None:
    if not (root / ".git").exists():
        raise SyncError(f"automation runtime is not a Git checkout: {root}")
    current = git_output(root, "branch", "--show-current")
    if current != branch:
        raise SyncError(
            f"automation runtime must be on {branch}, current branch is {current or 'detached'}"
        )
    dirty = git_output(root, "status", "--porcelain", "--untracked-files=all")
    if dirty:
        raise SyncError("automation runtime worktree must be clean before synchronization")


def local_commit_paths(root: Path, remote_ref: str) -> list[str]:
    merge_base = git_output(root, "merge-base", "HEAD", remote_ref)
    output = git_output(root, "diff", "--name-only", f"{merge_base}..HEAD")
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def validate_generated_only(paths: list[str]) -> None:
    rejected = [
        path
        for path in paths
        if not any(path.startswith(prefix) for prefix in ALLOWED_LOCAL_PREFIXES)
    ]
    if rejected:
        raise SyncError(
            "refusing to reconcile local source changes: " + ", ".join(rejected)
        )


def fetch(root: Path, remote: str, branch: str) -> None:
    result = git(root, "fetch", remote, branch, timeout=180)
    if result.returncode != 0:
        raise SyncError(result.stderr.strip() or "git fetch failed")


def push(root: Path, remote: str, branch: str) -> bool:
    return git(root, "push", remote, f"HEAD:{branch}", timeout=180).returncode == 0


def reconcile_once(root: Path, remote: str, branch: str) -> dict[str, Any]:
    fetch(root, remote, branch)
    remote_ref = f"{remote}/{branch}"
    head = git_output(root, "rev-parse", "HEAD")
    remote_head = git_output(root, "rev-parse", remote_ref)
    if head == remote_head:
        return {"status": "ok", "action": "already_current", "head": head}

    if is_ancestor(root, head, remote_head):
        result = git(root, "merge", "--ff-only", remote_ref)
        if result.returncode != 0:
            raise SyncError(result.stderr.strip() or "fast-forward merge failed")
        return {
            "status": "ok",
            "action": "fast_forwarded",
            "head": git_output(root, "rev-parse", "HEAD"),
        }

    paths = local_commit_paths(root, remote_ref)
    validate_generated_only(paths)
    if not is_ancestor(root, remote_head, head):
        result = git(root, "rebase", remote_ref, timeout=300)
        if result.returncode != 0:
            git(root, "rebase", "--abort")
            raise SyncError(
                result.stderr.strip()
                or "generated-data commits conflict with the latest source; rebase aborted"
            )
        action = "rebased_and_pushed"
    else:
        action = "pushed_pending_data"

    if not push(root, remote, branch):
        return {"status": "retry", "action": "remote_advanced"}
    return {
        "status": "ok",
        "action": action,
        "head": git_output(root, "rev-parse", "HEAD"),
        "generated_paths": paths,
    }


def synchronize(
    root: Path,
    *,
    remote: str = "origin",
    branch: str = "main",
    attempts: int = 3,
) -> dict[str, Any]:
    validate_runtime(root, branch)
    last: dict[str, Any] = {"status": "retry", "action": "not_started"}
    for attempt in range(1, attempts + 1):
        last = reconcile_once(root, remote, branch)
        if last["status"] == "ok":
            return {**last, "attempt": attempt}
        if attempt < attempts:
            time.sleep(attempt * 2)
    raise SyncError(f"remote advanced during all {attempts} synchronization attempts")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    try:
        payload = synchronize(
            args.root.resolve(),
            remote=args.remote,
            branch=args.branch,
            attempts=args.attempts,
        )
    except (OSError, SyncError) as exc:
        print(
            json.dumps(
                {"status": "error", "reason": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
