"""
Edge case tests for ShipControllableAdapter.

TCG-FND-010: Tests for adapter edge cases:
- Adapting ships with missing optional attributes
- Interface method calls when underlying ship methods fail
- Complete interface coverage verification
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.ai.interfaces.controllable import ShipControllableAdapter, IControllable
from game.core.constants import CombatConstants


@pytest.fixture
def mock_ship():
    """Create a mock ship with all required attributes."""
    ship = MagicMock()

    # Position/Movement attributes
    ship.position = MagicMock()
    ship.position.x = 100.0
    ship.position.y = 200.0
    ship.velocity = MagicMock()
    ship.angle = 45.0
    ship.radius = 50.0
    ship.max_speed = 100.0
    ship.current_speed = 50.0
    ship.turn_speed = 90.0
    ship.acceleration_rate = 10.0
    ship.is_thrusting = False
    ship.engine_throttle = 1.0
    ship.turn_throttle = 1.0

    # Combat attributes
    ship.team_id = 1
    ship.is_alive = True
    ship.max_weapon_range = 500.0
    ship.comp_trigger_pulled = False
    ship.current_target = None
    ship.secondary_targets = []
    ship.layers = {}

    # Methods
    ship.rotate = MagicMock()
    ship.thrust_forward = MagicMock()
    ship.get_components_by_ability = MagicMock(return_value=[])
    ship.get_all_components = MagicMock(return_value=[])

    return ship


class TestAdapterInitialization:
    """Tests for adapter initialization."""

    def test_adapter_stores_ship_reference(self, mock_ship):
        """Adapter stores reference to underlying ship."""
        adapter = ShipControllableAdapter(mock_ship)

        assert adapter._ship is mock_ship
        assert adapter.ship is mock_ship

    def test_adapter_is_icontrollable(self, mock_ship):
        """Adapter is instance of IControllable."""
        adapter = ShipControllableAdapter(mock_ship)

        assert isinstance(adapter, IControllable)


class TestOptionalAttributeDefaults:
    """Tests for attributes with special default handling."""

    # NOTE: Tests for missing movement_policy, vehicle_type, and max_targets were deleted
    # in PROJ-192 Phase 3. Ship ALWAYS has these attributes (set in __init__), so
    # testing fallback behavior for missing attributes was testing an impossible scenario.

    def test_get_secondary_targets_none(self, mock_ship):
        """secondary_targets = None returns empty list."""
        mock_ship.secondary_targets = None

        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_secondary_targets()
        assert result == []


class TestPositionAndMovement:
    """Tests for position and movement methods."""

    def test_get_position(self, mock_ship):
        """get_position returns ship.position."""
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_position()

        assert result is mock_ship.position

    def test_get_velocity(self, mock_ship):
        """get_velocity returns ship.velocity."""
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_velocity()

        assert result is mock_ship.velocity

    def test_get_rotation(self, mock_ship):
        """get_rotation returns ship.angle."""
        mock_ship.angle = 90.0
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_rotation()

        assert result == 90.0

    def test_set_throttle(self, mock_ship):
        """set_throttle sets ship.engine_throttle."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_throttle(0.5)

        assert mock_ship.engine_throttle == 0.5

    def test_set_turn_throttle(self, mock_ship):
        """set_turn_throttle sets ship.turn_throttle."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_turn_throttle(0.75)

        assert mock_ship.turn_throttle == 0.75

    def test_rotate_delegates(self, mock_ship):
        """rotate() delegates to ship.rotate()."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.rotate(1)

        mock_ship.rotate.assert_called_once_with(1)

    def test_thrust_forward_delegates(self, mock_ship):
        """thrust_forward() delegates to ship.thrust_forward()."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.thrust_forward()

        mock_ship.thrust_forward.assert_called_once()

    def test_set_rotation(self, mock_ship):
        """set_rotation sets ship.angle directly."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_rotation(180.0)

        assert mock_ship.angle == 180.0

    def test_adjust_position(self, mock_ship):
        """adjust_position adds delta to ship.position."""
        mock_ship.position = MagicMock()
        mock_ship.position.__iadd__ = MagicMock(return_value=mock_ship.position)
        delta = MagicMock()

        adapter = ShipControllableAdapter(mock_ship)
        adapter.adjust_position(delta)

        mock_ship.position.__iadd__.assert_called_once_with(delta)


class TestCombatMethods:
    """Tests for combat-related methods."""

    def test_get_weapon_range(self, mock_ship):
        """get_weapon_range returns ship.max_weapon_range."""
        mock_ship.max_weapon_range = 750.0
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_weapon_range()

        assert result == 750.0

    def test_set_trigger_pulled(self, mock_ship):
        """set_trigger_pulled sets ship.comp_trigger_pulled."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_trigger_pulled(True)

        assert mock_ship.comp_trigger_pulled is True

    def test_get_current_target(self, mock_ship):
        """get_current_target returns ship.current_target."""
        target = MagicMock()
        mock_ship.current_target = target
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_current_target()

        assert result is target

    def test_set_current_target(self, mock_ship):
        """set_current_target sets ship.current_target."""
        target = MagicMock()
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_current_target(target)

        assert mock_ship.current_target is target

    def test_set_secondary_targets(self, mock_ship):
        """set_secondary_targets sets ship.secondary_targets."""
        targets = [MagicMock(), MagicMock()]
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_secondary_targets(targets)

        assert mock_ship.secondary_targets == targets

    def test_get_components_by_ability(self, mock_ship):
        """get_components_by_ability delegates to ship."""
        components = [MagicMock(), MagicMock()]
        mock_ship.get_components_by_ability.return_value = components
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_components_by_ability('WeaponAbility')

        mock_ship.get_components_by_ability.assert_called_once_with('WeaponAbility', True)
        assert result == components

    def test_get_components_by_ability_with_operational_flag(self, mock_ship):
        """get_components_by_ability passes operational_only flag."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.get_components_by_ability('PDCAbility', operational_only=False)

        mock_ship.get_components_by_ability.assert_called_once_with('PDCAbility', False)

    def test_get_layers(self, mock_ship):
        """get_layers returns ship.layers."""
        layers = {'OUTER': [], 'INNER': []}
        mock_ship.layers = layers
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_layers()

        assert result is layers


class TestInterfaceCompleteness:
    """Tests to verify complete interface implementation."""

    def test_all_abstract_methods_implemented(self, mock_ship):
        """ShipControllableAdapter implements all abstract methods."""
        adapter = ShipControllableAdapter(mock_ship)

        # Get all abstract methods from IControllable
        abstract_methods = IControllable.__abstractmethods__

        # Verify each is callable on adapter
        for method_name in abstract_methods:
            method = getattr(adapter, method_name, None)
            assert method is not None, f"Missing method: {method_name}"
            assert callable(method), f"Not callable: {method_name}"

    def test_interface_methods_dont_raise_on_normal_ship(self, mock_ship):
        """All interface methods work without raising on normal ship."""
        adapter = ShipControllableAdapter(mock_ship)

        # Call each getter without args
        adapter.get_position()
        adapter.get_velocity()
        adapter.get_rotation()
        adapter.get_radius()
        adapter.get_max_speed()
        adapter.get_current_speed()
        adapter.get_turn_speed()
        adapter.get_acceleration_rate()
        adapter.get_is_thrusting()
        adapter.get_turn_throttle()
        adapter.get_team_id()
        adapter.is_alive()
        adapter.get_weapon_range()
        adapter.get_current_target()
        adapter.get_max_targets()
        adapter.get_secondary_targets()
        adapter.get_layers()
        adapter.get_movement_policy()
        adapter.get_targeting_policy()
        adapter.get_vehicle_type()
        adapter.get_all_components()

        # Call each setter
        adapter.set_throttle(1.0)
        adapter.set_turn_throttle(1.0)
        adapter.rotate(0)
        adapter.thrust_forward()
        adapter.set_rotation(0.0)
        adapter.adjust_position(MagicMock())
        adapter.set_trigger_pulled(False)
        adapter.set_current_target(None)
        adapter.set_secondary_targets([])
        adapter.get_components_by_ability('Test')


class TestIdentityAndState:
    """Tests for identity and state methods."""

    def test_get_team_id(self, mock_ship):
        """get_team_id returns ship.team_id."""
        mock_ship.team_id = 2
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_team_id()

        assert result == 2

    def test_is_alive_returns_true(self, mock_ship):
        """is_alive returns True when ship.is_alive is True."""
        mock_ship.is_alive = True
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.is_alive()

        assert result is True

    def test_is_alive_returns_false(self, mock_ship):
        """is_alive returns False when ship.is_alive is False."""
        mock_ship.is_alive = False
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.is_alive()

        assert result is False


# =============================================================================
# Migrated from controllable_interface/test_adapter_methods.py
# PROJ-156 Task 3.4: Tests for PROJ-24 __getattr__/__setattr__ removal
# =============================================================================


class TestAttributeDelegationRemoved:
    """Tests that PROJ-24 removed __getattr__/__setattr__ delegation.

    Note: PROJ-24 removed the __getattr__/__setattr__ delegation methods.
    Direct attribute access is no longer supported. Use interface methods instead.
    """

    def test_direct_attribute_access_raises_error(self, mock_ship):
        """Direct attribute access (bypassing interface) raises AttributeError."""
        mock_ship.some_custom_attribute = "test_value"

        adapter = ShipControllableAdapter(mock_ship)

        # Direct attribute access should fail (no __getattr__ delegation)
        with pytest.raises(AttributeError):
            _ = adapter.some_custom_attribute

    def test_direct_attribute_assignment_does_not_delegate(self, mock_ship):
        """Direct attribute assignment sets on adapter, not underlying ship."""
        adapter = ShipControllableAdapter(mock_ship)

        # Without __setattr__ delegation, assignment goes to adapter, not ship
        adapter.some_custom_attribute = "test_value"

        # Attribute is on adapter itself (in __dict__), not delegated to ship
        assert adapter.some_custom_attribute == "test_value"
        assert 'some_custom_attribute' in adapter.__dict__
