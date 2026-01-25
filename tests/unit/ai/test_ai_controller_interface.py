"""
Unit tests for AIController using IControllable interface.

PROJ-12 Phase 5: TDD tests written BEFORE implementation.
Tests that AIController can work with any IControllable implementation.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pygame.math import Vector2


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = MagicMock()
    grid.query_radius.return_value = []
    return grid


@pytest.fixture
def mock_controllable():
    """Create a mock IControllable implementation."""
    from game.ai.interfaces.controllable import IControllable

    controllable = MagicMock(spec=IControllable)
    controllable.get_position.return_value = Vector2(100, 200)
    controllable.get_velocity.return_value = Vector2(10, 5)
    controllable.get_rotation.return_value = 45.0
    controllable.get_team_id.return_value = 1
    controllable.is_alive.return_value = True
    controllable.get_max_speed.return_value = 100.0
    controllable.get_weapon_range.return_value = 500.0
    controllable.get_radius.return_value = 40.0
    controllable.get_current_speed.return_value = 50.0
    controllable.get_formation_members.return_value = []
    controllable.get_formation_master.return_value = None
    controllable.is_in_formation.return_value = False
    controllable.get_formation_offset.return_value = None
    controllable.get_current_target.return_value = None
    controllable.get_max_targets.return_value = 1

    # Also provide ship-like attributes for backward compatibility during transition
    controllable.position = Vector2(100, 200)
    controllable.angle = 45.0
    controllable.team_id = 1
    controllable.is_alive = True
    controllable.max_weapon_range = 500.0
    controllable.radius = 40.0
    controllable.turn_speed = 180.0
    controllable.current_target = None
    controllable.formation_members = []
    controllable.in_formation = False
    controllable.formation_master = None
    controllable.ai_strategy = 'standard_ranged'
    controllable.max_targets = 1
    controllable.secondary_targets = []
    controllable.vehicle_type = 'Ship'

    return controllable


@pytest.fixture
def mock_ship():
    """Create a mock ship for adapter testing."""
    ship = MagicMock()
    ship.position = Vector2(100, 200)
    ship.velocity = Vector2(10, 5)
    ship.angle = 45.0
    ship.team_id = 1
    ship.is_alive = True
    ship.max_speed = 100.0
    ship.max_weapon_range = 500.0
    ship.radius = 40.0
    ship.turn_speed = 180.0
    ship.acceleration_rate = 50.0
    ship.current_speed = 50.0
    ship.turn_throttle = 1.0
    ship.engine_throttle = 1.0
    ship.comp_trigger_pulled = False
    ship.current_target = None
    ship.secondary_targets = []
    ship.formation_members = []
    ship.formation_master = None
    ship.in_formation = False
    ship.formation_offset = None
    ship.vehicle_type = 'Ship'
    ship.ai_strategy = 'standard_ranged'
    ship.max_targets = 1
    ship.is_thrusting = False
    ship.is_derelict = False
    return ship


# =============================================================================
# Test: AIController with Adapter
# =============================================================================

class TestAIControllerWithAdapter:
    """Tests for AIController using ShipControllableAdapter."""

    def test_aicontroller_accepts_adapter(self, mock_ship, mock_grid):
        """AIController can be constructed with a ShipControllableAdapter."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        # AIController should accept the adapter
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        assert controller is not None
        assert controller.ship == adapter

    def test_aicontroller_can_access_position_via_adapter(self, mock_ship, mock_grid):
        """AIController can access position through adapter."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Access via adapter
        pos = controller.ship.get_position()

        assert pos == Vector2(100, 200)

    def test_aicontroller_can_access_ship_attributes_via_adapter_fallback(self, mock_ship, mock_grid):
        """AIController can access ship attributes via adapter's __getattr__ fallback."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Access via adapter fallback to ship
        assert controller.ship.position == Vector2(100, 200)
        assert controller.ship.angle == 45.0
        assert controller.ship.team_id == 1


# =============================================================================
# Test: AIController Behavior with Interface
# =============================================================================

class TestAIControllerBehavior:
    """Tests that AIController behaviors work with controllable interface."""

    def test_navigate_to_uses_position(self, mock_ship, mock_grid):
        """navigate_to uses the controllable's position."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.position = Vector2(0, 0)
        mock_ship.angle = 0.0

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Navigate to a target position
        target_pos = Vector2(100, 0)
        controller.navigate_to(target_pos)

        # Ship should have had thrust_forward called (target is straight ahead)
        mock_ship.thrust_forward.assert_called()

    def test_navigate_to_rotates_toward_target(self, mock_ship, mock_grid):
        """navigate_to rotates the controllable toward the target."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.position = Vector2(0, 0)
        mock_ship.angle = 0.0  # Facing right

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Navigate to a position that requires rotation
        target_pos = Vector2(0, 100)  # Above, requires 90 degree turn
        controller.navigate_to(target_pos)

        # Ship should have rotate called (need to turn)
        mock_ship.rotate.assert_called()


# =============================================================================
# Test: AIController Targeting with Interface
# =============================================================================

class TestAIControllerTargeting:
    """Tests that AIController targeting works with controllable interface."""

    def test_find_target_queries_grid_at_position(self, mock_ship, mock_grid):
        """find_target queries grid at controllable's position."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.position = Vector2(100, 200)

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        controller.find_target()

        # Grid should have been queried at the ship's position
        mock_grid.query_radius.assert_called()
        call_args = mock_grid.query_radius.call_args[0]
        assert call_args[0] == Vector2(100, 200)


# =============================================================================
# Test: AIController Update Loop
# =============================================================================

class TestAIControllerUpdate:
    """Tests for AIController update loop with interface."""

    def test_update_checks_is_alive(self, mock_ship, mock_grid):
        """update() checks if controllable is alive first."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.is_alive = False

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Update should return early if not alive
        controller.update()

        # No target finding should have occurred
        # (behavior would be different if we processed a dead ship)
        assert mock_ship.current_target is None

    def test_update_resets_throttles(self, mock_ship, mock_grid):
        """update() resets turn and engine throttles."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.is_alive = True
        mock_ship.formation_members = []
        mock_ship.in_formation = False
        mock_ship.current_target = None

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        controller.update()

        # Turn throttle should be reset to 1.0
        assert mock_ship.turn_throttle == 1.0


# =============================================================================
# Test: AIController Formation Support
# =============================================================================

class TestAIControllerFormation:
    """Tests for AIController formation handling with interface."""

    def test_update_handles_formation_master(self, mock_ship, mock_grid):
        """update() handles formation master ship."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        member = MagicMock()
        member.is_alive = True
        member.in_formation = True
        member.formation_offset = Vector2(50, 0)
        member.position = Vector2(150, 200)

        mock_ship.is_alive = True
        mock_ship.formation_members = [member]
        mock_ship.in_formation = False
        mock_ship.radius = 40

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Should not raise
        controller.update()

    def test_update_handles_formation_member(self, mock_ship, mock_grid):
        """update() handles ship in formation."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        master = MagicMock()
        master.is_alive = True
        master.current_target = None

        mock_ship.is_alive = True
        mock_ship.formation_members = []
        mock_ship.in_formation = True
        mock_ship.formation_master = master

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Should not raise
        controller.update()
