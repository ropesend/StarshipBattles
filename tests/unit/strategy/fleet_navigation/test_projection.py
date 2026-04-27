"""
Tests for FleetNavigationService path projection methods.

Tests for project_path, project_path_as_dicts, and calculate_fleet_next_hex methods.

PROJ-35: Unified fleet navigation logic for UI projection and turn execution.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType


class TestProjectPath:
    """Tests for FleetNavigationService.project_path()."""

    def test_project_path_produces_correct_segments(self):
        """project_path() should produce PathSegment objects with correct data."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, PathSegment
        )

        service = FleetNavigationService()

        # Create a fleet with a simple MOVE order and pre-computed path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0  # 2 moves per turn
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # Should produce 3 segments (one for each path step)
        assert len(segments) == 3
        assert all(isinstance(seg, PathSegment) for seg in segments)

        # First segment
        assert segments[0].start == HexCoord(0, 0)
        assert segments[0].end == HexCoord(1, 0)
        assert segments[0].is_warp is False

        # Last segment should be at the destination
        assert segments[-1].end == HexCoord(3, 0)

    def test_project_path_respects_max_turns(self):
        """project_path() should stop at max_turns."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Create a fleet with a long path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=1.0  # 1 move per turn
        )
        fleet.path = [HexCoord(i, 0) for i in range(1, 20)]  # 19 steps
        fleet.orders = [Order(OrderType.MOVE, HexCoord(19, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=3)

        # At speed 1, should only do 3 moves (one per turn for 3 turns)
        assert len(segments) == 3

    def test_project_path_handles_warp_detection(self):
        """project_path() should detect warp jumps (hex_distance > 1)."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Create a fleet with a warp jump in the path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )
        # Path with a warp jump: (0,0) -> (1,0) -> (5,0) which is distance > 1
        fleet.path = [HexCoord(1, 0), HexCoord(5, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(5, 0))]
        fleet.can_use_warp = MagicMock(return_value=True)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # First segment should be normal move
        assert segments[0].is_warp is False

        # Second segment should be warp (distance > 1)
        assert segments[1].is_warp is True

    def test_project_path_returns_empty_for_fleet_without_orders(self):
        """project_path() should return empty list if fleet has no orders."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = []
        fleet.orders = []
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        assert segments == []

    def test_project_path_calculates_turn_numbers(self):
        """project_path() should calculate correct turn numbers based on speed."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Speed 2 means 2 moves per turn
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(4, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # First two moves in turn 0, next two in turn 1
        assert segments[0].turn == 0
        assert segments[1].turn == 0
        assert segments[2].turn == 1
        assert segments[3].turn == 1


class TestProjectPathAsDicts:
    """Tests for FleetNavigationService.project_path_as_dicts()."""

    def test_project_path_as_dicts_returns_list_of_dicts(self):
        """project_path_as_dicts() should return list of dicts for backward compatibility."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(2, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.project_path_as_dicts(fleet, galaxy=MagicMock(), max_turns=5)

        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert len(result) == 2

        # Check dict structure
        assert 'start' in result[0]
        assert 'end' in result[0]
        assert 'turn' in result[0]
        assert 'is_warp' in result[0]
        assert 'hex' in result[0]  # Legacy field


class TestCalculateFleetNextHex:
    """Tests for FleetNavigationService.calculate_fleet_next_hex() - mutation bridge."""

    def test_calculate_fleet_next_hex_returns_next_hex(self):
        """calculate_fleet_next_hex() should return the next hex from path."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result == HexCoord(1, 0)

    def test_calculate_fleet_next_hex_updates_fleet_path(self):
        """calculate_fleet_next_hex() should update fleet.path (mutation bridge)."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [Order(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        # Path should be updated to remaining path
        assert fleet.path == [HexCoord(2, 0), HexCoord(3, 0)]

    def test_calculate_fleet_next_hex_pops_order_on_completion(self):
        """calculate_fleet_next_hex() should pop order when path exhausted."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0)]  # Only one step - order will complete
        fleet.orders = [Order(OrderType.MOVE, HexCoord(1, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        # Store original order count
        original_order_count = len(fleet.orders)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result == HexCoord(1, 0)
        # Order should be popped
        assert len(fleet.orders) == original_order_count - 1

    def test_calculate_fleet_next_hex_returns_none_for_no_orders(self):
        """calculate_fleet_next_hex() should return None if no orders."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = []
        fleet.orders = []
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result is None

    def test_calculate_fleet_next_hex_handles_order_complete_without_movement(self):
        """calculate_fleet_next_hex() should handle order complete when already at destination."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(5, 5),  # Already at destination
            speed=5.0
        )
        fleet.path = []
        fleet.orders = [Order(OrderType.MOVE, HexCoord(5, 5))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        # Should return None but pop the order
        assert result is None
        assert len(fleet.orders) == 0
