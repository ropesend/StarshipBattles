"""
Unit tests for FleetMovementEngine - Basic functionality.

Tests creation, movement calculation, and movement application.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Test: Movement Calculation
# =============================================================================

class TestMovementCalculation:
    """Tests for calculate_next_hex method."""

    def test_no_order_returns_none(self, mock_fleet, mock_galaxy):
        """Fleet with no orders returns None."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        mock_fleet.get_current_order.return_value = None

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        assert result is None

    def test_move_order_to_destination(self, mock_fleet, mock_galaxy):
        """MOVE order calculates path to destination."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target = HexCoord(10, 0)
        order = Order(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: Patch where the import is used (in the service that engine delegates to)
        with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

            mock_path.assert_called()
            # Should return first step in path (after removing current location)
            assert result == HexCoord(1, 0)

    def test_already_at_destination_pops_order(self, mock_fleet, mock_galaxy):
        """Fleet at destination pops the MOVE order."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target = HexCoord(0, 0)
        order = Order(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = target  # Already there

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None

    def test_uses_existing_path(self, mock_fleet, mock_galaxy):
        """Uses existing path if available and destination unchanged."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target = HexCoord(10, 0)
        order = Order(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = [HexCoord(5, 0), HexCoord(10, 0)]  # Pre-existing path
        mock_fleet.location = HexCoord(0, 0)

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        # Should pop from existing path
        assert result == HexCoord(5, 0)

    def test_recalculates_path_if_destination_changed(self, mock_fleet, mock_galaxy):
        """Recalculates path if destination differs from path endpoint.

        PROJ-322 Tasks 3.12 / 5.33: inject a fake nav-service via DI rather
        than monkey-patching the module-level ``find_hybrid_path``. This
        keeps the test focused on the public ``calculate_next_hex`` contract
        and avoids the brittle private-attribute reach.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        new_target = HexCoord(20, 0)  # Different destination
        order = Order(OrderType.MOVE, new_target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = [HexCoord(5, 0), HexCoord(10, 0)]  # Old path to (10,0)
        mock_fleet.location = HexCoord(0, 0)

        fake_nav_service = MagicMock()
        fake_nav_service.calculate_fleet_next_hex.return_value = HexCoord(1, 0)

        engine = FleetMovementEngine(nav_service=fake_nav_service)
        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        # Engine delegates to the injected nav service for fresh-path logic.
        fake_nav_service.calculate_fleet_next_hex.assert_called_once_with(
            mock_fleet, mock_galaxy
        )
        assert result == HexCoord(1, 0)


# =============================================================================
# Test: Movement Application
# =============================================================================

class TestMovementApplication:
    """Tests for apply_movement method."""

    def test_apply_movement_updates_location(self, mock_fleet, mock_galaxy):
        """apply_movement updates fleet location."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(5, 0)

        result = engine.apply_movement(mock_fleet, next_hex, mock_galaxy)

        assert mock_fleet.location == next_hex
        assert result.moved is True

    def test_apply_movement_consumes_resources(self, mock_fleet, mock_galaxy):
        """apply_movement consumes movement resources."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(1, 0)  # Adjacent hex
        mock_fleet.location = HexCoord(0, 0)

        engine.apply_movement(mock_fleet, next_hex, mock_galaxy)

        mock_fleet.resources.consume_movement_resources.assert_called_with(1)

    def test_apply_movement_fails_without_resources(self, mock_fleet, mock_galaxy):
        """apply_movement fails if fleet lacks resources."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(5, 0)
        mock_fleet.resources.has_resources_for_movement.return_value = False
        original_location = mock_fleet.location

        result = engine.apply_movement(mock_fleet, next_hex, mock_galaxy)

        assert result.moved is False
        assert result.stranded is True
        mock_fleet.clear_orders.assert_called()

    def test_apply_movement_does_not_pop_order(self, mock_fleet, mock_galaxy):
        """apply_movement does NOT pop order (popping is handled by calculate_next_hex).

        PROJ-35: Order popping moved to calculate_next_hex (via FleetNavigationService)
        to prevent double-popping when orders are chained (e.g., MOVE then COLONIZE).
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(5, 0)
        mock_fleet.path = []  # Empty path

        engine.apply_movement(mock_fleet, next_hex, mock_galaxy)

        mock_fleet.pop_order.assert_not_called()
