"""Gap-fill characterization tests for FleetNavigationService (PROJ-336).

Per Decision D-001, fleet_navigation already has 74 tests across
`tests/unit/strategy/fleet_navigation/`. This file pins ONLY behaviors
those existing tests do not cover:

- `_resolve_warp_exit` four outcome paths
- `_consume_ticks` pure static turn-boundary logic
- `project_path` re-entrancy guard
- `calculate_fleet_next_hex` invalid-MOVE_TO_FLEET early pop
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.fleet_navigation_service import (
    FleetNavigationService,
    NavigationState,
    _get_projection_stack,
)


class TestResolveWarpExit:
    """Pin all four outcome paths of `_resolve_warp_exit`."""

    def test_returns_none_when_warp_point_hex_not_in_index(self):
        service = FleetNavigationService()
        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {}  # nothing registered
        result = service._resolve_warp_exit(HexCoord(10, 5), galaxy)
        assert result is None

    def test_returns_none_when_local_warp_point_not_found_in_source_system(self):
        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)

        # Source system exists, but its `warp_points` list contains no entry
        # at the matching local offset.
        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.warp_points = []  # no matching local warp point
        source_system.name = "Source"

        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {warp_point_hex: source_system}

        result = service._resolve_warp_exit(warp_point_hex, galaxy)
        assert result is None

    def test_returns_none_when_destination_system_does_not_exist(self):
        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)

        wp = MagicMock()
        wp.location = HexCoord(0, 5)  # local offset matches warp_point_hex - global_location
        wp.destination_id = "Phantom"

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.warp_points = [wp]
        source_system.name = "Source"

        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {warp_point_hex: source_system}
        galaxy.get_system_by_name = MagicMock(return_value=None)

        result = service._resolve_warp_exit(warp_point_hex, galaxy)
        assert result is None

    def test_falls_back_to_destination_system_center_when_no_reciprocal_warp_point(self):
        service = FleetNavigationService()
        warp_point_hex = HexCoord(10, 5)

        wp = MagicMock()
        wp.location = HexCoord(0, 5)
        wp.destination_id = "Dest"

        source_system = MagicMock()
        source_system.global_location = HexCoord(10, 0)
        source_system.warp_points = [wp]
        source_system.name = "Source"

        # Destination system exists but has no warp point pointing back.
        dest_system = MagicMock()
        dest_system.global_location = HexCoord(50, 0)
        dest_system.name = "Dest"
        dest_system.warp_points = []  # no reciprocal

        galaxy = MagicMock()
        galaxy._global_hex_warp_points = {warp_point_hex: source_system}
        galaxy.get_system_by_name = MagicMock(return_value=dest_system)

        result = service._resolve_warp_exit(warp_point_hex, galaxy)
        # Fallback: destination system center.
        assert result == HexCoord(50, 0)


class TestConsumeTicks:
    """`_consume_ticks` is a pure staticmethod; pin its turn-boundary semantics."""

    def test_crosses_turn_boundary_when_moves_left_exhausted(self):
        # 1 move left, 5 moves/turn, 10-turn cap, consume 1 tick.
        # After consumption: moves_left -> 0 -> rolls into next turn,
        # moves_left resets to moves_per_turn (5), current_turn += 1.
        moves_left, current_turn = FleetNavigationService._consume_ticks(
            moves_left=1, current_turn=0, moves_per_turn=5,
            max_turns=10, ticks=1,
        )
        assert moves_left == 5
        assert current_turn == 1

    def test_stops_at_max_turns_even_with_remaining_ticks(self):
        # We're at the cap already — the while-loop condition
        # `current_turn < max_turns` is already false, so no ticks consume.
        moves_left, current_turn = FleetNavigationService._consume_ticks(
            moves_left=3, current_turn=10, moves_per_turn=5,
            max_turns=10, ticks=20,
        )
        assert current_turn == 10
        assert moves_left == 3  # untouched

    def test_consumes_partial_ticks_within_a_single_turn(self):
        # 5 moves/turn, consume 2 ticks → moves_left drops by 2 with no
        # turn rollover.
        moves_left, current_turn = FleetNavigationService._consume_ticks(
            moves_left=5, current_turn=0, moves_per_turn=5,
            max_turns=10, ticks=2,
        )
        assert moves_left == 3
        assert current_turn == 0


class TestProjectionGuard:
    def test_project_path_returns_empty_when_fleet_id_already_in_projection_guard(self):
        service = FleetNavigationService()
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        fleet.orders = [Order(OrderType.MOVE, HexCoord(5, 0))]

        stack = _get_projection_stack()
        stack.add(fleet.id)
        try:
            result = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)
            assert result == []
        finally:
            # Cleanup: never leak across tests.
            stack.discard(fleet.id)


class TestCalculateFleetNextHexInvalidTarget:
    def test_pops_invalid_move_to_fleet_target_before_compute(self):
        service = FleetNavigationService()
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        # MOVE_TO_FLEET with target=None — invalid; mutation bridge must
        # pop the order and return None without invoking compute_next_step.
        fleet.orders = [Order(OrderType.MOVE_TO_FLEET, target=None)]

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())
        assert result is None
        assert fleet.orders == []  # popped
