"""
ProductionEngine - Handles construction queue processing and spawning.

PROJ-12 Phase 3: Extracted from TurnEngine to decompose the god class.
PROJ-20: Standardized on dict format only.
PROJ-67 Phase 3: Added fleet production processing.

Responsibilities:
- Process construction queues for all colonies
- Process construction queues for fleets with space yards
- Spawn completed ships as new fleets (planet) or add to fleet (fleet yards)
- Spawn completed complexes as planetary facilities
"""

import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from game.core.logger import log_info, log_warning
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
    """

    def __init__(self):
        """Initialize the production engine."""
        pass

    def process_production(self, empires: List, galaxy=None, save_path: Optional[str] = None) -> None:
        """
        Process construction queues for all colonies.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for fleet spawning
            save_path: Path to savegame folder for loading designs
        """
        for emp in empires:
            for colony in emp.colonies:
                if not colony.construction_queue:
                    continue

                item: Dict[str, Any] = colony.construction_queue[0]
                vehicle_type = item.get("type", "ship")
                design_id = item["design_id"]

                # Check if item requires shipyard
                if vehicle_type in ["ship", "fighter", "satellite"]:
                    if not colony.has_space_shipyard:
                        log_info(f"Build paused at {colony.name}: no shipyard for {design_id}")
                        continue  # Skip this colony, don't decrement turns

                # Decrement turns now that validation passed
                item["turns_remaining"] -= 1
                turns_remaining = item["turns_remaining"]

                if turns_remaining <= 0:
                    colony.construction_queue.pop(0)
                    log_info(f"Production Complete: {design_id} ({vehicle_type})")

                    # Route to appropriate spawner
                    if vehicle_type == "complex":
                        self._spawn_complex(colony, design_id, emp, save_path)
                    else:
                        self._spawn_ship(colony, design_id, emp, galaxy, save_path)

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

                # Decrement turns
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
