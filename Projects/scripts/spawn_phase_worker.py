#!/usr/bin/env python3
"""03c: spawn a worktree for a phase that is currently eligible.

Usage:
    python Projects/scripts/spawn_phase_worker.py PROJ-XX <phase_id>

Verifies eligibility via phase_dag.eligible(); refuses if the phase is not
eligible right now. Creates a phase branch from the project tip if it does
not exist, then `git worktree add`s a worktree at
.worktrees/phases/PROJ-XX/<phase_id>/.

Writes a small worker-context file at
.agent_reports/proj-phase-session/PROJ-XX/<phase_id>/context.md.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from phase_workflow import dag as dag_mod
from phase_workflow import git_ops
from phase_workflow import state as state_mod

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
ACTIVE_DIR = PROJECT_ROOT / "Projects" / "active_projects"


def _state_path(project_id: str) -> Path:
    return ACTIVE_DIR / project_id / "phase_state.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="03c phase worker spawn")
    parser.add_argument("project_id")
    parser.add_argument("phase_id")
    parser.add_argument(
        "--repo",
        default=str(PROJECT_ROOT),
        help="Path to the git repository (default: project root)",
    )
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

    eligible = dag_mod.eligible(s)
    if args.phase_id not in eligible:
        print(
            f"phase {args.phase_id!r} is not currently eligible. "
            f"Eligible now: {eligible}",
            file=sys.stderr,
        )
        return 3

    project_branch = s["project_branch"]
    phase_branch = f"{project_branch.rsplit('/', 1)[0]}/{args.phase_id}"

    # Ensure project branch exists.
    if not git_ops.branch_exists(repo, project_branch):
        print(
            f"project branch {project_branch!r} does not exist. "
            f"Create it manually or via the project-start flow before spawning phase workers.",
            file=sys.stderr,
        )
        return 4

    # Create phase branch if it does not exist; resolve base SHA either way.
    if not git_ops.branch_exists(repo, phase_branch):
        git_ops.create_branch(repo, phase_branch, base_ref=project_branch)
    base_sha = git_ops.current_sha(repo, phase_branch)

    worktree_path = (
        PROJECT_ROOT / ".worktrees" / "phases" / args.project_id / args.phase_id
    )
    if worktree_path.exists():
        print(
            f"worktree already exists at {worktree_path}. "
            f"Remove it (git worktree remove --force) or pick another phase.",
            file=sys.stderr,
        )
        return 5

    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    git_ops.worktree_add(repo, worktree_path, ref=phase_branch)

    # Persist branch + base SHA + status into state.
    with state_mod.locked(state_path):
        s = state_mod.load_state(state_path)
        state_mod.set_phase_branch(
            s, args.phase_id, phase_branch=phase_branch, phase_base_sha=base_sha
        )
        state_mod.set_phase_status(s, args.phase_id, "in_progress")
        state_mod.save_state(state_path, s)

    # Write worker context.
    session_dir = (
        PROJECT_ROOT
        / ".agent_reports"
        / "proj-phase-session"
        / args.project_id
        / args.phase_id
    )
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "context.md").write_text(
        f"# Phase worker context: {args.project_id} / {args.phase_id}\n"
        f"\n"
        f"- Spawned at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- Phase branch: `{phase_branch}`\n"
        f"- Phase base SHA: `{base_sha}`\n"
        f"- Worktree: `{worktree_path}`\n"
        f"- Project branch: `{project_branch}`\n"
        f"\n"
        f"## Responsibilities\n"
        f"- TDD inner loop per Projects/protocols/03a_continue_working.md.\n"
        f"- Edit only your own phase_<id>_checklist.md, code, tests, and this session file.\n"
        f"- Do NOT touch plan.md, manifest.md, phase_state.json, findings_ledger.md.\n"
        f"- When done: `python Projects/scripts/phase_complete.py {args.project_id} {args.phase_id} --repo {worktree_path}`.\n",
        encoding="utf-8",
    )

    print(f"spawned: phase={args.phase_id} branch={phase_branch} worktree={worktree_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
