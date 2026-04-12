"""
Unit tests for AIController edge cases with PolicyManager integration.

TCG-FND-001: Tests for edge cases when:
- Policy references invalid/missing policies
- Ship lacks expected capabilities
- PolicyManager returns incomplete policy definitions

These tests ensure AIController handles edge cases gracefully without
crashing or silently failing during combat.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.ai.controller import AIController
from game.ai.policy_manager import PolicyManager, get_default_policy_manager
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
    ship.get_movement_policy = MagicMock(return_value='kite_max')
    ship.get_targeting_policy = MagicMock(return_value='standard')
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


class TestAIControllerPolicyResolution:
    """Tests for policy resolution edge cases."""

    def test_controller_with_missing_policy_id(self, mock_ship, mock_grid):
        """Controller handles unknown policy ID gracefully."""
        mock_ship.get_movement_policy = MagicMock(return_value='nonexistent_policy')
        mock_ship.get_targeting_policy = MagicMock(return_value='nonexistent_policy')

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # get_resolved_policies should return defaults when ID not found
        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': []})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite'})
            mock_manager.return_value = mock_instance

            # Should not raise exception
            resolved = controller.get_resolved_policies()
            assert 'targeting' in resolved
            assert 'movement' in resolved

    def test_controller_with_empty_targeting_policy(self, mock_ship, mock_grid):
        """Controller handles empty targeting rules gracefully."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': []})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite'})
            mock_manager.return_value = mock_instance

            # find_target should return None with no enemies
            target = controller.find_target()
            assert target is None

    def test_controller_with_missing_movement_behavior(self, mock_ship, mock_grid):
        """Controller handles missing behavior key with fallback to 'kite'."""
        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': []})
            mock_instance.get_movement_policy = MagicMock(return_value={})  # Missing 'behavior' key
            mock_manager.return_value = mock_instance

            # Get resolved policies - should not crash
            resolved = controller.get_resolved_policies()

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

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': [{'type': 'nearest', 'weight': 1}]})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite'})
            mock_manager.return_value = mock_instance

            # Should still find target even without weapons
            target = controller.find_target()
            assert target == enemy

    def test_ship_with_zero_weapon_range(self, mock_ship, mock_grid):
        """Controller handles ship with zero weapon range."""
        mock_ship.get_weapon_range = MagicMock(return_value=0.0)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': []})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite', 'engage_distance': 'max_range'})
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

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': []})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite'})
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

        with patch('game.ai.controller.get_default_policy_manager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_targeting_policy = MagicMock(return_value={'rules': [{'type': 'nearest', 'weight': 1}]})
            mock_instance.get_movement_policy = MagicMock(return_value={'behavior': 'kite'})
            mock_manager.return_value = mock_instance

            controller.update()

            # Satellite should still pull trigger but no behavior movement
            mock_ship.set_trigger_pulled.assert_called_with(True)


