"""Integration: Battle Setup 3-sided flow → BattleSpec (PROJ-275 Phase 8.4).

Exercises the full `BattleSetupState → build_manual_battle_spec →
BattleSpec` path with three sides. The engine itself has long supported
N teams; the cross-cutting goal of PROJ-275 is ensuring every entry
point (Combat Lab, Battle Setup, Strategy) reaches the engine with a
proper N-team spec. This file covers the Battle Setup route.
"""
import pytest

from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.formation import resolve_team_entry_vectors
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec
from game.ui.screens.battle_setup_state import BattleSetupState


def _minimal_design(name: str) -> dict:
    return {
        "name": name,
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


def _make_ship(name: str, owner_id: int, ship_factory) -> ShipInstance:
    return ship_factory(_minimal_design(name), owner_id=owner_id)


def _populate_side(state: BattleSetupState, side_index: int, owner_id: int,
                   name_prefix: str, ship_count: int, ship_factory) -> None:
    side = state.sides[side_index]
    fleet = Fleet(
        fleet_id=100 + side_index,
        owner_id=owner_id,
        location=side.fleets[0].location if side.fleets else None,
    )
    for i in range(ship_count):
        fleet.add_ship(_make_ship(f"{name_prefix}_{i}", owner_id, ship_factory))
    side.add_fleet(fleet)


def test_three_sided_state_compiles_to_three_team_battle_spec(
    session_registries, ship_factory
):
    """BattleSetupState with 3 sides compiles to a BattleSpec with 3 teams,
    each carrying the side's fleet ships."""
    state = BattleSetupState(side_count=3)
    _populate_side(state, 0, owner_id=0, name_prefix="A", ship_count=2, ship_factory=ship_factory)
    _populate_side(state, 1, owner_id=1, name_prefix="B", ship_count=1, ship_factory=ship_factory)
    _populate_side(state, 2, owner_id=2, name_prefix="C", ship_count=3, ship_factory=ship_factory)

    spec = build_manual_battle_spec(state, registries=session_registries)

    assert isinstance(spec, BattleSpec)
    assert len(spec.teams) == 3
    team_ids = [t.team_id for t in spec.teams]
    assert team_ids == [0, 1, 2]

    # Each team contains its side's ships.
    def _team_ship_count(team) -> int:
        return sum(
            len(sq.ships)
            for tf in team.fleet_hierarchy
            for sq in tf.squadrons
        )

    assert _team_ship_count(spec.teams[0]) == 2
    assert _team_ship_count(spec.teams[1]) == 1
    assert _team_ship_count(spec.teams[2]) == 3


def test_three_sided_state_uses_ring_entry_vectors(
    session_registries, ship_factory
):
    """Entry vectors match `resolve_team_entry_vectors(3)`."""
    state = BattleSetupState(side_count=3)
    for i in range(3):
        _populate_side(state, i, owner_id=i, name_prefix=f"S{i}", ship_count=1, ship_factory=ship_factory)

    spec = build_manual_battle_spec(state, registries=session_registries)
    expected = resolve_team_entry_vectors(team_count=3)

    for team_id, team in enumerate(spec.teams):
        exp = expected[team_id]
        assert team.entry_vector.origin.x == pytest.approx(exp.origin.x)
        assert team.entry_vector.origin.y == pytest.approx(exp.origin.y)
        assert team.entry_vector.facing == pytest.approx(exp.facing)


def test_add_side_allows_growing_from_two_to_three_at_runtime():
    """`BattleSetupState.add_side()` preserves existing sides and lets the
    compiler produce a 3-team spec afterward."""
    state = BattleSetupState(side_count=2)
    assert len(state.sides) == 2
    new_side = state.add_side()
    assert new_side.team_id == 2
    assert len(state.sides) == 3


def test_battle_setup_state_rejects_single_side_at_compile_time(
    session_registries,
):
    """`BattleSetupState(side_count=1)` is disallowed; compiler also
    validates `2 <= num_teams <= 8`."""
    with pytest.raises(ValueError):
        BattleSetupState(side_count=1)


def test_battle_setup_state_rejects_nine_sides():
    with pytest.raises(ValueError):
        BattleSetupState(side_count=9)
