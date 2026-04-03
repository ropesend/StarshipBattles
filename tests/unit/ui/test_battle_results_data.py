"""
Tests for battle results data extraction.

TDD tests for extracting post-battle statistics from engine state
into BattleResults dataclasses for the results screen.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.ui.screens.battle_results_data import (
    extract_battle_results,
    BattleResults,
    ShipResult,
    TeamSummary,
    WeaponStats,
)


# ============================================================================
# Test Helpers
# ============================================================================

def _make_weapon(name="Laser", shots_fired=100, shots_hit=75):
    """Create a mock weapon component."""
    weapon = Mock()
    weapon.name = name
    weapon.type = "Weapon"
    weapon.is_operational = True
    weapon.shots_fired = shots_fired
    weapon.shots_hit = shots_hit
    return weapon


def _make_ship(
    name="Ship", team_id=0, is_alive=True, is_derelict=False,
    hp=80.0, max_hp=100.0,
    current_shields=50.0, max_shields=100.0,
    weapons=None,
):
    """Create a mock ship for results extraction."""
    ship = Mock()
    ship.name = name
    ship.team_id = team_id
    ship.is_alive = is_alive
    ship.is_derelict = is_derelict
    ship.hp = hp
    ship.max_hp = max_hp
    ship.current_shields = current_shields
    ship.max_shields = max_shields

    all_components = weapons or []
    ship.get_all_components.return_value = all_components

    return ship


def _make_engine(ships=None, tick_counter=1000, winner=0):
    """Create a mock BattleEngine."""
    engine = Mock()
    engine.ships = ships or []
    engine.tick_counter = tick_counter
    engine.get_winner.return_value = winner
    return engine


# ============================================================================
# BattleResults extraction
# ============================================================================

class TestExtractBattleResults:
    """Tests for the extract_battle_results function."""

    def test_basic_extraction(self):
        ship1 = _make_ship(name="Alpha", team_id=0, hp=80, max_hp=100)
        ship2 = _make_ship(name="Beta", team_id=1, is_alive=False, hp=0, max_hp=100)
        engine = _make_engine(ships=[ship1, ship2], tick_counter=500, winner=0)

        results = extract_battle_results(engine, is_test_mode=False)

        assert isinstance(results, BattleResults)
        assert results.winner == 0
        assert results.tick_count == 500
        assert results.is_test_mode is False
        assert len(results.ships) == 2
        assert len(results.teams) == 2

    def test_ship_result_fields(self):
        weapon = _make_weapon("Laser Mk2", shots_fired=100, shots_hit=75)
        ship = _make_ship(
            name="Alpha", team_id=0, hp=80, max_hp=100,
            current_shields=50, max_shields=100,
            weapons=[weapon],
        )
        engine = _make_engine(ships=[ship])

        results = extract_battle_results(engine, is_test_mode=False)

        sr = results.ships[0]
        assert sr.name == "Alpha"
        assert sr.team_id == 0
        assert sr.is_alive is True
        assert sr.hp == 80.0
        assert sr.max_hp == 100.0
        assert sr.hp_percent == pytest.approx(80.0)
        assert sr.current_shields == 50.0
        assert sr.max_shields == 100.0
        assert len(sr.weapons) == 1
        assert sr.weapons[0].name == "Laser Mk2"
        assert sr.weapons[0].shots_fired == 100
        assert sr.weapons[0].shots_hit == 75
        assert sr.weapons[0].accuracy == pytest.approx(0.75)

    def test_weapon_zero_shots(self):
        weapon = _make_weapon("Rail Gun", shots_fired=0, shots_hit=0)
        ship = _make_ship(weapons=[weapon])
        engine = _make_engine(ships=[ship])

        results = extract_battle_results(engine, is_test_mode=False)

        ws = results.ships[0].weapons[0]
        assert ws.accuracy == 0.0

    def test_team_summary(self):
        ships = [
            _make_ship(name="A", team_id=0, is_alive=True),
            _make_ship(name="B", team_id=0, is_alive=False, hp=0, max_hp=100),
            _make_ship(name="C", team_id=0, is_alive=True, is_derelict=True),
            _make_ship(name="D", team_id=1, is_alive=True),
        ]
        engine = _make_engine(ships=ships)

        results = extract_battle_results(engine, is_test_mode=False)

        team0 = results.teams[0]
        assert team0.total_ships == 3
        assert team0.ships_alive == 1  # alive and not derelict
        assert team0.ships_derelict == 1
        assert team0.ships_destroyed == 1

        team1 = results.teams[1]
        assert team1.total_ships == 1
        assert team1.ships_alive == 1
        assert team1.ships_destroyed == 0

    def test_team_accuracy(self):
        w1 = _make_weapon(shots_fired=100, shots_hit=80)
        w2 = _make_weapon(shots_fired=50, shots_hit=10)
        ships = [
            _make_ship(team_id=0, weapons=[w1]),
            _make_ship(team_id=0, weapons=[w2]),
        ]
        engine = _make_engine(ships=ships)

        results = extract_battle_results(engine, is_test_mode=False)

        team0 = results.teams[0]
        assert team0.total_shots_fired == 150
        assert team0.total_shots_hit == 90
        assert team0.overall_accuracy == pytest.approx(0.6)

    def test_draw_result(self):
        ships = [
            _make_ship(team_id=0),
            _make_ship(team_id=1),
        ]
        engine = _make_engine(ships=ships, winner=-1)

        results = extract_battle_results(engine, is_test_mode=False)
        assert results.winner == -1

    def test_test_mode_flag(self):
        engine = _make_engine(ships=[])
        results = extract_battle_results(engine, is_test_mode=True)
        assert results.is_test_mode is True

    def test_duration_seconds(self):
        engine = _make_engine(ships=[], tick_counter=1000)
        results = extract_battle_results(engine, is_test_mode=False)
        # Default tick rate is 0.01, so 1000 ticks = 10 seconds
        assert results.duration_seconds == pytest.approx(10.0)

    def test_empty_battle(self):
        engine = _make_engine(ships=[], tick_counter=0, winner=-1)
        results = extract_battle_results(engine, is_test_mode=False)
        assert len(results.ships) == 0
        assert len(results.teams) == 0
