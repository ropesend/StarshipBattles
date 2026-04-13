"""Tests for Strategy spec compiler (PROJ-269 Phase 1 Task 1.9).

Covers:
- `build_strategy_battle_spec(...)` returns a `BattleSpec`
- Each input fleet becomes a `TeamSpec` (Phase 1: one team per fleet)
- Sector + system modifiers flow into `ModifierStack.global_`
- Per-empire modifiers flow into `ModifierStack.per_team`
- Boundary is pulled from `settings.combat_boundary_default`
- `post_battle_hook` is a non-None callable (wiring lands in Phase 2)
"""
import pytest

from game.core.hex_math import HexCoord
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import (
    CircleBoundary,
    ExitPolicy,
    UnboundedRegion,
)
from game.simulation.combat.telemetry import TelemetryLevel
from game.strategy.combat.spec_compiler import build_strategy_battle_spec
from game.strategy.data.fleet import Fleet


# ---------------------------------------------------------------------------
# Fixtures — minimal Fleet with one ShipInstance per team.
# ---------------------------------------------------------------------------


def _minimal_design(name: str) -> dict:
    return {
        "name": name,
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {},
        "expected_stats": {
            "max_hp": 100,
            "max_speed": 100,
            "acceleration_rate": 10,
            "turn_speed": 90,
            "total_thrust": 500,
            "strategic_movement": 10,
            "mass": 1000,
            "armor_hp_pool": 0,
            "warp_max_tonnage": 0,
            "warp_energy_cost": 0,
            "mass_valid": True,
            "resource_storage": {},
        },
        "_metadata": {},
    }


@pytest.fixture
def fleets_on_hex(session_registries, ship_factory):
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_a.add_ship(ship_factory(_minimal_design("FleetAShip1"), owner_id=0))
    fleet_a.add_ship(ship_factory(_minimal_design("FleetAShip2"), owner_id=0))

    fleet_b = Fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    fleet_b.add_ship(ship_factory(_minimal_design("FleetBShip1"), owner_id=1))

    return [fleet_a, fleet_b]


class _FakeSettings:
    """Minimal stand-in for game_settings. Only the fields the compiler
    reads are present."""

    def __init__(self, combat_boundary_default=None):
        self.combat_boundary_default = combat_boundary_default


# ---------------------------------------------------------------------------
# Compiler output
# ---------------------------------------------------------------------------


def test_compiler_returns_battle_spec(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert isinstance(spec, BattleSpec)


def test_compiler_one_team_per_fleet(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert len(spec.teams) == 2
    # Each team holds its fleet's ships
    team0_ship_count = sum(
        len(sq.ships)
        for tf in spec.teams[0].fleet_hierarchy
        for sq in tf.squadrons
    )
    team1_ship_count = sum(
        len(sq.ships)
        for tf in spec.teams[1].fleet_hierarchy
        for sq in tf.squadrons
    )
    assert team0_ship_count == 2
    assert team1_ship_count == 1


def test_compiler_defaults_to_normal_telemetry(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert spec.telemetry_level == TelemetryLevel.NORMAL


def test_compiler_uses_boundary_from_settings(fleets_on_hex, session_registries):
    boundary = CircleBoundary(radius=5000.0, exit_policy=ExitPolicy.DESTROY)
    settings = _FakeSettings(combat_boundary_default=boundary)
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=settings,
        registries=session_registries,
    )
    assert spec.boundary is boundary


def test_compiler_none_settings_boundary_falls_back_to_unbounded(
    fleets_on_hex, session_registries
):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=_FakeSettings(combat_boundary_default=None),
        registries=session_registries,
    )
    assert isinstance(spec.boundary, UnboundedRegion)


def test_compiler_post_battle_hook_is_callable(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert callable(spec.post_battle_hook)


# ---------------------------------------------------------------------------
# Modifier translation
# ---------------------------------------------------------------------------


# PROJ-271 Phase 9: deleted `test_compiler_system_modifier_flows_into_global`,
# `test_compiler_sector_modifier_flows_into_global`, and
# `test_compiler_empire_modifier_flows_into_per_team`. These tests
# exercised `_entries_from_modifier_source` — a helper emitting
# `stat_key="placeholder"` for ad-hoc `sector.modifiers` /
# `system.modifiers` / `empire.combat_modifiers` iterables. No
# production code populated those attributes; the helper was
# dead-with-landmine (would silently drop effects if ever wired).
# Helper + call sites deleted in Phase 9; tests no longer exercise
# anything meaningful.


# ---------------------------------------------------------------------------
# Phase 2 Task 2.3 — ShipSpec.components populated from ShipInstance.components
# ---------------------------------------------------------------------------


def test_compiler_populates_ship_spec_components_from_instance(
    session_registries, ship_factory
):
    """Phase 2: the strategy compiler reads `ShipInstance.components` and
    emits a tuple of `ComponentStateSpec` entries on each `ShipSpec`.
    Previously Phase 1 always emitted an empty tuple."""
    from game.core.hex_math import HexCoord
    from game.simulation.battle_spec import ComponentStateSpec
    from game.strategy.data.component_state import (
        ComponentState,
        component_state_key,
    )
    from game.strategy.data.fleet import Fleet

    # Design with two identical laser_cannon components so we can verify
    # both are carried through by instance_index.
    design = {
        "name": "LaserCruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [{"id": "laser_cannon"}, {"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }

    fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
    ship_instance = ship_factory(design, owner_id=0)
    fleet.add_ship(ship_instance)

    # Damage laser_cannon#0 to 30% HP via ShipInstance.components.
    key0 = component_state_key("laser_cannon", 0)
    cs0 = ship_instance.components[key0]
    damaged_hp = cs0.current_hp * 0.3
    ship_instance.components[key0] = ComponentState(
        component_id=cs0.component_id,
        instance_index=cs0.instance_index,
        current_hp=damaged_hp,
        is_active=cs0.is_active,
    )

    spec = build_strategy_battle_spec(
        [fleet],
        sector=None,
        system=None,
        empires={},
        settings=None,
        registries=session_registries,
    )

    ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    # Phase 2 must populate components (Phase 1 always produced empty tuple).
    assert ship_spec.components, "ShipSpec.components must not be empty"

    # All entries must be ComponentStateSpec (not ComponentState).
    for entry in ship_spec.components:
        assert isinstance(entry, ComponentStateSpec)

    # Find the damaged entry and verify its current_hp roundtrips.
    laser_entries = [
        c for c in ship_spec.components
        if c.component_id == "laser_cannon"
    ]
    assert len(laser_entries) == 2
    damaged_entry = min(laser_entries, key=lambda c: c.current_hp)
    assert damaged_entry.current_hp == pytest.approx(damaged_hp, abs=0.5)


def test_compiler_empty_instance_components_yields_empty_ship_spec_components(
    session_registries, ship_factory
):
    """If `ShipInstance.components` is empty (edge case — should normally
    be populated by ShipInstance.create), the compiled spec falls back to
    an empty tuple rather than crashing."""
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet

    design = {
        "name": "EmptyComps",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {"CORE": [{"id": "bridge"}], "ARMOR": []},
        "_metadata": {},
    }

    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    ship_instance = ship_factory(design, owner_id=0)
    # Force components empty to simulate a legacy-save-loaded instance
    # that hasn't been populated yet.
    ship_instance.components = {}
    fleet.add_ship(ship_instance)

    spec = build_strategy_battle_spec(
        [fleet],
        sector=None,
        system=None,
        empires={},
        settings=None,
        registries=session_registries,
    )

    ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship_spec.components == ()
