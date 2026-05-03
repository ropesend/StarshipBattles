#!/usr/bin/env python3
"""03c: inspect a project's phase DAG, status, and eligibility.

Subcommands:
    show       Print the DAG and per-phase status.
    validate   Detect cycles and dangling deps; exits non-zero on error.
    eligible   Print phase IDs that may start now (one per line).
    status     Per-phase status lines including review/verifying review IDs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from phase_workflow import dag as dag_mod
from phase_workflow import state as state_mod

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
ACTIVE_DIR = PROJECT_ROOT / "Projects" / "active_projects"


def _state_path(project_id: str) -> Path:
    return ACTIVE_DIR / project_id / "phase_state.json"


def _load(project_id: str) -> dict:
    path = _state_path(project_id)
    if not path.exists():
        print(f"phase_state.json not found at {path}", file=sys.stderr)
        sys.exit(2)
    return state_mod.load_state(path)


def _show(state: dict) -> int:
    print(f"# {state['project_id']} phase DAG")
    print(f"buffer_depth={state['buffer_depth']}")
    if state.get("buffer_depth_override_reason"):
        print(f"buffer_depth_override_reason: {state['buffer_depth_override_reason']}")
    print()
    for pid in dag_mod.topological_order(state):
        p = state["phases"][pid]
        deps = ", ".join(p["depends_on"]) if p["depends_on"] else "—"
        print(f"  {pid:14s}  status={p['status']:18s}  depends_on=[{deps}]")
    return 0


def _validate(state: dict) -> int:
    try:
        dag_mod.validate_dag(state)
    except ValueError as e:
        print(f"DAG validation FAILED: {e}", file=sys.stderr)
        return 1
    print("DAG OK")
    return 0


def _eligible(state: dict) -> int:
    for pid in dag_mod.eligible(state):
        print(pid)
    return 0


def _status(state: dict) -> int:
    print(f"# {state['project_id']} phase status")
    for pid in dag_mod.topological_order(state):
        p = state["phases"][pid]
        bits = [f"status={p['status']}"]
        if p.get("phase_head_sha"):
            bits.append(f"head={p['phase_head_sha'][:8]}")
        if p.get("review_request_id"):
            bits.append(f"review={p['review_request_id']}")
        if p.get("verifying_review_id"):
            bits.append(f"verifying={p['verifying_review_id']}")
        if p.get("review_dispatch_failed"):
            bits.append("review_dispatch_failed=TRUE")
        print(f"  {pid:14s}  " + "  ".join(bits))
    # Surface "phases built on unverified parents" counter when buffer_depth=1.
    if state["buffer_depth"] == 1:
        n = sum(
            1
            for pid, p in state["phases"].items()
            if p["status"] in ("in_progress", "committed", "under_review")
            and any(
                state["phases"][parent]["status"] not in ("verified",)
                for parent in p["depends_on"]
            )
        )
        print(f"\n  phases_built_on_unverified_parents={n}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="03c phase DAG inspector")
    parser.add_argument("project_id")
    parser.add_argument("subcommand", choices=("show", "validate", "eligible", "status"))
    args = parser.parse_args()

    state = _load(args.project_id)
    fns = {"show": _show, "validate": _validate, "eligible": _eligible, "status": _status}
    return fns[args.subcommand](state)


if __name__ == "__main__":
    sys.exit(main())
