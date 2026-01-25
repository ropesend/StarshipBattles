"""
Unit tests for FleetMovementEngine.

PROJ-12 Phase 3: TDD tests written before implementation.
Tests movement calculation, path management, resource consumption, and warp handling.
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Optional, List, Tuple

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy for pathfinding."""
    galaxy = MagicMock()
    galaxy.systems = {}
    return galaxy


@pytest.fixture
def mock_fleet():
    """Create a mock fleet with standard movement attributes."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.speed = 10.0
    fleet.path = []
    fleet.orders = []
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.clear_orders = MagicMock()
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.can_use_warp = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock()
    fleet.consume_warp_resources = MagicMock()
    return fleet


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
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
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
        mock_fleet.path = [HexCoord(5, 0), HexCoord(10, 0)]  # Old path to (10,0)
        mock_fleet.location = HexCoord(0, 0)

        with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(1, 0)]

            engine.calculate_next_hex(mock_fleet, mock_galaxy)

            # Path should be recalculated
            mock_path.assert_called()


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
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        with patch('game.strategy.engine.fleet_movement_engine.calculate_intercept_point') as mock_intercept:
            with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
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
        mock_fleet.path = []

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None

    def test_target_fleet_without_location_cancels_order(self, mock_fleet, mock_galaxy):
        """MOVE_TO_FLEET with target lacking location cancels order."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target_fleet = MagicMock(spec=[])  # No location attribute
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.path = []

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        mock_fleet.pop_order.assert_called()
        assert result is None


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

    def test_apply_movement_pops_order_when_path_empty(self, mock_fleet, mock_galaxy):
        """apply_movement pops order when path is exhausted."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        next_hex = HexCoord(5, 0)
        mock_fleet.path = []  # Empty path after this move

        engine.apply_movement(mock_fleet, next_hex, mock_galaxy)

        mock_fleet.pop_order.assert_called()


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
# Test: Movement Result
# =============================================================================

class TestMovementResult:
    """Tests for MovementResult dataclass."""

    def test_movement_result_has_required_fields(self):
        """MovementResult has expected fields."""
        from game.strategy.engine.fleet_movement_engine import MovementResult

        result = MovementResult(
            moved=True,
            stranded=False,
            warp_blocked=False,
            new_location=HexCoord(5, 0)
        )

        assert result.moved is True
        assert result.stranded is False
        assert result.warp_blocked is False
        assert result.new_location == HexCoord(5, 0)

    def test_movement_result_defaults(self):
        """MovementResult has sensible defaults."""
        from game.strategy.engine.fleet_movement_engine import MovementResult

        result = MovementResult(moved=True)

        assert result.moved is True
        assert result.stranded is False
        assert result.warp_blocked is False
        assert result.new_location is None


# =============================================================================
# Test: Collect Movements (Batch Processing)
# =============================================================================

class TestCollectMovements:
    """Tests for collect_movements batch method."""

    def test_collect_movements_returns_list(self, mock_galaxy):
        """collect_movements returns list of (fleet, next_hex) tuples."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        mock_empire = MagicMock()
        fleet = MagicMock()
        fleet.speed = 100.0  # High speed = moves every tick
        fleet.location = HexCoord(0, 0)
        fleet.path = [HexCoord(1, 0)]
        fleet.get_current_order.return_value = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        mock_empire.fleets = [fleet]

        moves = engine.collect_movements([mock_empire], mock_galaxy, tick=1)

        assert isinstance(moves, list)

    def test_collect_movements_respects_speed(self, mock_galaxy):
        """collect_movements only includes fleets that should move this tick."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        mock_empire = MagicMock()
        slow_fleet = MagicMock()
        slow_fleet.speed = 10.0  # Moves every 10 ticks
        slow_fleet.location = HexCoord(0, 0)
        slow_fleet.path = [HexCoord(1, 0)]
        slow_fleet.get_current_order.return_value = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        mock_empire.fleets = [slow_fleet]

        # Tick 5 should NOT trigger movement (10 % 5 != 0)
        moves_tick_5 = engine.collect_movements([mock_empire], mock_galaxy, tick=5)

        # Tick 10 SHOULD trigger movement (10 % 10 == 0)
        moves_tick_10 = engine.collect_movements([mock_empire], mock_galaxy, tick=10)

        assert len(moves_tick_5) == 0
        assert len(moves_tick_10) > 0 or slow_fleet.get_current_order.return_value is None

    def test_collect_movements_skips_zero_speed(self, mock_galaxy):
        """collect_movements skips fleets with zero speed."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        mock_empire = MagicMock()
        stationary_fleet = MagicMock()
        stationary_fleet.speed = 0.0
        stationary_fleet.location = HexCoord(0, 0)
        stationary_fleet.get_current_order.return_value = FleetOrder(OrderType.MOVE, HexCoord(10, 0))
        mock_empire.fleets = [stationary_fleet]

        moves = engine.collect_movements([mock_empire], mock_galaxy, tick=1)

        assert len(moves) == 0


# =============================================================================
# Test: Apply Movements (Batch)
# =============================================================================

class TestApplyMovements:
    """Tests for apply_movements batch method."""

    def test_apply_movements_processes_queue(self, mock_galaxy):
        """apply_movements processes all movements in queue."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        fleet1 = MagicMock()
        fleet1.location = HexCoord(0, 0)
        fleet1.path = []
        fleet1.has_resources_for_movement.return_value = True
        fleet1.has_resources_for_warp.return_value = True
        fleet1.can_use_warp.return_value = True

        fleet2 = MagicMock()
        fleet2.location = HexCoord(10, 0)
        fleet2.path = []
        fleet2.has_resources_for_movement.return_value = True
        fleet2.has_resources_for_warp.return_value = True
        fleet2.can_use_warp.return_value = True

        move_queue = [
            (fleet1, HexCoord(1, 0)),
            (fleet2, HexCoord(11, 0))
        ]

        results = engine.apply_movements(move_queue, mock_galaxy)

        assert len(results) == 2
        assert fleet1.location == HexCoord(1, 0)
        assert fleet2.location == HexCoord(11, 0)


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
        mock_fleet.path = []  # Empty, will calculate
        mock_fleet.location = HexCoord(0, 0)

        with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
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
        mock_fleet.path = []
        mock_fleet.location = HexCoord(0, 0)

        with patch('game.strategy.engine.fleet_movement_engine.find_hybrid_path') as mock_path:
            mock_path.return_value = []  # No path found

            result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

            assert result is None


# =============================================================================
# Test: Order Types Not Handled
# =============================================================================

class TestUnhandledOrderTypes:
    """Tests for order types not handled by movement engine."""

    def test_colonize_order_returns_none(self, mock_fleet, mock_galaxy):
        """COLONIZE order returns None (handled elsewhere)."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        order = FleetOrder(OrderType.COLONIZE, None)
        mock_fleet.get_current_order.return_value = order

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        assert result is None

    def test_join_fleet_order_returns_none(self, mock_fleet, mock_galaxy):
        """JOIN_FLEET order returns None for movement (handled as instant)."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(10, 0)
        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        # JOIN_FLEET should be handled differently (instant order, not movement)
        # This movement engine only handles MOVE and MOVE_TO_FLEET
        assert result is None
