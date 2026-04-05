"""
FleetMovementEngine - Handles fleet movement calculations and resource consumption.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
PROJ-40/NEW-STRAT-007: Added constructor injection for FleetNavigationService.
PROJ-189: Added environmental effect integration for storm speed reduction.

Responsibilities:
- Calculate next hex for fleet movement (MOVE and MOVE_TO_FLEET orders)
- Path management and recalculation
- Movement resource consumption
- Warp travel handling
- Environmental effect integration (storm speed reduction)
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, TYPE_CHECKING
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType, ACTION_ORDER_TYPES
from game.strategy.interfaces.engines import IMovementEngine
from game.strategy.services.fleet_speed_calculator import get_tick_interval

logger = logging.getLogger(__name__)
from game.core.hex_math import HexCoord, hex_distance

if TYPE_CHECKING:
    from game.strategy.services.fleet_navigation_service import FleetNavigationService
    from game.strategy.services.area_effect_manager import AreaEffectManager


@dataclass
class MovementResult:
    """Result of a movement operation."""
    moved: bool
    stranded: bool = False
    warp_blocked: bool = False
    new_location: Optional[HexCoord] = None


class FleetMovementEngine(IMovementEngine):
    """
    Engine for processing fleet movement.

    Extracted from TurnEngine to handle:
    - Movement calculation (_calculate_next_hex logic)
    - Path management
    - Resource consumption for movement
    - Warp travel handling

    Dependencies:
    - FleetNavigationService: For pathfinding and movement calculation
      (injected via constructor or lazily initialized)
    """

    def __init__(
        self,
        nav_service: Optional['FleetNavigationService'] = None,
        area_effect_manager: Optional['AreaEffectManager'] = None,
    ):
        """
        Initialize the fleet movement engine.

        Args:
            nav_service: Optional FleetNavigationService for dependency injection.
                         If None, service is lazily initialized on first use.
            area_effect_manager: Optional AreaEffectManager for environmental effects.
                         If None, creates default instance lazily.
        """
        self._nav_service = nav_service
        self._area_effect_manager = area_effect_manager

    def calculate_next_hex(self, fleet: Fleet, galaxy) -> Optional[HexCoord]:
        """
        Calculate (but don't apply) the next hex for a fleet.

        Returns the next hex to move to, or None if no movement.
        Side effect: Updates fleet.path if needed.

        PROJ-35: Delegates to FleetNavigationService for unified navigation logic.

        Args:
            fleet: Fleet to calculate movement for
            galaxy: Galaxy object for pathfinding

        Returns:
            Next hex coordinate to move to, or None if no movement
        """
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        if self._nav_service is None:
            self._nav_service = FleetNavigationService()

        return self._nav_service.calculate_fleet_next_hex(fleet, galaxy)

    def _get_effective_fleet_speed(self, fleet: Fleet, galaxy) -> float:
        """
        Calculate effective fleet speed considering environmental effects.

        PROJ-189: Storms can reduce fleet speed via strategic_mult.

        Uses the fleet's stored .speed attribute (already set by FleetSpeedCalculator
        when ships are added/removed) and applies environmental multipliers.

        Args:
            fleet: Fleet to calculate speed for
            galaxy: Galaxy for zone lookup

        Returns:
            Effective speed (hexes per turn), >= 0.0
        """
        # Use fleet's stored speed (maintained by FleetSpeedCalculator)
        base_speed = fleet.speed

        if base_speed <= 0:
            return 0.0

        # If no area_effect_manager, use base speed
        if self._area_effect_manager is None:
            # Lazy-initialize default AreaEffectManager
            from game.strategy.services.area_effect_manager import AreaEffectManager
            self._area_effect_manager = AreaEffectManager()

        # Query environmental effects at fleet location
        effects = self._area_effect_manager.get_effects_at_global_hex(galaxy, fleet.location)

        # Apply strategic movement multiplier from storms
        if effects.in_storm:
            modified_speed = base_speed * effects.strategic_mult
            return max(0.0, float(int(modified_speed)))

        return base_speed

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
        if not fleet.resources.has_resources_for_movement():
            logger.warning(f"Fleet {fleet.id} stranded - insufficient resources for movement")
            fleet.clear_orders()
            return MovementResult(moved=False, stranded=True)

        # Detect warp jump (hex distance > 1 indicates warp transit)
        is_warp = hex_distance(fleet.location, next_hex) > 1

        # Check and consume warp resources if this is a warp jump
        if is_warp:
            # Check warp CAPABILITY first
            # PROJ-207 EP-005: Use pop_order() instead of clear_orders() for warp failures.
            # Fleet can still move normally, so preserve subsequent orders.
            if not fleet.capabilities.can_use_warp():
                logger.debug(f"Fleet {fleet.id} warp blocked - no warp capability")
                logger.warning(f"Fleet {fleet.id} cannot warp - no warp capability")
                fleet.pop_order()
                return MovementResult(moved=False, warp_blocked=True)

            if not fleet.resources.has_resources_for_warp():
                logger.warning(f"Fleet {fleet.id} cannot warp - insufficient resources")
                fleet.pop_order()
                return MovementResult(moved=False, warp_blocked=False)

            logger.debug(f"Fleet {fleet.id} executing warp jump to {next_hex}")
            fleet.resources.consume_warp_resources()

        # Consume movement resources for this hex
        fleet.resources.consume_movement_resources(1)

        # Apply movement
        old_location = fleet.location
        fleet.location = next_hex

        # PROJ-35: Order popping is now handled by calculate_next_hex (via FleetNavigationService)
        # during the collect_movements phase. Don't pop again here.

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

        PROJ-189: Environmental effects (storms) can reduce fleet speed via
        strategic_mult. A fleet in a storm with strategic_mult=0.5 moves at
        half speed (double interval between moves).

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

                # PROJ-189: Calculate effective speed with environmental effects
                effective_speed = self._get_effective_fleet_speed(fleet, galaxy)
                if effective_speed <= 0:
                    continue  # Fleet cannot move (stuck in storm or immobile)

                # PROJ-204: Use shared tick interval calculation
                interval = get_tick_interval(effective_speed)

                if tick % interval == 0:
                    # Skip fleets with action orders - they are handled by ActionExecutionEngine
                    # PROJ-187: Action orders (COLONIZE, TRANSFER, superweapons) don't move
                    current_order = fleet.get_current_order()
                    if current_order and current_order.type in ACTION_ORDER_TYPES:
                        continue

                    # Skip fleets with BUILD order - they are stationary
                    if current_order and current_order.type == OrderType.BUILD:
                        continue

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
