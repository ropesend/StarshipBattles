"""
Unit tests for game/ai/controller.py

Tests AIController behavior selection, engage distance logic, and targeting.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship with standard interface."""
    ship = Mock()
    ship.get_position.return_value = Vector2(100, 100)
    ship.get_weapon_range.return_value = 200.0
    ship.get_rotation.return_value = 0.0
    ship.get_max_speed.return_value = 100.0
    ship.get_radius.return_value = 10.0
    ship.get_vehicle_type.return_value = 'Frigate'
    ship.get_ai_strategy.return_value = 'standard_ranged'
    ship.get_team_id.return_value = 0
    ship.is_alive.return_value = True
    ship.is_in_formation.return_value = False
    ship.get_formation_master.return_value = None
    ship.get_formation_members.return_value = []
    ship.get_current_target.return_value = None
    ship.get_max_targets.return_value = 1
    ship.get_components_by_ability.return_value = []
    ship.set_trigger_pulled = Mock()
    ship.set_current_target = Mock()
    ship.set_secondary_targets = Mock()
    ship.set_throttle = Mock()
    ship.set_turn_throttle = Mock()
    ship.id = 'test_ship'
    return ship


@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = Mock()
    grid.query_radius.return_value = []
    return grid


@pytest.fixture
def mock_strategy_manager():
    """Create mock StrategyManager with default strategy."""
    with patch('game.ai.controller.StrategyManager') as mock_sm:
        instance = Mock()
        instance.resolve_strategy.return_value = {
            'definition': {},
            'targeting': {'rules': []},
            'movement': {
                'behavior': 'kite',
                'engage_distance': 'max_range',
                'retreat_hp_threshold': 0.1,
            }
        }
        mock_sm.instance.return_value = instance
        yield mock_sm


@pytest.fixture
def controller(mock_ship, mock_grid, mock_strategy_manager):
    """Create an AIController instance."""
    from game.ai.controller import AIController
    return AIController(mock_ship, mock_grid, enemy_team_id=1)


class TestGetEngageDistanceMultiplier:
    """Tests for get_engage_distance_multiplier."""

    def test_get_engage_distance_max_range(self, controller):
        """'max_range' returns 1.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'max_range'})
        assert result == 1.0

    def test_get_engage_distance_ram(self, controller):
        """'ram' returns 0.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'ram'})
        assert result == 0.0

    def test_get_engage_distance_numeric(self, controller):
        """0.8 returns 0.8."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 0.8})
        assert result == 0.8

    def test_get_engage_distance_default(self, controller):
        """Unknown string returns 1.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'unknown'})
        assert result == 1.0

    def test_get_engage_distance_missing_key(self, controller):
        """Missing key returns 1.0 (default)."""
        result = controller.get_engage_distance_multiplier({})
        assert result == 1.0


class TestBehaviorSelection:
    """Tests for behavior selection logic."""

    def test_behavior_selection_formation(self, mock_ship, mock_grid, mock_strategy_manager):
        """In formation -> 'formation' behavior."""
        from game.ai.controller import AIController

        mock_ship.is_in_formation.return_value = True
        master = Mock()
        master.current_target = None
        mock_ship.get_formation_master.return_value = master

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.update()

        # Current behavior should be formation
        assert controller.current_behavior is controller.behaviors['formation']

    def test_behavior_selection_flee(self, mock_ship, mock_grid, mock_strategy_manager):
        """HP below threshold -> 'flee' behavior."""
        from game.ai.controller import AIController

        # Set up target so behavior runs
        target = Mock()
        target.is_alive = True
        target.position = Vector2(200, 100)
        mock_ship.get_current_target.return_value = target

        # Mock HP to be below retreat threshold (10%)
        with patch('game.ai.controller.get_hp_percent', return_value=0.05):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        assert controller.current_behavior is controller.behaviors['flee']

    def test_behavior_selection_policy(self, mock_ship, mock_grid, mock_strategy_manager):
        """Normal HP -> policy behavior (kite/ram/etc)."""
        from game.ai.controller import AIController

        target = Mock()
        target.is_alive = True
        target.position = Vector2(200, 100)
        mock_ship.get_current_target.return_value = target

        # Normal HP (50%)
        with patch('game.ai.controller.get_hp_percent', return_value=0.5):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        # Default behavior from mock strategy is 'kite'
        assert controller.current_behavior is controller.behaviors['kite']


class TestSatelliteException:
    """Tests for satellite-specific behavior."""

    def test_satellite_exception_no_movement(self, mock_ship, mock_grid, mock_strategy_manager):
        """Vehicle type 'Satellite' skips movement."""
        from game.ai.controller import AIController

        mock_ship.get_vehicle_type.return_value = 'Satellite'

        target = Mock()
        target.is_alive = True
        mock_ship.get_current_target.return_value = target

        with patch('game.ai.controller.get_hp_percent', return_value=0.5):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        # Satellite should not have a behavior assigned
        assert controller.current_behavior is None


class TestDeadShipHandling:
    """Tests for dead ship handling."""

    def test_dead_ship_no_action(self, mock_ship, mock_grid, mock_strategy_manager):
        """update() returns early for dead ship."""
        from game.ai.controller import AIController

        mock_ship.is_alive.return_value = False

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.update()

        # Should not set any behavior
        assert controller.current_behavior is None
        # Should not try to set target
        mock_ship.set_current_target.assert_not_called()


class TestFindTarget:
    """Tests for target finding logic."""

    def test_find_target_returns_highest_scored(self, mock_ship, mock_grid, mock_strategy_manager):
        """Multiple enemies, returns best scored."""
        from game.ai.controller import AIController

        # Create enemy ships
        enemy1 = Mock()
        enemy1.is_alive = True
        enemy1.team_id = 1
        enemy1.position = Vector2(200, 100)
        enemy1.id = 'enemy1'
        enemy1.get_components_by_ability = Mock(return_value=[])

        enemy2 = Mock()
        enemy2.is_alive = True
        enemy2.team_id = 1
        enemy2.position = Vector2(300, 100)
        enemy2.id = 'enemy2'
        enemy2.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [enemy1, enemy2]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Mock TargetEvaluator to return different scores
        with patch('game.ai.controller.TargetEvaluator.evaluate') as mock_eval:
            mock_eval.side_effect = lambda ship, target, rules, **kwargs: (
                100.0 if target.id == 'enemy1' else 50.0
            )
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is enemy1

    def test_find_target_no_enemies_returns_none(self, mock_ship, mock_grid, mock_strategy_manager):
        """Empty grid returns None."""
        from game.ai.controller import AIController

        mock_grid.query_radius.return_value = []

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        result = controller.find_target()

        assert result is None

    def test_find_target_filters_allies(self, mock_ship, mock_grid, mock_strategy_manager):
        """Only returns enemies, not allies."""
        from game.ai.controller import AIController

        ally = Mock()
        ally.is_alive = True
        ally.team_id = 0  # Same team as our ship
        ally.position = Vector2(200, 100)
        ally.get_components_by_ability = Mock(return_value=[])

        enemy = Mock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(300, 100)
        enemy.id = 'enemy'
        enemy.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [ally, enemy]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is enemy

    def test_find_target_filters_dead(self, mock_ship, mock_grid, mock_strategy_manager):
        """Only returns alive enemies."""
        from game.ai.controller import AIController

        dead_enemy = Mock()
        dead_enemy.is_alive = False
        dead_enemy.team_id = 1
        dead_enemy.position = Vector2(200, 100)
        dead_enemy.get_components_by_ability = Mock(return_value=[])

        alive_enemy = Mock()
        alive_enemy.is_alive = True
        alive_enemy.team_id = 1
        alive_enemy.position = Vector2(300, 100)
        alive_enemy.id = 'alive'
        alive_enemy.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [dead_enemy, alive_enemy]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is alive_enemy
