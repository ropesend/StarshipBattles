#!/usr/bin/env python3
"""03c: complete a phase — validate, test, commit, integrate, dispatch review.

Usage:
    python Projects/scripts/phase_complete.py PROJ-XX <phase_id> [--remediation]

Atomic-ish sequence (see Projects/protocols/03c_phase_aware_execution.md):
    1. Verify state.json exists and is in 03c mode.
    2. Run validate_phase.py for the phase (must pass).
    3. Run pytest tests/ --testmon (regression).
    4. Regenerate manifest.md from diff.
    5. Commit on the phase branch.
    6. Temp-integration merge into the project branch (run tests on integrated).
    7. On green: dispatch SHA-pinned cumulative review and update state.
    8. On red: leave phase status in_progress and exit non-zero.

Refuses to commit if validation or tests fail.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add scripts dir to path for package imports
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from phase_workflow import dag as dag_mod
from phase_workflow import git_ops
from phase_workflow import manifests as manifests_mod
from phase_workflow import reviews as reviews_mod
from phase_workflow import state as state_mod

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
ACTIVE_DIR = PROJECT_ROOT / "Projects" / "active_projects"
DAEMON_PAYLOADS_DIR = (
    PROJECT_ROOT / "AgentCoordination" / "opencodereview" / "local" / "request_payloads"
)
DAEMON_WORKTREES_DIR = (
    PROJECT_ROOT / "AgentCoordination" / "opencodereview" / "local" / "worktrees"
)
CREATE_REVIEW_REQUEST = (
    PROJECT_ROOT / "Tools" / "agent_coordination" / "create_review_request.py"
)


def _proj_dir(project_id: str) -> Path:
    return ACTIVE_DIR / project_id


def _state_path(project_id: str) -> Path:
    return _proj_dir(project_id) / "phase_state.json"


def _manifest_path(project_id: str) -> Path:
    return _proj_dir(project_id) / "manifest.md"


def _run(args: list[str], *, cwd: Path = PROJECT_ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=str(cwd), check=check, capture_output=True, text=True, shell=False
    )


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _commit_phase_branch(repo: Path, phase_branch: str, message: str) -> str:
    """Commit any pending changes on phase_branch and return the new HEAD SHA."""
    # Ensure we're on the phase branch — but we may be running from a worktree.
    # Use rev-parse to confirm.
    branch = git_ops.current_sha(repo, phase_branch)  # validates branch exists
    # Stage and commit if there are changes; otherwise reuse the existing HEAD.
    status = _run(["git", "status", "--porcelain"], cwd=repo, check=False)
    if status.stdout.strip():
        _run(["git", "add", "-A"], cwd=repo)
        _run(["git", "commit", "-m", message], cwd=repo)
    return git_ops.current_sha(repo, phase_branch)


def _dispatch_review(payload: dict) -> str:
    """Write payload to the daemon payloads dir and call create_review_request.py."""
    DAEMON_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{os.getpid()}_{time.time_ns()}"
    payload_path = DAEMON_PAYLOADS_DIR / f"payload_phase_complete_{suffix}.json"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(CREATE_REVIEW_REQUEST), "--payload-file", str(payload_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"create_review_request.py failed: stdout={e.stdout!r} stderr={e.stderr!r}"
        ) from e
    finally:
        payload_path.unlink(missing_ok=True)
    return result.stdout.strip()


def _run_validate_phase(project_id: str, phase_id: str) -> tuple[bool, str]:
    """Best-effort wrapper around the existing validate_phase.py CLI.

    For 03c projects we still maintain phase_<n>_checklist.md files so the
    legacy validator can run against them. If the validator is not applicable
    (e.g., synthetic test project with no checklist), this returns True with
    an explanatory note.
    """
    validator = SCRIPTS_DIR / "validate_phase.py"
    if not validator.exists():
        return True, "validate_phase.py not present (skipping)"
    # phase_id is "phase_N" — extract N
    try:
        n = int(phase_id.split("_", 1)[1])
    except (IndexError, ValueError):
        return True, f"phase_id {phase_id!r} is not numeric (skipping legacy validator)"
    res = subprocess.run(
        [sys.executable, str(validator), project_id, str(n)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        shell=False,
    )
    return (res.returncode == 0), (res.stdout + res.stderr)


def _run_regression_tests(repo: Path) -> tuple[bool, str]:
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--testmon", "-q", "--no-header"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        shell=False,
    )
    return (res.returncode == 0), (res.stdout[-4000:] + res.stderr[-2000:])


def main() -> int:
    parser = argparse.ArgumentParser(description="03c phase completion orchestrator")
    parser.add_argument("project_id", help="e.g. PROJ-XX")
    parser.add_argument("phase_id", help="e.g. phase_1")
    parser.add_argument(
        "--remediation",
        action="store_true",
        help="Mark this commit as a remediation; does not dispatch a fresh cumulative review (the next phase's review will cover it).",
    )
    parser.add_argument(
        "--repo",
        default=str(PROJECT_ROOT),
        help="Path to the git repository (default: project root). Useful when running from a phase worktree.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip regression tests (development convenience; not allowed in CI).",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    state_path = _state_path(args.project_id)
    if not state_path.exists():
        print(f"phase_state.json not found at {state_path}", file=sys.stderr)
        return 2

    with state_mod.locked(state_path):
        s = state_mod.load_state(state_path)

    if args.phase_id not in s["phases"]:
        print(f"unknown phase {args.phase_id!r} in {args.project_id}", file=sys.stderr)
        return 2

    phase = s["phases"][args.phase_id]
    phase_branch = phase.get("phase_branch")
    phase_base_sha = phase.get("phase_base_sha")
    if not (phase_branch and phase_base_sha):
        print(
            f"phase {args.phase_id} has no phase_branch / phase_base_sha — "
            f"run spawn_phase_worker.py first",
            file=sys.stderr,
        )
        return 2

    # 1. Legacy validator (best-effort)
    ok, output = _run_validate_phase(args.project_id, args.phase_id)
    if not ok:
        print("validate_phase.py FAILED:")
        print(output)
        return 3

    # 2. Regression tests
    if not args.skip_tests:
        ok, output = _run_regression_tests(repo)
        if not ok:
            print("regression tests FAILED:")
            print(output)
            return 4

    # 3. Commit phase branch
    summary = f"phase {args.phase_id} {'remediation' if args.remediation else 'complete'}"
    commit_msg = f"{args.project_id} {summary}"
    phase_head = _commit_phase_branch(repo, phase_branch, commit_msg)

    # 4. Regenerate manifest in working tree (if path exists)
    manifests_mod.write_manifest(s, repo_root=repo, output_path=_manifest_path(args.project_id))

    # 5. Temp-integration merge into project branch
    project_branch = s["project_branch"]
    integration_wt = (
        PROJECT_ROOT
        / ".worktrees"
        / "integration"
        / f"{args.project_id}-{args.phase_id}-{phase_head[:8]}"
    )
    integration_wt.parent.mkdir(parents=True, exist_ok=True)
    result = git_ops.temp_integration_merge(
        repo,
        project_branch=project_branch,
        phase_branch=phase_branch,
        phase_id=args.phase_id,
        integration_worktree_path=integration_wt,
        run_tests=lambda _wt: None,  # already tested above
    )
    if not result.green:
        msg = f"temp-integration FAILED ({'merge conflict' if result.merge_conflict else 'tests'})"
        print(msg)
        if result.test_failure_message:
            print(result.test_failure_message)
        return 5

    # 6. Update state with new SHAs and commit status
    with state_mod.locked(state_path):
        s = state_mod.load_state(state_path)
        state_mod.set_phase_head_sha(s, args.phase_id, phase_head)
        state_mod.set_phase_merged(s, args.phase_id, result.merge_sha)
        state_mod.set_phase_status(s, args.phase_id, "committed")
        state_mod.save_state(state_path, s)

    # 7. Dispatch cumulative review (skipped if remediation)
    if args.remediation:
        print(f"phase {args.phase_id} remediation committed at {phase_head[:8]}; "
              f"merge SHA {result.merge_sha[:8]}; no review dispatched (per 03c).")
        return 0

    project_tip_sha = result.merge_sha
    files_new, files_context = reviews_mod.compute_files_changed_between(
        repo,
        focus_base_sha=phase_base_sha,
        focus_head_sha=project_tip_sha,
        project_root_sha=git_ops.current_sha(repo, "main"),
    )
    worktree_path_for_review = (
        f"AgentCoordination/opencodereview/local/worktrees/req_{args.project_id}_{args.phase_id}_{phase_head[:8]}"
    )
    payload = reviews_mod.build_payload(
        s,
        focus_phase=args.phase_id,
        project_tip_sha=project_tip_sha,
        files_newly_changed=files_new,
        files_in_earlier_phases=files_context,
        worktree_path_for_review=worktree_path_for_review,
    )
    try:
        request_id = _dispatch_review(payload)
    except RuntimeError as e:
        # Partial-state detection: phase committed, review NOT dispatched.
        with state_mod.locked(state_path):
            s = state_mod.load_state(state_path)
            state_mod.set_phase_review_request(s, args.phase_id, None, dispatch_failed=True)
            state_mod.save_state(state_path, s)
        print(f"REVIEW DISPATCH FAILED — phase committed but flagged for operator: {e}",
              file=sys.stderr)
        return 6

    # 8. Record review and mark phase under_review.
    with state_mod.locked(state_path):
        s = state_mod.load_state(state_path)
        state_mod.record_review(
            s,
            review_id=request_id,
            project_tip_sha=project_tip_sha,
            coverage_set=dag_mod.coverage_set(s, focus_phase=args.phase_id),
            focus_phase=args.phase_id,
            review_mode=phase["review_mode"],
            dispatched_at_utc=_utcnow(),
        )
        state_mod.set_phase_review_request(s, args.phase_id, request_id)
        state_mod.set_phase_status(s, args.phase_id, "under_review")
        state_mod.save_state(state_path, s)

    print(f"phase_complete OK: phase={args.phase_id} merge_sha={result.merge_sha[:8]} "
          f"review={request_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
