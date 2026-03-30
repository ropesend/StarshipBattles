"""
Tests for tick mechanics and movement.

This test file covers:
- Movement calculation delegation
- Tick phase coordination
- JOIN_FLEET during tick processing
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Test: Movement Calculation
# =============================================================================


class TestMovementCalculation:
    """Tests for movement calculation via FleetMovementEngine.

    PROJ-36: Tests now use movement_engine.calculate_next_hex() directly.
    Legacy wrapper _calculate_next_hex removed.
    """

    def test_no_order_returns_none(self, turn_engine, mock_fleet, mock_galaxy):
        """Fleet with no orders returns None."""
        mock_fleet.get_current_order.return_value = None

        result = turn_engine.movement_engine.calculate_next_hex(mock_fleet, mock_galaxy)

        assert result is None

    def test_move_order_calculates_path(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE order triggers path calculation."""
        target = HexCoord(10, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: FleetMovementEngine delegates to FleetNavigationService, patch there
        with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            result = turn_engine.movement_engine.calculate_next_hex(mock_fleet, mock_galaxy)

            mock_path.assert_called()

    def test_at_destination_pops_order(self, turn_engine, mock_fleet, mock_galaxy):
        """Fleet at destination pops the MOVE order."""
        target = HexCoord(0, 0)
        order = FleetOrder(OrderType.MOVE, target)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = target  # Already there

        result = turn_engine.movement_engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None

    def test_move_to_fleet_uses_intercept(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET order uses intercept calculation."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(50, 0)
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        # PROJ-35: FleetMovementEngine delegates to FleetNavigationService
        # calculate_intercept_point is imported locally, so patch at source
        with patch('game.strategy.data.pathfinding.calculate_intercept_point') as mock_intercept:
            with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path') as mock_path:
                mock_intercept.return_value = HexCoord(25, 0)
                mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 0)]

                turn_engine.movement_engine.calculate_next_hex(mock_fleet, mock_galaxy)

                mock_intercept.assert_called()

    def test_invalid_target_fleet_cancels_order(self, turn_engine, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET with invalid target cancels order."""
        order = FleetOrder(OrderType.MOVE_TO_FLEET, None)  # Invalid target
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        mock_fleet.path = []

        result = turn_engine.movement_engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None


# =============================================================================
# Test: Tick Processing
# =============================================================================


class TestTickProcessing:
    """Tests for _process_tick method."""

    def test_tick_processes_phases(self, turn_engine, mock_empire, mock_galaxy):
        """Each tick processes resource and conflict phases."""
        mock_empire.fleets = []

        # PROJ-36: Combat delegated to ConflictResolutionEngine
        mock_conflict_engine = MagicMock()
        turn_engine._conflict_engine = mock_conflict_engine

        # PROJ-36: Resource consumption delegated to ConsumableManagementEngine
        mock_resource_engine = MagicMock()
        turn_engine._resource_engine = mock_resource_engine

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_resource_engine.process_per_turn_consumption.assert_called()
        mock_conflict_engine.resolve_all_conflicts.assert_called()

    def test_fleet_speed_determines_movement_frequency(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet speed affects when movement occurs."""
        # Create a real-ish fleet mock with proper speed attribute
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 10.0  # Move every 10 ticks
        fleet.orders = []
        fleet.path = []
        fleet.get_current_order = MagicMock(return_value=None)
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict engine
        turn_engine._conflict_engine = MagicMock()

        # PROJ-36: Set up mock resource engine
        turn_engine._resource_engine = MagicMock()

        # PROJ-36: Use movement_engine directly (wrapper removed)
        with patch.object(turn_engine.movement_engine, 'calculate_next_hex') as mock_calc:
            mock_calc.return_value = None

            # Tick 10 should trigger movement check (10 % 10 == 0)
            turn_engine._process_tick(10, [mock_empire], mock_galaxy)

            # Tick 5 should also check but still call calculate_next_hex
            turn_engine._process_tick(5, [mock_empire], mock_galaxy)

    def test_zero_speed_fleet_never_moves(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet with zero speed never moves."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 0.0  # Zero speed
        fleet.orders = []
        fleet.path = []
        fleet.get_current_order = MagicMock(return_value=None)
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        # PROJ-36: Use movement_engine directly (wrapper removed)
        with patch.object(turn_engine.movement_engine, 'calculate_next_hex') as mock_calc:
            for tick in range(1, 11):  # Check first 10 ticks
                turn_engine._process_tick(tick, [mock_empire], mock_galaxy)

            mock_calc.assert_not_called()

    def test_movement_consumes_resources(self, turn_engine, mock_empire, mock_galaxy):
        """Movement consumes fleet resources."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 100.0  # Move every tick
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # Pre-computed path
        fleet.get_current_order = MagicMock(return_value=order)
        fleet.pop_order = MagicMock()
        fleet.resources.has_resources_for_movement = MagicMock(return_value=True)
        fleet.resources.has_resources_for_warp = MagicMock(return_value=True)
        fleet.capabilities.can_use_warp = MagicMock(return_value=True)
        fleet.resources.consume_movement_resources = MagicMock()
        fleet.resources.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        fleet.resources.consume_movement_resources.assert_called()

    def test_stranded_fleet_clears_orders(self, turn_engine, mock_empire, mock_galaxy):
        """Fleet without movement resources clears orders."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.speed = 100.0
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        fleet.path = [HexCoord(1, 0)]  # Has path
        fleet.get_current_order = MagicMock(return_value=order)
        fleet.pop_order = MagicMock()
        fleet.resources.has_resources_for_movement = MagicMock(return_value=False)  # No resources
        fleet.resources.has_resources_for_warp = MagicMock(return_value=True)
        fleet.capabilities.can_use_warp = MagicMock(return_value=True)
        fleet.resources.consume_movement_resources = MagicMock()
        fleet.resources.consume_warp_resources = MagicMock()
        fleet.clear_orders = MagicMock()
        fleet.get_ship_instances = MagicMock(return_value=[])

        mock_empire.fleets = [fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        fleet.clear_orders.assert_called()


# =============================================================================
# Test: JOIN_FLEET During Tick
# =============================================================================


class TestJoinFleetDuringTick:
    """Tests for JOIN_FLEET instant order processing during ticks."""

    def test_join_fleet_at_same_location(self, turn_engine, mock_empire, mock_galaxy):
        """Fleets with JOIN_FLEET merge when co-located."""
        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(5, 5)
        target_fleet.speed = 10.0
        target_fleet.get_current_order = MagicMock(return_value=None)
        target_fleet.get_ship_instances = MagicMock(return_value=[])

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(5, 5)  # Same location
        joining_fleet.speed = 10.0
        joining_fleet.get_ship_instances = MagicMock(return_value=[])

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)
        joining_fleet.merge_with = MagicMock()

        mock_empire.fleets = [joining_fleet, target_fleet]
        mock_empire.remove_fleet = MagicMock()

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        # Process tick
        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        joining_fleet.merge_with.assert_called_with(target_fleet)
        mock_empire.remove_fleet.assert_called_with(joining_fleet)

    def test_join_fleet_not_at_location(self, turn_engine, mock_empire, mock_galaxy):
        """JOIN_FLEET does not merge when not co-located."""
        target_fleet = MagicMock()
        target_fleet.id = 2
        target_fleet.location = HexCoord(100, 100)
        target_fleet.speed = 10.0
        target_fleet.get_current_order = MagicMock(return_value=None)
        target_fleet.get_ship_instances = MagicMock(return_value=[])

        joining_fleet = MagicMock()
        joining_fleet.id = 1
        joining_fleet.location = HexCoord(0, 0)  # Different location
        joining_fleet.speed = 10.0
        joining_fleet.get_ship_instances = MagicMock(return_value=[])

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        joining_fleet.get_current_order = MagicMock(return_value=order)
        joining_fleet.merge_with = MagicMock()

        mock_empire.fleets = [joining_fleet, target_fleet]

        # PROJ-36: Set up mock conflict and resource engines
        turn_engine._conflict_engine = MagicMock()
        turn_engine._resource_engine = MagicMock()

        turn_engine._process_tick(1, [mock_empire], mock_galaxy)

        joining_fleet.merge_with.assert_not_called()
