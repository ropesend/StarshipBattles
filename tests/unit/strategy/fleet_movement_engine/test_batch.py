"""
Unit tests for FleetMovementEngine - Batch operations.

Tests collect/apply movements, movement results, and unhandled order types.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


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
        order = Order(OrderType.MOVE, HexCoord(10, 0))
        fleet.get_current_order.return_value = order
        fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        fleet.can_use_warp = MagicMock(return_value=True)
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
        order = Order(OrderType.MOVE, HexCoord(10, 0))
        slow_fleet.get_current_order.return_value = order
        slow_fleet.orders = [order]  # PROJ-35: Service uses orders list directly
        slow_fleet.can_use_warp = MagicMock(return_value=True)
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
        stationary_fleet.get_current_order.return_value = Order(OrderType.MOVE, HexCoord(10, 0))
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
# Test: Order Types Not Handled
# =============================================================================

class TestUnhandledOrderTypes:
    """Tests for order types not handled by movement engine."""

    def test_colonize_order_returns_none(self, mock_fleet, mock_galaxy):
        """COLONIZE order returns None (handled elsewhere)."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        order = Order(OrderType.COLONIZE, None)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        assert result is None

    def test_join_fleet_order_returns_none(self, mock_fleet, mock_galaxy):
        """JOIN_FLEET order returns None for movement (handled as instant)."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(10, 0)
        order = Order(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.orders = [order]  # PROJ-35: Service uses orders list directly

        result = engine.calculate_next_hex(mock_fleet, mock_galaxy)

        # JOIN_FLEET should be handled differently (instant order, not movement)
        # This movement engine only handles MOVE and MOVE_TO_FLEET
        assert result is None
