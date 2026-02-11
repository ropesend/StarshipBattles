"""
FleetNavigationService - Single source of truth for fleet navigation logic.

PROJ-35: Unify Fleet Movement Logic

This service consolidates navigation logic from FleetMovementSimulator and
FleetMovementEngine to ensure UI path projection always matches actual turn execution.

Migration Guide (from deprecated FleetMovementSimulator)
--------------------------------------------------------
FleetMovementSimulator was deprecated in PROJ-35 and removed in PROJ-42.
Use FleetNavigationService instead:

Before (deprecated):
    from game.strategy.engine.fleet_movement import FleetMovementSimulator
    simulator = FleetMovementSimulator()
    path = simulator.project_path(fleet, galaxy)
    next_hex = simulator.calculate_next_hex(fleet, galaxy)

After (current):
    from game.strategy.services.fleet_navigation_service import FleetNavigationService
    nav_service = FleetNavigationService()
    path = nav_service.project_path(fleet, galaxy)
    next_hex = nav_service.calculate_fleet_next_hex(fleet, galaxy)

API Mapping:
    | Old (FleetMovementSimulator)   | New (FleetNavigationService)        | Notes                    |
    |--------------------------------|-------------------------------------|--------------------------|
    | project_path()                 | project_path()                      | Same signature           |
    | calculate_path()               | compute_path()                      | Uses NavigationState     |
    | calculate_next_hex()           | calculate_fleet_next_hex()          | Same behavior            |
    | FleetState                     | NavigationState                     | Immutable (frozen)       |

Key Differences:
- NavigationState is immutable (frozen dataclass) - use NavigationState.from_fleet()
- NavigationState includes can_warp field - eliminates fake fleet object hack
- Methods are pure functions - no side effects on fleet object

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
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.pathfinding import find_hybrid_path
from game.core.logger import log_warning


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
            can_warp=fleet.can_use_warp() if hasattr(fleet, 'can_use_warp') else True
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
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
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
        max_turns: int = 10
    ) -> list:
        """
        Project fleet movement over multiple turns.

        Simulates future movement based on current orders and speed,
        returning a list of path segments for UI visualization.

        Args:
            fleet: The fleet to project
            galaxy: Galaxy object for pathfinding
            max_turns: Maximum turns to project

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

        # Safety limit to prevent infinite loops
        max_steps = max_turns * moves_per_turn + 100
        iterations = 0

        while (state.path or state.orders) and current_turn < max_turns:
            iterations += 1
            if iterations > max_steps:
                log_warning("project_path exceeded max iterations")
                break

            # If no path but have orders, generate path for current order
            if not state.path and state.orders:
                order = state.orders[0]

                if order.type not in (OrderType.MOVE, OrderType.MOVE_TO_FLEET):
                    # Skip non-movement orders
                    state = NavigationState(
                        location=state.location,
                        path=(),
                        orders=state.orders[1:],
                        speed=state.speed,
                        can_warp=state.can_warp
                    )
                    continue

                destination = self.get_destination(state, order, galaxy)
                if destination is None:
                    break

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

    def project_path_as_dicts(
        self,
        fleet: Fleet,
        galaxy,
        max_turns: int = 10
    ) -> list:
        """
        Project fleet path and return as list of dicts for backward compatibility.

        This is a wrapper around project_path() that converts PathSegments to dicts.

        Args:
            fleet: The fleet to project
            galaxy: Galaxy object for pathfinding
            max_turns: Maximum turns to project

        Returns:
            List of dicts with path segment data
        """
        segments = self.project_path(fleet, galaxy, max_turns)
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
        # Handle invalid MOVE_TO_FLEET orders (target is None or lacks location)
        # This must be checked before compute_next_step since it needs to pop the order
        order = fleet.get_current_order()
        if order and order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
                log_warning("FleetNavigationService: Target fleet invalid. Order cancelled.")
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
