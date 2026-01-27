"""
Unit tests for IControllable interface.

PROJ-12 Phase 5: TDD tests written BEFORE implementation.
Tests the AI controllable interface that decouples AI from Ship internals.
"""

import pytest
from unittest.mock import MagicMock, patch
from pygame.math import Vector2


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ship():
    """Create a mock ship with typical attributes."""
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
# Test: IControllable Interface Import and Definition
# =============================================================================

class TestIControllableDefinition:
    """Tests for IControllable interface definition."""

    def test_icontrollable_can_be_imported(self):
        """IControllable can be imported from interfaces module."""
        from game.ai.interfaces.controllable import IControllable

        assert IControllable is not None

    def test_icontrollable_is_protocol_or_abc(self):
        """IControllable is a Protocol or ABC for type checking."""
        from game.ai.interfaces.controllable import IControllable
        from typing import Protocol, runtime_checkable
        import abc

        # Should be either a Protocol or ABC
        is_protocol = isinstance(IControllable, type) and hasattr(IControllable, '__protocol_attrs__')
        is_abc = isinstance(IControllable, abc.ABCMeta)

        assert is_protocol or is_abc

    def test_icontrollable_has_get_position_method(self):
        """IControllable defines get_position method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_position')

    def test_icontrollable_has_get_velocity_method(self):
        """IControllable defines get_velocity method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_velocity')

    def test_icontrollable_has_get_rotation_method(self):
        """IControllable defines get_rotation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_rotation')

    def test_icontrollable_has_set_throttle_method(self):
        """IControllable defines set_throttle method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_throttle')

    def test_icontrollable_has_set_turn_throttle_method(self):
        """IControllable defines set_turn_throttle method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_turn_throttle')

    def test_icontrollable_has_get_team_id_method(self):
        """IControllable defines get_team_id method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_team_id')

    def test_icontrollable_has_get_weapon_range_method(self):
        """IControllable defines get_weapon_range method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_weapon_range')

    def test_icontrollable_has_is_alive_method(self):
        """IControllable defines is_alive method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'is_alive')


# =============================================================================
# Test: Extended IControllable Methods (AI-specific)
# =============================================================================

class TestIControllableExtendedMethods:
    """Tests for extended IControllable methods needed by AI."""

    def test_icontrollable_has_rotate_method(self):
        """IControllable defines rotate method for AI to command turns."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'rotate')

    def test_icontrollable_has_thrust_forward_method(self):
        """IControllable defines thrust_forward method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'thrust_forward')

    def test_icontrollable_has_get_radius_method(self):
        """IControllable defines get_radius for collision detection."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_radius')

    def test_icontrollable_has_get_max_speed_method(self):
        """IControllable defines get_max_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_max_speed')

    def test_icontrollable_has_get_current_speed_method(self):
        """IControllable defines get_current_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_current_speed')

    def test_icontrollable_has_get_turn_speed_method(self):
        """IControllable defines get_turn_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_turn_speed')

    def test_icontrollable_has_get_acceleration_rate_method(self):
        """IControllable defines get_acceleration_rate method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_acceleration_rate')

    def test_icontrollable_has_get_is_thrusting_method(self):
        """IControllable defines get_is_thrusting method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_is_thrusting')

    def test_icontrollable_has_set_rotation_method(self):
        """IControllable defines set_rotation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_rotation')

    def test_icontrollable_has_adjust_position_method(self):
        """IControllable defines adjust_position method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'adjust_position')

    def test_icontrollable_has_get_layers_method(self):
        """IControllable defines get_layers method for component inspection."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_layers')

    def test_icontrollable_has_get_turn_throttle_method(self):
        """IControllable defines get_turn_throttle method (PROJ-24 Phase 6)."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_turn_throttle')


# =============================================================================
# Test: Formation Support Methods
# =============================================================================

class TestIControllableFormationMethods:
    """Tests for formation-related IControllable methods."""

    def test_icontrollable_has_get_formation_members_method(self):
        """IControllable defines get_formation_members method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_members')

    def test_icontrollable_has_get_formation_master_method(self):
        """IControllable defines get_formation_master method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_master')

    def test_icontrollable_has_is_in_formation_method(self):
        """IControllable defines is_in_formation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'is_in_formation')

    def test_icontrollable_has_get_formation_offset_method(self):
        """IControllable defines get_formation_offset method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_offset')

    def test_icontrollable_has_set_in_formation_method(self):
        """IControllable defines set_in_formation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_in_formation')

    def test_icontrollable_has_set_formation_master_method(self):
        """IControllable defines set_formation_master method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_formation_master')


# =============================================================================
# Test: Combat State Methods
# =============================================================================

class TestIControllableCombatMethods:
    """Tests for combat-related IControllable methods."""

    def test_icontrollable_has_set_trigger_pulled_method(self):
        """IControllable defines set_trigger_pulled method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_trigger_pulled')

    def test_icontrollable_has_get_current_target_method(self):
        """IControllable defines get_current_target method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_current_target')

    def test_icontrollable_has_set_current_target_method(self):
        """IControllable defines set_current_target method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_current_target')

    def test_icontrollable_has_get_max_targets_method(self):
        """IControllable defines get_max_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_max_targets')

    def test_icontrollable_has_get_secondary_targets_method(self):
        """IControllable defines get_secondary_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_secondary_targets')

    def test_icontrollable_has_set_secondary_targets_method(self):
        """IControllable defines set_secondary_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_secondary_targets')

    def test_icontrollable_has_get_components_by_ability_method(self):
        """IControllable defines get_components_by_ability method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_components_by_ability')


# =============================================================================
# Test: Ship Adapter Implementation
# =============================================================================

class TestShipControllableAdapter:
    """Tests for ShipControllableAdapter that wraps Ship for IControllable."""

    def test_adapter_can_be_imported(self):
        """ShipControllableAdapter can be imported."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        assert ShipControllableAdapter is not None

    def test_adapter_wraps_ship(self, mock_ship):
        """ShipControllableAdapter wraps a Ship instance."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        assert adapter is not None
        assert adapter._ship == mock_ship

    def test_adapter_get_position_returns_ship_position(self, mock_ship):
        """get_position returns the ship's position."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_position()

        assert result == mock_ship.position

    def test_adapter_get_velocity_returns_ship_velocity(self, mock_ship):
        """get_velocity returns the ship's velocity."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_velocity()

        assert result == mock_ship.velocity

    def test_adapter_get_rotation_returns_ship_angle(self, mock_ship):
        """get_rotation returns the ship's angle."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_rotation()

        assert result == mock_ship.angle

    def test_adapter_set_throttle_sets_ship_engine_throttle(self, mock_ship):
        """set_throttle sets the ship's engine_throttle."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_throttle(0.5)

        assert mock_ship.engine_throttle == 0.5

    def test_adapter_set_turn_throttle_sets_ship_turn_throttle(self, mock_ship):
        """set_turn_throttle sets the ship's turn_throttle."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_turn_throttle(0.75)

        assert mock_ship.turn_throttle == 0.75

    def test_adapter_get_team_id_returns_ship_team_id(self, mock_ship):
        """get_team_id returns the ship's team_id."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_team_id()

        assert result == mock_ship.team_id

    def test_adapter_get_weapon_range_returns_ship_max_weapon_range(self, mock_ship):
        """get_weapon_range returns the ship's max_weapon_range."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_weapon_range()

        assert result == mock_ship.max_weapon_range

    def test_adapter_is_alive_returns_ship_is_alive(self, mock_ship):
        """is_alive returns the ship's is_alive status."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.is_alive()

        assert result == mock_ship.is_alive

    def test_adapter_rotate_calls_ship_rotate(self, mock_ship):
        """rotate calls the ship's rotate method."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.rotate(1)

        mock_ship.rotate.assert_called_once_with(1)

    def test_adapter_thrust_forward_calls_ship_thrust_forward(self, mock_ship):
        """thrust_forward calls the ship's thrust_forward method."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.thrust_forward()

        mock_ship.thrust_forward.assert_called_once()

    def test_adapter_get_radius_returns_ship_radius(self, mock_ship):
        """get_radius returns the ship's radius."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_radius()

        assert result == mock_ship.radius


# =============================================================================
# Test: Adapter Formation Methods
# =============================================================================

class TestShipControllableAdapterFormation:
    """Tests for adapter formation-related methods."""

    def test_adapter_get_formation_members_returns_ship_formation_members(self, mock_ship):
        """get_formation_members returns the ship's formation_members."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        member1 = MagicMock()
        member2 = MagicMock()
        mock_ship.formation_members = [member1, member2]

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_formation_members()

        assert result == [member1, member2]

    def test_adapter_get_formation_master_returns_ship_formation_master(self, mock_ship):
        """get_formation_master returns the ship's formation_master."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        master = MagicMock()
        mock_ship.formation_master = master

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_formation_master()

        assert result == master

    def test_adapter_is_in_formation_returns_ship_in_formation(self, mock_ship):
        """is_in_formation returns the ship's in_formation status."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.in_formation = True

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.is_in_formation()

        assert result is True


# =============================================================================
# Test: Adapter Combat Methods
# =============================================================================

class TestShipControllableAdapterCombat:
    """Tests for adapter combat-related methods."""

    def test_adapter_set_trigger_pulled_sets_ship_comp_trigger_pulled(self, mock_ship):
        """set_trigger_pulled sets the ship's comp_trigger_pulled."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_trigger_pulled(True)

        assert mock_ship.comp_trigger_pulled is True

    def test_adapter_get_current_target_returns_ship_current_target(self, mock_ship):
        """get_current_target returns the ship's current_target."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        target = MagicMock()
        mock_ship.current_target = target

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_current_target()

        assert result == target

    def test_adapter_set_current_target_sets_ship_current_target(self, mock_ship):
        """set_current_target sets the ship's current_target."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        target = MagicMock()

        adapter = ShipControllableAdapter(mock_ship)
        adapter.set_current_target(target)

        assert mock_ship.current_target == target

    def test_adapter_get_max_targets_returns_ship_max_targets(self, mock_ship):
        """get_max_targets returns the ship's max_targets."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.max_targets = 3

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_max_targets()

        assert result == 3


# =============================================================================
# Test: Ship Access (PROJ-24 - Delegation Removed)
# =============================================================================

class TestShipAccess:
    """Tests that adapter provides access to underlying ship.

    Note: PROJ-24 removed the __getattr__/__setattr__ delegation methods.
    Direct attribute access is no longer supported. Use interface methods instead.
    """

    def test_adapter_exposes_underlying_ship(self, mock_ship):
        """Adapter provides access to underlying ship via .ship property."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        # .ship property and _ship both access underlying ship
        assert adapter.ship == mock_ship
        assert adapter._ship == mock_ship

    def test_adapter_uses_interface_methods_not_direct_access(self, mock_ship):
        """Adapter requires interface methods for attribute access."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        # Setup mock with expected attributes
        mock_ship.turn_throttle = 0.5
        mock_ship.engine_throttle = 0.8
        mock_ship.comp_trigger_pulled = True
        mock_ship.current_target = "some_target"

        adapter = ShipControllableAdapter(mock_ship)

        # Use interface methods for setting
        adapter.set_turn_throttle(0.7)
        adapter.set_throttle(0.9)
        adapter.set_trigger_pulled(False)
        adapter.set_current_target(None)

        # Verify attributes were set on the ship
        assert mock_ship.turn_throttle == 0.7
        assert mock_ship.engine_throttle == 0.9
        assert mock_ship.comp_trigger_pulled is False
        assert mock_ship.current_target is None

    def test_direct_attribute_access_raises_error(self, mock_ship):
        """Direct attribute access (bypassing interface) raises AttributeError."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.some_custom_attribute = "test_value"

        adapter = ShipControllableAdapter(mock_ship)

        # Direct attribute access should fail (no __getattr__ delegation)
        with pytest.raises(AttributeError):
            _ = adapter.some_custom_attribute

    def test_direct_attribute_assignment_does_not_delegate(self, mock_ship):
        """Direct attribute assignment sets on adapter, not underlying ship."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        # Without __setattr__ delegation, assignment goes to adapter, not ship
        adapter.some_custom_attribute = "test_value"

        # Attribute is on adapter itself (in __dict__), not delegated to ship
        assert adapter.some_custom_attribute == "test_value"
        assert 'some_custom_attribute' in adapter.__dict__


# =============================================================================
# Test: New Interface Methods (PROJ-24)
# =============================================================================

class TestIControllableNewMethods:
    """Tests for new interface methods added in PROJ-24."""

    def test_adapter_get_turn_speed_returns_ship_turn_speed(self, mock_ship):
        """get_turn_speed returns the ship's turn_speed."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.turn_speed = 180.0

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_turn_speed()

        assert result == 180.0

    def test_adapter_get_acceleration_rate_returns_ship_acceleration_rate(self, mock_ship):
        """get_acceleration_rate returns the ship's acceleration_rate."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.acceleration_rate = 50.0

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_acceleration_rate()

        assert result == 50.0

    def test_adapter_get_is_thrusting_returns_ship_is_thrusting(self, mock_ship):
        """get_is_thrusting returns the ship's is_thrusting."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.is_thrusting = True

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_is_thrusting()

        assert result is True

    def test_adapter_set_rotation_sets_ship_angle(self, mock_ship):
        """set_rotation sets the ship's angle."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_rotation(90.0)

        assert mock_ship.angle == 90.0

    def test_adapter_set_in_formation_sets_ship_in_formation(self, mock_ship):
        """set_in_formation sets the ship's in_formation."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_in_formation(True)

        assert mock_ship.in_formation is True

    def test_adapter_set_formation_master_sets_ship_formation_master(self, mock_ship):
        """set_formation_master sets the ship's formation_master."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        master = MagicMock()

        adapter = ShipControllableAdapter(mock_ship)
        adapter.set_formation_master(master)

        assert mock_ship.formation_master == master

    def test_adapter_set_formation_master_to_none(self, mock_ship):
        """set_formation_master can set None."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.formation_master = MagicMock()

        adapter = ShipControllableAdapter(mock_ship)
        adapter.set_formation_master(None)

        assert mock_ship.formation_master is None

    def test_adapter_get_secondary_targets_returns_ship_secondary_targets(self, mock_ship):
        """get_secondary_targets returns the ship's secondary_targets."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        target1 = MagicMock()
        target2 = MagicMock()
        mock_ship.secondary_targets = [target1, target2]

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_secondary_targets()

        assert result == [target1, target2]

    def test_adapter_get_secondary_targets_returns_empty_list_if_none(self, mock_ship):
        """get_secondary_targets returns empty list if ship has None."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.secondary_targets = None

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_secondary_targets()

        assert result == []

    def test_adapter_set_secondary_targets_sets_ship_secondary_targets(self, mock_ship):
        """set_secondary_targets sets the ship's secondary_targets."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        target1 = MagicMock()
        target2 = MagicMock()
        targets = [target1, target2]

        adapter = ShipControllableAdapter(mock_ship)
        adapter.set_secondary_targets(targets)

        assert mock_ship.secondary_targets == targets

    def test_adapter_get_components_by_ability_calls_ship_method(self, mock_ship):
        """get_components_by_ability delegates to ship."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        comp1 = MagicMock()
        comp2 = MagicMock()
        mock_ship.get_components_by_ability.return_value = [comp1, comp2]

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_components_by_ability('weapon', operational_only=True)

        assert result == [comp1, comp2]
        mock_ship.get_components_by_ability.assert_called_once_with('weapon', True)

    def test_adapter_get_components_by_ability_with_false_operational(self, mock_ship):
        """get_components_by_ability passes operational_only flag."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.get_components_by_ability.return_value = []

        adapter = ShipControllableAdapter(mock_ship)

        adapter.get_components_by_ability('sensor', operational_only=False)

        mock_ship.get_components_by_ability.assert_called_once_with('sensor', False)

    def test_adapter_adjust_position_adds_delta_to_ship_position(self, mock_ship):
        """adjust_position adds the delta to ship's position."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.position = Vector2(100, 200)

        adapter = ShipControllableAdapter(mock_ship)
        adapter.adjust_position(Vector2(10, -5))

        # The adapter should add to position
        assert mock_ship.position == Vector2(110, 195)

    def test_adapter_get_layers_returns_ship_layers(self, mock_ship):
        """get_layers returns the ship's layers dict."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        layers = {'front': MagicMock(), 'mid': MagicMock(), 'rear': MagicMock()}
        mock_ship.layers = layers

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_layers()

        assert result == layers

    def test_adapter_get_turn_throttle_returns_ship_turn_throttle(self, mock_ship):
        """get_turn_throttle returns the ship's turn_throttle (PROJ-24 Phase 6)."""
        from game.ai.interfaces.controllable import ShipControllableAdapter

        mock_ship.turn_throttle = 0.75

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_turn_throttle()

        assert result == 0.75
