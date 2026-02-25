"""
FleetNavigationService - Single source of truth for fleet navigation logic.

This service consolidates navigation logic to ensure UI path projection
always matches actual turn execution.

Key design decisions:
- NavigationState is immutable (frozen dataclass) for pure function calculations
- Core methods are stateless/pure (no side effects)
- Mutation bridge (calculate_fleet_next_hex) wraps pure functions for FleetMovementEngine

Architecture:
- Core (stateless, pure):
  - get_destination(state, order, galaxy) → HexCoord?
  - compute_path(state, destination, galaxy) → [HexCoord]
  - compute_next_step(state, galaxy) → NavigationStep
- Projection (for UI):
  - project_path(fleet, galaxy, max_turns) → [PathSegment]
  - project_path_as_dicts(fleet, galaxy) → [dict]
- Execution (for TurnEngine):
  - calculate_fleet_next_hex(fleet, galaxy) → HexCoord?

PROJ-187: Path projection accounts for action_time on non-movement orders.
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import (
    Fleet, FleetOrder, OrderType,
    MOVEMENT_ORDER_TYPES, ACTION_ORDER_TYPES,
)
from game.strategy.data.pathfinding import find_hybrid_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NavigationState:
    """
    Immutable snapshot of fleet state for navigation calculations.

    This replaces FleetState from fleet_movement.py with added can_warp field
    to eliminate the fake fleet object hack in intercept calculation.
    """
    location: HexCoord
    path: tuple  # tuple[HexCoord, ...] - immutable
    orders: tuple  # tuple[FleetOrder, ...] - immutable
    speed: float
    can_warp: bool

    @classmethod
    def from_fleet(cls, fleet: Fleet) -> 'NavigationState':
        """
        Create an immutable NavigationState snapshot from a mutable Fleet.

        Args:
            fleet: The Fleet object to snapshot

        Returns:
            NavigationState with all navigation-relevant data copied
        """
        return cls(
            location=fleet.location,
            path=tuple(fleet.path),
            orders=tuple(fleet.orders),
            speed=fleet.speed,
            can_warp=fleet.can_use_warp()
        )


@dataclass(frozen=True)
class PathSegment:
    """
    Represents one step in a projected path.

    Moved from fleet_movement.py to consolidate in the unified service.
    """
    start: HexCoord
    end: HexCoord
    turn: int
    is_warp: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization.

        Note: The 'hex' field duplicates 'end' for consistency with internal
        path projection code in pathfinding.py that accesses pt['hex'].
        This is not external backward compatibility - it's internal API consistency.
        """
        return {
            'start': self.start,
            'end': self.end,
            'turn': self.turn,
            'is_warp': self.is_warp,
            'hex': self.end  # Alias for 'end', used by pathfinding.py intercept calculation
        }


@dataclass(frozen=True)
class NavigationStep:
    """
    Result of computing the next navigation step.

    Contains the next hex to move to (or None), the new state after the move,
    and whether the current order is complete.
    """
    next_hex: Optional[HexCoord]
    new_state: 'NavigationState'
    order_complete: bool = False


class FleetNavigationService:
    """
    Unified service for all fleet navigation calculations.

    Provides:
    1. Pure functions for calculating destinations, paths, and next steps
    2. UI projection methods for path visualization
    3. Execution wrapper for turn processing (mutation bridge)

    This is the single source of truth - both UI projection and turn
    execution use the same logic through this service.
    """

    def get_destination(
        self,
        state: NavigationState,
        order: FleetOrder,
        galaxy
    ) -> Optional[HexCoord]:
        """
        Determine the destination hex for a given order.

        Args:
            state: Current navigation state (immutable snapshot)
            order: The order to process
            galaxy: Galaxy object for pathfinding context

        Returns:
            HexCoord destination or None if order has no movement component
        """
        if order.type == OrderType.MOVE:
            return order.target
        elif order.type == OrderType.WARP:
            # PROJ-187: WARP order target is the warp point hex to enter
            return order.target
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            # Fleet always has location, just check target exists
            if target_fleet is None:
                return None
            # Use intercept calculation with NavigationState directly
            # (PROJ-35 Phase 3: calculate_intercept_point now accepts NavigationState)
            from game.strategy.data.pathfinding import calculate_intercept_point
            return calculate_intercept_point(state, target_fleet, galaxy)
        else:
            # COLONIZE, JOIN_FLEET etc. have no movement component
            return None

    def compute_path(
        self,
        state: NavigationState,
        destination: HexCoord,
        galaxy
    ) -> list:
        """
        Calculate path from current location to destination.

        Args:
            state: Current navigation state
            destination: Target hex
            galaxy: Galaxy object for pathfinding

        Returns:
            List of HexCoords representing the path (excluding start if it matches location)
        """
        if state.location == destination:
            return []

        # Use find_hybrid_path for pathfinding
        # Create minimal fleet-like object for warp capability check
        can_warp_value = state.can_warp
        fleet_like = type('Fleet', (), {
            'id': -1,  # Projection context, no real fleet ID
            'can_use_warp': lambda self: can_warp_value
        })()

        path = find_hybrid_path(galaxy, state.location, destination, fleet=fleet_like)

        if not path:
            return []

        # Remove start hex if it matches current location
        if path and path[0] == state.location:
            path = path[1:]

        return path if path else []

    def _needs_path_recalculation(
        self,
        state: NavigationState,
        destination: HexCoord
    ) -> bool:
        """
        Check if path needs to be recalculated.

        Args:
            state: Current navigation state
            destination: Target destination

        Returns:
            True if path needs recalculation, False otherwise
        """
        if not state.path:
            return True
        return state.path[-1] != destination

    def compute_path_for_warp(
        self,
        state: NavigationState,
        warp_point_hex: HexCoord,
        galaxy
    ) -> list:
        """
        Compute path for explicit WARP order.

        PROJ-187: Calculates path to warp point, then appends the exit hex
        on the other side of the warp connection.

        Args:
            state: Current navigation state
            warp_point_hex: The global hex of the warp point to enter
            galaxy: Galaxy object with warp point index

        Returns:
            List of HexCoords: path to warp point + exit hex after transit
        """
        path = []

        # 1. If not at warp point, compute path to it
        if state.location != warp_point_hex:
            path_to_wp = find_hybrid_path(galaxy, state.location, warp_point_hex)
            if path_to_wp:
                # Remove start if matches current location
                if path_to_wp and path_to_wp[0] == state.location:
                    path_to_wp = path_to_wp[1:]
                path.extend(path_to_wp)

        # 2. Look up warp point and resolve exit hex
        exit_hex = self._resolve_warp_exit(warp_point_hex, galaxy)
        if exit_hex:
            path.append(exit_hex)

        return path

    def _resolve_warp_exit(
        self,
        warp_point_hex: HexCoord,
        galaxy
    ) -> Optional[HexCoord]:
        """
        Resolve the exit hex for a warp point.

        Args:
            warp_point_hex: Global hex of the warp point entry
            galaxy: Galaxy with warp point index

        Returns:
            Global HexCoord of the exit warp point, or None if not found
        """
        # Look up source system from warp point index
        source_system = galaxy._global_hex_warp_points.get(warp_point_hex)
        if not source_system:
            logger.warning(f"No warp point found at {warp_point_hex}")
            return None

        # Find the warp point at this hex within the system
        local_offset = warp_point_hex - source_system.global_location
        source_wp = None
        for wp in source_system.warp_points:
            if wp.location == local_offset:
                source_wp = wp
                break

        if not source_wp:
            logger.warning(f"Warp point not found at local offset {local_offset} in {source_system.name}")
            return None

        # Get destination system
        dest_system = galaxy.get_system_by_name(source_wp.destination_id)
        if not dest_system:
            logger.warning(f"Destination system '{source_wp.destination_id}' not found")
            return None

        # Find reciprocal warp point in destination system
        for wp in dest_system.warp_points:
            if wp.destination_id == source_system.name:
                exit_hex = dest_system.global_location + wp.location
                return exit_hex

        # Fallback: use destination system center
        logger.warning(f"No reciprocal warp point found, using system center")
        return dest_system.global_location

    def compute_next_step(
        self,
        state: NavigationState,
        galaxy
    ) -> NavigationStep:
        """
        Calculate the next hex for movement without mutating the input state.

        This is a pure function: given a state, it returns the next hex to move to
        and a new state reflecting that movement.

        Args:
            state: Current navigation state (immutable)
            galaxy: Galaxy object for pathfinding

        Returns:
            NavigationStep with next_hex, new_state, and order_complete flag
        """
        if not state.orders:
            return NavigationStep(next_hex=None, new_state=state, order_complete=False)

        order = state.orders[0]
        destination = self.get_destination(state, order, galaxy)

        if destination is None:
            # Non-movement order (COLONIZE, JOIN_FLEET, etc.) - leave it for
            # other processors to handle. Don't pop it here.
            return NavigationStep(next_hex=None, new_state=state, order_complete=False)

        # Check if we need to recalculate path
        current_path = list(state.path)
        if self._needs_path_recalculation(state, destination):
            current_path = []  # Force recalc

        # Calculate path if needed
        if not current_path:
            # PROJ-187: Special handling for WARP orders at warp point
            if order.type == OrderType.WARP and state.location == destination:
                # Fleet is at warp point - resolve exit and execute warp
                exit_hex = self._resolve_warp_exit(destination, galaxy)
                if exit_hex:
                    # Warp transit: move directly to exit hex
                    new_orders = state.orders[1:]
                    new_state = NavigationState(
                        location=exit_hex,
                        path=(),
                        orders=new_orders,
                        speed=state.speed,
                        can_warp=state.can_warp
                    )
                    return NavigationStep(
                        next_hex=exit_hex,
                        new_state=new_state,
                        order_complete=True
                    )
                else:
                    # Warp point invalid - order fails
                    return NavigationStep(next_hex=None, new_state=state, order_complete=False)

            if state.location == destination:
                # Already at destination, complete order
                new_orders = state.orders[1:]
                new_state = NavigationState(
                    location=state.location,
                    path=(),
                    orders=new_orders,
                    speed=state.speed,
                    can_warp=state.can_warp
                )
                return NavigationStep(next_hex=None, new_state=new_state, order_complete=True)

            # PROJ-187: Use specialized path for WARP orders
            if order.type == OrderType.WARP:
                current_path = self.compute_path_for_warp(state, destination, galaxy)
            else:
                current_path = self.compute_path(state, destination, galaxy)

            if not current_path:
                # No path found, cannot move
                return NavigationStep(next_hex=None, new_state=state, order_complete=False)

        # Pop next hex from path
        if current_path:
            next_hex = current_path[0]
            remaining_path = tuple(current_path[1:])

            # Check if order completes after this move
            order_complete = len(remaining_path) == 0
            if order_complete:
                new_orders = state.orders[1:]
            else:
                new_orders = state.orders

            new_state = NavigationState(
                location=next_hex,
                path=remaining_path,
                orders=new_orders,
                speed=state.speed,
                can_warp=state.can_warp
            )
            return NavigationStep(
                next_hex=next_hex,
                new_state=new_state,
                order_complete=order_complete
            )

        return NavigationStep(next_hex=None, new_state=state, order_complete=False)

    def project_path(
        self,
        fleet: Fleet,
        galaxy,
        max_turns: int = 10,
        component_registry=None
    ) -> list:
        """
        Project fleet movement over multiple turns.

        Simulates future movement based on current orders and speed,
        returning a list of path segments for UI visualization.

        PROJ-187: Accounts for action_time on non-movement orders. When
        an action order is encountered, the projection consumes the
        appropriate number of ticks before advancing to the next order.

        Args:
            fleet: The fleet to project
            galaxy: Galaxy object for pathfinding
            max_turns: Maximum turns to project
            component_registry: Optional component registry for action_time lookup

        Returns:
            List of PathSegment objects
        """
        segments = []
        state = NavigationState.from_fleet(fleet)

        moves_per_turn = int(state.speed)
        if moves_per_turn <= 0:
            return segments

        moves_left_in_turn = moves_per_turn
        current_turn = 0

        # Track execution progress for first order (if any)
        # This is needed to account for partial progress on current action
        # FleetOrder always has execution_progress (default 0)
        first_order_progress = fleet.orders[0].execution_progress if fleet.orders else 0
        is_first_order = True

        # Safety limit to prevent infinite loops
        max_steps = max_turns * moves_per_turn + 100
        iterations = 0

        while (state.path or state.orders) and current_turn < max_turns:
            iterations += 1
            if iterations > max_steps:
                logger.warning("project_path exceeded max iterations")
                break

            # If no path but have orders, handle current order
            if not state.path and state.orders:
                order = state.orders[0]

                # PROJ-187: Handle action orders (non-movement)
                if order.type not in MOVEMENT_ORDER_TYPES:
                    # Calculate action_time for this order
                    action_time = self._get_action_time_for_projection(
                        fleet, order, component_registry
                    )

                    # Account for existing execution_progress on first order
                    if is_first_order and first_order_progress > 0:
                        action_time = max(0, action_time - first_order_progress)

                    # Consume action_time ticks
                    while action_time > 0 and current_turn < max_turns:
                        ticks_to_consume = min(action_time, moves_left_in_turn)
                        action_time -= ticks_to_consume
                        moves_left_in_turn -= ticks_to_consume

                        if moves_left_in_turn <= 0:
                            current_turn += 1
                            moves_left_in_turn = moves_per_turn

                    # Advance to next order
                    state = NavigationState(
                        location=state.location,
                        path=(),
                        orders=state.orders[1:],
                        speed=state.speed,
                        can_warp=state.can_warp
                    )
                    is_first_order = False
                    continue

                destination = self.get_destination(state, order, galaxy)
                if destination is None:
                    break

                # PROJ-187: Use specialized path for WARP orders
                if order.type == OrderType.WARP:
                    new_path = self.compute_path_for_warp(state, destination, galaxy)
                else:
                    new_path = self.compute_path(state, destination, galaxy)
                if not new_path:
                    break

                state = NavigationState(
                    location=state.location,
                    path=tuple(new_path),
                    orders=state.orders,
                    speed=state.speed,
                    can_warp=state.can_warp
                )
                is_first_order = False

            if not state.path:
                break

            # Execute one step
            start_hex = state.location
            next_hex = state.path[0]
            remaining_path = state.path[1:]

            # Detect warp jump (distance > 1)
            is_warp = hex_distance(start_hex, next_hex) > 1

            segment = PathSegment(
                start=start_hex,
                end=next_hex,
                turn=current_turn,
                is_warp=is_warp
            )
            segments.append(segment)

            # Update state
            if not remaining_path:
                # Order complete
                new_orders = state.orders[1:] if state.orders else ()
            else:
                new_orders = state.orders

            state = NavigationState(
                location=next_hex,
                path=remaining_path,
                orders=new_orders,
                speed=state.speed,
                can_warp=state.can_warp
            )

            # Movement cost
            moves_left_in_turn -= 1
            if moves_left_in_turn <= 0:
                current_turn += 1
                moves_left_in_turn = moves_per_turn

        return segments

    def _get_action_time_for_projection(
        self,
        fleet: Fleet,
        order: FleetOrder,
        component_registry
    ) -> int:
        """
        Get action_time for an order during path projection.

        PROJ-187: Uses ActionTimeResolver to look up action_time from abilities.

        Args:
            fleet: The fleet executing the order
            order: The order to get action_time for
            component_registry: Component registry for ability lookup

        Returns:
            Integer action_time (ticks), defaults to 1 for unknown orders
        """
        from game.strategy.services.action_time_resolver import ActionTimeResolver
        return ActionTimeResolver.resolve_action_time(fleet, order, component_registry)

    def project_path_as_dicts(
        self,
        fleet: Fleet,
        galaxy,
        max_turns: int = 10,
        component_registry=None
    ) -> list:
        """
        Project fleet path and return as list of dicts for backward compatibility.

        This is a wrapper around project_path() that converts PathSegments to dicts.

        Args:
            fleet: The fleet to project
            galaxy: Galaxy object for pathfinding
            max_turns: Maximum turns to project
            component_registry: Optional component registry for action_time lookup

        Returns:
            List of dicts with path segment data
        """
        segments = self.project_path(fleet, galaxy, max_turns, component_registry)
        return [seg.to_dict() for seg in segments]

    def calculate_fleet_next_hex(
        self,
        fleet: Fleet,
        galaxy
    ) -> Optional[HexCoord]:
        """
        Calculate next hex for fleet, applying state changes to mutable Fleet.

        This is the "mutation bridge" - it wraps the pure compute_next_step()
        function and applies the necessary mutations to the Fleet object.
        Used by FleetMovementEngine for turn execution.

        Args:
            fleet: The mutable Fleet object
            galaxy: Galaxy object for pathfinding

        Returns:
            Next hex coordinate to move to, or None if no movement
        """
        # Handle invalid MOVE_TO_FLEET orders (target is None)
        # Fleet always has location, just check target exists
        # This must be checked before compute_next_step since it needs to pop the order
        order = fleet.get_current_order()
        if order and order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if target_fleet is None:
                logger.warning("FleetNavigationService: Target fleet invalid. Order cancelled.")
                fleet.pop_order()
                return None

        state = NavigationState.from_fleet(fleet)
        step = self.compute_next_step(state, galaxy)

        if step.next_hex is None:
            if step.order_complete:
                fleet.pop_order()
            return None

        # Apply state changes to mutable fleet
        fleet.path = list(step.new_state.path)
        if step.order_complete:
            fleet.pop_order()

        return step.next_hex
