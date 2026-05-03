"""
Tests for BattleEngine.is_battle_over() with extended end conditions.

TDD tests for:
- Absolute ceiling enforcement (safety net)
- ESCAPE_BASED mode (distance-based termination)
- Integration with existing modes
"""
import pytest
from unittest.mock import Mock, patch
import pygame

from game.simulation.systems.battle_end_conditions import (
    TickLimitCondition,
    TeamEliminatedCondition,
    TeamIncapacitatedCondition,
    EscapeCondition,
    NeverCondition,
)
from game.simulation.systems.battle_engine import BattleEngine


def _make_mock_ship(team_id: int = 0) -> Mock:
    """Build a minimal Mock ship for engine end-condition tests."""
    ship = Mock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = team_id
    ship.position = pygame.math.Vector2(0, 0)
    ship.total_thrust = 100
    ship.turn_speed = 10
    ship.get_all_components.return_value = []
    return ship


@pytest.fixture
def mock_ship():
    """Create a mock ship for testing (team 0)."""
    return _make_mock_ship(team_id=0)


@pytest.fixture
def mock_ship_team1():
    """Create a mock ship for team 1."""
    return _make_mock_ship(team_id=1)


@pytest.fixture
def battle_engine():
    """Create a BattleEngine instance for testing."""
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        engine = BattleEngine()
        # Initialize minimal state
        engine.ships = []
        engine.tick_counter = 0
        engine.end_condition = TeamEliminatedCondition()
        return engine


class TestAbsoluteCeilingEnforcement:
    """Tests for absolute_max_ticks safety ceiling."""

    def test_absolute_ceiling_ends_manual_mode(self, battle_engine):
        """NeverCondition should end when absolute_max_ticks is reached."""
        battle_engine.end_condition = NeverCondition()
        battle_engine._absolute_max_ticks = 1000
        battle_engine.tick_counter = 1000

        assert battle_engine.is_battle_over() is True

    def test_absolute_ceiling_ends_with_no_tick_limit(self, battle_engine):
        """Safety ceiling should end battle even without a TickLimitCondition."""
        battle_engine.end_condition = TeamEliminatedCondition()
        battle_engine._absolute_max_ticks = 500
        battle_engine.tick_counter = 500

        assert battle_engine.is_battle_over() is True

    def test_absolute_ceiling_checked_first(self, battle_engine, mock_ship):
        """Absolute ceiling should be checked before condition-specific logic."""
        # TeamEliminated normally wouldn't end with ships alive
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = TeamEliminatedCondition()
        battle_engine._absolute_max_ticks = 100
        battle_engine.tick_counter = 100

        # Should end because ceiling reached, not because of elimination
        assert battle_engine.is_battle_over() is True

    def test_below_absolute_ceiling_respects_condition(self, battle_engine, mock_ship):
        """Below ceiling, condition-specific logic should apply."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = NeverCondition()
        battle_engine._absolute_max_ticks = 1000
        battle_engine.tick_counter = 500

        # NeverCondition, below ceiling, shouldn't end
        assert battle_engine.is_battle_over() is False

    def test_default_absolute_ceiling_is_one_million(self, battle_engine):
        """Default absolute ceiling should be 1,000,000."""
        battle_engine.end_condition = NeverCondition()

        # Should not end at 999,999
        battle_engine.tick_counter = 999_999
        assert battle_engine.is_battle_over() is False

        # Should end at 1,000,000
        battle_engine.tick_counter = 1_000_000
        assert battle_engine.is_battle_over() is True


class TestEscapeBasedMode:
    """Tests for ESCAPE_BASED battle termination."""

    # PROJ-323 Task 3.21: 3 single-ship escape mode tests parametrized.
    @pytest.mark.parametrize("position,is_alive,expected_over", [
        # ship beyond radius -> battle ends
        pytest.param((6000, 0), True, True, id="ship_exceeds_radius"),
        # ship within radius -> battle continues
        pytest.param((3000, 0), True, False, id="ship_inside_radius"),
        # dead ship beyond radius is ignored -> battle continues
        pytest.param((10000, 0), False, False, id="dead_ship_ignored"),
    ])
    def test_escape_mode_single_ship(
        self, battle_engine, mock_ship, position, is_alive, expected_over,
    ):
        """Escape condition reacts only to live ships beyond escape_radius."""
        mock_ship.position = pygame.math.Vector2(*position)
        mock_ship.is_alive = is_alive
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = EscapeCondition(escape_radius=5000.0)

        assert battle_engine.is_battle_over() is expected_over

    def test_escape_mode_team_specific(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """escape_team should limit escape check to specific team."""
        # Team 0 ship far away
        mock_ship.position = pygame.math.Vector2(10000, 0)
        # Team 1 ship close
        mock_ship_team1.position = pygame.math.Vector2(100, 0)

        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = EscapeCondition(
            escape_radius=5000.0,
            escape_team=1  # Only team 1 escaping ends battle
        )

        # Team 0 escaped but we only care about team 1
        assert battle_engine.is_battle_over() is False

        # Now team 1 escapes
        mock_ship_team1.position = pygame.math.Vector2(6000, 0)
        assert battle_engine.is_battle_over() is True

    def test_escape_mode_all_ships_required(
        self, battle_engine, mock_ship
    ):
        """escape_all_ships=True should require all ships to escape."""
        ship2 = Mock()
        ship2.is_alive = True
        ship2.team_id = 0
        ship2.position = pygame.math.Vector2(100, 0)  # Inside radius

        mock_ship.position = pygame.math.Vector2(6000, 0)  # Outside radius

        battle_engine.ships = [mock_ship, ship2]
        battle_engine.end_condition = EscapeCondition(
            escape_radius=5000.0,
            escape_all_ships=True
        )

        # One ship outside, one inside - shouldn't end
        assert battle_engine.is_battle_over() is False

        # Both ships outside - should end
        ship2.position = pygame.math.Vector2(6000, 0)
        assert battle_engine.is_battle_over() is True

    def test_escape_mode_all_ships_specific_team(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """escape_all_ships with escape_team should only count that team."""
        ship2_team1 = Mock()
        ship2_team1.is_alive = True
        ship2_team1.team_id = 1
        ship2_team1.position = pygame.math.Vector2(100, 0)  # Inside radius

        # Team 0 ship far away (shouldn't count)
        mock_ship.position = pygame.math.Vector2(10000, 0)
        # Team 1 ships
        mock_ship_team1.position = pygame.math.Vector2(6000, 0)  # Outside
        ship2_team1.position = pygame.math.Vector2(100, 0)  # Inside

        battle_engine.ships = [mock_ship, mock_ship_team1, ship2_team1]
        battle_engine.end_condition = EscapeCondition(
            escape_radius=5000.0,
            escape_team=1,
            escape_all_ships=True
        )

        # Only one team 1 ship outside - shouldn't end
        assert battle_engine.is_battle_over() is False

        # Both team 1 ships outside - should end
        ship2_team1.position = pygame.math.Vector2(6000, 0)
        assert battle_engine.is_battle_over() is True

    def test_escape_mode_uses_euclidean_distance(
        self, battle_engine, mock_ship
    ):
        """Escape distance should use Euclidean distance from origin."""
        # Position at (3000, 4000) = distance of 5000 (3-4-5 triangle)
        mock_ship.position = pygame.math.Vector2(3000, 4000)
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = EscapeCondition(escape_radius=5000.0)

        # Exactly at radius boundary - should not trigger (need to exceed)
        assert battle_engine.is_battle_over() is False

        # Just beyond boundary
        mock_ship.position = pygame.math.Vector2(3001, 4000)
        assert battle_engine.is_battle_over() is True


class TestExistingModesUnchanged:
    """Tests to verify existing modes still work correctly."""

    def test_tick_limit_condition_works(self, battle_engine, mock_ship):
        """TickLimitCondition should end at max_ticks."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = TickLimitCondition(max_ticks=100)

        battle_engine.tick_counter = 99
        assert battle_engine.is_battle_over() is False

        battle_engine.tick_counter = 100
        assert battle_engine.is_battle_over() is True

    def test_team_eliminated_condition_works(self, battle_engine, mock_ship, mock_ship_team1):
        """TeamEliminatedCondition should end when a team is eliminated."""
        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = TeamEliminatedCondition()

        # Both teams alive
        assert battle_engine.is_battle_over() is False

        # Team 1 eliminated
        mock_ship_team1.is_alive = False
        assert battle_engine.is_battle_over() is True

    def test_team_incapacitated_condition_works(self, battle_engine, mock_ship):
        """TeamIncapacitatedCondition should end when a team can't fight."""
        # Ship with no weapons and no movement
        mock_ship.total_thrust = 0
        mock_ship.turn_speed = 0
        mock_ship.get_all_components.return_value = []

        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = TeamIncapacitatedCondition()

        # Team has no combat capability
        assert battle_engine.is_battle_over() is True

    def test_never_condition_below_ceiling(self, battle_engine, mock_ship):
        """NeverCondition should not end automatically below ceiling."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = NeverCondition()
        battle_engine.tick_counter = 100_000

        assert battle_engine.is_battle_over() is False


class TestTeamAliveCountingConsistency:
    """Tests for derelict handling consistency between is_battle_over() and get_winner()."""

    def test_check_derelict_enabled_ends_battle(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """TeamEliminatedCondition with check_derelict=True treats derelicts as eliminated."""
        mock_ship.is_alive = True
        mock_ship.is_derelict = True

        mock_ship_team1.is_alive = True
        mock_ship_team1.is_derelict = False

        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = TeamEliminatedCondition(check_derelict=True)

        # is_battle_over should be True (team 0 has no non-derelict alive ships)
        assert battle_engine.is_battle_over() is True
        # get_winner returns -1 (draw) because both ships are still is_alive=True
        # The end condition treats derelicts as eliminated, but get_winner()
        # uses simple alive counting independent of the condition
        assert battle_engine.get_winner() == -1

    def test_check_derelict_disabled_keeps_battle_going(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """TeamEliminatedCondition with check_derelict=False counts derelicts as alive."""
        mock_ship.is_alive = True
        mock_ship.is_derelict = True

        mock_ship_team1.is_alive = True
        mock_ship_team1.is_derelict = False

        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = TeamEliminatedCondition(check_derelict=False)

        assert battle_engine.is_battle_over() is False
        assert battle_engine.get_winner() == -1

    def test_team_eliminated_both_teams_alive(self, battle_engine, mock_ship, mock_ship_team1):
        """TeamEliminatedCondition should not end when both teams have alive ships."""
        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = TeamEliminatedCondition(check_derelict=False)

        assert battle_engine.is_battle_over() is False
        assert battle_engine.get_winner() == -1

    def test_team_eliminated_derelict_check_counts_correctly(self, battle_engine, mock_ship, mock_ship_team1):
        """TeamEliminatedCondition with check_derelict=True correctly identifies eliminated team."""
        mock_ship.is_derelict = True
        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = TeamEliminatedCondition(check_derelict=True)

        # Team 0 is derelict, so end condition is met
        assert battle_engine.is_battle_over() is True
        # get_winner returns -1 because both ships are still is_alive=True
        assert battle_engine.get_winner() == -1
