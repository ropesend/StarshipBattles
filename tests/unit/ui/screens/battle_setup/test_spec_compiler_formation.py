"""Tests for Battle Setup compiler ↔ FormationResolver integration (PROJ-269 Phase 4 Task 4.5).

Confirms `build_manual_battle_spec`:
- Computes ship positions via `FormationResolver`
- Defaults to design-role-based formation when no explicit override
- Produces distinct entry vectors per side (team 0 vs team 1 positioning)
"""
import pytest

from game.core.math import Vector2
from game.simulation.combat.formation import FormationShape
from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec
from game.ui.screens.battle_setup_state import BattleSetupState


def _design(role: str) -> dict:
    return {
        "name": f"Ship_{role}",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": role,
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "ARMOR": [],
        },
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


def _ships_from_side(spec, team_id: int):
    return [
        s
        for tf in spec.teams[team_id].fleet_hierarchy
        for sq in tf.squadrons
        for s in sq.ships
    ]


def test_battle_setup_wires_formation_resolver(session_registries, ship_factory):
    """Three assault_ship ships on side 0 should produce a WEDGE
    (non-degenerate positions — xs not all 0)."""
    state = BattleSetupState()
    fleet = state.sides[0].create_fleet(name="Alpha")
    for _ in range(3):
        fleet.add_ship(ship_factory(_design("assault_ship"), owner_id=0))

    spec = build_manual_battle_spec(state, session_registries)
    ships = _ships_from_side(spec, team_id=0)
    xs = {round(s.position.x, 3) for s in ships}
    # WEDGE has distinct xs (leader at entry, others behind)
    assert len(xs) > 1


def test_battle_setup_defender_fleet_line_abreast(session_registries, ship_factory):
    """Defender-archetype fleet → LINE_ABREAST (single x column, distinct ys)."""
    state = BattleSetupState()
    fleet = state.sides[0].create_fleet(name="Alpha")
    for _ in range(3):
        fleet.add_ship(ship_factory(_design("line_combatant"), owner_id=0))

    spec = build_manual_battle_spec(state, session_registries)
    ships = _ships_from_side(spec, team_id=0)
    xs = {round(s.position.x, 3) for s in ships}
    ys = sorted(round(s.position.y, 3) for s in ships)
    assert len(xs) == 1
    assert len(set(ys)) == 3


def test_battle_setup_sides_have_opposing_entry_vectors(
    session_registries, ship_factory
):
    """Side 0 and side 1 should enter from opposite directions so
    ships don't start overlapping. Phase 4 MVP: side 0 faces east
    (facing=0), side 1 faces west (facing=180)."""
    state = BattleSetupState()
    fleet_a = state.sides[0].create_fleet(name="A")
    fleet_a.add_ship(ship_factory(_design("line_combatant"), owner_id=0))
    fleet_b = state.sides[1].create_fleet(name="B")
    fleet_b.add_ship(ship_factory(_design("line_combatant"), owner_id=1))

    spec = build_manual_battle_spec(state, session_registries)
    assert spec.teams[0].entry_vector.facing != spec.teams[1].entry_vector.facing


def test_battle_setup_ship_angles_match_entry_facing(
    session_registries, ship_factory
):
    state = BattleSetupState()
    fleet = state.sides[0].create_fleet(name="A")
    for _ in range(2):
        fleet.add_ship(ship_factory(_design("fleet_escort"), owner_id=0))
    spec = build_manual_battle_spec(state, session_registries)
    ships = _ships_from_side(spec, 0)
    facing = spec.teams[0].entry_vector.facing
    for s in ships:
        assert s.angle == pytest.approx(facing)
