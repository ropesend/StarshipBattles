"""PROJ-377 Phase 3: AST guard pinning the pathfinding shim's surviving function set.

The shim at `game/strategy/data/pathfinding.py` is no longer slated for
deletion (see `Projects/active_projects/PROJ-377/decisions.md` 2026-05-07
rows). It exists as a permanent test-patch transparency surface for the
~30 `unittest.mock.patch('game.strategy.data.pathfinding.X')` sites
across the test suite — Class B production callers (`game_session.py`,
`fleet_navigation_service.py`, `handlers/base.py`,
`facade/slices/planet_slice.py`, `strategy_superweapons.py`) still
import from the shim so those patches reach production code paths.

This guard prevents the shim's top-level function set from silently
*growing back* (the shim used to expose more forwarders before PROJ-377
moved Class A sites to direct service calls) or *shrinking* (a future
PR removing a function tests rely on for patching).

If you intentionally add or remove a function in `pathfinding.py`,
update `EXPECTED_SHIM_FUNCTIONS` below **deliberately**, log the change
in `Projects/active_projects/PROJ-377/decisions.md`, and verify no
`patch('game.strategy.data.pathfinding.X')` site references the
removed function.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


_SHIM_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "game" / "strategy" / "data" / "pathfinding.py"


# Free-function forwarders + the two helper factories Phase 2 closed on.
EXPECTED_SHIM_FUNCTIONS = frozenset({
    # Free-function forwarders kept for test-patch transparency.
    "strip_start_hex",
    "find_path_deep_space",
    "find_path_interstellar",
    "get_system_at_hex",
    "find_nearest_system",
    "find_hybrid_path",
    "project_fleet_path",
    "calculate_intercept_point",
    # Helpers used by the forwarders + by intercept_calculator.py.
    "_pathfinder_for",
    "_intercept_for",
})


def _top_level_function_names() -> frozenset[str]:
    tree = ast.parse(_SHIM_PATH.read_text())
    return frozenset(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    )


def test_pathfinding_shim_function_set_pinned() -> None:
    actual = _top_level_function_names()
    assert actual == EXPECTED_SHIM_FUNCTIONS, (
        f"pathfinding.py top-level function set drift:\n"
        f"  actual    = {sorted(actual)}\n"
        f"  expected  = {sorted(EXPECTED_SHIM_FUNCTIONS)}\n"
        f"  added     = {sorted(actual - EXPECTED_SHIM_FUNCTIONS)}\n"
        f"  removed   = {sorted(EXPECTED_SHIM_FUNCTIONS - actual)}\n"
        f"If this change is intentional, update EXPECTED_SHIM_FUNCTIONS and "
        f"log the change in PROJ-377 decisions.md."
    )


@pytest.mark.parametrize("helper", ["_pathfinder_for", "_intercept_for"])
def test_shim_helpers_present(helper: str) -> None:
    """The two helpers are load-bearing for every forwarder; pin them explicitly."""
    assert helper in _top_level_function_names()
