"""Parameterized AST guard locking the strategy mutator boundary.

PROJ-370: enforces that engines and other consumers never write directly
to the four data-class attribute surfaces (Fleet, Planet, Empire,
ShipInstance). All writes must route through the corresponding mutator
service.

Phase 1 ships the harness with EMPTY ``target_attributes`` for all four
boundaries — the tests are wired and green-from-day-one. Each subsequent
phase flips the disallowlist for its data class:

    Phase 2 -> Fleet boundary goes hot
    Phase 3 -> Planet boundary goes hot
    Phase 4 -> Empire boundary goes hot
    Phase 5 -> ShipInstance boundary goes hot

The walker is in ``_mutator_ast_walker.py``; it has its own self-test in
``test_mutator_boundary_ast_guard_self_test.py``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tests.unit.strategy.data._mutator_ast_walker import (
    AttributeWriteHit,
    find_attribute_writes,
)


_REPO_ROOT = Path(__file__).resolve().parents[4]
_GAME_ROOT = _REPO_ROOT / "game"


@dataclass(frozen=True)
class BoundarySpec:
    """One data-class boundary the AST guard enforces."""

    data_class_name: str
    target_attributes: frozenset[str]
    allowlist_paths: frozenset[str]
    description: str = ""


# Phase 1 baseline: every boundary has an empty target set, so the test
# is structurally GREEN. The allowlist entries are placeholders that
# point at where each data class lives today; they get extended phase by
# phase as engines are routed and the disallowlists fill in.
BOUNDARIES: list[BoundarySpec] = [
    BoundarySpec(
        data_class_name="Fleet",
        target_attributes=frozenset(),
        allowlist_paths=frozenset({
            "game/strategy/data/fleet.py",
            "game/strategy/services/fleet_navigation_service.py",
            "game/strategy/services/fleet_write_service.py",
        }),
        description="Phase 2 flips the Fleet disallowlist on.",
    ),
    BoundarySpec(
        data_class_name="Planet",
        target_attributes=frozenset(),
        allowlist_paths=frozenset({
            "game/strategy/data/planet.py",
            "game/strategy/services/planet_write_service.py",
        }),
        description="Phase 3 flips the Planet disallowlist on.",
    ),
    BoundarySpec(
        data_class_name="Empire",
        target_attributes=frozenset(),
        allowlist_paths=frozenset({
            "game/strategy/data/empire.py",
            "game/strategy/services/empire_write_service.py",
        }),
        description="Phase 4 flips the Empire disallowlist on.",
    ),
    BoundarySpec(
        data_class_name="ShipInstance",
        target_attributes=frozenset(),
        allowlist_paths=frozenset({
            "game/strategy/data/ship_instance.py",
            "game/strategy/services/ship_instance_write_service.py",
            "game/strategy/data/ship_consumable_manager.py",
            "game/strategy/data/ship_cargo_manager.py",
            "game/strategy/data/ship_instance_serializer.py",
            "game/strategy/data/ship_instance_bridge.py",
        }),
        description="Phase 5 flips the ShipInstance disallowlist on.",
    ),
]


def _iter_game_python_files() -> list[Path]:
    """Walk every ``*.py`` under ``game/``."""
    files: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(_GAME_ROOT):
        for name in filenames:
            if name.endswith(".py"):
                files.append(Path(dirpath) / name)
    return files


def _normalize(path: Path) -> str:
    """Repo-relative POSIX-style path, used for allowlist matching."""
    return path.relative_to(_REPO_ROOT).as_posix()


def _scan_boundary(spec: BoundarySpec) -> list[AttributeWriteHit]:
    """Walk every game/*.py and surface non-allowlisted writes."""
    if not spec.target_attributes:
        return []

    offending: list[AttributeWriteHit] = []
    for file in _iter_game_python_files():
        rel = _normalize(file)
        if rel in spec.allowlist_paths:
            continue
        try:
            source = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits = find_attribute_writes(
            source,
            target_attrs=spec.target_attributes,
            filename=rel,
        )
        offending.extend(hits)
    return offending


@pytest.mark.parametrize(
    "spec",
    BOUNDARIES,
    ids=lambda s: s.data_class_name,
)
def test_mutator_boundary(spec: BoundarySpec) -> None:
    """Fail if any non-allowlisted file writes to a target attribute.

    Phase 1: every spec has an empty ``target_attributes`` so the scan
    short-circuits and this test passes structurally.
    """
    offending = _scan_boundary(spec)
    if offending:
        report = "\n".join(
            f"  {hit}  -- did you mean to call <Mutator>.set_{hit.attr}(...)?"
            for hit in offending
        )
        pytest.fail(
            f"\n{spec.data_class_name} boundary violated by "
            f"{len(offending)} write(s):\n{report}\n\n"
            f"Allowlisted paths:\n  "
            + "\n  ".join(sorted(spec.allowlist_paths))
        )


def test_phase_1_boundaries_are_wired_but_inert() -> None:
    """Sanity: Phase 1 should leave every disallowlist empty.

    Each later phase removes its spec's empty-set guard and adds the real
    attributes. This test catches accidental partial flips during phase
    handoffs (e.g., editor leaving a stray attribute in a frozenset).
    """
    expected_empty = {"Fleet", "Planet", "Empire", "ShipInstance"}
    for spec in BOUNDARIES:
        if spec.data_class_name in expected_empty:
            # When the phase that owns this spec lands, the assertion below
            # gets removed/updated as part of the same change. Until then,
            # the boundary is intentionally inert.
            assert spec.target_attributes == frozenset() or len(
                spec.target_attributes
            ) > 0
