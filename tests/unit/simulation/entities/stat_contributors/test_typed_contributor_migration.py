"""
PROJ-367 Phase 1: AST regression — no `comp.abilities.get(...)` reads remain
in the Phase-3 stat-aggregation path.

This test parses every file in ``game/simulation/entities/stat_contributors/``
and the Phase-3 region of ``game/simulation/entities/ship_stats.py`` and
asserts that no expression of the form ``comp.abilities.get(...)`` (or any
attribute-name in place of ``comp``) appears.

The migration target is typed access via ``comp.has_ability(...)`` and
``comp.get_abilities(...)`` plus typed ability attributes.

Phase 5 helpers in ``ship_stats.py`` (``_phase_post_physics_aggregation`` /
``_phase_sensor_defense_scores``) are NOT in scope and are skipped.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Source roots
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[5]
STAT_CONTRIBUTORS_DIR = (
    REPO_ROOT / "game" / "simulation" / "entities" / "stat_contributors"
)
SHIP_STATS_PATH = (
    REPO_ROOT / "game" / "simulation" / "entities" / "ship_stats.py"
)

# Phase-3 method names — all `_aggregate_*` helpers and `_phase_stats_aggregation`.
# Phase-5 functions (`_phase_sensor_defense_scores`, etc.) are out of scope.
SHIP_STATS_PHASE3_FUNCS: frozenset[str] = frozenset({
    "_phase_stats_aggregation",
    "_aggregate_resource_abilities",
    "_aggregate_cargo_and_pod_abilities",
    "_apply_aggregated_stats",
    "_phase_damage_check_and_supply",  # contains the Armor reads in scope
})


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class _AbilitiesGetVisitor(ast.NodeVisitor):
    """Collect every ``<x>.abilities.get(...)`` call site."""

    def __init__(self) -> None:
        self.hits: list[tuple[int, str]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 — ast convention
        # Pattern: Call(func=Attribute(attr='get', value=Attribute(attr='abilities', ...)))
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "get"
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "abilities"
        ):
            # Try to capture the leading name for diagnostics
            inner = func.value.value
            obj_name = (
                inner.id if isinstance(inner, ast.Name) else type(inner).__name__
            )
            self.hits.append((node.lineno, f"{obj_name}.abilities.get(...)"))
        self.generic_visit(node)


def _scan_file(path: Path) -> list[tuple[Path, int, str]]:
    """Return all `<x>.abilities.get(...)` hits in the entire file."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    v = _AbilitiesGetVisitor()
    v.visit(tree)
    return [(path, ln, snippet) for (ln, snippet) in v.hits]


def _scan_ship_stats_phase3(path: Path) -> list[tuple[Path, int, str]]:
    """Return hits inside the Phase-3 functions only."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    hits: list[tuple[Path, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in SHIP_STATS_PHASE3_FUNCS:
            v = _AbilitiesGetVisitor()
            v.visit(node)
            hits.extend((path, ln, snippet) for (ln, snippet) in v.hits)
    return hits


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_no_abilities_get_in_stat_contributors() -> None:
    """No `<x>.abilities.get(...)` reads in `stat_contributors/`."""
    py_files = sorted(STAT_CONTRIBUTORS_DIR.glob("*.py"))
    assert py_files, f"No .py files found under {STAT_CONTRIBUTORS_DIR}"
    all_hits: list[tuple[Path, int, str]] = []
    for path in py_files:
        all_hits.extend(_scan_file(path))
    assert not all_hits, (
        "Found `<x>.abilities.get(...)` reads in stat_contributors/:\n  "
        + "\n  ".join(f"{p.name}:{ln} -> {s}" for (p, ln, s) in all_hits)
    )


def test_no_abilities_get_in_ship_stats_phase3() -> None:
    """No `<x>.abilities.get(...)` reads in Phase-3 region of ship_stats.py."""
    hits = _scan_ship_stats_phase3(SHIP_STATS_PATH)
    assert not hits, (
        "Found `<x>.abilities.get(...)` reads in Phase-3 region of "
        f"{SHIP_STATS_PATH.name}:\n  "
        + "\n  ".join(
            f"{p.name}:{ln} -> {s}" for (p, ln, s) in hits
        )
    )
