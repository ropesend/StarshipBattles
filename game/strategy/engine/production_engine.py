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
import uuid
from typing import Optional, List, Dict, Any, NamedTuple

from game.core.event_logging import log_event
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.services.design_cost_calculator import DesignCostCalculator

logger = logging.getLogger(__name__)

# PROJ-209 Phase 2: Named constants for production tick processing
TICKS_PER_TURN = 100  # Number of ticks per game turn
TICK_CAPACITY_EPSILON = 0.0001  # Minimum tick capacity to continue processing
COMPLETION_EPSILON = 0.001  # Tolerance for float comparison in completion check
MAX_QUEUE_ITERATIONS = 10  # Safety limit to prevent infinite loops


class TickExpenditure(NamedTuple):
    """Result of tick expenditure calculation.

    PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.
    """

    remaining_cost: Dict[str, float]  # Resources still needed
    ticks_to_spend: float  # Time fraction to spend this step
    cost_this_step: Dict[str, float]  # Resources to consume this step
    max_ticks_needed: float  # Total ticks needed to complete item


from game.strategy.data.build_queue_source import _facility_is_shipyard
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.systems.design_library import DesignLibrary


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

    def __init__(self, registries=None):
        """Initialize the production engine.

        PROJ-211: Added registries parameter for DI compliance.

        Args:
            registries: Optional GameRegistries for ship creation.
        """
        self._registries = registries

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
        empires: List,
        galaxy,
        save_path: Optional[str] = None,
    ) -> None:
        """Process per-tick resource consumption and completion for all construction queues.

        PROJ-79 Refactor:
        - Dynamic resource consumption based on limiting resource.
        - Carry-over production capacity (mid-tick completion).
        - Legacy turn-based decrement logic REMOVED.

        PROJ-161: Removed harvesting_engine parameter (harvesting now per-tick in TurnEngine).

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder for loading designs.
        """
        from game.strategy.data.build_queue_source import get_default_production_rates, _get_facility_production_rates, _facility_is_shipyard

        for empire in empires:
            for colony in empire.colonies:
                # 1. Base queue (complexes only)
                # Rate: Default planetary yard rate
                base_rate = get_default_production_rates("planetary_yard")
                self._process_queue_tick_dynamic(
                    colony.construction_queue, empire, tick, galaxy, save_path,
                    base_rate, colony_or_fleet=colony,
                    is_complex_only=True
                )

                # 2. Facility queues (shipyards)
                for facility in colony.facilities:
                    if facility.construction_queue and _facility_is_shipyard(facility):
                        # Rate: specific to facility
                        fac_rate = _get_facility_production_rates(facility)
                        self._process_queue_tick_dynamic(
                            facility.construction_queue, empire, tick, galaxy, save_path,
                            fac_rate, colony_or_fleet=colony,
                            is_complex_only=False
                        )

            # 3. Fleet queues
            for fleet in empire.fleets:
                if not fleet.is_building or not fleet.capabilities.has_space_shipyard:
                    continue
                
                # Check for complex production location constraints early
                # But we handle this per-item in _process_queue_tick_dynamic
                
                # Rate: per space yard component (assuming 1 queue per yard logic in source, 
                # but fleet has single queue list? 
                # Wait, BuildQueueSource splits fleet queue into multiple sources for UI, 
                # but the Fleet data object has a single `construction_queue` list.
                # If a fleet has 2 shipyards, does it process 2x items?
                # The current data model seems to have one queue per fleet.
                # We will assume total capacity = single yard rate * count, 
                # OR process the single queue with combined rate?
                # The UI shows "Shipyard 1", "Shipyard 2" which implies parallel queues?
                # Looking at BuildQueueSource._collect_fleet_sources:
                # It creates multiple sources, but they ALL point to `fleet.construction_queue`.
                # This implies the fleet queue is shared? 
                # If they share the same list object, they are the SAME queue.
                # If so, "parallel" processing means applying N times the capacity to the head of the queue?
                # OR does the fleet have multiple queues? 
                # Fleet object has `construction_queue = []`. It is a single list.
                # So multiple yards help build the FIRST item faster, they don't build in parallel?
                # The UI implies distinct queues... let's check BuildQueueSource again.
                # "sources.append(BuildQueueSource(..., construction_queue=fleet.construction_queue ...))"
                # They share the SAME list reference!
                # So if I add to "Shipyard 2", it goes effectively to the same list as "Shipyard 1".
                # This means multiple yards just equal more speed for the single queue.
                # So I should multiply rate by shipyard count.
                
                # However, logic in `process_fleet_production` (legacy) didn't seem to account for multiple yards speed,
                # it just processed the queue once.
                # To be safe and robust (and enable "parallel" if they were separate), 
                # I will calculate total rate based on all yards.
                # Default rate * count.
                
                yard_count = fleet.capabilities.space_shipyard_count
                base_rate = get_default_production_rates("fleet_space_yard")
                # Multiply rates by count
                total_rate = {k: v * yard_count for k, v in base_rate.items()}
                
                self._process_queue_tick_dynamic(
                    fleet.construction_queue, empire, tick, galaxy, save_path,
                    total_rate, colony_or_fleet=fleet,
                    is_complex_only=False
                )

    def _process_queue_tick_dynamic(
        self,
        queue: List[Dict],
        empire,
        tick: int,
        galaxy,
        save_path: Optional[str],
        production_rate: Dict[str, float],
        colony_or_fleet,
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
            if validation_result == "skip":
                queue.pop(0)
                continue
            if validation_result == "stop":
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
            if not self._check_affordability(empire, expenditure.cost_this_step):
                return  # Paused - insufficient resources

            # Consume resources (PROJ-209: extracted to helper)
            self._apply_resource_consumption(empire, item, expenditure.cost_this_step)

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
        colony_or_fleet,
        galaxy,
        is_complex_only: bool
    ) -> str:
        """Validate a queue item and determine if processing should continue.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.

        Args:
            item: The queue item dict.
            colony_or_fleet: The colony or fleet context.
            galaxy: Galaxy object for location checks.
            is_complex_only: Whether this queue only processes complexes.

        Returns:
            "valid" - Item can be processed.
            "skip" - Item is invalid, should be removed from queue and continue.
            "stop" - Processing should halt (constraint not met).
        """
        # Type check
        if not isinstance(item, dict):
            return "skip"

        vehicle_type = item.get('type', 'ship')
        design_id = item.get('design_id')

        # Filter check: complex-only queue can't build ships
        if is_complex_only and vehicle_type != 'complex':
            return "stop"

        # Fleet complex location check
        if isinstance(colony_or_fleet, Fleet) and vehicle_type == 'complex':
            if not galaxy:
                return "stop"
            planets_at_hex = galaxy.get_planets_at_global_hex(colony_or_fleet.location)
            if not planets_at_hex:
                return "stop"  # Paused, not at planet

        # Cost tracking check (AR-01 fix)
        if 'total_cost' not in item:
            logger.warning(
                f"Queue item {design_id} missing 'total_cost' - skipping "
                f"(should have been set by build queue controller)"
            )
            return "skip"

        return "valid"

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

        # Determine limiting resource and max ticks needed
        max_ticks_needed = 0.0
        for res, amount in remaining_cost.items():
            p_rate_per_turn = production_rate.get(res, 0.0)
            if p_rate_per_turn <= 0:
                # Cannot build - zero rate for required resource
                return None

            p_rate_per_tick = p_rate_per_turn / TICKS_PER_TURN
            ticks_needed = amount / p_rate_per_tick
            if ticks_needed > max_ticks_needed:
                max_ticks_needed = ticks_needed

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

    def _check_affordability(self, empire, cost_this_step: Dict[str, float]) -> bool:
        """Check if empire can afford the resource cost.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.

        Args:
            empire: The empire to check resources for.
            cost_this_step: Resources needed this step.

        Returns:
            True if empire has sufficient resources, False otherwise.
        """
        return empire.has_resources(cost_this_step)

    def _apply_resource_consumption(
        self,
        empire,
        item: Dict,
        cost_this_step: Dict[str, float]
    ) -> None:
        """Consume resources and update item's consumption tracking.

        PROJ-209 Phase 2: Extracted from _process_queue_tick_dynamic.

        Args:
            empire: Empire to deduct resources from.
            item: Queue item to update resources_consumed on.
            cost_this_step: Resources to consume.
        """
        for res, amount in cost_this_step.items():
            if amount > 0:
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

    def _complete_item(self, queue, item, empire, colony_or_fleet, galaxy, save_path, tick):
        """Handle completion of a construction item.

        PROJ-161: Removed harvesting_engine parameter. Mid-turn facilities now participate
        in per-tick harvesting automatically on subsequent ticks.
        """
        design_id = item['design_id']
        vehicle_type = item.get('type', 'ship')

        # Remove from queue
        queue.pop(0)

        # Log
        logger.info(f"Production Complete (tick {tick}): {design_id} ({vehicle_type})")

        # Spawn
        if isinstance(colony_or_fleet, Fleet):
            if vehicle_type == 'complex':
                target_planet_id = item.get('target_planet_id')
                self._spawn_fleet_complex(
                    colony_or_fleet, design_id, empire, galaxy, save_path,
                    target_planet_id=target_planet_id
                )
            else:
                self._spawn_fleet_ship(colony_or_fleet, design_id, empire, save_path)
        else:
            # Colony/planet
            if vehicle_type == 'complex':
                self._spawn_complex(colony_or_fleet, design_id, empire, save_path, galaxy)
                # PROJ-161: Harvesting is now per-tick, so mid-turn facilities
                # automatically participate in remaining ticks' harvesting
            else:
                self._spawn_ship(colony_or_fleet, design_id, empire, galaxy, save_path)

    def _spawn_complex(self, planet, design_id: str, empire, save_path: Optional[str] = None, galaxy=None) -> None:
        """
        Add completed complex to planet's facilities.

        Args:
            planet: Planet to add facility to
            design_id: ID of the complex design
            empire: Empire that owns the planet
            save_path: Path to savegame folder for loading design data
            galaxy: Galaxy for location calculation
        """
        # Load design data if possible
        design_data = {}

        if save_path:
            library = DesignLibrary(save_path, empire.id)
            loaded_data = library.load_design_data(design_id)
            if loaded_data:
                design_data = loaded_data
            else:
                logger.warning(f"Could not load design: {design_id}")
        else:
            logger.warning(f"No savegame path - creating empty facility for {design_id}")

        # Create facility instance
        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        planet.facilities.append(facility)
        logger.info(f"Built {facility.name} on {planet.name}")

        # FEAT-04: Compute global hex for event location
        # PROJ-215: Add system_name and local_hex for granular event log columns
        location_hex = None
        system_name = ""
        local_hex = None
        if galaxy:
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                loc = parent_sys.global_location + planet.location
                location_hex = [loc.q, loc.r]
                system_name = parent_sys.name
                local_hex = [planet.location.q, planet.location.r]

        log_event(
            EventType.COMPLEX_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {facility.name} on {planet.name}",
            design_id=design_id,
            planet_id=planet.id,
            location_name=planet.name,
            location_hex=location_hex,
            system_name=system_name,
            local_hex=local_hex,
        )

    def _spawn_ship(
        self,
        planet,
        design_id: str,
        empire,
        galaxy,
        save_path: Optional[str] = None
    ) -> None:
        """
        Spawn ship/satellite/fighter as fleet with ShipInstance.

        Args:
            planet: Planet where ship spawns
            design_id: ID of the ship design
            empire: Empire that owns the ship
            galaxy: Galaxy for location calculation
            save_path: Path to savegame folder for loading design data
        """
        # Calculate spawn location
        spawn_loc = planet.location
        if galaxy:
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                spawn_loc = parent_sys.global_location + planet.location

        # Load design data
        if not save_path:
            logger.warning(f"Cannot spawn {design_id}: no save_path provided")
            return

        design_library = DesignLibrary(save_path, empire.id)
        design_data = design_library.load_design_data(design_id)

        if not design_data:
            logger.warning(f"Cannot spawn {design_id}: design data not found")
            return

        # Create ShipInstance (with serial number)
        # PROJ-211: Pass registries for DI compliance
        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=design_data,
            owner_id=empire.id,
            name=design_data.get("name", design_id),
            empire=empire,
            registries=self._registries,
        )

        # Create fleet with unique ID
        fleet_id = empire.get_next_fleet_id()
        new_fleet = Fleet(fleet_id, empire.id, spawn_loc)
        new_fleet.add_ship(ship_instance)
        empire.add_fleet(new_fleet)

        # Increment design's times_built counter
        design_library.increment_built_count(design_id)

        # PROJ-215: Compute system_name and local_hex for granular event log columns
        system_name = ""
        local_hex = None
        if galaxy:
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                system_name = parent_sys.name
                local_hex = [planet.location.q, planet.location.r]

        logger.info(f"Spawned {design_data.get('name', design_id)} at {spawn_loc} (Fleet {new_fleet.id})")
        log_event(
            EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {design_data.get('name', design_id)} at {planet.name}",
            design_id=design_id,
            planet_id=planet.id,
            fleet_id=new_fleet.id,
            location_name=planet.name,
            location_hex=[spawn_loc.q, spawn_loc.r],
            system_name=system_name,
            local_hex=local_hex,
        )

    def _spawn_fleet_ship(
        self,
        fleet: Fleet,
        design_id: str,
        empire,
        save_path: Optional[str] = None
    ) -> None:
        """
        Spawn ship/satellite/fighter and add to the building fleet.

        PROJ-67 Phase 3: Ships built by fleet yards join the fleet directly.

        Args:
            fleet: Fleet building the ship
            design_id: ID of the ship design
            empire: Empire that owns the fleet
            save_path: Path to savegame folder for loading design data
        """
        # Load design data
        if not save_path:
            logger.warning(f"Cannot spawn {design_id}: no save_path provided")
            return

        design_library = DesignLibrary(save_path, empire.id)
        design_data = design_library.load_design_data(design_id)

        if not design_data:
            logger.warning(f"Cannot spawn {design_id}: design data not found")
            return

        # Create ShipInstance (with serial number)
        # PROJ-211: Pass registries for DI compliance
        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=design_data,
            owner_id=empire.id,
            name=design_data.get("name", design_id),
            empire=empire,
            registries=self._registries,
        )

        # Add ship to the building fleet
        fleet.add_ship(ship_instance)

        # Increment design's times_built counter
        design_library.increment_built_count(design_id)

        logger.info(f"Fleet {fleet.id} built {design_data.get('name', design_id)}")
        # PROJ-215: Fleet production in deep space has no system/local context
        log_event(
            EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Fleet {fleet.id} built {design_data.get('name', design_id)}",
            design_id=design_id,
            fleet_id=fleet.id,
            is_fleet_production=True,
            location_hex=[fleet.location.q, fleet.location.r],
            system_name="",
            local_hex=None,
        )

    def _spawn_fleet_complex(
        self,
        fleet: Fleet,
        design_id: str,
        empire,
        galaxy,
        save_path: Optional[str] = None,
        target_planet_id: Optional[int] = None
    ) -> None:
        """
        Spawn complex on planet at fleet's location.

        PROJ-67 Phase 3: Fleet yards can build complexes when at a planet hex.
        PROJ-79 Phase 4: Uses target_planet_id when specified.

        Args:
            fleet: Fleet building the complex
            design_id: ID of the complex design
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup
            save_path: Path to savegame folder for loading design data
            target_planet_id: Specific planet ID to receive the complex (PROJ-79)
        """
        # Find planet at fleet's location
        if galaxy is None:
            logger.warning(f"Cannot spawn complex {design_id}: no galaxy provided")
            return

        planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        if not planets_at_hex:
            logger.warning(f"Cannot spawn complex {design_id}: fleet not at planet hex")
            return

        # PROJ-79: Use target_planet_id if specified, otherwise fall back to first planet
        if target_planet_id is not None:
            planet = next(
                (p for p in planets_at_hex if p.id == target_planet_id),
                planets_at_hex[0]
            )
        else:
            planet = planets_at_hex[0]

        # Load design data
        design_data = {}
        if save_path:
            library = DesignLibrary(save_path, empire.id)
            loaded_data = library.load_design_data(design_id)
            if loaded_data:
                design_data = loaded_data
            else:
                logger.warning(f"Could not load design: {design_id}")
        else:
            logger.warning(f"No savegame path - creating empty facility for {design_id}")

        # Create facility instance
        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        planet.facilities.append(facility)
        logger.info(f"Fleet {fleet.id} built {facility.name} on {planet.name}")

        # PROJ-215: Compute system_name and local_hex for granular event log columns
        system_name = ""
        local_hex = None
        if hasattr(galaxy, 'get_system_of_planet'):
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                system_name = parent_sys.name
                if hasattr(planet, 'location') and planet.location is not None:
                    local_hex = [planet.location.q, planet.location.r]

        log_event(
            EventType.COMPLEX_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {facility.name} on {planet.name} (fleet yard)",
            design_id=design_id,
            planet_id=planet.id,
            location_name=planet.name,
            location_hex=[fleet.location.q, fleet.location.r],
            system_name=system_name,
            local_hex=local_hex,
        )
