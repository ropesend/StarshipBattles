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
from game.simulation.combat.modifier_stack import ModifierStack
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


def test_compiler_system_modifier_flows_into_global(
    fleets_on_hex, session_registries
):
    class _FakeSystem:
        modifiers = [{"design_id": "system_bonus", "display_name": "System Bonus"}]

    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=_FakeSystem(),
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert isinstance(spec.modifier_stack, ModifierStack)
    sources = [e.source for e in spec.modifier_stack.global_]
    assert any("system:" in s for s in sources), sources


def test_compiler_sector_modifier_flows_into_global(
    fleets_on_hex, session_registries
):
    class _FakeSector:
        modifiers = [{"design_id": "sector_bonus", "display_name": "Sector Bonus"}]

    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=_FakeSector(),
        system=None,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    sources = [e.source for e in spec.modifier_stack.global_]
    assert any("sector:" in s for s in sources), sources


def test_compiler_empire_modifier_flows_into_per_team(
    fleets_on_hex, session_registries
):
    class _FakeEmpire:
        def __init__(self, modifier_design_id):
            self.combat_modifiers = [
                {
                    "design_id": modifier_design_id,
                    "display_name": modifier_design_id,
                }
            ]

    empires = {
        0: _FakeEmpire("empire0_buff"),
        1: _FakeEmpire("empire1_buff"),
    }
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        sector=None,
        system=None,
        empires=empires,
        settings=_FakeSettings(),
        registries=session_registries,
    )
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    team1_entries = spec.modifier_stack.per_team.get(1, ())
    assert any("empire0_buff" in e.source for e in team0_entries)
    assert any("empire1_buff" in e.source for e in team1_entries)
