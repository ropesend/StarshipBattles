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
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from game.core.logger import log_info, log_warning, log_event
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.data.build_queue_source import _facility_is_shipyard
from game.strategy.data.fleet import Fleet, OrderType
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.systems.design_library import DesignLibrary

if TYPE_CHECKING:
    pass


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

    def process_construction_tick(self, tick: int, empires: List, galaxy) -> None:
        """Process per-tick resource consumption for all construction queues.

        PROJ-75 Phase 4: Called each subturn tick (1-100) to deduct resources
        from empire pools for active construction. Items without cost tracking
        fields (legacy items) are skipped.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object (unused, reserved for future use).
        """
        for empire in empires:
            for colony in empire.colonies:
                # Base queue (complexes)
                self._process_queue_tick(colony.construction_queue, empire)

                # Facility queues (shipyards)
                for facility in colony.facilities:
                    if hasattr(facility, 'construction_queue') and facility.construction_queue:
                        self._process_queue_tick(facility.construction_queue, empire)

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
        new_fleet.add_ship_instance(ship_instance)
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
                        self._spawn_fleet_complex(fleet, design_id, empire, galaxy, save_path)
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
        fleet.add_ship_instance(ship_instance)

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
        save_path: Optional[str] = None
    ) -> None:
        """
        Spawn complex on planet at fleet's location.

        PROJ-67 Phase 3: Fleet yards can build complexes when at a planet hex.

        Args:
            fleet: Fleet building the complex
            design_id: ID of the complex design
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet lookup
            save_path: Path to savegame folder for loading design data
        """
        # Find planet at fleet's location
        if galaxy is None:
            log_warning(f"Cannot spawn complex {design_id}: no galaxy provided")
            return

        planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        if not planets_at_hex:
            log_warning(f"Cannot spawn complex {design_id}: fleet not at planet hex")
            return

        # Use the first planet at the hex
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
