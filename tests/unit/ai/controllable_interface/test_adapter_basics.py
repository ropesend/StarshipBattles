"""
Unit tests for ShipControllableAdapter basic implementation.

Tests the adapter that wraps Ship for IControllable interface - basic methods.
Split from test_adapter.py - basic adapter tests.
"""

import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2


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
