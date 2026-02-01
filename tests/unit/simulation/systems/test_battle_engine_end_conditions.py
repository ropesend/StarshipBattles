"""
Tests for BattleEngine.is_battle_over() with extended end conditions.

TDD tests for:
- Absolute ceiling enforcement (safety net)
- ESCAPE_BASED mode (distance-based termination)
- Integration with existing modes
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

from game.simulation.systems.battle_end_conditions import (
    BattleEndMode,
    BattleEndCondition,
)
from game.simulation.systems.battle_engine import BattleEngine
from game.core.constants import SimulationConstants


@pytest.fixture
def mock_ship():
    """Create a mock ship for testing."""
    ship = Mock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = 0
    ship.position = pygame.math.Vector2(0, 0)
    ship.total_thrust = 100
    ship.turn_speed = 10
    ship.get_all_components.return_value = []
    return ship


@pytest.fixture
def mock_ship_team1():
    """Create a mock ship for team 1."""
    ship = Mock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = 1
    ship.position = pygame.math.Vector2(0, 0)
    ship.total_thrust = 100
    ship.turn_speed = 10
    ship.get_all_components.return_value = []
    return ship


@pytest.fixture
def battle_engine():
    """Create a BattleEngine instance for testing."""
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        engine = BattleEngine()
        # Initialize minimal state
        engine.ships = []
        engine.tick_counter = 0
        engine.end_condition = BattleEndCondition()
        return engine


class TestAbsoluteCeilingEnforcement:
    """Tests for absolute_max_ticks safety ceiling."""

    def test_absolute_ceiling_ends_manual_mode(self, battle_engine):
        """MANUAL mode should end when absolute_max_ticks is reached."""
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.MANUAL,
            absolute_max_ticks=1000
        )
        battle_engine.tick_counter = 1000

        assert battle_engine.is_battle_over() is True

    def test_absolute_ceiling_ends_time_based_mode(self, battle_engine):
        """TIME_BASED should end at absolute ceiling even if max_ticks not set."""
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=None,  # No max_ticks, but absolute ceiling applies
            absolute_max_ticks=500
        )
        battle_engine.tick_counter = 500

        assert battle_engine.is_battle_over() is True

    def test_absolute_ceiling_checked_first(self, battle_engine, mock_ship):
        """Absolute ceiling should be checked before mode-specific logic."""
        # HP_BASED normally wouldn't end with ships alive
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.HP_BASED,
            absolute_max_ticks=100
        )
        battle_engine.tick_counter = 100

        # Should end because ceiling reached, not because of HP
        assert battle_engine.is_battle_over() is True

    def test_below_absolute_ceiling_respects_mode(self, battle_engine, mock_ship):
        """Below ceiling, mode-specific logic should apply."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.MANUAL,
            absolute_max_ticks=1000
        )
        battle_engine.tick_counter = 500

        # MANUAL mode, below ceiling, shouldn't end
        assert battle_engine.is_battle_over() is False

    def test_default_absolute_ceiling_is_one_million(self, battle_engine):
        """Default absolute ceiling should be 1,000,000."""
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.MANUAL)

        # Should not end at 999,999
        battle_engine.tick_counter = 999_999
        assert battle_engine.is_battle_over() is False

        # Should end at 1,000,000
        battle_engine.tick_counter = 1_000_000
        assert battle_engine.is_battle_over() is True


class TestEscapeBasedMode:
    """Tests for ESCAPE_BASED battle termination."""

    def test_escape_mode_ends_when_ship_exceeds_radius(
        self, battle_engine, mock_ship
    ):
        """Battle should end when any ship exceeds escape_radius."""
        mock_ship.position = pygame.math.Vector2(6000, 0)  # Beyond 5000
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert battle_engine.is_battle_over() is True

    def test_escape_mode_continues_when_ships_inside_radius(
        self, battle_engine, mock_ship
    ):
        """Battle should continue when all ships within escape_radius."""
        mock_ship.position = pygame.math.Vector2(3000, 0)  # Within 5000
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert battle_engine.is_battle_over() is False

    def test_escape_mode_ignores_dead_ships(
        self, battle_engine, mock_ship
    ):
        """Dead ships should not trigger escape condition."""
        mock_ship.position = pygame.math.Vector2(10000, 0)  # Far beyond radius
        mock_ship.is_alive = False
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert battle_engine.is_battle_over() is False

    def test_escape_mode_team_specific(
        self, battle_engine, mock_ship, mock_ship_team1
    ):
        """escape_team should limit escape check to specific team."""
        # Team 0 ship far away
        mock_ship.position = pygame.math.Vector2(10000, 0)
        # Team 1 ship close
        mock_ship_team1.position = pygame.math.Vector2(100, 0)

        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
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
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
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
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
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
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        # Exactly at radius boundary - should not trigger (need to exceed)
        assert battle_engine.is_battle_over() is False

        # Just beyond boundary
        mock_ship.position = pygame.math.Vector2(3001, 4000)
        assert battle_engine.is_battle_over() is True


class TestExistingModesUnchanged:
    """Tests to verify existing modes still work correctly."""

    def test_time_based_mode_unchanged(self, battle_engine, mock_ship):
        """TIME_BASED should still work as before."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=100
        )

        battle_engine.tick_counter = 99
        assert battle_engine.is_battle_over() is False

        battle_engine.tick_counter = 100
        assert battle_engine.is_battle_over() is True

    def test_hp_based_mode_unchanged(self, battle_engine, mock_ship, mock_ship_team1):
        """HP_BASED should still work as before."""
        battle_engine.ships = [mock_ship, mock_ship_team1]
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.HP_BASED)

        # Both teams alive
        assert battle_engine.is_battle_over() is False

        # Team 1 eliminated
        mock_ship_team1.is_alive = False
        assert battle_engine.is_battle_over() is True

    def test_capability_based_mode_unchanged(self, battle_engine, mock_ship):
        """CAPABILITY_BASED should still work as before."""
        # Ship with no weapons and no movement
        mock_ship.total_thrust = 0
        mock_ship.turn_speed = 0
        mock_ship.get_all_components.return_value = []

        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(
            mode=BattleEndMode.CAPABILITY_BASED
        )

        # Team has no combat capability
        assert battle_engine.is_battle_over() is True

    def test_manual_mode_unchanged_below_ceiling(self, battle_engine, mock_ship):
        """MANUAL should not end automatically below ceiling."""
        battle_engine.ships = [mock_ship]
        battle_engine.end_condition = BattleEndCondition(mode=BattleEndMode.MANUAL)
        battle_engine.tick_counter = 100_000

        assert battle_engine.is_battle_over() is False
