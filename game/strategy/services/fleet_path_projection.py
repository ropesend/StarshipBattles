"""Fleet path-projection helpers.

PROJ-382 Phase 5: extracted from ``FleetNavigationService`` to bring the
parent module under the 500 LOC ceiling.  These functions implement the
multi-turn UI projection — the per-tick simulation loop that walks a
fleet's order list, consumes action time, and emits ``PathSegment``
items for the strategy renderer.

The functions take an explicit ``svc`` (FleetNavigationService) reference
because they call ``svc.get_destination`` / ``svc.compute_path`` /
``svc.compute_path_for_warp`` to resolve order paths.  They do not own
any state of their own.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import TYPE_CHECKING, Optional, Tuple

from game.core.hex_math import hex_distance
from game.strategy.data.fleet import (
    Fleet, OrderType, MOVEMENT_ORDER_TYPES,
)
from game.strategy.data.order_types import Order

if TYPE_CHECKING:
    from game.strategy.services.fleet_navigation_service import (
        FleetNavigationService, NavigationState, PathSegment,
    )


logger = logging.getLogger(__name__)


def project_path_inner(
    svc: "FleetNavigationService",
    fleet: Fleet,
    galaxy,
    max_turns: int,
    component_registry,
) -> list:
    """Inner projection loop — extracted from ``FleetNavigationService._project_path_inner``."""
    from game.strategy.services.fleet_navigation_service import (
        NavigationState, PathSegment,
    )

    segments: list = []
    state = NavigationState.from_fleet(fleet)

    moves_per_turn = int(state.speed)
    if moves_per_turn <= 0:
        return segments

    moves_left_in_turn = moves_per_turn
    current_turn = 0

    # Pre-adjust for execution_progress on first action order
    # This handles partial completion of in-progress actions
    initial_progress = fleet.orders[0].execution_progress if fleet.orders else 0

    # Safety limit to prevent infinite loops
    max_steps = max_turns * moves_per_turn + 100
    iterations = 0

    while (state.path or state.orders) and current_turn < max_turns:
        iterations += 1
        if iterations > max_steps:
            logger.warning("project_path exceeded max iterations")
            break

        # Handle current order if no path computed
        if not state.path and state.orders:
            order = state.orders[0]

            # Action orders: consume ticks and advance
            if order.type not in MOVEMENT_ORDER_TYPES:
                state, moves_left_in_turn, current_turn, initial_progress = (
                    project_action_order(
                        svc, state, order, fleet, component_registry,
                        moves_left_in_turn, current_turn, moves_per_turn,
                        max_turns, initial_progress,
                    )
                )
                continue

            # Movement orders: resolve path
            new_state = resolve_path_for_order(
                svc, state, order, galaxy, self_fleet=fleet,
            )
            if new_state is None:
                break
            state = new_state

        if not state.path:
            break

        # Execute one movement step
        start_hex = state.location
        next_hex = state.path[0]
        remaining_path = state.path[1:]
        is_warp = hex_distance(start_hex, next_hex) > 1

        segments.append(PathSegment(
            start=start_hex,
            end=next_hex,
            turn=current_turn,
            is_warp=is_warp,
        ))

        # Update state for next iteration
        new_orders = state.orders[1:] if not remaining_path and state.orders else state.orders
        state = replace(state, location=next_hex, path=remaining_path, orders=new_orders)

        # Consume movement tick
        moves_left_in_turn, current_turn = consume_ticks(
            moves_left_in_turn, current_turn, moves_per_turn, max_turns, 1,
        )

    return segments


def consume_ticks(
    moves_left: int,
    current_turn: int,
    moves_per_turn: int,
    max_turns: int,
    ticks: int,
) -> tuple:
    """Consume ticks and advance turns as needed (pure)."""
    while ticks > 0 and current_turn < max_turns:
        ticks_to_consume = min(ticks, moves_left)
        ticks -= ticks_to_consume
        moves_left -= ticks_to_consume

        if moves_left <= 0:
            current_turn += 1
            moves_left = moves_per_turn

    return (moves_left, current_turn)


def get_action_time_for_projection(
    fleet: Fleet,
    order: Order,
    component_registry,
) -> int:
    """PROJ-187: resolve action_time via ActionTimeResolver."""
    from game.strategy.services.action_time_resolver import ActionTimeResolver
    return ActionTimeResolver.resolve_action_time(fleet, order, component_registry)


def project_action_order(
    svc: "FleetNavigationService",
    state: "NavigationState",
    order: Order,
    fleet: Fleet,
    component_registry,
    moves_left: int,
    current_turn: int,
    moves_per_turn: int,
    max_turns: int,
    initial_progress: int,
) -> Tuple["NavigationState", int, int, int]:
    """Consume ticks for an action order and advance to next order."""
    action_time = get_action_time_for_projection(
        fleet, order, component_registry,
    )
    action_time = max(0, action_time - initial_progress)
    initial_progress = 0  # Only applies to first action order

    # Consume action_time ticks
    moves_left, current_turn = consume_ticks(
        moves_left, current_turn, moves_per_turn, max_turns, action_time,
    )

    # Advance to next order
    new_state = replace(state, path=(), orders=state.orders[1:])
    return (new_state, moves_left, current_turn, initial_progress)


def resolve_path_for_order(
    svc: "FleetNavigationService",
    state: "NavigationState",
    order: Order,
    galaxy,
    self_fleet=None,
) -> Optional["NavigationState"]:
    """Resolve destination + compute path for a movement order."""
    destination = svc.get_destination(state, order, galaxy, self_fleet=self_fleet)
    if destination is None:
        return None

    # Compute path based on order type
    if order.type == OrderType.WARP:
        new_path = svc.compute_path_for_warp(state, destination, galaxy)
    else:
        new_path = svc.compute_path(state, destination, galaxy)

    if not new_path:
        return None

    return replace(state, path=tuple(new_path))
