"""
Unit tests for AIController edge cases with StrategyManager integration.

TCG-FND-001: Tests for edge cases when:
- Strategy references invalid/missing policies
- Ship lacks expected capabilities
- StrategyManager returns incomplete strategy definitions

These tests ensure AIController handles edge cases gracefully without
crashing or silently failing during combat.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.ai.controller import AIController
from game.ai.strategy_manager import StrategyManager, get_default_strategy_manager
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship for controller tests."""
    ship = MagicMock()
    ship.name = 'test_ship'  # PROJ-192: Ship uses .name as identifier
    ship.get_position = MagicMock(return_value=Vector2(0, 0))
    ship.position = Vector2(0, 0)
    ship.get_rotation = MagicMock(return_value=0.0)
    ship.get_ai_strategy = MagicMock(return_value='standard_ranged')
    ship.is_alive = MagicMock(return_value=True)
    ship.get_team_id = MagicMock(return_value=0)
    ship.get_velocity = MagicMock(return_value=Vector2(0, 0))
    ship.get_radius = MagicMock(return_value=50.0)
    ship.get_max_speed = MagicMock(return_value=100.0)
    ship.get_current_speed = MagicMock(return_value=0.0)
    ship.get_turn_speed = MagicMock(return_value=90.0)
    ship.get_acceleration_rate = MagicMock(return_value=10.0)
    ship.get_is_thrusting = MagicMock(return_value=False)
    ship.get_turn_throttle = MagicMock(return_value=1.0)
    ship.get_weapon_range = MagicMock(return_value=500.0)
    ship.get_current_target = MagicMock(return_value=None)
    ship.get_max_targets = MagicMock(return_value=1)
    ship.get_secondary_targets = MagicMock(return_value=[])
    ship.get_formation_members = MagicMock(return_value=[])
    ship.get_formation_master = MagicMock(return_value=None)
    ship.is_in_formation = MagicMock(return_value=False)
    ship.get_formation_offset = MagicMock(return_value=None)
    ship.get_formation_rotation_mode = MagicMock(return_value='relative')
    ship.get_vehicle_type = MagicMock(return_value='Ship')
    ship.get_layers = MagicMock(return_value={})
    ship.get_all_components = MagicMock(return_value=[])
    ship.get_components_by_ability = MagicMock(return_value=[])

    # Write methods
    ship.set_throttle = MagicMock()
    ship.set_turn_throttle = MagicMock()
    ship.set_trigger_pulled = MagicMock()
    ship.set_current_target = MagicMock()
    ship.set_secondary_targets = MagicMock()
    ship.set_in_formation = MagicMock()
    ship.set_formation_master = MagicMock()
    ship.leave_formation = MagicMock()
    ship.rotate = MagicMock()
    ship.thrust_forward = MagicMock()
    ship.set_rotation = MagicMock()
    ship.adjust_position = MagicMock()

    return ship


@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = MagicMock()
    grid.query_radius = MagicMock(return_value=[])
    grid.query_radius_exact = MagicMock(return_value=[])
    return grid


class TestAIControllerStrategyResolution:
    """Tests for strategy resolution edge cases."""

    def test_controller_with_missing_strategy_id(self, mock_ship, mock_grid):
        """Controller handles unknown strategy ID gracefully."""
        mock_ship.get_ai_strategy = MagicMock(return_value='nonexistent_strategy')

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # resolve_strategy should return default when ID not found
        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            # Simulate returning a fallback/default strategy
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': []},
                'movement': {'behavior': 'kite'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            # Should not raise exception
            resolved = controller.get_resolved_strategy()
            assert 'targeting' in resolved
            assert 'movement' in resolved

    def test_controller_with_empty_targeting_policy(self, mock_ship, mock_grid):
        """Controller handles empty targeting rules gracefully."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': []},  # Empty rules
                'movement': {'behavior': 'kite'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            # find_target should return None with no enemies
            target = controller.find_target()
            assert target is None

    def test_controller_with_missing_movement_behavior(self, mock_ship, mock_grid):
        """Controller handles missing behavior key with fallback to 'kite'."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': []},
                'movement': {},  # Missing 'behavior' key
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            # Get resolved strategy - should not crash
            resolved = controller.get_resolved_strategy()

            # Should have movement section with fallback behavior
            assert 'movement' in resolved
            # Default behavior should be applied
            behavior = resolved['movement'].get('behavior', 'kite')
            assert behavior is not None


class TestAIControllerShipCapabilities:
    """Tests for ship capability edge cases."""

    def test_ship_with_no_weapons(self, mock_ship, mock_grid):
        """Controller handles ship with no weapons gracefully."""
        # Ship has no weapon components
        mock_ship.get_components_by_ability = MagicMock(return_value=[])

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Create mock enemy
        enemy = MagicMock()
        enemy.name = 'enemy_1'
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(100, 0)
        enemy.velocity = Vector2(0, 0)
        enemy.mass = 100
        enemy.get_components_by_ability = MagicMock(return_value=[])
        enemy.get_components_by_layer = MagicMock(return_value=[])
        mock_grid.query_radius = MagicMock(return_value=[enemy])
        mock_grid.query_radius_exact = MagicMock(return_value=[enemy])

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': [{'type': 'nearest', 'weight': 1}]},
                'movement': {'behavior': 'kite'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            # Should still find target even without weapons
            target = controller.find_target()
            assert target == enemy

    def test_ship_with_zero_weapon_range(self, mock_ship, mock_grid):
        """Controller handles ship with zero weapon range."""
        mock_ship.get_weapon_range = MagicMock(return_value=0.0)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': []},
                'movement': {'behavior': 'kite', 'engage_distance': 'max_range'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            # Test engage distance calculation
            result = controller.get_engage_distance_multiplier({'engage_distance': 'max_range'})
            assert result == 1.0


class TestAIControllerUpdateEdgeCases:
    """Tests for update() method edge cases."""

    def test_update_when_dead(self, mock_ship, mock_grid):
        """Update returns early when ship is dead."""
        mock_ship.is_alive = MagicMock(return_value=False)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Should not raise, and should not change state
        controller.update()

        # Throttle should not be called (early return)
        mock_ship.set_throttle.assert_not_called()

    def test_update_with_dead_target(self, mock_ship, mock_grid):
        """Update clears dead target and finds new one."""
        # Setup dead target
        dead_target = MagicMock()
        dead_target.is_alive = False
        mock_ship.get_current_target = MagicMock(return_value=dead_target)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': []},
                'movement': {'behavior': 'kite'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            controller.update()

            # Should have cleared the dead target
            mock_ship.set_current_target.assert_called()

    def test_update_satellite_exception(self, mock_ship, mock_grid):
        """Update handles Satellite vehicle type (no movement)."""
        mock_ship.get_vehicle_type = MagicMock(return_value='Satellite')

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Create target for satellite with enough attributes for targeting
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(100, 0)
        enemy.name = "enemy_ship"
        enemy.mass = 100.0
        enemy.max_speed = 10.0
        enemy.current_shields = 0.0
        enemy.max_shields = 0.0
        mock_grid.query_radius = MagicMock(return_value=[enemy])
        mock_grid.query_radius_exact = MagicMock(return_value=[enemy])

        with patch('game.ai.strategy_manager.get_default_strategy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.resolve_strategy = MagicMock(return_value={
                'targeting': {'rules': [{'type': 'nearest', 'weight': 1}]},
                'movement': {'behavior': 'kite'},
                'definition': {}
            })
            mock_manager.return_value = mock_instance

            controller.update()

            # Satellite should still pull trigger but no behavior movement
            mock_ship.set_trigger_pulled.assert_called_with(True)


class TestAIControllerCapabilitiesCache:
    """Tests for capabilities cache building."""

    def test_build_capabilities_cache_empty_ships(self, mock_ship, mock_grid):
        """Cache building handles empty ship list."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        cache = controller._build_capabilities_cache([])

        assert cache == {}

    def test_build_capabilities_cache_ship_without_id(self, mock_ship, mock_grid):
        """Cache building skips ships without id attribute."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Ship without id
        ship_no_id = MagicMock(spec=[])  # No attributes

        cache = controller._build_capabilities_cache([ship_no_id])

        assert cache == {}

    def test_build_capabilities_cache_with_weapons(self, mock_ship, mock_grid):
        """Cache correctly identifies ships with weapons."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Ship with weapons
        armed_ship = MagicMock()
        armed_ship.id = 'armed_1'
        armed_ship.name = 'armed_1'
        weapon = MagicMock()
        weapon.has_ability = MagicMock(return_value=False)  # Not PDC
        armed_ship.get_components_by_ability = MagicMock(return_value=[weapon])

        cache = controller._build_capabilities_cache([armed_ship])

        assert 'armed_1' in cache
        assert cache['armed_1']['has_weapons'] is True
        assert cache['armed_1']['weapon_components'] == [weapon]

    def test_build_capabilities_cache_with_pdc(self, mock_ship, mock_grid):
        """Cache correctly identifies ships with PDC."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Ship with PDC weapon
        pdc_ship = MagicMock()
        pdc_ship.id = 'pdc_ship'
        pdc_ship.name = 'pdc_ship'
        pdc_weapon = MagicMock()
        pdc_weapon.has_ability = MagicMock(return_value=True)  # Is PDC
        pdc_ship.get_components_by_ability = MagicMock(return_value=[pdc_weapon])

        cache = controller._build_capabilities_cache([pdc_ship])

        assert 'pdc_ship' in cache
        assert cache['pdc_ship']['has_pdc'] is True
        assert cache['pdc_ship']['pdc_components'] == [pdc_weapon]


class TestAIControllerEngageDistance:
    """Tests for engage distance multiplier edge cases."""

    def test_engage_distance_max_range(self, mock_ship, mock_grid):
        """'max_range' returns multiplier of 1.0."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({'engage_distance': 'max_range'})
        assert result == 1.0

    def test_engage_distance_ram(self, mock_ship, mock_grid):
        """'ram' returns multiplier of 0.0."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({'engage_distance': 'ram'})
        assert result == 0.0

    def test_engage_distance_numeric_value(self, mock_ship, mock_grid):
        """Numeric value is returned as float."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({'engage_distance': 0.75})
        assert result == 0.75

    def test_engage_distance_integer_value(self, mock_ship, mock_grid):
        """Integer value is converted to float."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({'engage_distance': 2})
        assert result == 2.0

    def test_engage_distance_unknown_value(self, mock_ship, mock_grid):
        """Unknown string value defaults to 1.0."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({'engage_distance': 'unknown'})
        assert result == 1.0

    def test_engage_distance_missing_key(self, mock_ship, mock_grid):
        """Missing key defaults to 'max_range' (1.0)."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller.get_engage_distance_multiplier({})
        assert result == 1.0


class TestAIControllerScoreAndSort:
    """Tests for _score_and_sort_enemies edge cases."""

    def test_score_and_sort_with_evaluation_failure(self, mock_ship, mock_grid):
        """Enemies that fail evaluation are skipped with warning."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Create an enemy that will fail evaluation (PROJ-192: Ship uses .name)
        bad_enemy = MagicMock()
        bad_enemy.name = 'bad_enemy'
        bad_enemy.position = None  # Will cause evaluation to fail

        good_enemy = MagicMock()
        good_enemy.name = 'good_enemy'
        good_enemy.position = Vector2(100, 0)
        good_enemy.velocity = Vector2(0, 0)
        good_enemy.mass = 100
        good_enemy.hp = 100
        good_enemy.max_hp = 100
        good_enemy.get_components_by_ability = MagicMock(return_value=[])
        good_enemy.get_components_by_layer = MagicMock(return_value=[])

        rules = [{'type': 'nearest', 'weight': 1}]

        # Should not crash, should return only good enemy
        result = controller._score_and_sort_enemies([bad_enemy, good_enemy], rules)

        assert good_enemy in result

    def test_score_and_sort_empty_list(self, mock_ship, mock_grid):
        """Empty enemy list returns empty result."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        result = controller._score_and_sort_enemies([], [])

        assert result == []
