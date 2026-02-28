"""Tests for BUILD order movement blocking (PROJ-67 Phase 2)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.engine.fleet_movement_engine import FleetMovementEngine


class TestMovementBlockingForBuildOrder:
    """Test cases for BUILD order blocking fleet movement."""

    @pytest.fixture
    def movement_engine(self):
        """Create a FleetMovementEngine instance."""
        return FleetMovementEngine()

    @pytest.fixture
    def mock_empire(self):
        """Create a mock empire with fleets list."""
        empire = MagicMock()
        empire.fleets = []
        return empire

    @pytest.fixture
    def mock_galaxy(self):
        """Create a mock galaxy."""
        return MagicMock()

    @pytest.fixture
    def fleet_with_build_order(self):
        """Create a fleet with BUILD order."""
        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.BUILD))
        fleet.construction_queue = [{'design_id': 'frigate', 'turns_remaining': 5}]
        return fleet

    @pytest.fixture
    def fleet_with_move_order(self):
        """Create a fleet with MOVE order."""
        fleet = Fleet("f2", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 5)))
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # Pre-calculated path
        return fleet

    def test_fleet_with_build_order_not_in_movement_collection(
        self, movement_engine, mock_empire, mock_galaxy, fleet_with_build_order
    ):
        """Test fleet with BUILD order is NOT included in movement collection."""
        mock_empire.fleets = [fleet_with_build_order]

        move_queue = movement_engine.collect_movements([mock_empire], mock_galaxy, tick=20)

        # Fleet should NOT be in the move queue
        fleet_ids = [f.id for f, _ in move_queue]
        assert fleet_with_build_order.id not in fleet_ids

    def test_fleet_with_move_order_is_in_movement_collection(
        self, movement_engine, mock_empire, mock_galaxy, fleet_with_move_order
    ):
        """Test fleet with MOVE order IS still included in movement collection."""
        mock_empire.fleets = [fleet_with_move_order]

        # Mock the navigation service to return a next hex
        nav_service = MagicMock()
        nav_service.calculate_fleet_next_hex.return_value = HexCoord(1, 0)
        movement_engine._nav_service = nav_service

        move_queue = movement_engine.collect_movements([mock_empire], mock_galaxy, tick=20)

        # Fleet should be in the move queue
        fleet_ids = [f.id for f, _ in move_queue]
        assert fleet_with_move_order.id in fleet_ids

    def test_fleet_with_build_then_move_does_not_move(
        self, movement_engine, mock_empire, mock_galaxy
    ):
        """Test fleet with BUILD order followed by MOVE doesn't move until BUILD is popped."""
        fleet = Fleet("f3", 0, HexCoord(0, 0), speed=5.0)
        fleet.add_order(FleetOrder(OrderType.BUILD))  # Current order
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(10, 10)))  # Queued after
        fleet.construction_queue = [{'design_id': 'cruiser', 'turns_remaining': 10}]
        mock_empire.fleets = [fleet]

        move_queue = movement_engine.collect_movements([mock_empire], mock_galaxy, tick=20)

        # Fleet should NOT be in the move queue because BUILD is current
        fleet_ids = [f.id for f, _ in move_queue]
        assert fleet.id not in fleet_ids

    def test_mixed_fleets_only_non_building_move(
        self, movement_engine, mock_empire, mock_galaxy, fleet_with_build_order, fleet_with_move_order
    ):
        """Test that only non-building fleets are collected for movement."""
        mock_empire.fleets = [fleet_with_build_order, fleet_with_move_order]

        # Mock the navigation service
        nav_service = MagicMock()
        nav_service.calculate_fleet_next_hex.return_value = HexCoord(1, 0)
        movement_engine._nav_service = nav_service

        move_queue = movement_engine.collect_movements([mock_empire], mock_galaxy, tick=20)

        fleet_ids = [f.id for f, _ in move_queue]
        assert fleet_with_build_order.id not in fleet_ids
        assert fleet_with_move_order.id in fleet_ids

    def test_fleet_no_order_still_not_moved(self, movement_engine, mock_empire, mock_galaxy):
        """Test fleet with no order is not moved (base case)."""
        fleet = Fleet("f4", 0, HexCoord(0, 0), speed=5.0)
        # No orders added
        mock_empire.fleets = [fleet]

        # Mock nav service returns None for no-order fleet
        nav_service = MagicMock()
        nav_service.calculate_fleet_next_hex.return_value = None
        movement_engine._nav_service = nav_service

        move_queue = movement_engine.collect_movements([mock_empire], mock_galaxy, tick=20)

        fleet_ids = [f.id for f, _ in move_queue]
        assert fleet.id not in fleet_ids
