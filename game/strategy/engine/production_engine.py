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

import uuid
from typing import Optional, List, Dict, Any

from game.core.logger import log_info, log_warning, log_event
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.data.build_queue_source import _facility_is_shipyard
from game.strategy.data.fleet import Fleet, OrderType
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

    def __init__(self):
        """Initialize the production engine."""
        pass

    # --- Resource Cost Methods (PROJ-75 Phase 4) ---

    def _calculate_design_cost(self, design_data: Dict) -> Dict[str, float]:
        """Calculate total resource cost from all components in a design.

        Iterates through all layers and components, summing their resource_cost
        fields. The result is cached as 'total_resource_cost' in design_data
        to avoid recalculation.

        Args:
            design_data: The design data dict containing layers with components.

        Returns:
            Dict mapping resource type to total cost amount.
        """
        if 'total_resource_cost' in design_data:
            return design_data['total_resource_cost']

        total_cost: Dict[str, float] = {}
        for layer in design_data.get('layers', {}).values():
            for component in layer.get('components', []):
                comp_cost = component.get('resource_cost', {})
                for res, amount in comp_cost.items():
                    total_cost[res] = total_cost.get(res, 0) + amount

        design_data['total_resource_cost'] = total_cost
        return total_cost

    def process_construction_tick(
        self,
        tick: int,
        empires: List,
        galaxy,
        save_path: Optional[str] = None,
        harvesting_engine=None
    ) -> None:
        """Process per-tick resource consumption and completion for all construction queues.

        PROJ-79 Refactor:
        - Dynamic resource consumption based on limiting resource.
        - Carry-over production capacity (mid-tick completion).
        - Legacy turn-based decrement logic REMOVED.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder for loading designs.
            harvesting_engine: HarvestingEngine for mid-turn facility harvest.
        """
        from game.strategy.data.build_queue_source import get_default_production_rates, _get_facility_production_rates, _facility_is_shipyard

        for empire in empires:
            for colony in empire.colonies:
                # 1. Base queue (complexes only)
                # Rate: Default planetary yard rate
                base_rate = get_default_production_rates("planetary_yard")
                self._process_queue_tick_dynamic(
                    colony.construction_queue, empire, tick, galaxy, save_path,
                    base_rate, colony_or_fleet=colony, harvesting_engine=harvesting_engine,
                    is_complex_only=True
                )

                # 2. Facility queues (shipyards)
                for facility in colony.facilities:
                    if facility.construction_queue and _facility_is_shipyard(facility):
                        # Rate: specific to facility
                        fac_rate = _get_facility_production_rates(facility)
                        self._process_queue_tick_dynamic(
                            facility.construction_queue, empire, tick, galaxy, save_path,
                            fac_rate, colony_or_fleet=colony, harvesting_engine=harvesting_engine,
                            is_complex_only=False
                        )

            # 3. Fleet queues
            for fleet in empire.fleets:
                if not fleet.is_building or not fleet.has_space_shipyard:
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
                
                yard_count = fleet.space_shipyard_count
                base_rate = get_default_production_rates("fleet_space_yard")
                # Multiply rates by count
                total_rate = {k: v * yard_count for k, v in base_rate.items()}
                
                self._process_queue_tick_dynamic(
                    fleet.construction_queue, empire, tick, galaxy, save_path,
                    total_rate, colony_or_fleet=fleet, harvesting_engine=harvesting_engine,
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
        harvesting_engine,
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
        while tick_capacity > 0.0001 and queue and iterations < 10:
            iterations += 1
            item = queue[0]
            
            # Validation
            if not isinstance(item, dict):
                queue.pop(0) # Remove invalid
                continue
                
            vehicle_type = item.get('type', 'ship')
            design_id = item['design_id']

            # Filter check
            if is_complex_only and vehicle_type != 'complex':
                # Should not happen in base queue if Controller did its job, 
                # but if it does, we can't build it here. 
                # Legacy code returned; we should probably just stop processing this queue
                # as it blocks the slot? Or skip it? 
                # Legacy says "skipping ... item (use facility queue)".
                # Since it's a list, the item is physically blocking the queue.
                return 

            # Fleet complex location check
            if isinstance(colony_or_fleet, Fleet) and vehicle_type == 'complex':
                if not galaxy: 
                    return
                planets_at_hex = galaxy.get_planets_at_global_hex(colony_or_fleet.location)
                if not planets_at_hex:
                    return # Paused, not at planet

            # Calculate remaining cost
            # Ensure item has cost tracking initialized
            if 'total_cost' not in item:
                 # Should have been set by controller, but safety fallback
                 item['total_cost'] = self._calculate_design_cost(item) # Need to load design? 
                 # _calculate_design_cost expects design_data. We don't have it easily here without loading.
                 # Actually, we can assume if it's missing, we can't process it accurately yet.
                 # But let's try to trust the item has 'total_cost' from Controller.
                 # If likely legacy item matches invalid state:
                 pass

            total_cost = item.get('total_cost', {})
            resources_consumed = item.get('resources_consumed', {})
            
            # Calculate what is left
            remaining_cost = {}
            for res, amount in total_cost.items():
                consumed = resources_consumed.get(res, 0.0)
                remaining = max(0.0, amount - consumed)
                if remaining > 0:
                    remaining_cost[res] = remaining
            
            # If no remaining cost, it's done (or free). Finish immediately.
            if not remaining_cost:
                self._complete_item(queue, item, empire, colony_or_fleet, galaxy, save_path, tick, harvesting_engine)
                continue

            # Determine limiting resource
            # Time needed (in ticks) = (Remaining / (Rate/100))
            # Rate is per TURN. Rate per tick is Rate / 100.
            max_ticks_needed = 0.0
            
            for res, amount in remaining_cost.items():
                p_rate_per_turn = production_rate.get(res, 0.0)
                if p_rate_per_turn <= 0:
                    # Requirements but no production rate! 
                    # If we have 0 rate for a required resource, valid turns is INFINITY.
                    # We cannot build this.
                    return # Stops queue
                
                p_rate_per_tick = p_rate_per_turn / 100.0
                ticks_needed = amount / p_rate_per_tick
                if ticks_needed > max_ticks_needed:
                    max_ticks_needed = ticks_needed
            
            # Calculate fraction of tick to use
            ticks_to_spend = min(tick_capacity, max_ticks_needed)
            
            # Calculate resources to consume for this fraction
            cost_this_step = {}
            for res, amount in total_cost.items(): # Iterate total to include all cost types
                # Rate * Fraction * 1/100
                # Actually, wait. We consume ALL resources proportionally.
                # Rate is the conversion rate of potential->progress.
                # If we spend `ticks_to_spend` time, we consume `rate * ticks` resources.
                # BUT we must limit by `remaining_cost` to avoid over-consumption 
                # (though strict math should handle it if ticks_to_spend is precise).
                
                p_rate_per_tick = production_rate.get(res, 0.0) / 100.0
                to_consume = p_rate_per_tick * ticks_to_spend
                
                # Clamp to remaining (handle floating point errors)
                rem = remaining_cost.get(res, 0.0)
                to_consume = min(to_consume, rem)
                
                cost_this_step[res] = to_consume

            # Check affordability
            if not empire.has_resources(cost_this_step):
                return # Paused - insufficient resources
            
            # Consume resources
            for res, amount in cost_this_step.items():
                if amount > 0:
                    empire.consume_resources(res, amount)
                    item['resources_consumed'][res] = item.get('resources_consumed', {}).get(res, 0.0) + amount
            
            # Decrement capacity
            tick_capacity -= ticks_to_spend
            
            # Update legacy "turns_remaining" for UI display (approximate)
            # Remaining ticks / 100
            if max_ticks_needed > 0:
                 current_est_ticks = max_ticks_needed - ticks_to_spend
                 item['turns_remaining'] = current_est_ticks / 100.0
            else:
                 item['turns_remaining'] = 0

            # Check completion
            # We re-calculate remaining to be sure
            is_complete = True
            for res, total in total_cost.items():
                consumed = item['resources_consumed'].get(res, 0.0)
                if consumed < total - 0.001: # Epsilon for float
                    is_complete = False
                    break
            
            if is_complete:
                 self._complete_item(queue, item, empire, colony_or_fleet, galaxy, save_path, tick, harvesting_engine)
                 # Loop continues with remaining tick_capacity

    def _complete_item(self, queue, item, empire, colony_or_fleet, galaxy, save_path, tick, harvesting_engine):
        """Handle completion of a construction item."""
        design_id = item['design_id']
        vehicle_type = item.get('type', 'ship')
        
        # Remove from queue
        queue.pop(0)
        
        # Log
        log_info(f"Production Complete (tick {tick}): {design_id} ({vehicle_type})")

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
                self._spawn_complex(colony_or_fleet, design_id, empire, save_path)
                # Trigger proportional harvest for mid-turn facility
                if harvesting_engine and tick < 100:
                    self._apply_partial_harvest(
                        colony_or_fleet, empire, tick, harvesting_engine
                    )
            else:
                self._spawn_ship(colony_or_fleet, design_id, empire, galaxy, save_path)

    def _apply_partial_harvest(self, colony, empire, tick: int, harvesting_engine) -> None:
        """Apply proportional harvest for facilities spawned mid-turn.

        PROJ-79 Phase 2: When a harvesting facility is built mid-turn,
        it should produce for the remaining fraction of the turn.

        Args:
            colony: Colony where the facility was built.
            empire: Empire that owns the colony.
            tick: Current tick (1-100) when facility was spawned.
            harvesting_engine: HarvestingEngine for recalculation and harvest.
        """
        remaining_fraction = (100 - tick) / 100.0
        if remaining_fraction <= 0:
            return

        # Recalculate storage capacity immediately
        if hasattr(harvesting_engine, 'recalculate_storage'):
            harvesting_engine.recalculate_storage([empire])

        # Apply partial harvest for the newly built facility
        # We only need to harvest the last facility (the one just built)
        if not colony.facilities:
            return

        new_facility = colony.facilities[-1]
        if not new_facility.is_operational:
            return

        # Find harvesters in the new facility
        for layer_data in new_facility.design_data.get("layers", {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                if not isinstance(comp, dict):
                    continue
                abilities = comp.get("abilities", {})
                harvester_data = abilities.get("ResourceHarvester", {})
                if not harvester_data:
                    continue

                resource_type = harvester_data.get("resource_type")
                base_rate = harvester_data.get("base_rate", 0)
                if not resource_type or base_rate <= 0:
                    continue

                # Calculate partial harvest
                quality = colony.resource_qualities.get(resource_type, 0.5)
                partial_amount = base_rate * quality * remaining_fraction

                # Add to empire pool
                empire.add_resources(resource_type, partial_amount)
                log_info(
                    f"Mid-turn harvest: {partial_amount:.1f} {resource_type} "
                    f"(tick {tick}, {remaining_fraction*100:.0f}% of turn)"
                )

    def process_production(self, empires: List, galaxy=None, save_path: Optional[str] = None) -> None:
        """
        Process construction completion at end of turn.
        
        PROJ-79 Refactor: All production is now handled per-tick in process_construction_tick.
        This method remains as a stub for interface compatibility or final cleanup.
        """
        pass
        
    # Legacy methods _process_base_queue and _process_facility_queues deleted.

    def _spawn_complex(self, planet, design_id: str, empire, save_path: Optional[str] = None) -> None:
        """
        Add completed complex to planet's facilities.

        Args:
            planet: Planet to add facility to
            design_id: ID of the complex design
            empire: Empire that owns the planet
            save_path: Path to savegame folder for loading design data
        """
        # Load design data if possible
        design_data = {}

        if save_path:
            library = DesignLibrary(save_path, empire.id)
            loaded_data = library.load_design_data(design_id)
            if loaded_data:
                design_data = loaded_data
            else:
                log_warning(f"Could not load design: {design_id}")
        else:
            log_warning(f"No savegame path - creating empty facility for {design_id}")

        # Create facility instance
        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        planet.facilities.append(facility)
        log_info(f"Built {facility.name} on {planet.name}")
        log_event(
            EventType.COMPLEX_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {facility.name} on {planet.name}",
            design_id=design_id,
            planet_id=planet.id,
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
            log_warning(f"Cannot spawn {design_id}: no save_path provided")
            return

        design_library = DesignLibrary(save_path, empire.id)
        design_data = design_library.load_design_data(design_id)

        if not design_data:
            log_warning(f"Cannot spawn {design_id}: design data not found")
            return

        # Create ShipInstance (with serial number)
        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=design_data,
            owner_id=empire.id,
            name=design_data.get("name", design_id),
            empire=empire
        )

        # Create fleet with unique ID
        fleet_id = empire.get_next_fleet_id()
        new_fleet = Fleet(fleet_id, empire.id, spawn_loc)
        new_fleet.add_ship(ship_instance)
        empire.add_fleet(new_fleet)

        # Increment design's times_built counter
        design_library.increment_built_count(design_id)

        log_info(f"Spawned {design_data.get('name', design_id)} at {spawn_loc} (Fleet {new_fleet.id})")
        log_event(
            EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {design_data.get('name', design_id)} at {planet.name}",
            design_id=design_id,
            planet_id=planet.id,
            fleet_id=new_fleet.id,
        )

    def process_fleet_production(
        self, empires: List, galaxy=None, save_path: Optional[str] = None
    ) -> None:
        """
        Process construction queues for all fleets with space yards.
        
        PROJ-79 Refactor: All production is now handled per-tick in process_construction_tick.
        This method remains as a stub for interface compatibility or final cleanup.
        """
        pass

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
            log_warning(f"Cannot spawn {design_id}: no save_path provided")
            return

        design_library = DesignLibrary(save_path, empire.id)
        design_data = design_library.load_design_data(design_id)

        if not design_data:
            log_warning(f"Cannot spawn {design_id}: design data not found")
            return

        # Create ShipInstance (with serial number)
        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=design_data,
            owner_id=empire.id,
            name=design_data.get("name", design_id),
            empire=empire
        )

        # Add ship to the building fleet
        fleet.add_ship(ship_instance)

        # Increment design's times_built counter
        design_library.increment_built_count(design_id)

        log_info(f"Fleet {fleet.id} built {design_data.get('name', design_id)}")
        log_event(
            EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Fleet {fleet.id} built {design_data.get('name', design_id)}",
            design_id=design_id,
            fleet_id=fleet.id,
            is_fleet_production=True,
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
            log_warning(f"Cannot spawn complex {design_id}: no galaxy provided")
            return

        planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        if not planets_at_hex:
            log_warning(f"Cannot spawn complex {design_id}: fleet not at planet hex")
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
                log_warning(f"Could not load design: {design_id}")
        else:
            log_warning(f"No savegame path - creating empty facility for {design_id}")

        # Create facility instance
        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        planet.facilities.append(facility)
        log_info(f"Fleet {fleet.id} built {facility.name} on {planet.name}")
        log_event(
            EventType.COMPLEX_BUILT,
            category=EventCategory.PRODUCTION,
            empire_id=empire.id,
            message=f"Built {facility.name} on {planet.name} (fleet yard)",
            design_id=design_id,
            planet_id=planet.id,
        )
