"""
Tests for FleetNavigationService path projection with action timing (PROJ-187).

These tests verify that project_path() correctly accounts for action_time
on non-movement orders, delaying subsequent movement appropriately.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType


class TestProjectPathActionTiming:
    """Tests for action_time consumption during path projection."""

    def test_move_colonize_shows_action_delay(self):
        """MOVE -> COLONIZE(action_time=1) shows colonize delay in turn calculation.

        With speed=2 (2 moves per turn):
        - Turn 0: 2 movement steps
        - After arrival, COLONIZE takes 1 tick
        - This tick should be consumed from the next turn's movement budget
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Create fleet at (0,0) with MOVE -> COLONIZE orders
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0  # 2 moves per turn
        )

        # Pre-computed path to (2,0) and queued colonize order
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        target_planet = MagicMock()
        fleet.orders = [
            FleetOrder(OrderType.MOVE, HexCoord(2, 0)),
            FleetOrder(OrderType.COLONIZE, target_planet),
            FleetOrder(OrderType.MOVE, HexCoord(4, 0)),  # Continue after colonize
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        # Mock component registry that returns action_time=1 for colonize
        mock_registry = {}

        # Create mock galaxy that returns path for second MOVE
        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            # Return path from (2,0) to (4,0) after colonize
            mock_find_path.return_value = [HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0)]

            # Patch action time resolver to return 1 for colonize
            with patch(
                'game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time'
            ) as mock_action_time:
                mock_action_time.return_value = 1

                segments = service.project_path(
                    fleet, mock_galaxy, max_turns=5, component_registry=mock_registry
                )

        # Verify segments exist
        assert len(segments) >= 3, f"Expected at least 3 movement segments, got {len(segments)}"

        # First two movements should be turn 0 (speed=2)
        assert segments[0].turn == 0
        assert segments[1].turn == 0

        # After colonize (1 tick), we have 1 move left in turn 1
        # So segment to (3,0) should be turn 1
        if len(segments) > 2:
            assert segments[2].turn == 1

    def test_stellerate_star_shows_multi_tick_delay(self):
        """MOVE -> STELLERATE_STAR(action_time=5) shows 5 tick delay.

        With speed=2 (2 moves per turn):
        - Turn 0: 2 movement steps to reach target
        - STELLERATE_STAR takes 5 ticks = 2.5 turns worth of ticks
        - Next movement should start in turn 3 (turn 0 movement + 5 ticks)
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )

        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        fleet.orders = [
            FleetOrder(OrderType.MOVE, HexCoord(2, 0)),
            FleetOrder(OrderType.STELLERATE_STAR, None),
            FleetOrder(OrderType.MOVE, HexCoord(4, 0)),
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            mock_find_path.return_value = [HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0)]

            with patch(
                'game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time'
            ) as mock_action_time:
                # STELLERATE_STAR takes 5 ticks
                mock_action_time.return_value = 5

                segments = service.project_path(
                    fleet, mock_galaxy, max_turns=10, component_registry={}
                )

        # First 2 moves in turn 0
        assert segments[0].turn == 0
        assert segments[1].turn == 0

        # After 5 ticks of stellerate:
        # - Turn 0 complete (used 2 movement + 0 from stellerate)
        # - Turn 1: stellerate uses 2 ticks (3 remaining)
        # - Turn 2: stellerate uses 2 ticks (1 remaining)
        # - Turn 3: stellerate uses 1 tick (done), 1 move available
        # So segment[2] should be turn 3
        if len(segments) > 2:
            assert segments[2].turn == 3, f"Expected turn 3, got {segments[2].turn}"

    def test_in_progress_action_shows_remaining_ticks(self):
        """In-progress action (execution_progress=2, action_time=5) shows 3 remaining ticks.

        If colonize is already 2 ticks in, only 3 more ticks needed.
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(5, 5),  # Already at target
            speed=2.0
        )

        # Action already in progress with 2 ticks done
        colonize_order = FleetOrder(OrderType.COLONIZE, MagicMock())
        colonize_order.execution_progress = 2

        fleet.path = []
        fleet.orders = [
            colonize_order,
            FleetOrder(OrderType.MOVE, HexCoord(7, 5)),
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            mock_find_path.return_value = [HexCoord(5, 5), HexCoord(6, 5), HexCoord(7, 5)]

            with patch(
                'game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time'
            ) as mock_action_time:
                # Full action time is 5
                mock_action_time.return_value = 5

                segments = service.project_path(
                    fleet, mock_galaxy, max_turns=10, component_registry={}
                )

        # With 3 remaining ticks (5-2):
        # - Turn 0: 2 ticks consumed (1 tick left)
        # - Turn 1: 1 tick consumed (action done), 1 move available -> segment[0]
        # - Turn 1: 2nd move available -> segment[1]
        if len(segments) >= 1:
            # First movement should be turn 1 (after 3 ticks consumed)
            assert segments[0].turn == 1, f"Expected turn 1, got {segments[0].turn}"

    def test_instant_action_no_delay(self):
        """Action with action_time=0 or movement order causes no delay."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )

        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        fleet.orders = [
            FleetOrder(OrderType.MOVE, HexCoord(2, 0)),
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, MagicMock(), max_turns=5)

        # All movements should be turn 0
        assert all(seg.turn == 0 for seg in segments)


class TestProjectPathActionTimingEdgeCases:
    """Edge case tests for action timing in path projection."""

    def test_multiple_actions_accumulate_delay(self):
        """Multiple action orders accumulate their delays."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )

        # Two action orders before movement
        fleet.path = []
        fleet.orders = [
            FleetOrder(OrderType.TRANSFER, {'direction': 'load'}),  # 1 tick
            FleetOrder(OrderType.COLONIZE, MagicMock()),  # 1 tick
            FleetOrder(OrderType.MOVE, HexCoord(2, 0)),
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            mock_find_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            with patch(
                'game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time'
            ) as mock_action_time:
                # Both actions take 1 tick each = 2 ticks total
                mock_action_time.return_value = 1

                segments = service.project_path(
                    fleet, mock_galaxy, max_turns=10, component_registry={}
                )

        # After 2 ticks of action (1+1), fleet has 0 moves left in turn 0
        # Turn 1 starts fresh with 2 moves
        if len(segments) >= 1:
            assert segments[0].turn == 1, f"Expected turn 1, got {segments[0].turn}"

    def test_action_timing_respects_max_turns(self):
        """Long action doesn't project beyond max_turns."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=1.0  # 1 move per turn
        )

        fleet.path = []
        fleet.orders = [
            FleetOrder(OrderType.STELLERATE_STAR, None),  # Very long action
            FleetOrder(OrderType.MOVE, HexCoord(2, 0)),
        ]
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            mock_find_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

            with patch(
                'game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time'
            ) as mock_action_time:
                # Very long action (100 ticks)
                mock_action_time.return_value = 100

                # Only project 5 turns
                segments = service.project_path(
                    fleet, mock_galaxy, max_turns=5, component_registry={}
                )

        # Should return empty or partial since action exceeds max_turns
        # (100 ticks at speed 1 = 100 turns, way past max_turns=5)
        assert len(segments) == 0 or all(seg.turn < 5 for seg in segments)


class TestProjectPathWarpOrders:
    """Tests for WARP order type in path projection (TC-003)."""

    def test_warp_order_projects_via_compute_path_for_warp(self):
        """TC-003: WARP order projection uses compute_path_for_warp.

        Verifies that when a WARP order is present, the projection:
        1. Computes path to warp point
        2. Appends exit hex after warp transit
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Fleet at (0, 0) with WARP order to warp point at (3, 0)
        fleet = Fleet(
            fleet_id='warp_test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        warp_point_hex = HexCoord(3, 0)
        exit_hex = HexCoord(100, 0)  # Exit on other side of warp

        fleet.orders = [FleetOrder(OrderType.WARP, warp_point_hex)]
        fleet.path = []
        fleet.can_use_warp = MagicMock(return_value=True)

        # Setup mock galaxy with warp point
        mock_galaxy = MagicMock()
        mock_system = MagicMock()
        mock_system.global_location = HexCoord(0, 0)
        mock_warp_point = MagicMock()
        mock_warp_point.location = warp_point_hex
        mock_warp_point.destination_id = 'DestSystem'
        mock_system.warp_points = [mock_warp_point]
        mock_system.name = 'SourceSystem'

        mock_dest_system = MagicMock()
        mock_dest_system.global_location = HexCoord(97, 0)
        mock_dest_wp = MagicMock()
        mock_dest_wp.location = HexCoord(3, 0)  # Local offset
        mock_dest_wp.destination_id = 'SourceSystem'
        mock_dest_system.warp_points = [mock_dest_wp]
        mock_dest_system.name = 'DestSystem'

        mock_galaxy._global_hex_warp_points = {warp_point_hex: mock_system}
        mock_galaxy.get_system_by_name = MagicMock(return_value=mock_dest_system)

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path'
        ) as mock_find_path:
            # Path to warp point
            mock_find_path.return_value = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]

            segments = service.project_path(fleet, mock_galaxy, max_turns=5)

        # Should have projected path to warp point + exit hex
        assert len(segments) >= 3, f"Expected at least 3 segments, got {len(segments)}"

        # Final segment should be warp jump (distance > 1)
        warp_segments = [s for s in segments if s.is_warp]
        assert len(warp_segments) >= 1, "Expected at least one warp segment"

    def test_warp_order_at_warp_point_projects_exit(self):
        """TC-003b: WARP order when already at warp point projects exit hex."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        warp_point_hex = HexCoord(5, 5)
        exit_hex = HexCoord(105, 5)

        fleet = Fleet(
            fleet_id='warp_at_point',
            owner_id=0,
            location=warp_point_hex,  # Already at warp point
            speed=5.0
        )
        fleet.orders = [FleetOrder(OrderType.WARP, warp_point_hex)]
        fleet.path = []
        fleet.can_use_warp = MagicMock(return_value=True)

        # Mock galaxy with warp connection
        mock_galaxy = MagicMock()
        mock_system = MagicMock()
        mock_system.global_location = HexCoord(5, 0)
        mock_wp = MagicMock()
        mock_wp.location = HexCoord(0, 5)  # Local offset = (5,5) - (5,0)
        mock_wp.destination_id = 'DestSystem'
        mock_system.warp_points = [mock_wp]
        mock_system.name = 'SourceSystem'

        mock_dest = MagicMock()
        mock_dest.global_location = HexCoord(100, 5)
        mock_dest_wp = MagicMock()
        mock_dest_wp.location = HexCoord(5, 0)
        mock_dest_wp.destination_id = 'SourceSystem'
        mock_dest.warp_points = [mock_dest_wp]

        mock_galaxy._global_hex_warp_points = {warp_point_hex: mock_system}
        mock_galaxy.get_system_by_name = MagicMock(return_value=mock_dest)

        segments = service.project_path(fleet, mock_galaxy, max_turns=5)

        # Should project single warp transit
        assert len(segments) >= 1
        # First segment is warp (distance > 1)
        assert segments[0].is_warp, "Expected warp jump segment"


class TestProjectPathPathfindingFailure:
    """Tests for graceful handling when pathfinding fails mid-projection (TC-008)."""

    def test_pathfinding_failure_stops_projection_gracefully(self):
        """TC-008: When find_hybrid_path returns None for second order, projection stops cleanly.

        Scenario: Fleet has two MOVE orders. First completes, but second has no valid path.
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='path_fail_test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )

        first_dest = HexCoord(2, 0)
        second_dest = HexCoord(10, 0)  # Unreachable

        fleet.orders = [
            FleetOrder(OrderType.MOVE, first_dest),
            FleetOrder(OrderType.MOVE, second_dest),
        ]
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # Pre-computed for first order
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        call_count = 0

        def mock_find_path_selective(galaxy, start, end, fleet=None):
            nonlocal call_count
            call_count += 1
            if end == second_dest:
                return None  # No path to second destination
            return [start, HexCoord(3, 0), HexCoord(4, 0)]  # Dummy path

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path',
            side_effect=mock_find_path_selective
        ):
            segments = service.project_path(fleet, mock_galaxy, max_turns=10)

        # Should project first order's path but stop when second fails
        assert len(segments) == 2, f"Expected 2 segments (first order only), got {len(segments)}"
        assert segments[-1].end == first_dest, "Last segment should be first destination"

    def test_first_order_pathfinding_failure_returns_empty(self):
        """TC-008b: When first order has no path, projection returns empty."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='first_fail',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )

        unreachable = HexCoord(100, 100)
        fleet.orders = [FleetOrder(OrderType.MOVE, unreachable)]
        fleet.path = []  # No pre-computed path
        fleet.can_use_warp = MagicMock(return_value=False)

        mock_galaxy = MagicMock()
        mock_galaxy._global_hex_warp_points = {}

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path',
            return_value=None
        ):
            segments = service.project_path(fleet, mock_galaxy, max_turns=10)

        assert len(segments) == 0, "Expected empty segments when no path exists"


class TestConsumeTicksHelper:
    """Unit tests for FleetNavigationService._consume_ticks helper."""

    def test_consume_within_same_turn(self):
        """Consuming ticks that fit within current turn."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        # 3 moves left, consume 2 ticks -> 1 move left, same turn
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=3, current_turn=0, moves_per_turn=5, max_turns=10, ticks=2
        )
        assert moves_left == 1
        assert turn == 0

    def test_consume_exact_turn_boundary(self):
        """Consuming exactly the remaining ticks crosses to next turn."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        # 2 moves left, consume 2 ticks -> turn advances, moves reset
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=2, current_turn=0, moves_per_turn=5, max_turns=10, ticks=2
        )
        assert moves_left == 5  # Reset to full
        assert turn == 1  # Advanced

    def test_consume_multi_turn(self):
        """Consuming multiple turns worth of ticks."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        # 2 moves left, consume 12 ticks with 5 per turn:
        # Turn 0: 2 consumed, 10 left, advance to turn 1
        # Turn 1: 5 consumed, 5 left, advance to turn 2
        # Turn 2: 5 consumed, 0 left, advance to turn 3
        # Result: 5 moves left (reset), turn 3
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=2, current_turn=0, moves_per_turn=5, max_turns=10, ticks=12
        )
        assert turn == 3
        assert moves_left == 5  # Full turn available

    def test_consume_respects_max_turns(self):
        """Tick consumption stops at max_turns."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        # 1 move left, try to consume 100 ticks, but max_turns=3
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=1, current_turn=0, moves_per_turn=5, max_turns=3, ticks=100
        )
        # Should stop at turn 3
        assert turn == 3

    def test_consume_zero_ticks(self):
        """Consuming zero ticks has no effect."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=3, current_turn=2, moves_per_turn=5, max_turns=10, ticks=0
        )
        assert moves_left == 3
        assert turn == 2

    def test_consume_single_movement_tick(self):
        """Single movement tick (normal move step)."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        # 2 moves left, consume 1 tick
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=2, current_turn=0, moves_per_turn=2, max_turns=10, ticks=1
        )
        assert moves_left == 1
        assert turn == 0

        # 1 move left, consume 1 tick -> advance turn
        moves_left, turn = FleetNavigationService._consume_ticks(
            moves_left=1, current_turn=0, moves_per_turn=2, max_turns=10, ticks=1
        )
        assert moves_left == 2  # Reset
        assert turn == 1
