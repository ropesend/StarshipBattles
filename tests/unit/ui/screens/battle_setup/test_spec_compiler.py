"""Tests for Battle Setup spec compiler (PROJ-269 Phase 1 Task 1.8).

Covers:
- `build_manual_battle_spec(ui_state, registries)` returns a `BattleSpec`
- Ships from `ui_state.side_0.fleets` flow into `spec.teams[0]`
  (and side_1 → team[1])
- Modifier toggles from UI (system_complexes / sector_complexes) flow
  into `ModifierStack.per_team` (do NOT mutate ships)
- `telemetry_level` defaults to NORMAL
"""
import pytest

from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec
from game.ui.screens.battle_setup_state import BattleSetupState
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Fixtures — build a minimal UI state with real ShipInstances from the
# session registries.
# ---------------------------------------------------------------------------


def _minimal_design_data(name: str) -> dict:
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
def ui_state_with_ships(session_registries, ship_factory) -> BattleSetupState:
    state = BattleSetupState()

    fleet_a = state.side_0.create_fleet(name="Side 0 Fleet A")
    fleet_a.add_ship(ship_factory(_minimal_design_data("SideZeroShipA1"), owner_id=0))
    fleet_a.add_ship(ship_factory(_minimal_design_data("SideZeroShipA2"), owner_id=0))

    fleet_b = state.side_1.create_fleet(name="Side 1 Fleet B")
    fleet_b.add_ship(ship_factory(_minimal_design_data("SideOneShipB1"), owner_id=1))

    return state


# ---------------------------------------------------------------------------
# Compiler output
# ---------------------------------------------------------------------------


def test_compiler_returns_battle_spec(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec, BattleSpec)


def test_compiler_side_0_ships_flow_into_team_0(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0 = spec.teams[0]
    ships = [
        s for tf in team0.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
    ]
    assert len(ships) == 2
    names = {s.name for s in ships}
    assert names == {"SideZeroShipA1", "SideZeroShipA2"}


def test_compiler_side_1_ships_flow_into_team_1(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team1 = spec.teams[1]
    ships = [
        s for tf in team1.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
    ]
    assert len(ships) == 1
    assert ships[0].name == "SideOneShipB1"


def test_compiler_preserves_instance_ids_from_ship_instances(
    ui_state_with_ships, session_registries
):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    spec_ids = []
    for team in spec.teams:
        for tf in team.fleet_hierarchy:
            for sq in tf.squadrons:
                for s in sq.ships:
                    spec_ids.append(s.instance_id)

    ui_ids = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                ui_ids.append(ship.instance_id)

    assert set(spec_ids) == set(ui_ids)


def test_compiler_defaults_to_normal_telemetry(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert spec.telemetry_level == TelemetryLevel.NORMAL


def test_compiler_uses_unbounded_region_by_default(
    ui_state_with_ships, session_registries
):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec.boundary, UnboundedRegion)


# ---------------------------------------------------------------------------
# Modifier translation — complex toggles do NOT mutate the input ships.
# ---------------------------------------------------------------------------


def test_compiler_system_complex_toggle_flows_into_modifier_stack(
    ui_state_with_ships, session_registries
):
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "shield_booster", "display_name": "Shield Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec.modifier_stack, ModifierStack)
    # Team 0 should carry at least one entry tagged to the complex.
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    assert len(team0_entries) >= 1
    assert any("shield_booster" in e.source for e in team0_entries)


def test_compiler_sector_complex_toggle_flows_into_modifier_stack(
    ui_state_with_ships, session_registries
):
    ui_state_with_ships.side_1.sector_complexes.append(
        {"design_id": "damage_booster", "display_name": "Damage Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team1_entries = spec.modifier_stack.per_team.get(1, ())
    assert len(team1_entries) >= 1
    assert any("damage_booster" in e.source for e in team1_entries)


def test_compiler_does_not_mutate_ships(ui_state_with_ships, session_registries):
    # Capture ship attributes before compilation.
    snapshots = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                snapshots.append(
                    (
                        ship.instance_id,
                        ship.design_id,
                        ship.name,
                        ship.owner_id,
                    )
                )

    # Add some modifiers — these should NOT cause ship mutation.
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "shield_booster", "display_name": "Shield Booster"}
    )
    ui_state_with_ships.side_1.sector_complexes.append(
        {"design_id": "damage_booster", "display_name": "Damage Booster"}
    )

    build_manual_battle_spec(ui_state_with_ships, session_registries)

    # Re-check every attribute.
    after = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                after.append(
                    (
                        ship.instance_id,
                        ship.design_id,
                        ship.name,
                        ship.owner_id,
                    )
                )
    assert after == snapshots


def test_compiler_empty_ui_state_yields_empty_teams(session_registries):
    empty = BattleSetupState()
    spec = build_manual_battle_spec(empty, session_registries)
    assert len(spec.teams) == 2
    for team in spec.teams:
        ships = [
            s for tf in team.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
        ]
        assert ships == []
