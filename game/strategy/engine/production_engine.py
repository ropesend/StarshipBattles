"""
ProductionEngine - Handles construction queue processing and spawning.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
PROJ-20: Standardized on dict format only.
PROJ-67 Phase 3: Added fleet production processing.
PROJ-69 Phase 2: Parallel facility queue processing (multiple shipyards).
PROJ-75 Phase 4: Per-tick resource consumption for construction.

Responsibilities:
- Process base construction queue (complexes only) for all colonies
- Process shipyard facility queues independently (parallel construction)
- Process construction queues for fleets with space yards
- Spawn completed ships as new fleets (planet) or add to fleet (fleet yards)
- Spawn completed complexes as planetary facilities
- Per-tick resource consumption from empire pool during construction
"""

import logging
from enum import Enum, auto
from typing import Optional, List, Dict, Any, NamedTuple, TYPE_CHECKING

from game.core.event_logging import log_event
from game.strategy.data.build_queue_source import get_default_production_rates, _get_facility_production_rates
from game.strategy.engine.production_math import find_limiting_resource_ticks
from game.strategy.engine.production_spawner import ProductionSpawner
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.services.design_cost_calculator import DesignCostCalculator

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy

logger = logging.getLogger(__name__)

# PROJ-209 Phase 2: Named constants for production tick processing
from game.strategy.engine.turn_engine import TICKS_PER_TURN
TICK_CAPACITY_EPSILON = 0.0001  # Minimum tick capacity to continue processing
COMPLETION_EPSILON = 0.001  # Tolerance for float comparison in completion check
MAX_QUEUE_ITERATIONS = 10  # Safety limit to prevent infinite loops


class QueueItemAction(Enum):
    """Result of queue item validation."""
    VALID = auto()
    SKIP = auto()
    STOP = auto()


class TickExpenditure(NamedTuple):
    """Result of tick expenditure calculation.

    PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.
    """

    remaining_cost: Dict[str, float]  # Resources still needed
    ticks_to_spend: float  # Time fraction to spend this step
    cost_this_step: Dict[str, float]  # Resources to consume this step
    max_ticks_needed: float  # Total ticks needed to complete item


from game.strategy.data.fleet import Fleet


class ProductionEngine:
    """
    Engine for processing production/construction.

    Extracted from TurnEngine to handle:
    - Construction queue processing
    - Ship spawning
    - Complex spawning

    Queue items must be dicts with keys:
    - design_id: str - The design identifier
    - type: str - "ship", "fighter", "satellite", or "complex" (defaults to "ship")
    - turns_remaining: int - Turns until completion

    PROJ-75 Phase 4: Queue items may also have cost tracking fields:
    - total_cost: Dict[str, float] - Total resource cost for the build
    - cost_per_tick: Dict[str, float] - Per-tick resource cost
    - resources_consumed: Dict[str, float] - Cumulative resources consumed
    - ticks_in_current_turn: int - Tick counter within current turn
    """

    def __init__(self, registries: Optional['GameRegistries'] = None):
        """Initialize the production engine.

        PROJ-211: Added registries parameter for DI compliance.
        PROJ-233: Added ProductionSpawner for spawn delegation.

        Args:
            registries: Optional GameRegistries for ship creation.
        """
        self._registries = registries
        self._spawner = ProductionSpawner(registries=registries)

    # --- Resource Cost Methods (PROJ-75 Phase 4) ---

    def _calculate_design_cost(self, design_data: Dict) -> Dict[str, float]:
        """Calculate total resource cost from all components in a design.

        Delegates to DesignCostCalculator for centralized cost calculation.
        The result is cached as 'total_resource_cost' in design_data
        to avoid recalculation.

        Args:
            design_data: The design data dict containing layers with components.

        Returns:
            Dict mapping resource type to total cost amount.
        """
        if 'total_resource_cost' in design_data:
            return design_data['total_resource_cost']

        # PROJ-218: Pass registries for Ship-loading cost calculation
        total_cost = DesignCostCalculator.calculate_total_cost(design_data, self._registries)
        design_data['total_resource_cost'] = total_cost
        return total_cost

    def process_construction_tick(
        self,
        tick: int,
        empires: List['Empire'],
        galaxy: Optional['Galaxy'],
        save_path: Optional[str] = None,
    ) -> None:
        """Process per-tick resource consumption and completion for all construction queues.

        PROJ-79: Dynamic resource consumption with carry-over capacity.
        PROJ-161: Removed harvesting_engine parameter.
        PROJ-233: Cleaned up fleet rate resolution and removed design-discussion comment.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder for loading designs.
        """
        for empire in empires:
            for colony in empire.colonies:
                # 1. Base queue (complexes only)
                base_rate = get_default_production_rates("planetary_yard")
                self._process_queue_tick_dynamic(
                    colony.construction_queue, empire, tick, galaxy, save_path,
                    base_rate, colony_or_fleet=colony,
                    is_complex_only=True
                )

                # 2. Facility queues (each shipyard independently)
                for facility in colony.facilities:
                    if facility.construction_queue and facility.is_shipyard:
                        fac_rate = _get_facility_production_rates(facility)
                        self._process_queue_tick_dynamic(
                            facility.construction_queue, empire, tick, galaxy, save_path,
                            fac_rate, colony_or_fleet=colony,
                            is_complex_only=False
                        )

            # 3. Fleet queues
            # Fleet yards share one queue; multiple yards multiply build speed.
            for fleet in empire.fleets:
                if not fleet.is_building or not fleet.capabilities.has_space_shipyard:
                    continue

                total_rate = self._resolve_fleet_production_rate(fleet)
                self._process_queue_tick_dynamic(
                    fleet.construction_queue, empire, tick, galaxy, save_path,
                    total_rate, colony_or_fleet=fleet,
                    is_complex_only=False
                )

    def _resolve_fleet_production_rate(self, fleet) -> Dict[str, float]:
        """Calculate combined production rate for a fleet's space yards."""
        yard_count = fleet.capabilities.space_shipyard_count
        base_rate = get_default_production_rates("fleet_space_yard")
        return {k: v * yard_count for k, v in base_rate.items()}

    def _process_queue_tick_dynamic(
        self,
        queue: List[Dict],
        empire: 'Empire',
        tick: int,
        galaxy: Optional['Galaxy'],
        save_path: Optional[str],
        production_rate: Dict[str, float],
        colony_or_fleet: Any,
        is_complex_only: bool = False
    ) -> None:
        """Process one tick of production for a queue with dynamic resource consumption.

        Logic:
        1. Available time capacity = 1.0 (100% of a tick).
        2. While capacity > 0 and queue has items:
           a. Check constraints (complex at planet, etc).
           b. Calculate remaining cost for item.
           c. Determine limiting resource vs production rate.
           d. Calculate time needed to finish item.
           e. Spend minimum(available_capacity, time_needed).
           f. Consume resources and reduce capacity.
           g. If complete -> spawn, pop, continue.
           h. If resources insufficient -> stop for this tick.

        PROJ-161: Removed harvesting_engine parameter (harvesting now per-tick in TurnEngine).

        Args:
            queue: The construction queue.
            empire: Owner empire.
            tick: Current tick (1-100).
            save_path: Save path.
            production_rate: Rate per TURN (100 ticks).
            colony_or_fleet: Context.
            is_complex_only: Filter.
        """
        if not queue:
            return

        # FEAT-09: Reset shortage flags at the start of each turn
        if tick == 1:
            for q_item in queue:
                if isinstance(q_item, dict):
                    q_item.pop('_shortage_logged', None)

        # Capacity in fractional ticks (0.0 to 1.0)
        tick_capacity = 1.0
        
        # Max iterations to prevent infinite loops if something weird happens (e.g. 0 cost items)
        iterations = 0
        while tick_capacity > TICK_CAPACITY_EPSILON and queue and iterations < MAX_QUEUE_ITERATIONS:
            iterations += 1
            item = queue[0]

            # Validate queue item (PROJ-209: extracted to helper)
            validation_result = self._validate_queue_item(
                item, colony_or_fleet, galaxy, is_complex_only
            )
            if validation_result == QueueItemAction.SKIP:
                queue.pop(0)
                continue
            if validation_result == QueueItemAction.STOP:
                return

            # Calculate tick expenditure (PROJ-209: extracted to helper)
            expenditure = self._calculate_tick_expenditure(
                item, tick_capacity, production_rate
            )

            # Handle special cases
            if expenditure is None:
                # Zero production rate for required resource - cannot build
                return

            if not expenditure.remaining_cost:
                # No remaining cost = complete/free item
                self._complete_item(queue, item, empire, colony_or_fleet, galaxy, save_path, tick)
                continue

            # Check affordability (PROJ-209: extracted to helper)
            if not self._check_affordability(empire, expenditure.cost_this_step, colony_or_fleet):
                # FEAT-09: Log shortage event once per item per turn
                if not item.get('_shortage_logged'):
                    self._log_resource_shortage(
                        empire, item, expenditure.cost_this_step, colony_or_fleet
                    )
                    item['_shortage_logged'] = True
                return  # Paused - insufficient resources

            # Consume resources (PROJ-209: extracted to helper)
            self._apply_resource_consumption(empire, item, expenditure.cost_this_step, colony_or_fleet)

            # Decrement capacity
            tick_capacity -= expenditure.ticks_to_spend

            # Update UI display (PROJ-209: extracted to helper)
            self._update_turns_remaining(item, expenditure)

            # Check completion (PROJ-209: extracted to helper)
            if self._check_item_completion(item):
                self._complete_item(queue, item, empire, colony_or_fleet, galaxy, save_path, tick)
                # Loop continues with remaining tick_capacity

    def _validate_queue_item(
        self,
        item: Dict,
        colony_or_fleet: Any,
        galaxy: Optional['Galaxy'],
        is_complex_only: bool
    ) -> QueueItemAction:
        """Validate a queue item and determine if processing should continue.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.
        PROJ-233: Returns QueueItemAction enum instead of magic strings.

        Args:
            item: The queue item dict.
            colony_or_fleet: The colony or fleet context.
            galaxy: Galaxy object for location checks.
            is_complex_only: Whether this queue only processes complexes.

        Returns:
            QueueItemAction.VALID - Item can be processed.
            QueueItemAction.SKIP - Item is invalid, remove from queue and continue.
            QueueItemAction.STOP - Processing should halt (constraint not met).
        """
        # Type check
        if not isinstance(item, dict):
            return QueueItemAction.SKIP

        vehicle_type = item.get('type', 'ship')
        design_id = item.get('design_id')

        # Filter check: complex-only queue can't build ships
        if is_complex_only and vehicle_type != 'complex':
            return QueueItemAction.STOP

        # Fleet complex location check
        if isinstance(colony_or_fleet, Fleet) and vehicle_type == 'complex':
            if not galaxy:
                return QueueItemAction.STOP
            planets_at_hex = galaxy.get_planets_at_global_hex(colony_or_fleet.location)
            if not planets_at_hex:
                return QueueItemAction.STOP  # Paused, not at planet

        # Cost tracking check (AR-01 fix)
        if 'total_cost' not in item:
            logger.warning(
                f"Queue item {design_id} missing 'total_cost' - skipping "
                f"(should have been set by build queue controller)"
            )
            return QueueItemAction.SKIP

        return QueueItemAction.VALID

    def _calculate_tick_expenditure(
        self,
        item: Dict,
        tick_capacity: float,
        production_rate: Dict[str, float]
    ) -> Optional[TickExpenditure]:
        """Calculate resource expenditure for a single production tick.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.
        This method is pure - no side effects.

        Args:
            item: The queue item dict with total_cost and resources_consumed.
            tick_capacity: Available tick capacity (0.0 to 1.0).
            production_rate: Production rate per turn for each resource.

        Returns:
            TickExpenditure with calculated values, or None if:
            - No remaining cost (item is complete/free)
            - Zero production rate for a required resource
        """
        total_cost = item['total_cost']
        resources_consumed = item.get('resources_consumed', {})

        # Calculate remaining cost
        remaining_cost = {}
        for res, amount in total_cost.items():
            consumed = resources_consumed.get(res, 0.0)
            remaining = max(0.0, amount - consumed)
            if remaining > 0:
                remaining_cost[res] = remaining

        # No remaining cost = complete/free
        if not remaining_cost:
            return TickExpenditure(
                remaining_cost={},
                ticks_to_spend=0.0,
                cost_this_step={},
                max_ticks_needed=0.0
            )

        # Determine limiting resource and max ticks needed (PROJ-233: shared formula)
        max_ticks_needed = find_limiting_resource_ticks(
            remaining_cost, production_rate, TICKS_PER_TURN
        )
        if max_ticks_needed is None:
            # Cannot build - zero rate for required resource
            return None

        # Calculate fraction of tick to use
        ticks_to_spend = min(tick_capacity, max_ticks_needed)

        # Calculate resources to consume
        cost_this_step = {}
        for res in total_cost:
            p_rate_per_tick = production_rate.get(res, 0.0) / TICKS_PER_TURN
            to_consume = p_rate_per_tick * ticks_to_spend
            # Clamp to remaining (handle floating point errors)
            rem = remaining_cost.get(res, 0.0)
            to_consume = min(to_consume, rem)
            cost_this_step[res] = to_consume

        return TickExpenditure(
            remaining_cost=remaining_cost,
            ticks_to_spend=ticks_to_spend,
            cost_this_step=cost_this_step,
            max_ticks_needed=max_ticks_needed
        )

    def _check_affordability(
        self, empire: 'Empire', cost_this_step: Dict[str, float],
        colony_or_fleet: Any = None,
    ) -> bool:
        """Check if the build location can afford the resource cost.

        For planet construction: checks planet.stockpile (local storage).
        For fleet construction: checks empire pool (Phase 6 will switch to fleet cargo).

        Args:
            empire: The empire (fallback for fleet construction).
            cost_this_step: Resources needed this step.
            colony_or_fleet: Build location (Planet or Fleet).

        Returns:
            True if sufficient resources available, False otherwise.
        """
        ctx = getattr(colony_or_fleet, 'context_type', None)
        if ctx == 'planet':
            return colony_or_fleet.has_stockpile(cost_this_step)
        if ctx == 'fleet':
            return colony_or_fleet.has_cargo_resources(cost_this_step)
        return empire.has_resources(cost_this_step)

    def _log_resource_shortage(
        self,
        empire: 'Empire',
        item: Dict,
        cost_this_step: Dict[str, float],
        colony_or_fleet: Any,
    ) -> None:
        """Log a RESOURCE_SHORTAGE event identifying the bottleneck resource.

        FEAT-09: Called once per item per turn when affordability check fails.

        Args:
            empire: The empire that cannot afford production.
            item: The blocked queue item.
            cost_this_step: Resources needed this tick step.
            colony_or_fleet: Build location context (Planet or Fleet).
        """
        # Find the limiting resource: largest shortfall ratio (needed / available)
        limiting_resource = ""
        worst_ratio = -1.0
        limiting_available = 0.0
        limiting_needed = 0.0

        for resource, needed in cost_this_step.items():
            if needed <= 0:
                continue
            ctx = getattr(colony_or_fleet, 'context_type', None)
            if ctx == 'planet':
                available = colony_or_fleet.get_stockpile(resource)
            elif ctx == 'fleet':
                available = colony_or_fleet.get_cargo_resource(resource)
            else:
                available = empire.resource_pool.get(resource, 0.0)
            if available >= needed:
                continue
            shortfall_ratio = needed / max(available, 0.0001)
            if shortfall_ratio > worst_ratio:
                worst_ratio = shortfall_ratio
                limiting_resource = resource
                limiting_available = available
                limiting_needed = needed

        design_id = item.get('design_id', 'unknown')
        vehicle_type = item.get('type', 'ship')

        location_hex = None
        if hasattr(colony_or_fleet, 'location'):
            loc = colony_or_fleet.location
            if hasattr(loc, 'q') and hasattr(loc, 'r'):
                location_hex = [loc.q, loc.r]

        log_event(
            EventType.RESOURCE_SHORTAGE,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Production paused: insufficient {limiting_resource} for {design_id}",
            design_id=design_id,
            vehicle_type=vehicle_type,
            limiting_resource=limiting_resource,
            available=limiting_available,
            needed=limiting_needed,
            location_hex=location_hex,
        )

    def _apply_resource_consumption(
        self,
        empire: 'Empire',
        item: Dict,
        cost_this_step: Dict[str, float],
        colony_or_fleet: Any = None,
    ) -> None:
        """Consume resources and update item's consumption tracking.

        For planet construction: consumes from planet.stockpile (local storage).
        For fleet construction: consumes from fleet cargo.

        Args:
            empire: Empire (unused fallback).
            item: Queue item to update resources_consumed on.
            cost_this_step: Resources to consume.
            colony_or_fleet: Build location (Planet or Fleet).
        """
        ctx = getattr(colony_or_fleet, 'context_type', None)
        for res, amount in cost_this_step.items():
            if amount > 0:
                if ctx == 'planet':
                    colony_or_fleet.consume_from_stockpile(res, amount)
                elif ctx == 'fleet':
                    colony_or_fleet.consume_cargo_resource(res, amount)
                else:
                    empire.consume_resources(res, amount)
                item['resources_consumed'][res] = (
                    item.get('resources_consumed', {}).get(res, 0.0) + amount
                )

    def _check_item_completion(self, item: Dict) -> bool:
        """Check if an item has been fully produced.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.
        Pure function - no side effects.

        Args:
            item: Queue item with total_cost and resources_consumed.

        Returns:
            True if all resources have been consumed (within epsilon).
        """
        total_cost = item['total_cost']
        for res, total in total_cost.items():
            consumed = item['resources_consumed'].get(res, 0.0)
            if consumed < total - COMPLETION_EPSILON:
                return False
        return True

    def _update_turns_remaining(self, item: Dict, expenditure: TickExpenditure) -> None:
        """Update the turns_remaining field for UI display.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.

        Args:
            item: Queue item to update.
            expenditure: The tick expenditure result.
        """
        if expenditure.max_ticks_needed > 0:
            current_est_ticks = expenditure.max_ticks_needed - expenditure.ticks_to_spend
            item['turns_remaining'] = current_est_ticks / TICKS_PER_TURN
        else:
            item['turns_remaining'] = 0

    def _complete_item(self, queue: List[Dict], item: Dict, empire: 'Empire',
                       colony_or_fleet: Any, galaxy: Optional['Galaxy'],
                       save_path: Optional[str], tick: int) -> None:
        """Handle completion of a construction item.

        PROJ-161: Removed harvesting_engine parameter.
        PROJ-233: Delegates spawning to ProductionSpawner.
        """
        design_id = item['design_id']
        vehicle_type = item.get('type', 'ship')

        # Remove from queue
        queue.pop(0)

        # Log
        logger.info(f"Production Complete (tick {tick}): {design_id} ({vehicle_type})")

        # Spawn via dedicated spawner
        self._spawner.spawn_completed_item(
            item, empire, colony_or_fleet, galaxy, save_path, tick
        )
