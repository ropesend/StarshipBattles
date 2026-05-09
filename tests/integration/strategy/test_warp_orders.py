"""
Integration tests for WARP order functionality (PROJ-187 Phase 6).

Tests the complete flow of WARP orders:
- Command validation and handler
- Fleet navigation through warp points
- Movement engine processing
- Serialization round-trip
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueWarpCommand
from game.strategy.engine.command_handlers import WarpCommandHandler
from game.core.validation import ValidationResult


class TestWarpOrderCommand:
    """Tests for IssueWarpCommand and WarpCommandHandler."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock game session with galaxy."""
        session = MagicMock()

        # Create warp point at (10, 5) in source system
        warp_point = MagicMock()
        warp_point.destination_id = "DestSystem"
        warp_point.location = HexCoord(0, 5)

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.name = "SourceSystem"
        source_system.warp_points = [warp_point]

        session.galaxy = MagicMock()
        session.galaxy.state.global_hex_warp_points = {HexCoord(10, 5): source_system}

        # BUG-125: align active_empire with the test fleet's owner (0).
        session.active_empire = MagicMock(id=0)

        return session

    @pytest.fixture
    def warp_capable_fleet(self):
        """Create a fleet that can use warp."""
        fleet = Fleet("test_fleet", 0, HexCoord(10, 5), speed=5.0)
        # PROJ-210: can_use_warp accessed via fleet.capabilities property
        fleet._capabilities = MagicMock()
        fleet._capabilities.can_use_warp = MagicMock(return_value=True)
        fleet._capabilities.get_warp_limiting_ship = MagicMock(return_value=None)
        return fleet

    @pytest.fixture
    def non_warp_fleet(self):
        """Create a fleet that cannot use warp."""
        fleet = Fleet("test_fleet", 0, HexCoord(10, 5), speed=5.0)
        # PROJ-210: can_use_warp accessed via fleet.capabilities property
        fleet._capabilities = MagicMock()
        fleet._capabilities.can_use_warp = MagicMock(return_value=False)
        limiting_ship = MagicMock()
        limiting_ship.name = "Heavy Freighter"
        fleet._capabilities.get_warp_limiting_ship = MagicMock(return_value=limiting_ship)
        return fleet

    def test_warp_command_at_warp_point_queues_warp_order(
        self, mock_session, warp_capable_fleet
    ):
        """Fleet at warp point should only queue WARP order."""
        mock_session._get_fleet_by_id = MagicMock(return_value=warp_capable_fleet)
        warp_point_hex = HexCoord(10, 5)

        handler = WarpCommandHandler()
        cmd = IssueWarpCommand(fleet_id="test_fleet", warp_point_hex=warp_point_hex)

        result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(warp_capable_fleet.orders) == 1
        assert warp_capable_fleet.orders[0].type == OrderType.WARP
        assert warp_capable_fleet.orders[0].target == warp_point_hex

    def test_warp_command_not_at_warp_point_queues_move_then_warp(
        self, mock_session, warp_capable_fleet
    ):
        """Fleet NOT at warp point should queue MOVE then WARP."""
        warp_capable_fleet.location = HexCoord(5, 3)  # Away from warp point
        mock_session._get_fleet_by_id = MagicMock(return_value=warp_capable_fleet)
        warp_point_hex = HexCoord(10, 5)

        handler = WarpCommandHandler()
        cmd = IssueWarpCommand(fleet_id="test_fleet", warp_point_hex=warp_point_hex)

        result = handler.execute(mock_session, cmd)

        assert result.is_valid
        assert len(warp_capable_fleet.orders) == 2
        assert warp_capable_fleet.orders[0].type == OrderType.MOVE
        assert warp_capable_fleet.orders[0].target == warp_point_hex
        assert warp_capable_fleet.orders[1].type == OrderType.WARP
        assert warp_capable_fleet.orders[1].target == warp_point_hex

    def test_warp_command_rejects_non_warp_fleet(
        self, mock_session, non_warp_fleet
    ):
        """Fleet without warp capability should be rejected."""
        mock_session._get_fleet_by_id = MagicMock(return_value=non_warp_fleet)
        warp_point_hex = HexCoord(10, 5)

        handler = WarpCommandHandler()
        cmd = IssueWarpCommand(fleet_id="test_fleet", warp_point_hex=warp_point_hex)

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "Heavy Freighter" in result.errors[0]
        assert len(non_warp_fleet.orders) == 0

    def test_warp_command_rejects_invalid_warp_point(
        self, mock_session, warp_capable_fleet
    ):
        """Invalid warp point hex should be rejected."""
        mock_session._get_fleet_by_id = MagicMock(return_value=warp_capable_fleet)
        invalid_hex = HexCoord(99, 99)  # No warp point here

        handler = WarpCommandHandler()
        cmd = IssueWarpCommand(fleet_id="test_fleet", warp_point_hex=invalid_hex)

        result = handler.execute(mock_session, cmd)

        assert not result.is_valid
        assert "No warp point" in result.errors[0]
        assert len(warp_capable_fleet.orders) == 0


class TestWarpOrderNavigation:
    """Tests for warp order navigation integration."""

    @pytest.fixture
    def galaxy_with_warp(self):
        """Create a galaxy with connected warp points."""
        # Source system at (10, 0) with warp point at local (0, 5) = global (10, 5)
        source_wp = MagicMock()
        source_wp.destination_id = "DestSystem"
        source_wp.location = HexCoord(0, 5)

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.name = "SourceSystem"
        source_system.warp_points = [source_wp]

        # Dest system at (50, 0) with reciprocal warp point at local (2, 2) = global (52, 2)
        dest_wp = MagicMock()
        dest_wp.destination_id = "SourceSystem"
        dest_wp.location = HexCoord(2, 2)

        dest_system = MagicMock()
        dest_system.global_location = HexCoord(50, 0)
        dest_system.name = "DestSystem"
        dest_system.warp_points = [dest_wp]

        galaxy = MagicMock()
        galaxy.state.global_hex_warp_points = {HexCoord(10, 5): source_system}
        galaxy.get_system_by_name = MagicMock(return_value=dest_system)
        galaxy.systems = {
            source_system.global_location: source_system,
            dest_system.global_location: dest_system
        }
        galaxy.name_map = {
            "SourceSystem": source_system,
            "DestSystem": dest_system
        }

        return galaxy

    def test_navigation_service_computes_warp_exit(self, galaxy_with_warp):
        """FleetNavigationService should resolve warp exit hex."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)

        state = NavigationState(
            location=warp_point_hex,
            path=(),
            orders=(Order(OrderType.WARP, target=warp_point_hex),),
            speed=10.0,
            can_warp=True
        )

        step = service.compute_next_step(state, galaxy_with_warp)

        # Should warp to exit hex (52, 2)
        assert step.next_hex == HexCoord(52, 2)
        assert step.order_complete

    def test_compute_path_for_warp_includes_movement_to_warp(self, galaxy_with_warp):
        """compute_path_for_warp should include path to warp point + exit."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)

        state = NavigationState(
            location=HexCoord(8, 3),  # Not at warp point
            path=(),
            orders=(Order(OrderType.WARP, target=warp_point_hex),),
            speed=10.0,
            can_warp=True
        )

        path = service.compute_path_for_warp(state, warp_point_hex, galaxy_with_warp)

        # Path should end at exit hex
        assert path[-1] == HexCoord(52, 2)


class TestWarpOrderSerialization:
    """Tests for WARP order serialization."""

    def test_warp_order_roundtrip(self):
        """WARP order should serialize and deserialize correctly."""
        warp_target = HexCoord(15, 8)
        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.orders.append(Order(OrderType.WARP, target=warp_target))

        # Serialize
        data = fleet.to_dict()

        # Deserialize
        restored = Fleet.from_dict(data)

        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.WARP
        assert restored.orders[0].target == warp_target

    def test_warp_order_with_execution_progress(self):
        """WARP order with execution progress should preserve it."""
        warp_target = HexCoord(20, 10)
        order = Order(OrderType.WARP, target=warp_target)
        order.execution_progress = 5  # Shouldn't normally happen, but test it

        fleet = Fleet("f1", 0, HexCoord(0, 0), speed=5.0)
        fleet.orders.append(order)

        # Serialize
        data = fleet.to_dict()
        assert data['orders'][0].get('execution_progress') == 5

        # Deserialize
        restored = Fleet.from_dict(data)
        assert restored.orders[0].execution_progress == 5
