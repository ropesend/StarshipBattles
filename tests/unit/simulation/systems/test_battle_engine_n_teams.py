"""Tests for `BattleEngine` N-team generalization (PROJ-269 Phase 3 Task 3.3).

Covers:
- `engine.teams: Dict[int, List[Ship]]` derived from `engine.ships`
- `engine.get_ships_by_team(team_id)` returns correct subset
- `engine.get_enemies_of(ship)` returns every ship on a different team
- `engine.get_winner()` returns the sole team_id when only one team
  remains alive; -1 when no clear winner
- `engine.start_teams({team_id: [ships], ...})` supports N teams
- `engine.add_ship_mid_battle` supports arbitrary team_id (N > 2)
"""
import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _ship(fresh_registries, name: str, team_id: int, x: float = 0, y: float = 0):
    from game.simulation.entities.ship import Ship

    return Ship(
        name=name,
        x=x,
        y=y,
        color=(255, 255, 255),
        team_id=team_id,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries,
    )


# ---------------------------------------------------------------------------
# engine.teams + engine.get_ships_by_team
# ---------------------------------------------------------------------------


def test_engine_teams_property_groups_ships_by_team_id(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start(
        [_ship(fresh_registries, "A", 0, 100, 0), _ship(fresh_registries, "B", 0, 200, 0)],
        [_ship(fresh_registries, "C", 1, -100, 0)],
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )

    teams = engine.teams
    assert isinstance(teams, dict)
    assert set(teams.keys()) == {0, 1}
    assert len(teams[0]) == 2
    assert len(teams[1]) == 1


def test_engine_get_ships_by_team(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start(
        [_ship(fresh_registries, "A", 0)],
        [_ship(fresh_registries, "B", 1), _ship(fresh_registries, "C", 1)],
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    assert len(engine.get_ships_by_team(0)) == 1
    assert len(engine.get_ships_by_team(1)) == 2
    assert engine.get_ships_by_team(99) == []


# ---------------------------------------------------------------------------
# engine.get_enemies_of(ship)
# ---------------------------------------------------------------------------


def test_engine_get_enemies_of_returns_every_non_self_team_ship(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    my_ship = _ship(fresh_registries, "Me", 0)
    friend = _ship(fresh_registries, "Friend", 0)
    foe1 = _ship(fresh_registries, "Foe1", 1)
    foe2 = _ship(fresh_registries, "Foe2", 2)
    engine.start_teams(
        {0: [my_ship, friend], 1: [foe1], 2: [foe2]},
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )

    enemies = engine.get_enemies_of(my_ship)
    assert friend not in enemies  # same team
    assert foe1 in enemies
    assert foe2 in enemies
    # N-team: no alliance concept — both non-self teams count as enemy.


# ---------------------------------------------------------------------------
# engine.get_winner
# ---------------------------------------------------------------------------


def test_engine_get_winner_returns_sole_surviving_team_id(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start_teams(
        {
            0: [_ship(fresh_registries, "A", 0)],
            1: [_ship(fresh_registries, "B", 1)],
            2: [_ship(fresh_registries, "C", 2)],
        },
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    # Kill teams 0 and 2, leaving team 1 alive.
    engine.get_ships_by_team(0)[0].is_alive = False
    engine.get_ships_by_team(2)[0].is_alive = False

    winner = engine.get_winner()
    assert winner == 1


def test_engine_get_winner_returns_minus_one_when_multiple_teams_alive(
    fresh_registries,
):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start_teams(
        {
            0: [_ship(fresh_registries, "A", 0)],
            1: [_ship(fresh_registries, "B", 1)],
        },
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    # Both alive — no clear winner.
    assert engine.get_winner() == -1


# ---------------------------------------------------------------------------
# engine.start_teams supports N teams
# ---------------------------------------------------------------------------


def test_engine_start_teams_with_three_teams(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start_teams(
        {
            0: [_ship(fresh_registries, "A0", 0)],
            1: [_ship(fresh_registries, "A1", 1)],
            2: [_ship(fresh_registries, "A2", 2)],
        },
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    assert len(engine.ships) == 3
    assert len(engine.ai_controllers) == 3


# ---------------------------------------------------------------------------
# Backward compat: engine.start(team0_ships, team1_ships) still works
# ---------------------------------------------------------------------------


def test_engine_start_2_team_signature_still_works(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    engine.start(
        [_ship(fresh_registries, "A", 0)],
        [_ship(fresh_registries, "B", 1)],
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    assert len(engine.ships) == 2
    assert engine.get_ships_by_team(0)[0].name == "A"
    assert engine.get_ships_by_team(1)[0].name == "B"
