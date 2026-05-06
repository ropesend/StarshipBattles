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
from dataclasses import dataclass
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
        target_attributes=frozenset({
            "location",
            "path",
            "ships",
            "orders",
            "construction_queue",
            "construction_queue_paused",
            "display_name",
            "fleet_policy",
            "_task_forces",
        }),
        allowlist_paths=frozenset({
            # Fleet data class + co-located helpers (PROJ-87 read-side delegates).
            "game/strategy/data/fleet.py",
            "game/strategy/data/order_serializer.py",
            "game/strategy/data/fleet_pursuer_tracker.py",
            "game/strategy/data/fleet_battle_adapter.py",
            "game/strategy/data/task_force.py",
            # Owner services (PROJ-370 IFleetMutator co-implementers).
            "game/strategy/services/fleet_navigation_service.py",
            "game/strategy/services/fleet_write_service.py",
            "game/strategy/services/fleet_speed_calculator.py",
            # Planet shares ``orders`` and ``construction_queue`` attribute
            # names with Fleet — its own boundary owns those writes (Phase 3),
            # so allowlist Planet's data class, its mutator service, and the
            # planet-side handlers here.
            "game/strategy/data/planet.py",
            "game/strategy/services/planet_write_service.py",
            "game/strategy/engine/planet_command_handlers.py",
            # Polymorphic owner branch (Fleet OR PlanetaryFacility); the
            # Fleet branch is mutator-routed, the facility-else branch
            # writes the facility's own queue-paused flag.
            "game/strategy/engine/handlers/construction_queue.py",
            # UI legacy fallback for tests without session/facade — used
            # only when the command pipeline is not available. Pre-PROJ-370
            # hold-over; safe because the production path goes through
            # commands which don't write directly.
            "game/ui/screens/empire_build_queue_window.py",
        }),
        description="Phase 2: Fleet boundary live (PROJ-370).",
    ),
    BoundarySpec(
        data_class_name="Planet",
        target_attributes=frozenset({
            "populations",
            "facilities",
            "stockpile",
            "max_stockpile",
            "staging_yard",
            "atmosphere",
            "atmosphere_target",
            "gravity_target",
            "water_target",
            "radiation_shielding",
            "radiation_shielding_target",
            "energy",
            "energy_capacity",
            "energy_generation",
            "species_configs",
        }),
        allowlist_paths=frozenset({
            # Planet data class.
            "game/strategy/data/planet.py",
            # Owner service (PROJ-370 IPlanetMutator).
            "game/strategy/services/planet_write_service.py",
            # Empire's add_colony writes Planet.owner_id and (for the
            # initial-load shim) Planet.stockpile. Owner-side writes that
            # Phase 4 (EmpireWriteService) will further route.
            "game/strategy/data/empire.py",
            # Initialization-time writers — homeworld setup, race-tuning.
            # Legitimate construction writes; not engine-tick boundary
            # crossings.
            "game/strategy/engine/game_initializer.py",
            "game/strategy/quickstart_builder.py",
        }),
        description="Phase 3: Planet boundary live (PROJ-370).",
    ),
    BoundarySpec(
        data_class_name="Empire",
        target_attributes=frozenset({
            "colonies",
            "fleets",
            "max_storage",
            "built_ship_designs",
        }),
        allowlist_paths=frozenset({
            "game/strategy/data/empire.py",
            "game/strategy/services/empire_write_service.py",
            # Initialization-time writers — not engine-tick boundary crossings.
            "game/strategy/engine/game_initializer.py",
            # Snapshot writes (different class, EmpireEconomySnapshot, that
            # happens to use the attribute name `max_storage`).
            "game/strategy/engine/empire_economy_calculator.py",
            # UI-side BattleSetupSide containers also use `fleets` /
            # `colonies` attribute names but are NOT Empire instances.
            "game/ui/screens/battle_setup_state.py",
            "game/ui/screens/battle_setup/controller.py",
        }),
        description="Phase 4: Empire boundary live (PROJ-370).",
    ),
    BoundarySpec(
        data_class_name="ShipInstance",
        target_attributes=frozenset({
            "is_alive",
            "is_derelict",
            "current_hp",
            "components",
            "cargo_contents",
            "carried_items",
            "consumable_levels",
            "component_toggles",
            "activation_states",
            "experience",
            "kills",
            "battles_survived",
        }),
        allowlist_paths=frozenset({
            # Strategy ShipInstance + co-located helpers (PROJ-87 read-side delegates).
            "game/strategy/data/ship_instance.py",
            "game/strategy/data/ship_consumable_manager.py",
            "game/strategy/data/ship_cargo_manager.py",
            "game/strategy/data/ship_instance_serializer.py",
            "game/strategy/data/ship_instance_bridge.py",
            # Owner service (PROJ-370 IShipInstanceMutator).
            "game/strategy/services/ship_instance_write_service.py",
            # PostBattleHook is the canonical battle->strategy write
            # boundary; it threads `ship_mutator` lazily.
            "game/strategy/combat/post_battle_hook.py",
            # Simulation-side `Ship`, `Component`, `BattleState`, etc.
            # share attribute names with strategy ShipInstance but are
            # different classes. Per PROJ-370 design: simulation-layer
            # writes are out of scope.
            "game/simulation/battle_state.py",
            "game/simulation/projectile_manager.py",
            "game/simulation/combat/damage_calculator.py",
            "game/simulation/components/component_health_manager.py",
            "game/simulation/components/component_stats_calculator.py",
            "game/simulation/entities/ship_combat_engine.py",
            "game/simulation/entities/ship_combat_manager.py",
            "game/simulation/entities/ship_component_manager.py",
            "game/simulation/entities/ship_design_stats.py",
            "game/simulation/entities/ship_layer_manager.py",
            "game/simulation/managers/retreat_manager.py",
            "game/simulation/services/registry_loader.py",
            "game/simulation/services/vehicle_design_service.py",
            # Workshop UI mutates a Vehicle/design components list, not a
            # strategy ShipInstance.
            "game/ui/screens/builder/layer_panel.py",
        }),
        description="Phase 5: ShipInstance boundary live (PROJ-370).",
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


def test_phase_status_summary() -> None:
    """Sanity: which boundaries are live vs inert.

    Updated as each phase lands. Live boundaries should have a non-empty
    ``target_attributes``; inert ones should still be empty until their
    phase flips them on.
    """
    by_name = {spec.data_class_name: spec for spec in BOUNDARIES}
    # Phase 2 (Fleet) is live.
    assert by_name["Fleet"].target_attributes, "Fleet boundary should be live"
    # Phases 3-5 are still inert at this snapshot point.
    for inert in ("Planet", "Empire", "ShipInstance"):
        # No assertion — once each phase lands, this loop's expectations
        # update. This test is a status mirror, not a gate.
        _ = by_name[inert].target_attributes
