#!/usr/bin/env python3
"""03c: prune phase worktrees whose branches have merged into the project branch.

Usage:
    python Projects/scripts/cleanup_phase_worktrees.py PROJ-XX [--all]

Default: only prune worktrees whose branches are fully merged into the project
branch. With --all: prune any phase worktree that has no uncommitted changes,
regardless of merge status (use carefully).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from phase_workflow import git_ops
from phase_workflow import state as state_mod

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
ACTIVE_DIR = PROJECT_ROOT / "Projects" / "active_projects"


def _state_path(project_id: str) -> Path:
    return ACTIVE_DIR / project_id / "phase_state.json"


def _is_merged_into(repo: Path, ancestor_sha: str, descendant_branch: str) -> bool:
    """True if `ancestor_sha` is reachable from `descendant_branch`."""
    res = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor_sha, descendant_branch],
        cwd=str(repo),
        capture_output=True,
        text=True,
        shell=False,
    )
    return res.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="03c phase worktree cleanup")
    parser.add_argument("project_id")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Prune even non-merged worktrees (must still be clean)",
    )
    parser.add_argument("--repo", default=str(PROJECT_ROOT))
    args = parser.parse_args()

    state_path = _state_path(args.project_id)
    if not state_path.exists():
        print(f"phase_state.json not found at {state_path}", file=sys.stderr)
        return 2

    repo = Path(args.repo).resolve()
    s = state_mod.load_state(state_path)
    project_branch = s["project_branch"]

    base_dir = PROJECT_ROOT / ".worktrees" / "phases" / args.project_id
    if not base_dir.exists():
        print(f"no phase worktrees for {args.project_id}")
        return 0

    pruned = 0
    skipped = 0
    for wt in base_dir.iterdir():
        if not wt.is_dir():
            continue
        phase_id = wt.name
        phase = s["phases"].get(phase_id)
        if not phase:
            print(f"  skip {phase_id}: no state record")
            skipped += 1
            continue
        head_sha = phase.get("phase_head_sha")
        is_merged = head_sha and _is_merged_into(repo, head_sha, project_branch)
        if not is_merged and not args.all:
            print(f"  skip {phase_id}: phase head not merged into project branch")
            skipped += 1
            continue
        try:
            git_ops.worktree_remove(repo, wt, force=False)
            pruned += 1
            print(f"  pruned {phase_id} at {wt}")
        except git_ops.GitOpsError as e:
            print(f"  skip {phase_id}: {e}")
            skipped += 1
    print(f"done: pruned={pruned} skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
