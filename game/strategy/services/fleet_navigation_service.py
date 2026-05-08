"""FleetNavigationService — single source of truth for fleet navigation
logic.  Path projection (UI) and turn execution share the same pure
core (``get_destination`` / ``compute_path`` / ``compute_next_step``);
the mutation bridge ``calculate_fleet_next_hex`` is the only stateful
hand-off to ``FleetMovementEngine``.

PROJ-382 Phase 5: warp resolution and multi-turn projection helpers
moved to ``fleet_warp_resolution.py`` and ``fleet_path_projection.py``;
this module now coordinates the destination + per-step pure-function
core only.  PROJ-187: action_time-aware projection lives in the
projection helper.
"""
import logging
import threading
from dataclasses import dataclass, replace
from typing import Any, Dict, Optional, Tuple

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import (
    Fleet, OrderType,
    MOVEMENT_ORDER_TYPES, ACTION_ORDER_TYPES,
)
from game.strategy.data.order_types import Order
from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex

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
    orders: tuple  # tuple[Order, ...] - immutable
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
            can_warp=fleet.capabilities.can_use_warp()
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


# Per-thread set of fleet IDs currently being projected.
# Guards against cyclic MOVE_TO_FLEET orders (A intercepts B, B intercepts A,
# or longer chains) that would otherwise infinite-recurse through
# project_path -> get_destination -> calculate_intercept_point ->
# project_fleet_path -> project_path.
_projection_guard = threading.local()


def _get_projection_stack() -> set:
    stack = getattr(_projection_guard, "fleet_ids", None)
    if stack is None:
        stack = set()
        _projection_guard.fleet_ids = stack
    return stack


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

    def _is_mutual_pursuit(self, self_fleet, target_fleet) -> bool:
        """FEAT-28: Mutual-pursuit predicate.

        Returns True iff `target_fleet`'s current head order is
        `MOVE_TO_FLEET` or `JOIN_FLEET` and points back at `self_fleet`.
        The order queue is canonical; the pursuer tracker is a derived
        index that can lag, so we read the head order directly.
        """
        if self_fleet is None or target_fleet is None:
            return False
        target_order = target_fleet.get_current_order()
        if target_order is None:
            return False
        if target_order.type not in (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET):
            return False
        return target_order.target is self_fleet

    def get_destination(
        self,
        state: NavigationState,
        order: Order,
        galaxy,
        self_fleet=None,
    ) -> Optional[HexCoord]:
        """Destination hex for ``order``, or None if non-movement.

        ``self_fleet`` (optional) is required for FEAT-28 mutual-pursuit
        detection on MOVE_TO_FLEET; pass None when projecting a synthesised
        state without a Fleet identity.
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
            # FEAT-28: When two fleets are mutually pursuing each other (each
            # head order is MOVE_TO_FLEET / JOIN_FLEET targeting the other),
            # `calculate_intercept_point` is asymmetric — its evaluator
            # ranks "stay still" as the best intercept (chaser_turns=0 at
            # chaser's own location), so one fleet sits while the other
            # chases. Bypass intercept and pathfind directly to the target's
            # current hex; both fleets converge along the shortest line at
            # their own speeds.
            if self._is_mutual_pursuit(self_fleet, target_fleet):
                return target_fleet.location
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

        # PROJ-239: Pass can_warp directly instead of constructing a fake fleet object
        path = find_hybrid_path(galaxy, state.location, destination, can_warp=state.can_warp)

        if not path:
            return []

        # PROJ-204: Remove start hex if it matches current location
        stripped = strip_start_hex(state.location, path)
        return stripped if stripped else []

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
        galaxy,
    ) -> list:
        """Delegate to ``fleet_warp_resolution.compute_path_for_warp``
        (PROJ-382 Phase 5 extraction)."""
        from game.strategy.services import fleet_warp_resolution as _warp
        return _warp.compute_path_for_warp(state, warp_point_hex, galaxy)

    def _resolve_warp_exit(
        self,
        warp_point_hex: HexCoord,
        galaxy,
    ) -> Optional[HexCoord]:
        """Delegate to ``fleet_warp_resolution.resolve_warp_exit`` (PROJ-382)."""
        from game.strategy.services import fleet_warp_resolution as _warp
        return _warp.resolve_warp_exit(warp_point_hex, galaxy)

    def compute_next_step(
        self,
        state: NavigationState,
        galaxy,
        self_fleet=None,
    ) -> NavigationStep:
        """
        Calculate the next hex for movement without mutating the input state.

        This is a pure function: given a state, it returns the next hex to move to
        and a new state reflecting that movement.

        Args:
            state: Current navigation state (immutable)
            galaxy: Galaxy object for pathfinding
            self_fleet: Optional Fleet — passed through to `get_destination`
                for FEAT-28 mutual-pursuit detection on MOVE_TO_FLEET orders.

        Returns:
            NavigationStep with next_hex, new_state, and order_complete flag
        """
        if not state.orders:
            return NavigationStep(next_hex=None, new_state=state, order_complete=False)

        order = state.orders[0]
        destination = self.get_destination(state, order, galaxy, self_fleet=self_fleet)

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
                    new_state = replace(
                        state, location=exit_hex, path=(), orders=state.orders[1:]
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
                new_state = replace(state, path=(), orders=state.orders[1:])
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
            order_complete = len(remaining_path) == 0
            new_orders = state.orders[1:] if order_complete else state.orders
            new_state = replace(
                state, location=next_hex, path=remaining_path, orders=new_orders
            )
            return NavigationStep(
                next_hex=next_hex, new_state=new_state, order_complete=order_complete
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
        # Re-entrancy guard: a fleet's projected path cannot recursively
        # depend on itself. If we're already projecting this fleet up the
        # call stack (mutual or chained MOVE_TO_FLEET intercepts), return
        # an empty path. calculate_intercept_point handles an empty target
        # path by chasing the target's current location.
        stack = _get_projection_stack()
        if fleet.id in stack:
            return []
        stack.add(fleet.id)
        try:
            return self._project_path_inner(fleet, galaxy, max_turns, component_registry)
        finally:
            stack.discard(fleet.id)

    def _project_path_inner(
        self,
        fleet: Fleet,
        galaxy,
        max_turns: int,
        component_registry,
    ) -> list:
        """Delegate to ``fleet_path_projection.project_path_inner``
        (PROJ-382 Phase 5 extraction)."""
        from game.strategy.services import fleet_path_projection as _proj
        return _proj.project_path_inner(self, fleet, galaxy, max_turns, component_registry)

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
        step = self.compute_next_step(state, galaxy, self_fleet=fleet)

        if step.next_hex is None:
            if step.order_complete:
                fleet.pop_order()
            return None

        # Apply state changes to mutable fleet
        fleet.path = list(step.new_state.path)
        if step.order_complete:
            fleet.pop_order()

        return step.next_hex

    # PROJ-382 Phase 5: ``_consume_ticks`` re-exposed as a thin static
    # forwarder so existing pure-function tests keep working after the
    # logic moved to ``fleet_path_projection``.
    @staticmethod
    def _consume_ticks(
        moves_left: int,
        current_turn: int,
        moves_per_turn: int,
        max_turns: int,
        ticks: int,
    ) -> tuple:
        """Forwarder to ``fleet_path_projection.consume_ticks`` (PROJ-382)."""
        from game.strategy.services import fleet_path_projection as _proj
        return _proj.consume_ticks(moves_left, current_turn, moves_per_turn, max_turns, ticks)

    # --- IFleetMutator navigation slice (PROJ-370 Phase 2) ---
    # Explicit named seams that engines and the FleetWriteService composite
    # route through. The existing calculate_fleet_next_hex above also writes
    # ``fleet.path`` inline; both call sites are inside this module which is
    # the AST-guard allowlist for navigation writes.

    def set_location(self, fleet: Fleet, new_location: HexCoord) -> None:
        """Set the fleet's location. Owner-service write for ``fleet.location``."""
        fleet.location = new_location

    def set_path(self, fleet: Fleet, new_path) -> None:
        """Replace the fleet's movement path."""
        fleet.path = list(new_path)
