"""
Unit tests for FleetMovementEngine - Warp and path functionality.

Tests warp travel, path management, and fleet intercept.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Test: MOVE_TO_FLEET Intercept
# =============================================================================

class TestMoveToFleetIntercept:
    """Tests for MOVE_TO_FLEET order with intercept calculation."""

    def test_move_to_fleet_uses_intercept(self, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET order uses intercept calculation."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(50, 0)
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: Patch at the source module since it's imported locally in get_destination()
        with patch('game.strategy.data.pathfinding.calculate_intercept_point') as mock_intercept:
            with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
                mock_intercept.return_value = HexCoord(25, 0)
                mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 0)]

                engine.calculate_next_hex(mock_fleet, mock_galaxy)

                mock_intercept.assert_called()

    def test_invalid_target_fleet_cancels_order(self, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET with invalid target cancels order."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        order = FleetOrder(OrderType.MOVE_TO_FLEET, None)  # Invalid target
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None

    # NOTE: test_target_fleet_without_location_cancels_order removed
    # Fleet always has location attribute - testing "target lacking location" is obsolete
    # test_move_to_fleet_no_target_cancels_order covers the None target case


# =============================================================================
# Test: Warp Travel
# =============================================================================

class TestWarpTravel:
    """Tests for warp travel handling."""

    def test_warp_detected_for_distant_hex(self, mock_fleet, mock_galaxy):
        """Warp is detected when hex distance > 1."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        mock_fleet.location = HexCoord(0, 0)
        distant_hex = HexCoord(50, 0)  # Far away

        result = engine.apply_movement(mock_fleet, distant_hex, mock_galaxy)

        mock_fleet.consume_warp_resources.assert_called()

    def test_warp_not_detected_for_adjacent_hex(self, mock_fleet, mock_galaxy):
        """Warp is not detected for adjacent hex."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        mock_fleet.location = HexCoord(0, 0)
        adjacent_hex = HexCoord(1, 0)  # Adjacent

        engine.apply_movement(mock_fleet, adjacent_hex, mock_galaxy)

        mock_fleet.consume_warp_resources.assert_not_called()

    def test_warp_fails_without_capability(self, mock_fleet, mock_galaxy):
        """Warp fails if fleet lacks warp capability."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        mock_fleet.location = HexCoord(0, 0)
        distant_hex = HexCoord(50, 0)
        mock_fleet.can_use_warp.return_value = False

        result = engine.apply_movement(mock_fleet, distant_hex, mock_galaxy)

        assert result.moved is False
        assert result.warp_blocked is True
        mock_fleet.clear_orders.assert_called()

    def test_warp_fails_without_resources(self, mock_fleet, mock_galaxy):
        """Warp fails if fleet lacks warp resources."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        mock_fleet.location = HexCoord(0, 0)
        distant_hex = HexCoord(50, 0)
        mock_fleet.can_use_warp.return_value = True
        mock_fleet.has_resources_for_warp.return_value = False

        result = engine.apply_movement(mock_fleet, distant_hex, mock_galaxy)

        assert result.moved is False
        mock_fleet.clear_orders.assert_called()


# =============================================================================
# Test: Path Management
# =============================================================================

class TestPathManagement:
    """Tests for path-related functionality."""

    def test_removes_current_location_from_path(self, mock_fleet, mock_galaxy):
        """Removes current location if path starts with it."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target = HexCoord(10, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []  # Empty, will calculate
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: Patch where the import is used (in the service that engine delegates to)
        with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
            # Path starts with current location
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

            # Should return HexCoord(1, 0), not HexCoord(0, 0)
            assert result == HexCoord(1, 0)

    def test_handles_empty_path_result(self, mock_fleet, mock_galaxy):
        """Handles case where pathfinding returns empty path."""
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
            mock_path.return_value = []  # No path found

            result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

            assert result is None
