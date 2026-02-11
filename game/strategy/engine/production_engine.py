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

        PROJ-75 Phase 4: Called each subturn tick (1-100) to deduct resources
        from empire pools for active construction. Items without cost tracking
        fields (legacy items) are skipped for resource consumption but still
        processed at end-of-turn.

        PROJ-79 Phase 2: Added mid-turn completion. When all resources are
        consumed, the item completes immediately and the next item starts.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder for loading designs.
            harvesting_engine: HarvestingEngine for mid-turn facility harvest.
        """
        for empire in empires:
            for colony in empire.colonies:
                # Base queue (complexes)
                self._process_queue_tick_with_completion(
                    colony.construction_queue, empire, tick, galaxy, save_path,
                    colony_or_fleet=colony, harvesting_engine=harvesting_engine,
                    is_complex_only=True
                )

                # Facility queues (shipyards)
                for facility in colony.facilities:
                    if hasattr(facility, 'construction_queue') and facility.construction_queue:
                        self._process_queue_tick_with_completion(
                            facility.construction_queue, empire, tick, galaxy, save_path,
                            colony_or_fleet=colony, harvesting_engine=harvesting_engine,
                            is_complex_only=False
                        )

            # Fleet queues (PROJ-79)
            for fleet in empire.fleets:
                if not fleet.is_building or not fleet.has_space_shipyard:
                    continue
                if fleet.construction_queue:
                    self._process_queue_tick_with_completion(
                        fleet.construction_queue, empire, tick, galaxy, save_path,
                        colony_or_fleet=fleet, harvesting_engine=harvesting_engine,
                        is_complex_only=False
                    )

    def _process_queue_tick(self, queue: List[Dict], empire) -> None:
        """Process one tick of resource consumption for a single queue.

        Only the first item in the queue is processed. If the empire lacks
        sufficient resources, the tick is skipped (production paused).

        Args:
            queue: Construction queue (list of queue item dicts).
            empire: Empire that owns the queue.
        """
        if not queue:
            return

        item = queue[0]
        cost_per_tick = item.get('cost_per_tick')

        # Skip legacy items without cost tracking
        if cost_per_tick is None:
            return

        # Check if empire has all resources for this tick
        if not empire.has_resources(cost_per_tick):
            return  # Paused - insufficient resources

        # Consume resources
        for res, amount in cost_per_tick.items():
            empire.consume_resources(res, amount)
            item['resources_consumed'][res] = item.get('resources_consumed', {}).get(res, 0) + amount

        # Track tick progress
        item['ticks_in_current_turn'] = item.get('ticks_in_current_turn', 0) + 1
        if item['ticks_in_current_turn'] >= 100:
            item['ticks_in_current_turn'] = 0
            item['turns_remaining'] -= 1

    def _process_queue_tick_with_completion(
        self,
        queue: List[Dict],
        empire,
        tick: int,
        galaxy,
        save_path: Optional[str],
        colony_or_fleet,
        harvesting_engine,
        is_complex_only: bool = False
    ) -> None:
        """Process one tick with mid-turn completion support.

        PROJ-79 Phase 2: Enhanced tick processing that:
        1. Consumes resources per tick
        2. Checks if item is complete (all resources consumed)
        3. Spawns completed items immediately
        4. Starts next item in same tick if queue not empty
        5. Triggers proportional harvest for mid-turn complexes

        Args:
            queue: Construction queue (list of queue item dicts).
            empire: Empire that owns the queue.
            tick: Current tick number (1-100).
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder.
            colony_or_fleet: Planet or Fleet that owns the queue.
            harvesting_engine: For mid-turn facility harvest.
            is_complex_only: If True, skip non-complex items.
        """
        if not queue:
            return

        item = queue[0]

        # Skip if item is not a dict (e.g., MagicMock from tests)
        if not isinstance(item, dict):
            return

        vehicle_type = item.get('type', 'ship')

        # Base queue only processes complexes
        if is_complex_only and vehicle_type != 'complex':
            return

        cost_per_tick = item.get('cost_per_tick')

        # Legacy items without cost tracking - fall back to old behavior
        if cost_per_tick is None:
            return

        # Check if empire has all resources for this tick
        if not empire.has_resources(cost_per_tick):
            return  # Paused - insufficient resources

        # Fleet complexes require fleet to be at planet
        if isinstance(colony_or_fleet, Fleet) and vehicle_type == 'complex':
            if galaxy is None:
                return
            planets_at_hex = galaxy.get_planets_at_global_hex(colony_or_fleet.location)
            if not planets_at_hex:
                return  # Paused - not at planet

        # Consume resources
        for res, amount in cost_per_tick.items():
            empire.consume_resources(res, amount)
            item['resources_consumed'][res] = item.get('resources_consumed', {}).get(res, 0) + amount

        # Track tick progress (for display purposes)
        item['ticks_in_current_turn'] = item.get('ticks_in_current_turn', 0) + 1
        if item['ticks_in_current_turn'] >= 100:
            item['ticks_in_current_turn'] = 0
            item['turns_remaining'] -= 1

        # Check if item is complete (all resources consumed)
        total_cost = item.get('total_cost', {})
        resources_consumed = item.get('resources_consumed', {})
        is_complete = all(
            resources_consumed.get(res, 0) >= total_cost.get(res, 0)
            for res in total_cost
        )

        if is_complete:
            design_id = item['design_id']
            queue.pop(0)
            log_info(f"Mid-turn Production Complete (tick {tick}): {design_id} ({vehicle_type})")

            # Spawn the completed item
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
        Process construction queues for all colonies.

        PROJ-69 Phase 2: Two loops per colony:
        1. Base queue (colony.construction_queue) - complexes only
        2. Facility queues - each operational shipyard facility processes independently

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for fleet spawning
            save_path: Path to savegame folder for loading designs
        """
        for emp in empires:
            for colony in emp.colonies:
                # --- Base queue: complexes only ---
                self._process_base_queue(colony, emp, galaxy, save_path)

                # --- Facility queues: each shipyard processes independently ---
                self._process_facility_queues(colony, emp, galaxy, save_path)

    def _process_base_queue(
        self, colony, empire, galaxy=None, save_path: Optional[str] = None
    ) -> None:
        """Process the colony's base construction queue (complexes only).

        Ship/fighter/satellite items in the base queue are skipped - they
        belong in facility queues. Only complex items are processed here.

        Args:
            colony: Planet/colony to process.
            empire: Empire that owns the colony.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder.
        """
        if not colony.construction_queue:
            return

        item: Dict[str, Any] = colony.construction_queue[0]
        vehicle_type = item.get("type", "ship")
        design_id = item["design_id"]

        # Base queue only processes complexes
        if vehicle_type != "complex":
            log_info(f"Base queue at {colony.name}: skipping {vehicle_type} item {design_id} (use facility queue)")
            return

        # Decrement turns
        item["turns_remaining"] -= 1
        turns_remaining = item["turns_remaining"]

        if turns_remaining <= 0:
            colony.construction_queue.pop(0)
            log_info(f"Production Complete: {design_id} ({vehicle_type})")
            self._spawn_complex(colony, design_id, empire, save_path)

    def _process_facility_queues(
        self, colony, empire, galaxy=None, save_path: Optional[str] = None
    ) -> None:
        """Process each operational shipyard facility's construction queue.

        Each shipyard facility has its own construction_queue and processes
        independently, enabling parallel construction.

        Args:
            colony: Planet/colony to process.
            empire: Empire that owns the colony.
            galaxy: Galaxy object for spawning.
            save_path: Path to savegame folder.
        """
        for facility in colony.facilities:
            if not _facility_is_shipyard(facility):
                continue

            if not facility.construction_queue:
                continue

            item: Dict[str, Any] = facility.construction_queue[0]
            vehicle_type = item.get("type", "ship")
            design_id = item["design_id"]

            # Decrement turns
            item["turns_remaining"] -= 1
            turns_remaining = item["turns_remaining"]

            if turns_remaining <= 0:
                facility.construction_queue.pop(0)
                log_info(f"Facility Production Complete: {design_id} ({vehicle_type})")

                # Route to appropriate spawner
                if vehicle_type == "complex":
                    self._spawn_complex(colony, design_id, empire, save_path)
                else:
                    self._spawn_ship(colony, design_id, empire, galaxy, save_path)

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

        PROJ-67 Phase 3: Fleet-based production processing.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for complex spawning (planet proximity check)
            save_path: Path to savegame folder for loading designs
        """
        for empire in empires:
            for fleet in empire.fleets:
                # Skip fleets not in BUILD mode
                if not fleet.is_building:
                    continue

                # Skip fleets with empty queues
                if not fleet.construction_queue:
                    continue

                # Check if fleet still has a shipyard
                if not fleet.has_space_shipyard:
                    log_info(f"Fleet {fleet.id} production paused: no shipyard")
                    continue

                item: Dict[str, Any] = fleet.construction_queue[0]
                vehicle_type = item.get("type", "ship")
                design_id = item["design_id"]

                # PROJ-67 Phase 6: Complex items require fleet to be at planet
                if vehicle_type == "complex":
                    if galaxy is None:
                        log_info(f"Fleet {fleet.id} complex production paused: no galaxy")
                        continue
                    planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
                    if not planets_at_hex:
                        log_info(f"Fleet {fleet.id} complex production paused: not at planet")
                        continue  # Don't decrement turns - complex paused

                # Decrement turns (only if we got here - passed all checks)
                item["turns_remaining"] -= 1
                turns_remaining = item["turns_remaining"]

                if turns_remaining <= 0:
                    fleet.construction_queue.pop(0)
                    log_info(f"Fleet Production Complete: {design_id} ({vehicle_type})")

                    # Route to appropriate spawner
                    if vehicle_type == "complex":
                        target_planet_id = item.get('target_planet_id')
                        self._spawn_fleet_complex(
                            fleet, design_id, empire, galaxy, save_path,
                            target_planet_id=target_planet_id
                        )
                    else:
                        self._spawn_fleet_ship(fleet, design_id, empire, save_path)

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
