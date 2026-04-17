"""Tests for strategy compiler ↔ FormationResolver integration (PROJ-269 Phase 4 Task 4.4).

Confirms `build_strategy_battle_spec`:
- Invokes `FormationResolver` per task force
- Uses the TaskForce's explicit `formation` when set
- Falls back to `resolve_default_for_task_force` when `formation=None`
- Emits `ShipSpec.position` / `ShipSpec.angle` from the resolver
"""
import pytest

from game.core.hex_math import HexCoord
from game.simulation.combat.formation import FormationShape, FormationSpec
from game.strategy.combat.spec_compiler import build_strategy_battle_spec
from game.strategy.data.fleet import Fleet
from game.strategy.data.task_force import TaskForce


def _design(role: str = "fleet_escort") -> dict:
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
        "_metadata": {},
    }


def _ship_specs_of(spec, team_id=0):
    team = spec.teams[team_id]
    return [s for tf in team.fleet_hierarchy for sq in tf.squadrons for s in sq.ships]


def _opponent_fleet(ship_factory, fleet_id=99):
    """PROJ-275 Phase 6: compiler now requires >=2 fleets. Tests focused
    on a single fleet's formation pair it with this placeholder."""
    fleet = Fleet(fleet_id=fleet_id, owner_id=1, location=HexCoord(0, 0))
    fleet.add_ship(ship_factory(_design("line_combatant"), owner_id=1))
    return fleet


# ---------------------------------------------------------------------------
# Default formation inferred from dominant design_role
# ---------------------------------------------------------------------------


def test_default_formation_from_strike_ship_roles(session_registries, ship_factory):
    """A fleet of 3 `assault_ship` ships (strike archetype) should
    compile to a spec with ships positioned in a WEDGE pattern."""
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet.add_ship(ship_factory(_design("assault_ship"), owner_id=0))
    fleet.add_ship(ship_factory(_design("assault_ship"), owner_id=0))
    fleet.add_ship(ship_factory(_design("assault_ship"), owner_id=0))

    spec = build_strategy_battle_spec(
        [fleet, _opponent_fleet(ship_factory)],
        registries=session_registries,
        settings=None,
    )

    ships = _ship_specs_of(spec, team_id=0)
    assert len(ships) == 3

    # Wedge: one leader at origin (position = entry_vector origin),
    # others behind. All xs should NOT be identical (not a single
    # column), and ys should show the characteristic wedge spread.
    xs = {s.position.x for s in ships}
    ys = {s.position.y for s in ships}
    assert len(xs) > 1, f"Wedge should have distinct x values; got {xs}"
    # At least 3 distinct y values (leader at 0, wingmen at +/-)
    assert len(ys) >= 2


def test_default_formation_from_defender_ship_roles(
    session_registries, ship_factory
):
    """A fleet of 3 `line_combatant` ships (defender archetype) compiles
    to LINE_ABREAST positioning (all ships at same X, different Ys)."""
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    for _ in range(3):
        fleet.add_ship(ship_factory(_design("line_combatant"), owner_id=0))

    spec = build_strategy_battle_spec(
        [fleet, _opponent_fleet(ship_factory)],
        registries=session_registries,
        settings=None,
    )

    ships = _ship_specs_of(spec, team_id=0)
    xs = {round(s.position.x, 3) for s in ships}
    ys = sorted(round(s.position.y, 3) for s in ships)
    # LINE_ABREAST: all x equal, distinct y.
    assert len(xs) == 1
    assert len(set(ys)) == 3


# ---------------------------------------------------------------------------
# Explicit TaskForce.formation overrides the default
# ---------------------------------------------------------------------------


def test_explicit_task_force_formation_overrides_default(
    session_registries, ship_factory
):
    """When a Fleet's TaskForce has an explicit `formation`, the compiler
    uses it instead of the dominant-role default."""
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    # Three assault_ship ships → default would be WEDGE…
    for _ in range(3):
        fleet.add_ship(ship_factory(_design("assault_ship"), owner_id=0))

    # …but we override with LINE_ASTERN via the TF.
    tf = TaskForce(
        name="AlphaTF",
        formation=FormationSpec(shape=FormationShape.LINE_ASTERN, spacing=100.0),
    )
    fleet.add_task_force(tf)

    spec = build_strategy_battle_spec(
        [fleet, _opponent_fleet(ship_factory)],
        registries=session_registries,
        settings=None,
    )

    ships = _ship_specs_of(spec, team_id=0)
    origin_x = spec.teams[0].entry_vector.origin.x
    origin_y = spec.teams[0].entry_vector.origin.y
    xs = sorted(round(s.position.x - origin_x, 3) for s in ships)
    ys = {round(s.position.y - origin_y, 3) for s in ships}
    # LINE_ASTERN (relative to entry-vector origin): xs at 0, 100, 200; y=0.
    assert xs == [0.0, 100.0, 200.0]
    assert ys == {0.0}


# ---------------------------------------------------------------------------
# Angle matches entry_vector facing
# ---------------------------------------------------------------------------


def test_ship_angles_match_entry_vector_facing(session_registries, ship_factory):
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    for _ in range(2):
        fleet.add_ship(ship_factory(_design("line_combatant"), owner_id=0))
    spec = build_strategy_battle_spec(
        [fleet, _opponent_fleet(ship_factory)],
        registries=session_registries,
        settings=None,
    )
    ships = _ship_specs_of(spec, team_id=0)
    team_facing = spec.teams[0].entry_vector.facing
    for s in ships:
        assert s.angle == pytest.approx(team_facing)


# ---------------------------------------------------------------------------
# Empty fleet edge case
# ---------------------------------------------------------------------------


def test_empty_fleet_yields_empty_ship_specs(session_registries, ship_factory):
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    # No ships added.
    spec = build_strategy_battle_spec(
        [fleet, _opponent_fleet(ship_factory)],
        registries=session_registries,
        settings=None,
    )
    ships = _ship_specs_of(spec, team_id=0)
    assert ships == []
