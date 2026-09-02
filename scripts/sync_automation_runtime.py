#!/usr/bin/env python3
"""Safely reconcile an automation runtime with origin/main.

Automation runtimes may have local generated-data commits when source changes
land on origin/main. They may also have uncommitted generated outputs from a
collector that ran before the next source sync. This helper preserves both
kinds of generated output; it refuses to rewrite or publish local source-code
changes.
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


def worktree_paths(root: Path) -> list[str]:
    commands = (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    )
    paths: set[str] = set()
    for arguments in commands:
        output = git_output(root, *arguments)
        paths.update(line.strip() for line in output.splitlines() if line.strip())
    return sorted(paths)


def validate_runtime(root: Path, branch: str) -> list[str]:
    if not (root / ".git").exists():
        raise SyncError(f"automation runtime is not a Git checkout: {root}")
    current = git_output(root, "branch", "--show-current")
    if current != branch:
        raise SyncError(
            f"automation runtime must be on {branch}, current branch is {current or 'detached'}"
        )
    dirty_paths = worktree_paths(root)
    validate_generated_only(dirty_paths, context="uncommitted source changes")
    return dirty_paths


def local_commit_paths(root: Path, remote_ref: str) -> list[str]:
    merge_base = git_output(root, "merge-base", "HEAD", remote_ref)
    output = git_output(root, "diff", "--name-only", f"{merge_base}..HEAD")
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def validate_generated_only(
    paths: list[str],
    *,
    context: str = "local source changes",
) -> None:
    rejected = [
        path
        for path in paths
        if not any(path.startswith(prefix) for prefix in ALLOWED_LOCAL_PREFIXES)
    ]
    if rejected:
        raise SyncError(
            f"refusing to reconcile {context}: " + ", ".join(rejected)
        )


def stash_worktree(root: Path) -> str:
    result = git(
        root,
        "stash",
        "push",
        "--include-untracked",
        "--message",
        "automation-runtime-sync",
    )
    if result.returncode != 0:
        raise SyncError(result.stderr.strip() or "failed to preserve generated worktree")
    return git_output(root, "rev-parse", "refs/stash")


def drop_stash(root: Path, stash_oid: str) -> None:
    output = git_output(root, "stash", "list", "--format=%H")
    for index, oid in enumerate(output.splitlines()):
        if oid.strip() != stash_oid:
            continue
        result = git(root, "stash", "drop", f"stash@{{{index}}}")
        if result.returncode != 0:
            raise SyncError(result.stderr.strip() or "failed to drop restored stash")
        return
    raise SyncError(f"preserved generated worktree stash disappeared: {stash_oid}")


def restore_worktree(root: Path, stash_oid: str) -> None:
    result = git(root, "stash", "apply", "--index", stash_oid)
    if result.returncode != 0:
        raise SyncError(
            "generated worktree was preserved but could not be restored cleanly; "
            f"recover it from stash {stash_oid}: "
            + (result.stderr.strip() or result.stdout.strip() or "stash apply failed")
        )
    drop_stash(root, stash_oid)


def remote_changed_paths(root: Path, remote_ref: str) -> list[str]:
    merge_base = git_output(root, "merge-base", "HEAD", remote_ref)
    output = git_output(root, "diff", "--name-only", f"{merge_base}..{remote_ref}")
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def fetch(root: Path, remote: str, branch: str) -> None:
    result = git(root, "fetch", remote, branch, timeout=180)
    if result.returncode != 0:
        raise SyncError(result.stderr.strip() or "git fetch failed")


def push(root: Path, remote: str, branch: str) -> bool:
    return git(root, "push", remote, f"HEAD:{branch}", timeout=180).returncode == 0


def reconcile_once(
    root: Path,
    remote: str,
    branch: str,
    *,
    preserved_worktree_paths: list[str] | None = None,
) -> dict[str, Any]:
    fetch(root, remote, branch)
    remote_ref = f"{remote}/{branch}"
    head = git_output(root, "rev-parse", "HEAD")
    remote_head = git_output(root, "rev-parse", remote_ref)
    if head == remote_head:
        return {"status": "ok", "action": "already_current", "head": head}

    preserved = set(preserved_worktree_paths or [])
    overlap = sorted(preserved.intersection(remote_changed_paths(root, remote_ref)))
    if overlap:
        raise SyncError(
            "generated worktree overlaps upstream changes; preserved without synchronization: "
            + ", ".join(overlap)
        )

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
    dirty_paths = validate_runtime(root, branch)
    stash_oid = stash_worktree(root) if dirty_paths else None
    result: dict[str, Any] | None = None
    sync_error: BaseException | None = None
    try:
        last: dict[str, Any] = {"status": "retry", "action": "not_started"}
        for attempt in range(1, attempts + 1):
            last = reconcile_once(
                root,
                remote,
                branch,
                preserved_worktree_paths=dirty_paths,
            )
            if last["status"] == "ok":
                result = {**last, "attempt": attempt}
                break
            if attempt < attempts:
                time.sleep(attempt * 2)
        if result is None:
            raise SyncError(
                f"remote advanced during all {attempts} synchronization attempts"
            )
    except BaseException as exc:
        sync_error = exc
    finally:
        if stash_oid:
            try:
                restore_worktree(root, stash_oid)
            except BaseException as exc:
                if sync_error is not None:
                    raise SyncError(f"{sync_error}; additionally, {exc}") from exc
                raise
    if sync_error is not None:
        raise sync_error
    assert result is not None
    if dirty_paths:
        result["preserved_worktree_paths"] = dirty_paths
    return result


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
