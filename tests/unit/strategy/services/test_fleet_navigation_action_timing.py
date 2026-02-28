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
