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

    # Formation attributes
    ship.formation = MagicMock()
    ship.formation.members = []
    ship.formation.master = None
    ship.formation.active = False
    ship.formation.offset = None
    ship.formation.rotation_mode = 'relative'

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


class TestMissingOptionalAttributes:
    """Tests for ships with missing optional attributes."""

    def test_get_ai_strategy_missing(self):
        """Missing ai_strategy returns default 'standard_ranged'."""
        ship = MagicMock(spec=['position', 'velocity', 'angle'])
        # ai_strategy not in spec

        adapter = ShipControllableAdapter(ship)

        result = adapter.get_ai_strategy()
        assert result == 'standard_ranged'

    def test_get_vehicle_type_missing(self):
        """Missing vehicle_type returns default 'Ship'."""
        ship = MagicMock(spec=['position', 'velocity', 'angle'])
        # vehicle_type not in spec

        adapter = ShipControllableAdapter(ship)

        result = adapter.get_vehicle_type()
        assert result == 'Ship'

    def test_get_max_targets_missing(self):
        """Missing max_targets returns DEFAULT_MAX_TARGETS."""
        ship = MagicMock(spec=['position', 'velocity', 'angle'])
        # max_targets not in spec

        adapter = ShipControllableAdapter(ship)

        result = adapter.get_max_targets()
        assert result == CombatConstants.DEFAULT_MAX_TARGETS

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


class TestFormationMethods:
    """Tests for formation-related methods."""

    def test_get_formation_members(self, mock_ship):
        """get_formation_members returns ship.formation.members."""
        members = [MagicMock(), MagicMock()]
        mock_ship.formation.members = members
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_formation_members()

        assert result == members

    def test_get_formation_members_none(self, mock_ship):
        """get_formation_members returns empty list if members is None."""
        mock_ship.formation.members = None
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_formation_members()

        assert result == []

    def test_get_formation_master(self, mock_ship):
        """get_formation_master returns ship.formation.master."""
        master = MagicMock()
        mock_ship.formation.master = master
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.get_formation_master()

        assert result is master

    def test_is_in_formation(self, mock_ship):
        """is_in_formation returns ship.formation.active."""
        mock_ship.formation.active = True
        adapter = ShipControllableAdapter(mock_ship)

        result = adapter.is_in_formation()

        assert result is True

    def test_set_in_formation(self, mock_ship):
        """set_in_formation sets ship.formation.active."""
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_in_formation(True)

        assert mock_ship.formation.active is True

    def test_set_formation_master(self, mock_ship):
        """set_formation_master sets ship.formation.master."""
        master = MagicMock()
        adapter = ShipControllableAdapter(mock_ship)

        adapter.set_formation_master(master)

        assert mock_ship.formation.master is master


class TestLeaveFormation:
    """Tests for leave_formation edge cases."""

    def test_leave_formation_removes_from_master(self, mock_ship):
        """leave_formation removes ship from master's members list."""
        master = MagicMock()
        master.formation.members = [mock_ship]
        mock_ship.formation.master = master

        adapter = ShipControllableAdapter(mock_ship)
        adapter.leave_formation()

        assert mock_ship not in master.formation.members

    def test_leave_formation_no_master(self, mock_ship):
        """leave_formation handles no master gracefully."""
        mock_ship.formation.master = None

        adapter = ShipControllableAdapter(mock_ship)

        # Should not raise
        adapter.leave_formation()

    def test_leave_formation_not_in_members(self, mock_ship):
        """leave_formation handles ship not in members list."""
        master = MagicMock()
        master.formation.members = []  # Ship not in list
        mock_ship.formation.master = master

        adapter = ShipControllableAdapter(mock_ship)

        # Should not raise
        adapter.leave_formation()

    def test_leave_formation_broken_formation_structure(self, mock_ship):
        """leave_formation handles broken formation gracefully."""
        master = MagicMock(spec=['name'])  # No formation attribute
        mock_ship.formation.master = master

        adapter = ShipControllableAdapter(mock_ship)

        # Should not raise
        adapter.leave_formation()


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
        adapter.get_ai_strategy()
        adapter.get_vehicle_type()
        adapter.get_all_components()
        adapter.get_formation_members()
        adapter.get_formation_master()
        adapter.is_in_formation()
        adapter.get_formation_offset()
        adapter.get_formation_rotation_mode()

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
        adapter.set_in_formation(False)
        adapter.set_formation_master(None)
        adapter.leave_formation()


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
