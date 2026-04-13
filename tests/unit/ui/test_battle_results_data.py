"""
Tests for battle results data extraction.

PROJ-270 Phase 4.5: rewritten. `extract_battle_results` now consumes
`BattleOutcome` instead of a live `BattleEngine`; tests build real
frozen DTOs rather than mock engines.
"""
import pytest

from game.core.math import Vector2
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TaskForceOutcome,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.combat.telemetry import TelemetryLevel
from game.ui.screens.battle_results_data import (
    extract_battle_results,
    BattleResults,
    ShipResult,
    TeamSummary,
    WeaponStats,
)


# ============================================================================
# Builders — real frozen outcome DTOs
# ============================================================================


_ZERO_STATS = ShipStats(
    total_damage_taken=0.0, peak_speed=0.0, ticks_derelict=0, ticks_alive=0,
)


def _weapon(name="Laser", shots_fired=100, shots_hit=75):
    return WeaponSummary(
        component_id=name.lower().replace(" ", "_"),
        component_name=name,
        shots_fired=shots_fired,
        shots_hit=shots_hit,
    )


def _ship_outcome(
    name="Ship",
    status=ShipStatus.SURVIVED,
    hp=80.0,
    max_hp=100.0,
    current_shields=50.0,
    max_shields=100.0,
    weapons=(),
    ship_class="Escort",
):
    return ShipOutcome(
        instance_id=name,
        status=status,
        final_position=Vector2(0.0, 0.0),
        final_angle=0.0,
        final_velocity=Vector2(0.0, 0.0),
        components=(),
        weapons=tuple(weapons),
        hits_taken=(),
        stats=_ZERO_STATS,
        name=name,
        ship_class=ship_class,
        hp=hp,
        max_hp=max_hp,
        current_shields=current_shields,
        max_shields=max_shields,
    )


def _team_outcome(team_id, ships):
    return TeamOutcome(
        team_id=team_id,
        name=f"Team {team_id}",
        fleet_hierarchy=(),
        ships=tuple(ships),
    )


def _outcome(teams, duration_ticks=500):
    return BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=duration_ticks,
        seed=0,
        teams=tuple(teams),
        telemetry_level=TelemetryLevel.NORMAL,
    )


# ============================================================================
# BattleResults extraction tests
# ============================================================================


class TestExtractBattleResults:
    """Tests for the extract_battle_results function."""

    def test_basic_extraction(self):
        ships_t0 = [_ship_outcome(name="Alpha", status=ShipStatus.SURVIVED)]
        ships_t1 = [_ship_outcome(
            name="Beta",
            status=ShipStatus.DESTROYED,
            hp=0.0,
        )]
        outcome = _outcome([
            _team_outcome(0, ships_t0),
            _team_outcome(1, ships_t1),
        ], duration_ticks=500)

        results = extract_battle_results(outcome, return_destination="battle_setup")

        assert isinstance(results, BattleResults)
        assert results.winner == 0  # only team 0 has survivors
        assert results.tick_count == 500
        assert results.return_destination == "battle_setup"
        assert len(results.ships) == 2
        assert len(results.teams) == 2

    def test_ship_result_fields(self):
        weapon = _weapon("Laser Mk2", shots_fired=100, shots_hit=75)
        ships_t0 = [_ship_outcome(
            name="Alpha", hp=80, max_hp=100,
            current_shields=50, max_shields=100,
            weapons=(weapon,),
        )]
        outcome = _outcome([_team_outcome(0, ships_t0)])

        results = extract_battle_results(outcome, return_destination="battle_setup")

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
        weapon = _weapon("Rail Gun", shots_fired=0, shots_hit=0)
        ships_t0 = [_ship_outcome(weapons=(weapon,))]
        outcome = _outcome([_team_outcome(0, ships_t0)])

        results = extract_battle_results(outcome, return_destination="battle_setup")
        assert results.ships[0].weapons[0].accuracy == 0.0

    def test_team_summary(self):
        ships_t0 = [
            _ship_outcome(name="A", status=ShipStatus.SURVIVED),
            _ship_outcome(name="B", status=ShipStatus.DESTROYED, hp=0),
            _ship_outcome(name="C", status=ShipStatus.DERELICT),
        ]
        ships_t1 = [_ship_outcome(name="D", status=ShipStatus.SURVIVED)]
        outcome = _outcome([
            _team_outcome(0, ships_t0),
            _team_outcome(1, ships_t1),
        ])

        results = extract_battle_results(outcome, return_destination="battle_setup")

        team0 = results.teams[0]
        assert team0.total_ships == 3
        assert team0.ships_alive == 1
        assert team0.ships_derelict == 1
        assert team0.ships_destroyed == 1

        team1 = results.teams[1]
        assert team1.total_ships == 1
        assert team1.ships_alive == 1
        assert team1.ships_destroyed == 0

    def test_team_accuracy(self):
        w1 = _weapon(shots_fired=100, shots_hit=80)
        w2 = _weapon(shots_fired=50, shots_hit=10)
        ships_t0 = [
            _ship_outcome(name="A", weapons=(w1,)),
            _ship_outcome(name="B", weapons=(w2,)),
        ]
        outcome = _outcome([_team_outcome(0, ships_t0)])

        results = extract_battle_results(outcome, return_destination="battle_setup")
        team0 = results.teams[0]
        assert team0.total_shots_fired == 150
        assert team0.total_shots_hit == 90
        assert team0.overall_accuracy == pytest.approx(0.6)

    def test_draw_result(self):
        """Both teams have survivors → winner is -1 (draw)."""
        ships_t0 = [_ship_outcome(name="A", status=ShipStatus.SURVIVED)]
        ships_t1 = [_ship_outcome(name="B", status=ShipStatus.SURVIVED)]
        outcome = _outcome([
            _team_outcome(0, ships_t0),
            _team_outcome(1, ships_t1),
        ])
        results = extract_battle_results(outcome, return_destination="battle_setup")
        assert results.winner == -1

    def test_return_destination_passed_through(self):
        outcome = _outcome([_team_outcome(0, [])])
        results = extract_battle_results(outcome, return_destination="test_lab")
        assert results.return_destination == "test_lab"

    def test_duration_seconds(self):
        outcome = _outcome([_team_outcome(0, [])], duration_ticks=1000)
        results = extract_battle_results(outcome, return_destination="battle_setup")
        # Default tick rate 0.01 → 1000 ticks ≈ 10 seconds
        assert results.duration_seconds == pytest.approx(10.0)

    def test_empty_battle(self):
        outcome = _outcome([], duration_ticks=0)
        results = extract_battle_results(outcome, return_destination="battle_setup")
        assert len(results.ships) == 0
        assert len(results.teams) == 0
