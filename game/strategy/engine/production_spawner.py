"""ProductionSpawner - Handles spawning of completed production items.

PROJ-233: Extracted from ProductionEngine to separate spawn logic from
queue processing logic. Handles ship spawning (new fleets at planets,
added to existing fleets) and facility spawning (complexes on planets).
"""

import logging
import uuid
from typing import Optional, Any, Dict, List, Tuple, TYPE_CHECKING

from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.data.ship_instance import ShipInstance

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.planet import Planet
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.systems.design_library import DesignLibrary

logger = logging.getLogger(__name__)


class ProductionSpawner:
    """Handles spawning of completed production items (ships, complexes).

    PROJ-233: Extracted from ProductionEngine. Owns all entity creation,
    design loading, and event logging for completed construction items.
    """

    def __init__(self, registries: Optional['GameRegistries'] = None, event_bus=None):
        """Initialize the spawner.

        Args:
            registries: Optional GameRegistries for ship creation (DI).
            event_bus: Optional EventBus for structured event logging.
        """
        self._registries = registries
        self._event_bus = event_bus

    def spawn_completed_item(self, item: Dict, empire: 'Empire',
                             colony_or_fleet: Any, galaxy: Optional['Galaxy'],
                             save_path: Optional[str], tick: int) -> None:
        """Dispatch to appropriate spawn method based on item type and context.

        Args:
            item: The completed queue item dict.
            empire: Empire that owns the production.
            colony_or_fleet: Build context (Planet or Fleet).
            galaxy: Galaxy for location resolution.
            save_path: Path to savegame folder.
            tick: Current tick number (for logging).
        """
        design_id = item['design_id']
        vehicle_type = item.get('type', 'ship').lower().replace(' ', '_')

        if isinstance(colony_or_fleet, Fleet):
            if vehicle_type in ('complex', 'planetary_complex'):
                target_planet_id = item.get('target_planet_id')
                self._spawn_fleet_complex(
                    colony_or_fleet, design_id, empire, galaxy, save_path,
                    target_planet_id=target_planet_id
                )
            else:
                self._spawn_fleet_ship(colony_or_fleet, design_id, empire, save_path)
        else:
            # Colony/planet
            if vehicle_type in ('complex', 'planetary_complex'):
                self._create_and_place_facility(
                    colony_or_fleet, design_id, empire, save_path, galaxy
                )
            elif vehicle_type in ('drop_pod', 'fighter'):
                self._spawn_to_staging_yard(
                    colony_or_fleet, design_id, item, empire, save_path
                )
            else:
                self._spawn_ship(colony_or_fleet, design_id, empire, galaxy, save_path)

    # --- Location Resolution ---

    def _resolve_planet_location(
        self, planet: 'Planet', galaxy: Optional['Galaxy']
    ) -> Tuple[Optional[List], str, Optional[List]]:
        """Resolve event logging location info for a planet.

        PROJ-233: Extracted from duplicated blocks in _create_and_place_facility
        and _spawn_ship.

        Returns:
            Tuple of (location_hex, system_name, local_hex) where each may be
            None/empty if galaxy context is unavailable.
        """
        location_hex = None
        system_name = ""
        local_hex = None
        if galaxy and hasattr(galaxy, 'get_system_of_planet'):
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                system_name = parent_sys.name
                if hasattr(planet, 'location') and planet.location is not None:
                    loc = parent_sys.global_location + planet.location
                    location_hex = [loc.q, loc.r]
                    local_hex = [planet.location.q, planet.location.r]
        return location_hex, system_name, local_hex

    # --- Design Loading ---

    def _load_design(self, design_id: str, empire: 'Empire', save_path: Optional[str]) -> dict:
        """Load design data from the design library.

        Args:
            design_id: Design to load.
            empire: Empire owning the design.
            save_path: Path to savegame folder.

        Returns:
            Design data dict, or empty dict on failure.
        """
        if not save_path:
            logger.warning(f"No savegame path - creating empty data for {design_id}")
            return {}
        library = DesignLibrary(save_path, empire.id)
        result = library.load_design_data(design_id)
        if result.success:
            return result.data
        logger.warning(f"Could not load design: {design_id} ({result.error})")
        return {}

    def _load_and_create_ship(
        self, design_id: str, empire: 'Empire', save_path: Optional[str]
    ) -> Optional[ShipInstance]:
        """Load design and create a ship instance.

        Shared by _spawn_ship (colony production) and _spawn_fleet_ship
        (fleet production). Handles design loading, ship creation, and
        built count increment.

        Args:
            design_id: ID of the ship design.
            empire: Empire that owns the design.
            save_path: Path to savegame folder.

        Returns:
            ShipInstance if successful, None on failure.
        """
        if not save_path:
            logger.warning(f"Cannot spawn {design_id}: no save_path provided")
            return None

        design_library = DesignLibrary(save_path, empire.id)
        load_result = design_library.load_design_data(design_id)

        if not load_result.success:
            logger.warning(f"Cannot spawn {design_id}: {load_result.error}")
            return None

        ship_instance = ShipInstance.create(
            design_id=design_id,
            design_data=load_result.data,
            owner_id=empire.id,
            name=load_result.data.get("name", design_id),
            empire=empire,
            registries=self._registries,
        )

        design_library.increment_built_count(design_id)
        return ship_instance

    # --- Spawn Methods ---

    def _create_and_place_facility(
        self, planet: 'Planet', design_id: str, empire: 'Empire',
        save_path: Optional[str], galaxy: Optional['Galaxy'] = None,
        log_prefix: str = ""
    ) -> None:
        """Create a facility and place it on a planet.

        Shared by colony complex production and fleet complex production.
        Handles design loading, facility creation, placement, and event logging.

        Args:
            planet: Planet to add facility to.
            design_id: ID of the complex design.
            empire: Empire that owns the production.
            save_path: Path to savegame folder.
            galaxy: Galaxy for location calculation.
            log_prefix: Optional prefix for log messages (e.g., "Fleet 5 ").
        """
        design_data = self._load_design(design_id, empire, save_path)

        facility = PlanetaryFacility(
            instance_id=str(uuid.uuid4()),
            design_id=design_id,
            name=design_data.get("name", design_id),
            design_data=design_data,
            is_operational=True
        )

        planet.facilities.append(facility)
        logger.info(f"{log_prefix}Built {facility.name} on {planet.name}")

        # Compute location info for event logging (PROJ-233: shared helper)
        location_hex, system_name, local_hex = self._resolve_planet_location(
            planet, galaxy
        )

        suffix = " (fleet yard)" if log_prefix else ""
        if self._event_bus:
            self._event_bus.log_event(
                EventType.COMPLEX_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Built {facility.name} on {planet.name}{suffix}",
                design_id=design_id,
                planet_id=planet.id,
                location_name=planet.name,
                location_hex=location_hex,
                system_name=system_name,
                local_hex=local_hex,
            )

    def _spawn_to_staging_yard(
        self,
        planet: 'Planet',
        design_id: str,
        item: Dict,
        empire: 'Empire',
        save_path: Optional[str],
    ) -> None:
        """Spawn a completed drop pod or fighter to the planet's staging yard.

        Args:
            planet: Planet where the item was built.
            design_id: Design identifier.
            item: Queue item dict with design_data.
            empire: Empire that owns the production.
            save_path: Path to savegame folder.
        """
        design_data = item.get('design_data')
        if not design_data:
            design_data = self._load_design(design_id, empire, save_path)
        if not design_data:
            logger.warning(f"Cannot spawn to staging yard: design '{design_id}' not found")
            return

        # Calculate mass from design using simulation Ship (single source of truth)
        total_mass = 0.0
        if self._registries:
            from game.simulation.entities.ship_design_stats import calculate_design_stats
            stats = calculate_design_stats(design_data, self._registries)
            total_mass = stats.get('mass', 0.0)

        staging_item = {
            'design_id': design_id,
            'name': design_data.get('name', design_id),
            'vehicle_type': item.get('type', 'drop_pod'),
            'design_data': design_data,
            'mass': total_mass,
            'owner_id': empire.id,
        }

        if planet.add_to_staging_yard(staging_item):
            logger.info(
                f"Spawned {staging_item['vehicle_type']} '{staging_item['name']}' "
                f"to staging yard on {planet.name} (mass: {total_mass:.0f})"
            )
        else:
            logger.warning(
                f"Staging yard full on {planet.name}: cannot store "
                f"'{staging_item['name']}' (mass: {total_mass:.0f})"
            )

    def _spawn_ship(
        self,
        planet: 'Planet',
        design_id: str,
        empire: 'Empire',
        galaxy: Optional['Galaxy'],
        save_path: Optional[str] = None
    ) -> None:
        """Spawn ship/satellite/fighter as fleet with ShipInstance.

        Args:
            planet: Planet where ship spawns.
            design_id: ID of the ship design.
            empire: Empire that owns the ship.
            galaxy: Galaxy for location calculation.
            save_path: Path to savegame folder for loading design data.
        """
        ship_instance = self._load_and_create_ship(design_id, empire, save_path)
        if ship_instance is None:
            return

        # Calculate spawn location (PROJ-233: uses shared helper for event fields)
        spawn_loc = planet.location
        system_name = ""
        local_hex = None
        if galaxy:
            parent_sys = galaxy.get_system_of_planet(planet)
            if parent_sys:
                spawn_loc = parent_sys.global_location + planet.location
                system_name = parent_sys.name
                local_hex = [planet.location.q, planet.location.r]

        # Create fleet with globally unique ID from Galaxy
        fleet_id = galaxy.get_next_fleet_id() if galaxy else 0
        display_name = f"Fleet {empire.get_next_fleet_display_number()}"
        new_fleet = Fleet(fleet_id, empire.id, spawn_loc, display_name=display_name)
        new_fleet.add_ship(ship_instance)
        empire.add_fleet(new_fleet)  # PROJ-219: Auto-registers via empire._galaxy

        logger.info(f"Spawned {ship_instance.name} at {spawn_loc} (Fleet {new_fleet.id})")
        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Built {ship_instance.name} at {planet.name}",
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
        empire: 'Empire',
        save_path: Optional[str] = None
    ) -> None:
        """Spawn ship/satellite/fighter and add to the building fleet.

        PROJ-67 Phase 3: Ships built by fleet yards join the fleet directly.

        Args:
            fleet: Fleet building the ship.
            design_id: ID of the ship design.
            empire: Empire that owns the fleet.
            save_path: Path to savegame folder for loading design data.
        """
        ship_instance = self._load_and_create_ship(design_id, empire, save_path)
        if ship_instance is None:
            return

        fleet.add_ship(ship_instance)

        logger.info(f"Fleet {fleet.id} built {ship_instance.name}")
        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIP_BUILT,
                category=EventCategory.PRODUCTION,
                empire_id=empire.id,
                message=f"Fleet {fleet.id} built {ship_instance.name}",
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
        empire: 'Empire',
        galaxy: Optional['Galaxy'],
        save_path: Optional[str] = None,
        target_planet_id: Optional[int] = None
    ) -> None:
        """Spawn complex on planet at fleet's location.

        PROJ-67 Phase 3: Fleet yards can build complexes when at a planet hex.
        PROJ-79 Phase 4: Uses target_planet_id when specified.

        Args:
            fleet: Fleet building the complex.
            design_id: ID of the complex design.
            empire: Empire that owns the fleet.
            galaxy: Galaxy for planet lookup.
            save_path: Path to savegame folder for loading design data.
            target_planet_id: Specific planet ID to receive the complex (PROJ-79).
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

        self._create_and_place_facility(
            planet, design_id, empire, save_path, galaxy,
            log_prefix=f"Fleet {fleet.id} "
        )
