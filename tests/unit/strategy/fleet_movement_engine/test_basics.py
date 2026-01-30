"""
Unit tests for FleetMovementEngine - Basic functionality.

Tests creation, movement calculation, and movement application.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Test: FleetMovementEngine Creation
# =============================================================================

class TestFleetMovementEngineCreation:
    """Tests for FleetMovementEngine initialization."""

    def test_fleet_movement_engine_can_be_created(self):
        """FleetMovementEngine can be instantiated."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        assert engine is not None

    def test_fleet_movement_engine_has_calculate_next_hex(self):
        """FleetMovementEngine has calculate_next_hex method."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        assert hasattr(engine, 'calculate_next_hex')
        assert callable(engine.calculate_next_hex)

    def test_fleet_movement_engine_has_apply_movement(self):
        """FleetMovementEngine has apply_movement method."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        assert hasattr(engine, 'apply_movement')
        assert callable(engine.apply_movement)


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
        order = FleetOrder(OrderType.MOVE, target)
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
        order = FleetOrder(OrderType.MOVE, target)
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
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = [HexCoord(5, 0), HexCoord(10, 0)]  # Pre-existing path
        mock_fleet.location = HexCoord(0, 0)

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        # Should pop from existing path
        assert result == HexCoord(5, 0)

    def test_recalculates_path_if_destination_changed(self, mock_fleet, mock_galaxy):
        """Recalculates path if destination differs from path endpoint."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        new_target = HexCoord(20, 0)  # Different destination
        order = FleetOrder(OrderType.MOVE, new_target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = [HexCoord(5, 0), HexCoord(10, 0)]  # Old path to (10,0)
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: Patch where the import is used (in the service that engine delegates to)
        with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0)]

            engine.calculate_next_hex(mock_fleet, mock_galaxy)

            # Path should be recalculated
            mock_path.assert_called()


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

        mock_fleet.consume_movement_resources.assert_called_with(1)

    def test_apply_movement_fails_without_resources(self, mock_fleet, mock_galaxy):
        """apply_movement fails if fleet lacks resources."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(5, 0)
        mock_fleet.has_resources_for_movement.return_value = False
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
