"""
FleetMovementEngine - Handles fleet movement calculations and resource consumption.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.

Responsibilities:
- Calculate next hex for fleet movement (MOVE and MOVE_TO_FLEET orders)
- Path management and recalculation
- Movement resource consumption
- Warp travel handling
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, TYPE_CHECKING

from game.core.logger import log_debug, log_warning
from game.strategy.data.fleet import Fleet, OrderType
from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.data.pathfinding import find_hybrid_path, calculate_intercept_point

if TYPE_CHECKING:
    pass


@dataclass
class MovementResult:
    """Result of a movement operation."""
    moved: bool
    stranded: bool = False
    warp_blocked: bool = False
    new_location: Optional[HexCoord] = None


class FleetMovementEngine:
    """
    Engine for processing fleet movement.

    Extracted from TurnEngine to handle:
    - Movement calculation (_calculate_next_hex logic)
    - Path management
    - Resource consumption for movement
    - Warp travel handling
    """

    def __init__(self):
        """Initialize the fleet movement engine."""
        pass

    def calculate_next_hex(self, fleet: Fleet, galaxy) -> Optional[HexCoord]:
        """
        Calculate (but don't apply) the next hex for a fleet.

        Returns the next hex to move to, or None if no movement.
        Side effect: Updates fleet.path if needed.

        Args:
            fleet: Fleet to calculate movement for
            galaxy: Galaxy object for pathfinding

        Returns:
            Next hex coordinate to move to, or None if no movement
        """
        order = fleet.get_current_order()
        if not order:
            return None

        destination = None

        if order.type == OrderType.MOVE:
            destination = order.target
        elif order.type == OrderType.MOVE_TO_FLEET:
            target_fleet = order.target
            if not target_fleet or not hasattr(target_fleet, 'location'):
                log_warning("FleetMovementEngine: Target fleet invalid. Order cancelled.")
                fleet.pop_order()
                return None

            # Use Predictive Intercept
            destination = calculate_intercept_point(fleet, target_fleet, galaxy)
        else:
            # Other order types (COLONIZE, JOIN_FLEET) not handled here
            return None

        # Check for Re-Pathing (for Dynamic Targets)
        if fleet.path:
            current_dest = fleet.path[-1]
            if current_dest != destination:
                fleet.path = []  # Force recalc

        # Calculate path if needed
        if not fleet.path:
            if fleet.location == destination:
                fleet.pop_order()
                return None

            fleet.path = find_hybrid_path(galaxy, fleet.location, destination, fleet=fleet)

            # Remove start hex if path begins with current location
            if fleet.path and fleet.path[0] == fleet.location:
                fleet.path.pop(0)

            if not fleet.path:
                if fleet.location != destination:
                    pass  # Retry next tick
                else:
                    fleet.pop_order()
                return None

        if fleet.path:
            # Pop next hex from path
            return fleet.path.pop(0)

        return None

    def apply_movement(
        self,
        fleet: Fleet,
        next_hex: HexCoord,
        galaxy
    ) -> MovementResult:
        """
        Apply movement to a fleet, handling resources and warp.

        Args:
            fleet: Fleet to move
            next_hex: Target hex coordinate
            galaxy: Galaxy object

        Returns:
            MovementResult with success/failure details
        """
        # Check resources before moving
        if not fleet.has_resources_for_movement():
            log_warning(f"Fleet {fleet.id} stranded - insufficient resources for movement")
            fleet.clear_orders()
            return MovementResult(moved=False, stranded=True)

        # Detect warp jump (hex distance > 1 indicates warp transit)
        is_warp = hex_distance(fleet.location, next_hex) > 1

        # Check and consume warp resources if this is a warp jump
        if is_warp:
            # Check warp CAPABILITY first
            if not fleet.can_use_warp():
                log_debug(f"Fleet {fleet.id} warp blocked - no warp capability")
                log_warning(f"Fleet {fleet.id} cannot warp - no warp capability")
                fleet.clear_orders()
                return MovementResult(moved=False, warp_blocked=True)

            if not fleet.has_resources_for_warp():
                log_warning(f"Fleet {fleet.id} cannot warp - insufficient resources")
                fleet.clear_orders()
                return MovementResult(moved=False, warp_blocked=False)

            log_debug(f"Fleet {fleet.id} executing warp jump to {next_hex}")
            fleet.consume_warp_resources()

        # Consume movement resources for this hex
        fleet.consume_movement_resources(1)

        # Apply movement
        old_location = fleet.location
        fleet.location = next_hex

        # If path complete, order is done
        if not fleet.path:
            fleet.pop_order()

        return MovementResult(
            moved=True,
            stranded=False,
            warp_blocked=False,
            new_location=next_hex
        )

    def collect_movements(
        self,
        empires: List,
        galaxy,
        tick: int
    ) -> List[Tuple[Fleet, HexCoord]]:
        """
        Collect all fleet movements for this tick.

        Calculates which fleets should move based on speed and tick,
        and determines their next hex.

        Args:
            empires: List of Empire objects
            galaxy: Galaxy object for pathfinding
            tick: Current tick number (1-100)

        Returns:
            List of (fleet, next_hex) tuples for fleets that should move
        """
        move_queue = []

        for empire in empires:
            for fleet in empire.fleets:
                if fleet.speed <= 0:
                    continue

                interval = int(100 // fleet.speed)
                if interval <= 0:
                    interval = 1  # Safety

                if tick % interval == 0:
                    # Calculate next hex WITHOUT moving yet
                    next_hex = self.calculate_next_hex(fleet, galaxy)
                    if next_hex is not None:
                        move_queue.append((fleet, next_hex))

        return move_queue

    def apply_movements(
        self,
        move_queue: List[Tuple[Fleet, HexCoord]],
        galaxy
    ) -> List[MovementResult]:
        """
        Apply all movements in the queue.

        Args:
            move_queue: List of (fleet, next_hex) tuples
            galaxy: Galaxy object

        Returns:
            List of MovementResult objects
        """
        results = []

        for fleet, next_hex in move_queue:
            result = self.apply_movement(fleet, next_hex, galaxy)
            results.append(result)

        return results
