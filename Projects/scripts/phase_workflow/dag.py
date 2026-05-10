"""DAG parsing, eligibility computation, and coverage_set rendering.

Reads phase dependencies from `state["phases"][id]["depends_on"]`.

Eligibility rules (see Projects/protocols/03c_phase_aware_execution.md):
    - 0 parents (root): eligible immediately if status == not_started.
    - 1 parent + buffer_depth=0: parent must be `verified`.
    - 1 parent + buffer_depth=1: parent must be `committed` AND every ancestor
      at distance >= 2 must be `verified`.
    - >= 2 parents: ALL parents must be `verified`, regardless of buffer_depth.
    - Any phase already running (in_progress, committed, under_review,
      verified, scrapped) is excluded from the eligible set.
    - Among eligible phases that share planned_files, only the
      lexicographically earliest phase_id is reported eligible; the others
      block until it advances out of the eligible set.
"""
from __future__ import annotations

from typing import Any


def _phase(state: dict[str, Any], phase_id: str) -> dict[str, Any]:
    if phase_id not in state["phases"]:
        raise KeyError(f"unknown phase: {phase_id!r}")
    return state["phases"][phase_id]


def parents(state: dict[str, Any], phase_id: str) -> list[str]:
    return list(_phase(state, phase_id)["depends_on"])


def ancestors(state: dict[str, Any], phase_id: str) -> list[str]:
    """Transitive closure of parents, excluding phase_id itself.

    Returned in topological order (deepest ancestor first).
    """
    visited: set[str] = set()
    order: list[str] = []

    def visit(pid: str) -> None:
        for p in parents(state, pid):
            if p in visited:
                continue
            visit(p)
            visited.add(p)
            order.append(p)

    visit(phase_id)
    return order


def validate_dag(state: dict[str, Any]) -> None:
    """Raise ValueError on cycles or dangling dependencies."""
    phases = state["phases"]
    # Dangling deps
    for pid, phase in phases.items():
        for dep in phase["depends_on"]:
            if dep not in phases:
                raise ValueError(f"phase {pid!r} depends on unknown phase {dep!r}")
            if dep == pid:
                raise ValueError(f"phase {pid!r} has a cycle (depends on itself)")
    # Cycles via DFS
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {pid: WHITE for pid in phases}

    def dfs(pid: str, stack: list[str]) -> None:
        color[pid] = GRAY
        for dep in phases[pid]["depends_on"]:
            if color[dep] == GRAY:
                cycle_path = stack[stack.index(dep):] + [dep]
                raise ValueError(f"cycle detected: {' -> '.join(cycle_path)}")
            if color[dep] == WHITE:
                dfs(dep, stack + [dep])
        color[pid] = BLACK

    for pid in phases:
        if color[pid] == WHITE:
            dfs(pid, [pid])


def topological_order(state: dict[str, Any]) -> list[str]:
    """Return phase IDs in topological order (parents before children).

    Stable: ties broken by lexicographic phase_id.
    """
    validate_dag(state)
    phases = state["phases"]
    indegree = {pid: len(phase["depends_on"]) for pid, phase in phases.items()}
    children: dict[str, list[str]] = {pid: [] for pid in phases}
    for pid, phase in phases.items():
        for dep in phase["depends_on"]:
            children[dep].append(pid)
    # Kahn's algorithm with sorted ready queue for determinism.
    ready = sorted(pid for pid, d in indegree.items() if d == 0)
    out: list[str] = []
    while ready:
        pid = ready.pop(0)
        out.append(pid)
        for child in sorted(children[pid]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort()
    if len(out) != len(phases):
        raise ValueError("cycle detected during topological sort")
    return out


def _all_ancestors_verified(state: dict[str, Any], phase_id: str) -> bool:
    return all(_phase(state, a)["status"] == "verified" for a in ancestors(state, phase_id))


def _ancestors_at_distance_ge_2_verified(state: dict[str, Any], phase_id: str) -> bool:
    """For depth-1 buffer: parent at distance 1; ancestors at distance >= 2 must be verified."""
    direct_parents = set(parents(state, phase_id))
    for a in ancestors(state, phase_id):
        if a in direct_parents:
            continue
        if _phase(state, a)["status"] != "verified":
            return False
    return True


def _phase_dag_eligible(state: dict[str, Any], phase_id: str) -> bool:
    """DAG-only eligibility (ignores file-conflict serialization)."""
    phase = _phase(state, phase_id)
    if phase["status"] != "not_started":
        return False
    deps = phase["depends_on"]
    if not deps:
        return True
    if len(deps) >= 2:
        return all(_phase(state, p)["status"] == "verified" for p in deps)
    # Exactly 1 parent.
    parent_id = deps[0]
    parent_status = _phase(state, parent_id)["status"]
    if state["buffer_depth"] == 0:
        return parent_status == "verified"
    # buffer_depth == 1
    if parent_status not in ("committed", "under_review", "verified"):
        return False
    return _ancestors_at_distance_ge_2_verified(state, phase_id)


def eligible(state: dict[str, Any]) -> list[str]:
    """Return phase IDs that can start now, sorted by phase_id.

    Applies file-conflict serialization: among phases with overlapping
    planned_files (DAG-eligible OR currently in flight), only the
    lexicographically earliest phase_id is included.
    """
    validate_dag(state)
    candidates = sorted(
        pid for pid in state["phases"] if _phase_dag_eligible(state, pid)
    )
    # File-conflict serialization. A candidate is excluded if its
    # planned_files overlap with files held by:
    #   (a) another candidate with a lexicographically smaller phase_id, OR
    #   (b) any phase currently in_progress / committed / under_review.
    held_files: dict[str, str] = {}  # file -> holder phase_id
    for pid, phase in sorted(state["phases"].items()):
        if phase["status"] in ("in_progress", "committed", "under_review"):
            for f in phase["planned_files"]:
                held_files.setdefault(f, pid)

    out: list[str] = []
    for pid in candidates:
        files = set(_phase(state, pid)["planned_files"])
        conflict = files & set(held_files)
        if conflict:
            continue
        out.append(pid)
        # Reserve files for later candidates in this same pass.
        for f in files:
            held_files.setdefault(f, pid)
    return out


def coverage_set(state: dict[str, Any], focus_phase: str) -> list[str]:
    """All phases that should be in the cumulative review for `focus_phase`.

    Includes the focus phase plus every ancestor whose status is at least
    `committed` (so was merged into the project branch). Excludes phases
    not yet committed (they aren't on the project tip).
    """
    if focus_phase not in state["phases"]:
        raise KeyError(f"unknown focus_phase: {focus_phase!r}")
    out = [focus_phase]
    for a in ancestors(state, focus_phase):
        if _phase(state, a)["status"] in ("committed", "under_review", "verified"):
            out.append(a)
    return sorted(out)
