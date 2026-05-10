"""Tests for N-team-aware end conditions (PROJ-269 Phase 3 Task 3.5).

`TeamEliminatedCondition` fires when `number_of_teams_with_alive_ships <= 1`
— not when the first team dies. For 2-team battles the semantics are
equivalent; for N-team battles this is the difference between a
premature stop (first team down) and a correct stop (last team standing).
"""
from types import SimpleNamespace
from typing import List

from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TeamIncapacitatedCondition,
)


def _mk(team_id: int, alive: bool = True, derelict: bool = False):
    """Minimal ship-like object for condition tests."""
    return SimpleNamespace(
        team_id=team_id,
        is_alive=alive,
        is_derelict=derelict,
        total_thrust=10.0 if alive and not derelict else 0.0,
        turn_speed=10.0 if alive and not derelict else 0.0,
        get_all_components=lambda: [],
    )


# ---------------------------------------------------------------------------
# TeamEliminatedCondition — N-team
# ---------------------------------------------------------------------------


def test_team_eliminated_2_team_one_side_dead():
    """Regression: in a 2-team battle, condition fires when one team
    has 0 alive ships. (Same behavior as before Task 3.5.)"""
    ships = [_mk(0, alive=True), _mk(1, alive=False)]
    assert TeamEliminatedCondition().is_met(ships, 1) is True


def test_team_eliminated_3_team_one_down_still_contested():
    """In 3-team battle, condition must NOT fire when one team dies
    but two teams still have alive ships."""
    ships = [
        _mk(0, alive=True),
        _mk(1, alive=False),  # dead team
        _mk(2, alive=True),
    ]
    assert TeamEliminatedCondition().is_met(ships, 1) is False


def test_team_eliminated_3_team_two_down_last_standing():
    """N-team: fires when only one team remains with alive ships."""
    ships = [
        _mk(0, alive=True),
        _mk(1, alive=False),
        _mk(2, alive=False),
    ]
    assert TeamEliminatedCondition().is_met(ships, 1) is True


def test_team_eliminated_empty_ship_list_false():
    assert TeamEliminatedCondition().is_met([], 1) is False


def test_team_eliminated_check_derelict_3_team():
    """With check_derelict=True, derelict ships count as eliminated.
    Team 0 alive/op, team 1 derelict, team 2 dead → only team 0 counts → fire."""
    ships = [
        _mk(0, alive=True, derelict=False),
        _mk(1, alive=True, derelict=True),
        _mk(2, alive=False),
    ]
    assert TeamEliminatedCondition(check_derelict=True).is_met(ships, 1) is True


# ---------------------------------------------------------------------------
# TeamIncapacitatedCondition — N-team
# ---------------------------------------------------------------------------


def test_team_incapacitated_3_team_one_incap_still_contested():
    """Three teams, one team is incapacitated (no thrust, no weapons)
    but two teams still capable → no fire."""
    ships = [
        _mk(0, alive=True, derelict=False),
        _mk(1, alive=True, derelict=True),   # incap (derelict)
        _mk(2, alive=True, derelict=False),
    ]
    assert TeamIncapacitatedCondition().is_met(ships, 1) is False


def test_team_incapacitated_3_team_two_incap_fire():
    ships = [
        _mk(0, alive=True, derelict=False),
        _mk(1, alive=True, derelict=True),   # incap (derelict)
        _mk(2, alive=True, derelict=True),   # incap (derelict)
    ]
    assert TeamIncapacitatedCondition().is_met(ships, 1) is True


def test_team_incapacitated_2_team_backwards_compat():
    """2-team: unchanged behavior."""
    ships = [_mk(0, alive=True), _mk(1, alive=True, derelict=True)]
    assert TeamIncapacitatedCondition().is_met(ships, 1) is True
