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
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata
from game.strategy.interfaces.engines import IMovementEngine
from game.strategy.services.fleet_speed_calculator import get_tick_interval

logger = logging.getLogger(__name__)
from game.core.hex_math import HexCoord, hex_distance

if TYPE_CHECKING:
    from game.core.protocols import IFleetMutator
    from game.strategy.services.fleet_navigation_service import FleetNavigationService


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
        fleet_mutator: Optional['IFleetMutator'] = None,
    ):
        """
        Initialize the fleet movement engine.

        Args:
            nav_service: Optional FleetNavigationService for dependency injection.
                         If None, service is lazily initialized on first use.
            fleet_mutator: Optional IFleetMutator (PROJ-370) for routing fleet
                           writes through the named owner-service seam. If None,
                           a default ``FleetWriteService`` (composed with the
                           same nav_service) is constructed lazily on first use.

        PROJ-300 Phase 7: AreaEffectManager removed; environmental speed
        modifiers are now read by `_get_effective_fleet_speed` directly via
        the unified `system_effects_collector`.
        """
        self._nav_service = nav_service
        self._fleet_mutator = fleet_mutator

    def _get_fleet_mutator(self) -> 'IFleetMutator':
        """Lazy-default the mutator using the engine's nav_service."""
        if self._fleet_mutator is None:
            from game.strategy.services.fleet_write_service import FleetWriteService
            from game.strategy.services.fleet_navigation_service import (
                FleetNavigationService,
            )
            if self._nav_service is None:
                self._nav_service = FleetNavigationService()
            self._fleet_mutator = FleetWriteService(
                navigation_service=self._nav_service,
            )
        return self._fleet_mutator

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

        PROJ-189: Storms can reduce fleet speed via StrategicSpeedModifier.
        PROJ-300: Migrated to the unified IAbilitySource pipeline — queries
        `collect_sector_effects` for the fleet's hex and aggregates the
        StrategicSpeedModifier multiplier across all sources (storms,
        facilities, future planet/star/system intrinsics).

        Returns:
            Effective speed (hexes per turn), >= 0.0
        """
        base_speed = fleet.speed
        if base_speed <= 0:
            return 0.0

        from game.strategy.services.system_effects_collector import (
            collect_sector_effects, aggregate_value_or,
        )
        get_system = getattr(galaxy, 'get_system_at_location', None)
        if get_system is None:
            return base_speed
        system = get_system(fleet.location)
        if system is None:
            return base_speed

        effects = collect_sector_effects(
            system, fleet.location, empire_id=fleet.owner_id, registries=None,
        )
        mult = aggregate_value_or(effects, 'StrategicSpeedModifier', 1.0)
        if mult >= 1.0 - 1e-9:
            return base_speed
        modified_speed = base_speed * mult
        return max(0.0, float(int(modified_speed)))

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
        # PROJ-370 Phase 2: route the location write through IFleetMutator.
        self._get_fleet_mutator().set_location(fleet, next_hex)

        # PROJ-35: Order popping is now handled by calculate_next_hex (via FleetNavigationService)
        # during the collect_movements phase. Don't pop again here.

        return MovementResult(
            moved=True,
            stranded=False,
            warp_blocked=False,
            new_location=next_hex
        )

    def _validate_tick_inputs(self, empires: List) -> None:
        """PROJ-251: Validate preconditions before movement calculations.

        Raises:
            ValidationException: If any fleet has invalid location.
        """
        from game.core.exceptions import ValidationException
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    raise ValidationException(
                        f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                        context={"empire_id": empire.id, "fleet_id": fleet.id}
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
        self._validate_tick_inputs(empires)
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
                    if current_order and current_order.type in order_metadata.action_order_types:
                        continue

                    # Skip fleets with BUILD order - they are stationary
                    if current_order and current_order.type == OrderType.BUILD:
                        continue

                    # Calculate next hex WITHOUT moving yet
                    next_hex = self.calculate_next_hex(fleet, galaxy)
                    if next_hex is not None:
                        move_queue.append((fleet, next_hex))

        # FEAT-28: Drop the larger fleet's move from any mutual-pursuit pair
        # whose next-hexes would swap. Otherwise the pair oscillates past
        # each other forever at parity speed (e.g. distance 1, both speed 2).
        move_queue = self._filter_jump_past_collisions(move_queue)

        return move_queue

    def _filter_jump_past_collisions(
        self,
        move_queue: List[Tuple[Fleet, HexCoord]],
    ) -> List[Tuple[Fleet, HexCoord]]:
        """FEAT-28: Drop the larger fleet's queue entry when both fleets in a
        mutual-pursuit pair would swap hexes on the same tick.

        "Larger" = more ships; tiebreak smaller `fleet.id` (mirrors BUG-122
        `_elect_canonical_merges`). After dropping, the smaller fleet still
        moves to the larger's current hex this tick, the larger waits, and
        next tick they co-locate so OrderProcessor Phase 1 fires the merge.

        v1 covers swap parity only (`next_a == fleet_b.location and
        next_b == fleet_a.location`). The broader leapfrog case (e.g.
        distance 3, both speed 2 → A moves 2, B moves 2, they pass through
        but neither lands on the other's start) is deferred — fleets at
        distance 3 land 1 hex apart and merge naturally next tick.
        """
        if not move_queue:
            return move_queue

        by_fleet = {fleet: next_hex for fleet, next_hex in move_queue}
        drop_ids: set = set()

        # When `calculate_next_hex` resolves a MOVE_TO_FLEET path of length
        # 1 (e.g. distance 1, both speed 2 — destination = next hex), it
        # pops the MOVE_TO_FLEET so the queue head becomes JOIN_FLEET. The
        # filter must therefore accept either order type as the trigger,
        # matching `_is_mutual_pursuit`.
        _PURSUIT = (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET)
        for fleet_a, next_a in move_queue:
            if id(fleet_a) in drop_ids:
                continue
            order_a = fleet_a.get_current_order()
            if order_a is None or order_a.type not in _PURSUIT:
                continue
            fleet_b = order_a.target
            if not isinstance(fleet_b, Fleet) or fleet_b not in by_fleet:
                continue
            order_b = fleet_b.get_current_order()
            if order_b is None or order_b.type not in _PURSUIT:
                continue
            if order_b.target is not fleet_a:
                continue
            next_b = by_fleet[fleet_b]
            # Swap parity: A is heading to B's current hex AND B is heading
            # to A's current hex on the same tick.
            if next_a != fleet_b.location or next_b != fleet_a.location:
                continue
            # Pick the larger fleet to delay.
            ships_a = len(fleet_a.ships)
            ships_b = len(fleet_b.ships)
            if ships_a > ships_b:
                drop_ids.add(id(fleet_a))
            elif ships_b > ships_a:
                drop_ids.add(id(fleet_b))
            else:
                # Tie on ships: smaller id delays (BUG-122 precedent).
                if str(fleet_a.id) < str(fleet_b.id):
                    drop_ids.add(id(fleet_a))
                else:
                    drop_ids.add(id(fleet_b))

        if not drop_ids:
            return move_queue
        return [(f, h) for f, h in move_queue if id(f) not in drop_ids]

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
