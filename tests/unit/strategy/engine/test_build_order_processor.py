"""Tests for BUILD order processing in FleetOrderProcessor (PROJ-67 Phase 2)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor


class TestBuildOrderProcessing:
    """Test cases for BUILD order processing in FleetOrderProcessor."""

    @pytest.fixture
    def order_processor(self):
        """Create a FleetOrderProcessor instance."""
        return FleetOrderProcessor()

    @pytest.fixture
    def mock_empire(self):
        """Create a mock empire."""
        empire = MagicMock()
        empire.fleets = []
        return empire

    @pytest.fixture
    def mock_galaxy(self):
        """Create a mock galaxy."""
        return MagicMock()

    @pytest.fixture
    def fleet_with_build_order(self):
        """Create a fleet with BUILD order and items in queue."""
        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [
            {'design_id': 'frigate', 'type': 'ship', 'turns_remaining': 5}
        ]
        return fleet

    def test_build_order_persists_while_queue_has_items(
        self, order_processor, mock_empire, mock_galaxy, fleet_with_build_order
    ):
        """Test BUILD order persists across turns while queue has items."""
        initial_order = fleet_with_build_order.get_current_order()

        # Process end turn - BUILD order should persist
        consumed = order_processor.process_end_turn_orders(
            fleet_with_build_order, mock_empire, mock_galaxy
        )

        # Fleet should not be consumed (it's still building)
        assert consumed is False
        # BUILD order should still be there
        current = fleet_with_build_order.get_current_order()
        assert current is not None
        assert current.type == OrderType.BUILD

    def test_build_order_auto_completes_when_queue_empties(
        self, mock_empire, mock_galaxy
    ):
        """Test BUILD order auto-completes when construction_queue empties.

        Note: BUILD auto-pop is handled by ActionExecutionEngine, not FleetOrderProcessor.
        """
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = []  # Empty queue
        mock_empire.fleets = [fleet]

        order_processor = FleetOrderProcessor()
        engine = ActionExecutionEngine(order_processor)

        # Process tick - BUILD order should auto-pop when queue empty
        engine.process_action_ticks([mock_empire], mock_galaxy, tick=20)

        # BUILD order should be popped
        current = fleet.get_current_order()
        assert current is None

    def test_build_order_can_be_manually_cancelled(
        self, order_processor, fleet_with_build_order
    ):
        """Test BUILD order can be manually cancelled (pop_order)."""
        # Verify order exists
        assert fleet_with_build_order.get_current_order().type == OrderType.BUILD

        # Manual cancellation via pop_order
        cancelled = fleet_with_build_order.pop_order()

        assert cancelled is not None
        assert cancelled.type == OrderType.BUILD
        assert fleet_with_build_order.get_current_order() is None

    def test_build_order_not_consumed_like_colonize(
        self, order_processor, mock_empire, mock_galaxy, fleet_with_build_order
    ):
        """Test BUILD order doesn't consume the fleet like COLONIZE does."""
        mock_empire.fleets = [fleet_with_build_order]
        initial_fleet_count = len(mock_empire.fleets)

        consumed = order_processor.process_end_turn_orders(
            fleet_with_build_order, mock_empire, mock_galaxy
        )

        # Fleet should NOT be removed
        assert consumed is False
        # (We can't directly check mock_empire.fleets wasn't modified,
        # but consumed=False means no removal action was taken)

    def test_process_end_turn_ignores_build_with_queue(
        self, order_processor, mock_empire, mock_galaxy
    ):
        """Test process_end_turn_orders keeps BUILD order when queue has items."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [{'design_id': 'destroyer', 'turns_remaining': 3}]

        result = order_processor.process_end_turn_orders(fleet, mock_empire, mock_galaxy)

        assert result is False
        assert fleet.get_current_order().type == OrderType.BUILD
        assert len(fleet.orders) == 1

    def test_queued_orders_remain_after_build_completion(
        self, mock_empire, mock_galaxy
    ):
        """Test orders queued after BUILD remain when BUILD completes.

        Note: BUILD auto-pop is handled by ActionExecutionEngine, not FleetOrderProcessor.
        """
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))  # Queued after
        fleet.construction_queue = []  # Empty, BUILD will complete
        mock_empire.fleets = [fleet]

        order_processor = FleetOrderProcessor()
        engine = ActionExecutionEngine(order_processor)

        engine.process_action_ticks([mock_empire], mock_galaxy, tick=20)

        # BUILD should be popped, MOVE should now be current
        current = fleet.get_current_order()
        assert current is not None
        assert current.type == OrderType.MOVE
