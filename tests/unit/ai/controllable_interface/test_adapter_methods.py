"""
Unit tests for ShipControllableAdapter advanced methods.

Tests ship access patterns and new interface methods (PROJ-24).
Split from test_adapter.py - advanced adapter methods.
"""

import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2


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
