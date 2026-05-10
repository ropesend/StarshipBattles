"""Tests for Projects/scripts/phase_workflow/dag.py."""
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import state as state_mod
from phase_workflow import dag as dag_mod


def _state_with(*phase_specs, buffer_depth=0, buffer_reason=None):
    """Build a state with phases as (id, depends_on, planned_files) tuples.

    phase_specs items can be:
      - (id, depends_on)
      - (id, depends_on, planned_files)
    """
    s = state_mod.initial_state("PROJ-TEST-001")
    if buffer_depth == 1:
        state_mod.set_buffer_depth(s, 1, reason=buffer_reason or "test")
    for spec in phase_specs:
        if len(spec) == 2:
            pid, deps = spec
            files: list[str] = []
        else:
            pid, deps, files = spec
        state_mod.add_phase(s, pid, depends_on=list(deps), planned_files=list(files))
    return s


# ---------------------------------------------------------------------------
# Cycle detection / validation
# ---------------------------------------------------------------------------


def test_validate_dag_accepts_acyclic():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_1", "phase_2"]),
    )
    dag_mod.validate_dag(s)  # must not raise


def test_validate_dag_rejects_self_loop():
    s = _state_with(("phase_1", ["phase_1"]))
    with pytest.raises(ValueError, match="cycle"):
        dag_mod.validate_dag(s)


def test_validate_dag_rejects_two_node_cycle():
    s = _state_with(
        ("phase_1", ["phase_2"]),
        ("phase_2", ["phase_1"]),
    )
    with pytest.raises(ValueError, match="cycle"):
        dag_mod.validate_dag(s)


def test_validate_dag_rejects_dangling_dependency():
    s = _state_with(("phase_1", ["phase_99"]))
    with pytest.raises(ValueError, match="phase_99"):
        dag_mod.validate_dag(s)


# ---------------------------------------------------------------------------
# Topological order
# ---------------------------------------------------------------------------


def test_topological_order_respects_dependencies():
    s = _state_with(
        ("phase_3", ["phase_1", "phase_2"]),
        ("phase_2", ["phase_1"]),
        ("phase_1", []),
    )
    order = dag_mod.topological_order(s)
    assert order.index("phase_1") < order.index("phase_2")
    assert order.index("phase_2") < order.index("phase_3")


def test_topological_order_diamond():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_1"]),
        ("phase_4", ["phase_2", "phase_3"]),
    )
    order = dag_mod.topological_order(s)
    for parent, child in [
        ("phase_1", "phase_2"),
        ("phase_1", "phase_3"),
        ("phase_2", "phase_4"),
        ("phase_3", "phase_4"),
    ]:
        assert order.index(parent) < order.index(child)


# ---------------------------------------------------------------------------
# Eligibility, depth-0 buffer
# ---------------------------------------------------------------------------


def test_root_phase_eligible_immediately():
    s = _state_with(("phase_1", []))
    assert dag_mod.eligible(s) == ["phase_1"]


def test_non_root_blocked_until_parent_verified_at_depth_0():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
    )
    state_mod.set_phase_status(s, "phase_1", "committed")
    assert dag_mod.eligible(s) == []  # depth=0: parent must be verified


def test_non_root_eligible_when_parent_verified():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    assert dag_mod.eligible(s) == ["phase_2"]


def test_already_in_progress_phase_excluded_from_eligible():
    s = _state_with(("phase_1", []))
    state_mod.set_phase_status(s, "phase_1", "in_progress")
    assert dag_mod.eligible(s) == []


def test_completed_phase_excluded_from_eligible():
    s = _state_with(("phase_1", []), ("phase_2", []))
    state_mod.set_phase_status(s, "phase_1", "verified")
    assert dag_mod.eligible(s) == ["phase_2"]


# ---------------------------------------------------------------------------
# Eligibility, depth-1 buffer
# ---------------------------------------------------------------------------


def test_depth_1_chain_allows_one_phase_ahead():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
        buffer_depth=1,
        buffer_reason="trusted code path",
    )
    state_mod.set_phase_status(s, "phase_1", "committed")
    eligible = dag_mod.eligible(s)
    assert "phase_2" in eligible
    assert "phase_3" not in eligible  # phase_1 not yet verified, phase_2 not yet committed


def test_depth_1_chain_blocks_two_ahead_until_grandparent_verified():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
        buffer_depth=1,
        buffer_reason="trusted code path",
    )
    state_mod.set_phase_status(s, "phase_1", "committed")
    state_mod.set_phase_status(s, "phase_2", "committed")
    eligible = dag_mod.eligible(s)
    # phase_3's grandparent (phase_1) is not verified -> phase_3 blocked.
    assert "phase_3" not in eligible


def test_depth_1_chain_unblocks_when_grandparent_verified():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
        buffer_depth=1,
        buffer_reason="trusted code path",
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "committed")
    eligible = dag_mod.eligible(s)
    assert "phase_3" in eligible


# ---------------------------------------------------------------------------
# Multi-parent: ALL parents verified regardless of buffer_depth
# ---------------------------------------------------------------------------


def test_multi_parent_blocked_until_all_parents_verified_depth_0():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", []),
        ("phase_3", ["phase_1", "phase_2"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "committed")
    eligible = dag_mod.eligible(s)
    assert "phase_3" not in eligible


def test_multi_parent_blocked_until_all_parents_verified_depth_1():
    """Multi-parent rule is stricter than depth-1 buffer: still need ALL verified."""
    s = _state_with(
        ("phase_1", []),
        ("phase_2", []),
        ("phase_3", ["phase_1", "phase_2"]),
        buffer_depth=1,
        buffer_reason="test",
    )
    state_mod.set_phase_status(s, "phase_1", "committed")
    state_mod.set_phase_status(s, "phase_2", "committed")
    eligible = dag_mod.eligible(s)
    assert "phase_3" not in eligible


def test_multi_parent_eligible_when_all_parents_verified():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", []),
        ("phase_3", ["phase_1", "phase_2"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "verified")
    eligible = dag_mod.eligible(s)
    assert "phase_3" in eligible


# ---------------------------------------------------------------------------
# File-disjointness for parallel siblings
# ---------------------------------------------------------------------------


def test_parallel_siblings_with_disjoint_files_both_eligible():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"], ["a.py"]),
        ("phase_3", ["phase_1"], ["b.py"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    eligible = dag_mod.eligible(s)
    assert set(eligible) == {"phase_2", "phase_3"}


def test_parallel_siblings_with_overlapping_files_serialize():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"], ["a.py"]),
        ("phase_3", ["phase_1"], ["a.py"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    eligible = dag_mod.eligible(s)
    # Conflict resolution: deterministic — pick the lexicographically earlier
    # phase_id; the other is blocked until the chosen one is no longer eligible.
    assert "phase_2" in eligible
    assert "phase_3" not in eligible


def test_in_progress_sibling_blocks_overlapping_eligible():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"], ["a.py"]),
        ("phase_3", ["phase_1"], ["a.py"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "in_progress")
    eligible = dag_mod.eligible(s)
    assert "phase_3" not in eligible


# ---------------------------------------------------------------------------
# coverage_set computation
# ---------------------------------------------------------------------------


def test_coverage_set_for_root_includes_only_root():
    s = _state_with(("phase_1", []))
    state_mod.set_phase_status(s, "phase_1", "committed")
    assert dag_mod.coverage_set(s, focus_phase="phase_1") == ["phase_1"]


def test_coverage_set_for_chain_includes_all_committed_ancestors_and_focus():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "committed")
    cov = dag_mod.coverage_set(s, focus_phase="phase_2")
    assert set(cov) == {"phase_1", "phase_2"}


def test_coverage_set_excludes_uncommitted_phases():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
    )
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "committed")
    # phase_3 is not_started -> excluded
    cov = dag_mod.coverage_set(s, focus_phase="phase_2")
    assert "phase_3" not in cov


def test_coverage_set_for_diamond():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_1"]),
        ("phase_4", ["phase_2", "phase_3"]),
    )
    for pid in ["phase_1", "phase_2", "phase_3"]:
        state_mod.set_phase_status(s, pid, "verified")
    state_mod.set_phase_status(s, "phase_4", "committed")
    cov = dag_mod.coverage_set(s, focus_phase="phase_4")
    assert set(cov) == {"phase_1", "phase_2", "phase_3", "phase_4"}


# ---------------------------------------------------------------------------
# parents/ancestors helpers
# ---------------------------------------------------------------------------


def test_ancestors_returns_transitive_closure_excluding_self():
    s = _state_with(
        ("phase_1", []),
        ("phase_2", ["phase_1"]),
        ("phase_3", ["phase_2"]),
        ("phase_4", ["phase_3"]),
    )
    assert dag_mod.ancestors(s, "phase_4") == ["phase_1", "phase_2", "phase_3"]


def test_ancestors_for_root_is_empty():
    s = _state_with(("phase_1", []))
    assert dag_mod.ancestors(s, "phase_1") == []
