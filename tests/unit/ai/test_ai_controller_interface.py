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

    def test_aicontroller_uses_interface_methods_not_direct_access(self, mock_ship, mock_grid):
        """AIController uses interface methods, not direct attribute access."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Access via interface methods (PROJ-24 migration complete)
        assert controller.ship.get_position() == Vector2(100, 200)
        assert controller.ship.get_rotation() == 45.0
        assert controller.ship.get_team_id() == 1


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


# =============================================================================
# Test: AIController Avoidance Self-Skip (Fix 9.1)
# =============================================================================

class TestAIControllerAvoidance:
    """Tests for AIController check_avoidance() correctly skipping self."""

    def test_check_avoidance_skips_own_ship_when_using_adapter(self, mock_ship, mock_grid):
        """
        check_avoidance() should skip the ship's own object when grid returns it.

        BUG FIX (PROJ-12 Phase 9.1): When AIController uses ShipControllableAdapter,
        self.ship is the adapter but grid.query_radius() returns raw Ship objects.
        The comparison `obj == self.ship` fails because adapter != raw_ship.
        The fix is to compare `obj == self.ship.ship` to unwrap the adapter.
        """
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter
        from game.core.config import BattleConfig

        # Set up ship
        mock_ship.is_alive = True
        mock_ship.position = Vector2(100, 100)
        mock_ship.radius = 40
        mock_ship.team_id = 1

        # Create an enemy that IS within collision threshold
        enemy_ship = MagicMock()
        enemy_ship.is_alive = True
        enemy_ship.position = Vector2(110, 100)  # Only 10 units away (overlap with radii 40)
        enemy_ship.radius = 40
        enemy_ship.team_id = 2

        # Grid returns BOTH the ship itself (raw Ship) AND the enemy
        mock_grid.query_radius.return_value = [mock_ship, enemy_ship]

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        result = controller.check_avoidance()

        # With ships overlapping (distance 10, combined radii 80), should return avoidance
        assert result is not None, "Should return avoidance position for nearby enemy"

        # The avoidance position should be AWAY from the enemy (negative X direction
        # since enemy is at +10 X relative to ship at 100,100)
        assert result.x < mock_ship.position.x, (
            f"Avoidance position {result} should be away from enemy at {enemy_ship.position}"
        )

    def test_check_avoidance_does_not_avoid_itself(self, mock_ship, mock_grid):
        """
        When only the ship itself is in the query results, no avoidance is needed.

        If the bug exists, the ship would try to avoid itself (distance 0).
        """
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.is_alive = True
        mock_ship.position = Vector2(100, 100)
        mock_ship.radius = 40
        mock_ship.team_id = 1

        # Grid returns ONLY the ship itself
        mock_grid.query_radius.return_value = [mock_ship]

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        result = controller.check_avoidance()

        # Should return None because the ship correctly skips itself
        assert result is None, "Should not try to avoid itself"


class TestFormationIntegrityWithAdapter:
    """Tests for _check_formation_integrity with ShipControllableAdapter.

    Fix 10.1: Verifies that formation member removal works correctly when
    AIController.ship is a ShipControllableAdapter wrapping a raw Ship,
    but formation_members list contains raw Ships.
    """

    def test_formation_member_removed_when_ship_damaged(self, mock_grid):
        """When ship breaks formation due to damage, it should be removed from formation_members."""
        from game.ai.interfaces.controllable import ShipControllableAdapter
        from game.ai.controller import AIController

        # Create a mock ship that is in a formation
        mock_ship = MagicMock()
        mock_ship.position = Vector2(100, 100)
        mock_ship.velocity = Vector2(0, 0)
        mock_ship.angle = 0.0
        mock_ship.team_id = 1
        mock_ship.is_alive = True
        mock_ship.radius = 40
        mock_ship.in_formation = True

        # Create formation master with members list containing RAW ships (not adapters)
        mock_master = MagicMock()
        mock_master.formation_members = [mock_ship]  # Raw ship in list
        mock_ship.formation_master = mock_master

        # Create a damaged propulsion component
        damaged_component = MagicMock()
        damaged_component.current_hp = 50
        damaged_component.max_hp = 100
        # Code calls get_components_by_ability for 'CombatPropulsion' and 'ManeuveringThruster'
        mock_ship.get_components_by_ability.return_value = [damaged_component]

        # Wrap in adapter (as production does)
        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        # Verify ship is in formation_members before
        assert mock_ship in mock_master.formation_members

        # Call _check_formation_integrity which should detect damage and remove from formation
        controller._check_formation_integrity()

        # Verify ship was removed from formation_members
        assert mock_ship not in mock_master.formation_members, \
            "Ship should be removed from formation_members when breaking formation"
        # Verify formation state was cleared
        assert mock_ship.in_formation is False

    def test_formation_member_not_removed_when_undamaged(self, mock_grid):
        """When ship is undamaged, it should stay in formation."""
        from game.ai.interfaces.controllable import ShipControllableAdapter
        from game.ai.controller import AIController

        mock_ship = MagicMock()
        mock_ship.position = Vector2(100, 100)
        mock_ship.velocity = Vector2(0, 0)
        mock_ship.angle = 0.0
        mock_ship.team_id = 1
        mock_ship.is_alive = True
        mock_ship.radius = 40
        mock_ship.in_formation = True

        mock_master = MagicMock()
        mock_master.formation_members = [mock_ship]
        mock_ship.formation_master = mock_master

        # Undamaged propulsion component
        undamaged_component = MagicMock()
        undamaged_component.current_hp = 100
        undamaged_component.max_hp = 100
        mock_ship.get_components_by_ability.return_value = [undamaged_component]

        adapter = ShipControllableAdapter(mock_ship)
        controller = AIController(adapter, mock_grid, enemy_team_id=2)

        controller._check_formation_integrity()

        # Ship should still be in formation
        assert mock_ship in mock_master.formation_members
        assert mock_ship.in_formation is True
