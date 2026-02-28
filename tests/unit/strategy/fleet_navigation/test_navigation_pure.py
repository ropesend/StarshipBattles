"""
Unit tests for fleet navigation service pure unit tests.

Tests NavigationState and NavigationStep data structures.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


class TestNavigationState:
    """Tests for NavigationState data structure."""

    def test_navigation_service_exists(self):
        """Fleet navigation service module can be imported."""
        from game.strategy.services import fleet_navigation_service
        assert fleet_navigation_service is not None

    def test_navigation_state_creation(self):
        """NavigationState can be created."""
        from game.strategy.services.fleet_navigation_service import NavigationState
        # Create with actual required params
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=10.0,
            can_warp=False
        )
        assert state.location == HexCoord(0, 0)
        assert state.speed == 10.0


class TestNavigationStep:
    """Tests for NavigationStep data structure."""

    def test_navigation_step_exists(self):
        """NavigationStep class exists."""
        from game.strategy.services.fleet_navigation_service import NavigationStep
        assert NavigationStep is not None


class TestWarpOrderNavigation:
    """Tests for WARP order handling in FleetNavigationService (PROJ-187 Phase 6)."""

    def test_get_destination_warp_returns_target_hex(self):
        """get_destination for WARP order returns the warp point hex as destination."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )
        from game.strategy.data.order_types import FleetOrder, OrderType

        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)
        order = FleetOrder(OrderType.WARP, target=warp_point_hex)

        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=10.0,
            can_warp=True
        )

        # Galaxy mock - not needed for simple WARP destination
        galaxy = MagicMock()

        destination = service.get_destination(state, order, galaxy)
        assert destination == warp_point_hex

    def test_compute_path_for_warp_includes_exit_point(self):
        """compute_path for WARP creates path to warp point, then adds exit point."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )
        from game.strategy.data.order_types import FleetOrder, OrderType

        service = FleetNavigationService()

        # Create warp point at hex (10, 5) in system at (10, 0)
        # Exit warp point in destination system at (50, 0) + local (2, 2) = (52, 2)
        warp_point_hex = HexCoord(10, 5)
        exit_hex = HexCoord(52, 2)

        order = FleetOrder(OrderType.WARP, target=warp_point_hex)

        state = NavigationState(
            location=HexCoord(5, 3),  # Fleet is a few hexes away
            path=(),
            orders=(order,),
            speed=10.0,
            can_warp=True
        )

        # Mock galaxy with warp point lookup
        warp_point = MagicMock()
        warp_point.destination_id = "DestSystem"
        warp_point.location = HexCoord(0, 5)  # local offset

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.name = "SourceSystem"  # For reciprocal lookup
        source_system.warp_points = [warp_point]

        dest_system = MagicMock()
        dest_system.global_location = HexCoord(50, 0)
        dest_system.name = "DestSystem"

        # Reciprocal warp point points back to SourceSystem
        dest_warp_point = MagicMock()
        dest_warp_point.destination_id = "SourceSystem"
        dest_warp_point.location = HexCoord(2, 2)
        dest_system.warp_points = [dest_warp_point]

        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {warp_point_hex: source_system}
        galaxy.get_system_by_name = MagicMock(return_value=dest_system)

        # compute_path_for_warp should return path including exit hex
        path = service.compute_path_for_warp(state, warp_point_hex, galaxy)

        # Should end at exit hex (after warp transit)
        assert path[-1] == exit_hex

    def test_warp_order_treated_as_movement_by_navigation(self):
        """WARP order is handled like MOVE for navigation purposes."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )
        from game.strategy.data.order_types import FleetOrder, OrderType

        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)
        order = FleetOrder(OrderType.WARP, target=warp_point_hex)

        state = NavigationState(
            location=warp_point_hex,  # Already at warp point
            path=(),
            orders=(order,),
            speed=10.0,
            can_warp=True
        )

        # Mock galaxy with simple warp lookup
        exit_hex = HexCoord(52, 2)

        warp_point = MagicMock()
        warp_point.destination_id = "DestSystem"
        warp_point.location = HexCoord(0, 5)

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.name = "SourceSystem"  # For reciprocal lookup
        source_system.warp_points = [warp_point]

        dest_system = MagicMock()
        dest_system.global_location = HexCoord(50, 0)
        dest_system.name = "DestSystem"

        # Reciprocal warp point points back to SourceSystem
        dest_warp_point = MagicMock()
        dest_warp_point.destination_id = "SourceSystem"
        dest_warp_point.location = HexCoord(2, 2)
        dest_system.warp_points = [dest_warp_point]

        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {warp_point_hex: source_system}
        galaxy.get_system_by_name = MagicMock(return_value=dest_system)

        # compute_next_step should calculate warp transit
        step = service.compute_next_step(state, galaxy)

        # Should have next_hex (the exit point after warp)
        assert step.next_hex == exit_hex
