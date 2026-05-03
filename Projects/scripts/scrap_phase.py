#!/usr/bin/env python3
"""03c: scrap a phase and reset it to not_started.

Use when remediating a parent caused changes too large for the descendant
to rebase cleanly.

Usage:
    python Projects/scripts/scrap_phase.py PROJ-XX <phase_id> [--cascade] --reason "..."

Default behavior:
    - Pause descendants whose status is in_progress / committed / under_review.
    - Remove this phase's worktree (refuses if uncommitted changes).
    - Delete this phase's branch.
    - Reset phase to not_started; clear SHAs and review IDs; append scrap entry.

With --cascade: scrap descendants recursively.
"""
from __future__ import annotations

import argparse
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


def _descendants(state: dict, phase_id: str) -> list[str]:
    """All phases that transitively depend on phase_id."""
    out: list[str] = []
    queue = [phase_id]
    while queue:
        head = queue.pop(0)
        for pid, phase in state["phases"].items():
            if head in phase["depends_on"] and pid not in out:
                out.append(pid)
                queue.append(pid)
    return out


def _scrap_one(repo: Path, state: dict, phase_id: str, reason: str) -> None:
    phase = state["phases"][phase_id]
    branch = phase.get("phase_branch")
    worktree = (
        PROJECT_ROOT / ".worktrees" / "phases" / state["project_id"] / phase_id
    )
    if worktree.exists():
        try:
            git_ops.worktree_remove(repo, worktree, force=False)
        except git_ops.GitOpsError as e:
            print(f"refusing to scrap {phase_id}: {e}", file=sys.stderr)
            sys.exit(6)
    if branch and git_ops.branch_exists(repo, branch):
        git_ops.delete_branch(repo, branch, force=True)
    state_mod.record_scrap(state, phase_id, reason=reason)


def main() -> int:
    parser = argparse.ArgumentParser(description="03c phase scrap-and-restart")
    parser.add_argument("project_id")
    parser.add_argument("phase_id")
    parser.add_argument("--cascade", action="store_true", help="Scrap descendants too")
    parser.add_argument("--reason", required=True, help="Why this phase is being scrapped")
    parser.add_argument("--repo", default=str(PROJECT_ROOT))
    args = parser.parse_args()

    state_path = _state_path(args.project_id)
    if not state_path.exists():
        print(f"phase_state.json not found at {state_path}", file=sys.stderr)
        return 2

    repo = Path(args.repo).resolve()

    with state_mod.locked(state_path):
        s = state_mod.load_state(state_path)

        if args.phase_id not in s["phases"]:
            print(f"unknown phase {args.phase_id!r}", file=sys.stderr)
            return 2

        live_descendants = [
            d for d in _descendants(s, args.phase_id)
            if s["phases"][d]["status"] in ("in_progress", "committed", "under_review")
        ]

        if live_descendants and not args.cascade:
            for d in live_descendants:
                # Pause: revert to not_started but leave history annotated.
                state_mod.record_scrap(
                    s,
                    d,
                    reason=f"paused: ancestor {args.phase_id} scrapped, awaiting redo",
                )
            print(
                f"paused descendants (re-run scrap with --cascade to fully scrap): "
                f"{', '.join(live_descendants)}"
            )
        elif live_descendants and args.cascade:
            # Scrap deepest first so worktree teardown is safe.
            for d in reversed(live_descendants):
                _scrap_one(repo, s, d, reason=f"cascade: ancestor {args.phase_id} scrapped")

        # Now scrap the requested phase.
        _scrap_one(repo, s, args.phase_id, reason=args.reason)

        state_mod.save_state(state_path, s)

    print(f"scrapped {args.phase_id}; ready to respawn via spawn_phase_worker.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
