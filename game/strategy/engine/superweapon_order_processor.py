"""
SuperweaponOrderProcessor - Processes superweapon orders during turn execution.

PROJ-102 Phase 6: Turn execution logic for strategic superweapon orders.

Each superweapon order consumes the ship carrying the ability and executes
a galaxy-altering effect (destroy planet, destroy star, open/close warp points,
create Dyson Sphere, or self-destruct).
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import logging

from game.core.hex_math import HexCoord, hex_distance
from game.core.event_logging import log_event
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType

logger = logging.getLogger(__name__)
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.validation.superweapon_validator import SuperweaponValidator
from game.strategy.data.pathfinding import get_system_at_hex

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire


@dataclass
class SuperweaponResult:
    """Result of a superweapon order execution."""
    success: bool
    fleet_consumed: bool = False
    message: str = ""


class SuperweaponOrderProcessor:
    """
    Processor for superweapon order execution during turn processing.

    Each method handles a specific superweapon type:
    - process_implode_planet() - Destroy a target planet
    - process_stellerate_star() - Destroy star and everything in system (suicide)
    - process_open_warp_point() - Create warp link between two systems
    - process_close_warp_point() - Remove warp link between two systems
    - process_create_dyson_sphere() - Encase star in Dyson Sphere
    - process_self_destruct() - Destroy specific ships in fleet
    """

    def __init__(self):
        """Initialize the superweapon order processor."""
        pass

    def _finalize_superweapon(
        self,
        fleet: Fleet,
        empire: 'Empire',
        ship,
        event_type,
        event_message: str,
        log_message: str,
        **event_kwargs
    ) -> SuperweaponResult:
        """
        Finalize superweapon execution after effect is applied.

        Common end-pattern for superweapon methods:
        1. Remove ship from fleet
        2. Pop order
        3. Check if fleet is empty
        4. Remove empty fleet from empire (SG-003 fix)
        5. Log event
        6. Return result

        Args:
            fleet: Fleet with superweapon order
            empire: Empire that owns the fleet
            ship: Ship to remove (the one carrying the superweapon)
            event_type: EventType for logging
            event_message: Message for log_event and result
            log_message: Message for logger.info
            **event_kwargs: Additional kwargs for log_event

        Returns:
            SuperweaponResult with success=True and fleet_consumed flag.
        """
        # Remove ship
        if ship:
            fleet.remove_ship(ship)

        # Pop order
        fleet.pop_order()

        # Check if fleet is now empty
        fleet_consumed = len(fleet.ships) == 0

        # Clean up empty fleet (SG-003 fix)
        if fleet_consumed:
            empire.remove_fleet(fleet)

        # Log
        logger.info(log_message)
        log_event(
            event_type,
            category=EventCategory.SUPERWEAPONS,
            empire_id=empire.id,
            message=event_message,
            fleet_id=fleet.id,
            **event_kwargs
        )

        return SuperweaponResult(
            success=True,
            fleet_consumed=fleet_consumed,
            message=event_message
        )

    def process_implode_planet(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """
        Process an IMPLODE_PLANET order.

        Destroys the target planet, removes the ship with DestroyPlanet ability.

        Args:
            fleet: Fleet with IMPLODE_PLANET order
            empire: Empire that owns the fleet
            galaxy: Galaxy for planet operations
            empires: All empires (needed to remove planet from any owner's colonies)
            component_registry: Component registry for ability lookup

        Returns:
            SuperweaponResult with success status and fleet_consumed flag.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.IMPLODE_PLANET:
            return SuperweaponResult(success=False, message="No IMPLODE_PLANET order")

        target_planet = order.target
        if target_planet is None:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No target planet")

        # Find ship with DestroyPlanet ability
        ship = None
        if component_registry:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "DestroyPlanet", component_registry
            )

        if ship is None:
            logger.warning(f"Fleet {fleet.id}: No ship with DestroyPlanet ability found, canceling order")
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No ship with DestroyPlanet ability")

        # === Execute effect ===
        # Remove planet from colony list if owned (iterate all empires to catch enemy planets)
        if target_planet.owner_id is not None:
            for emp in empires:
                if target_planet in emp.colonies:
                    emp.colonies.remove(target_planet)

        # Unregister planet from galaxy
        galaxy.unregister_planet(target_planet)

        # === Finalize ===
        return self._finalize_superweapon(
            fleet=fleet,
            empire=empire,
            ship=ship,
            event_type=EventType.PLANET_DESTROYED,
            event_message=f"Planet {target_planet.name} destroyed",
            log_message=f"Planet {target_planet.name} destroyed by fleet {fleet.id}",
            planet_id=target_planet.id,
            planet_name=target_planet.name,
        )

    def process_stellerate_star(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """
        Process a STELLERATE_STAR order.

        Destroys all stars and planets in the system, destroys ALL fleets
        (including the executing fleet - this is a suicide weapon).
        Warp points are preserved.

        Args:
            fleet: Fleet with STELLERATE_STAR order
            empire: Empire that owns the fleet
            galaxy: Galaxy for system operations
            empires: All empires (needed to destroy all fleets)
            component_registry: Component registry for ability lookup

        Returns:
            SuperweaponResult with fleet_consumed always True.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.STELLERATE_STAR:
            return SuperweaponResult(success=False, message="No STELLERATE_STAR order")

        # Find system at fleet location
        system = get_system_at_hex(galaxy, fleet.location)
        if system is None:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="Fleet not at a star system")

        system_name = system.name

        # 1. Remove all planets from system and galaxy
        for planet in list(system.planets):
            # Remove from empire colonies if owned
            if planet.owner_id is not None:
                for emp in empires:
                    if planet in emp.colonies:
                        emp.colonies.remove(planet)
            galaxy.unregister_planet(planet)

        # 2. Collect and destroy ALL fleets in the system (including actor)
        all_fleets_in_system = galaxy.get_all_fleets_in_system(system, empires)
        for (owner_empire, victim_fleet) in all_fleets_in_system:
            # Unregister from galaxy (Galaxy always has unregister_fleet)
            galaxy.unregister_fleet(victim_fleet)
            # Remove from empire
            owner_empire.remove_fleet(victim_fleet)

        # 3. Remove all stars (but NOT warp points)
        system.stars = []

        logger.info(f"Star system {system_name} stellerated by fleet {fleet.id}")
        log_event(
            EventType.STAR_DESTROYED,
            category=EventCategory.SUPERWEAPONS,
            empire_id=empire.id,
            message=f"Star system {system_name} destroyed",
            fleet_id=fleet.id,
            system_name=system_name,
        )

        return SuperweaponResult(
            success=True,
            fleet_consumed=True,  # Always - suicide weapon
            message=f"Star system {system_name} destroyed"
        )

    def process_open_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """
        Process an OPEN_WARP_POINT order.

        Creates bidirectional warp points between current system and target system.
        Consumes the ship with OpenWarpPoint ability.

        Args:
            fleet: Fleet with OPEN_WARP_POINT order
            empire: Empire that owns the fleet
            galaxy: Galaxy for warp point operations
            component_registry: Component registry for ability lookup

        Returns:
            SuperweaponResult with success status.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.OPEN_WARP_POINT:
            return SuperweaponResult(success=False, message="No OPEN_WARP_POINT order")

        # Extract target from order
        params = order.target
        if not isinstance(params, dict):
            fleet.pop_order()
            return SuperweaponResult(success=False, message="Invalid warp point params")

        target_system_name = params.get('target_system_name', '')

        # Find current system
        current_system = get_system_at_hex(galaxy, fleet.location)
        if current_system is None:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="Fleet not at a star system")

        # Find target system
        target_system = galaxy.name_map.get(target_system_name)
        if target_system is None:
            fleet.pop_order()
            return SuperweaponResult(
                success=False,
                message=f"Target system '{target_system_name}' not found"
            )

        # Find ship with OpenWarpPoint ability
        ship = None
        if component_registry:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "OpenWarpPoint", component_registry
            )

        if ship is None:
            logger.warning(f"Fleet {fleet.id}: No ship with OpenWarpPoint ability found, canceling order")
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No ship with OpenWarpPoint ability")

        # === Execute effect ===
        # Calculate warp point locations
        # Near-end: at fleet's local position within system
        fleet_local = fleet.location - current_system.global_location
        near_wp = WarpPoint(target_system.name, fleet_local)

        # Far-end: calculate direction from target to current, place at edge
        direction_q = current_system.global_location.q - target_system.global_location.q
        direction_r = current_system.global_location.r - target_system.global_location.r

        # Normalize to unit-ish direction, then scale to typical orbit distance (6 hexes)
        dist = max(abs(direction_q), abs(direction_r), 1)
        orbit_distance = 6
        far_q = round(direction_q / dist * orbit_distance)
        far_r = round(direction_r / dist * orbit_distance)
        far_wp = WarpPoint(current_system.name, HexCoord(far_q, far_r))

        # Add warp points to both systems
        current_system.warp_points.append(near_wp)
        target_system.warp_points.append(far_wp)

        # === Finalize ===
        return self._finalize_superweapon(
            fleet=fleet,
            empire=empire,
            ship=ship,
            event_type=EventType.WARP_POINT_OPENED,
            event_message=f"Warp point opened to {target_system.name}",
            log_message=f"Warp point opened between {current_system.name} and {target_system.name}",
            source_system=current_system.name,
            target_system=target_system.name,
        )

    def process_close_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """
        Process a CLOSE_WARP_POINT order.

        Removes both ends of the warp link. Consumes the ship with CloseWarpPoint ability.

        Args:
            fleet: Fleet with CLOSE_WARP_POINT order
            empire: Empire that owns the fleet
            galaxy: Galaxy for warp point operations
            component_registry: Component registry for ability lookup

        Returns:
            SuperweaponResult with success status.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.CLOSE_WARP_POINT:
            return SuperweaponResult(success=False, message="No CLOSE_WARP_POINT order")

        # Target is destination ID string
        destination_id = order.target
        if not destination_id:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No destination specified")

        # Find current system
        current_system = get_system_at_hex(galaxy, fleet.location)
        if current_system is None:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="Fleet not at a star system")

        # Find ship with CloseWarpPoint ability
        ship = None
        if component_registry:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "CloseWarpPoint", component_registry
            )

        if ship is None:
            logger.warning(f"Fleet {fleet.id}: No ship with CloseWarpPoint ability found, canceling order")
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No ship with CloseWarpPoint ability")

        # === Execute effect ===
        # Remove warp link (both ends)
        galaxy.remove_warp_link(current_system.name, destination_id)

        # === Finalize ===
        return self._finalize_superweapon(
            fleet=fleet,
            empire=empire,
            ship=ship,
            event_type=EventType.WARP_POINT_CLOSED,
            event_message=f"Warp point to {destination_id} closed",
            log_message=f"Warp point closed between {current_system.name} and {destination_id}",
            source_system=current_system.name,
            target_system=destination_id,
        )

    def process_create_dyson_sphere(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """
        Process a CREATE_DYSON_SPHERE order.

        Removes star and nearby planets (<= 9 hexes), creates Dyson Sphere planet.
        Consumes the ship with CreateDysonSphere ability.

        Args:
            fleet: Fleet with CREATE_DYSON_SPHERE order
            empire: Empire that owns the fleet
            galaxy: Galaxy for system operations
            empires: All empires (needed to remove planets from any owner's colonies)
            component_registry: Component registry for ability lookup

        Returns:
            SuperweaponResult with success status.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.CREATE_DYSON_SPHERE:
            return SuperweaponResult(success=False, message="No CREATE_DYSON_SPHERE order")

        # Find system at fleet location
        system = get_system_at_hex(galaxy, fleet.location)
        if system is None:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="Fleet not at a star system")

        if not system.stars:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="System has no stars")

        # Get primary star location for distance calculations
        primary_star = system.stars[0]
        star_loc = primary_star.location

        # Find ship with CreateDysonSphere ability
        ship = None
        if component_registry:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "CreateDysonSphere", component_registry
            )

        if ship is None:
            logger.warning(f"Fleet {fleet.id}: No ship with CreateDysonSphere ability found, canceling order")
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No ship with CreateDysonSphere ability")

        # === Execute effect ===
        # Remove planets within zone radius (5 hexes for 11-hex diameter sphere)
        dyson_radius = 5
        planets_to_remove = []
        for planet in system.planets:
            dist = hex_distance(planet.location, star_loc)
            if dist <= dyson_radius:
                planets_to_remove.append(planet)

        for planet in planets_to_remove:
            # Remove from empire colonies if owned (iterate all empires to catch enemy planets)
            if planet.owner_id is not None:
                for emp in empires:
                    if planet in emp.colonies:
                        emp.colonies.remove(planet)
            galaxy.unregister_planet(planet)

        # Remove all stars
        system.stars = []

        # Extract environmental conditions from creator's race_config
        race = empire.race_config if empire else None
        if race:
            # Use race's ideal conditions for perfect habitability
            gravity = race.gravity_ideal * 9.81  # Convert g to m/s^2
            temperature = race.temperature_ideal
            water = race.water_ideal
            # Build atmosphere from positive preferences (scaled to partial pressure)
            atmosphere = {}
            for gas, preference in race.atmosphere_preferences.items():
                if preference > 0:
                    # Scale preference (0-100) to partial pressure (mbar)
                    atmosphere[gas] = preference * 10.0  # e.g., 21% O2 -> 210 mbar
        else:
            # Fallback to human-comfortable defaults
            gravity = 9.81  # 1g
            temperature = 288.0  # ~15°C
            water = 0.3
            atmosphere = {"Oxygen": 210.0, "Nitrogen": 780.0}  # Earth-like

        # Create Dyson Sphere planet at system center
        # Dyson Sphere properties (mega-engineering structure enclosing a star)
        dyson = Planet(
            name=f"Dyson Sphere ({system.name})",
            location=HexCoord(0, 0),
            orbit_distance=0,
            mass=2e30,  # ~1 solar mass (enclosing material)
            radius=1.5e11,  # ~1 AU radius
            surface_area=1e18,  # Massive surface area (inner surface)
            density=1.0,  # Very thin shell
            surface_gravity=gravity,  # From race_config or default
            surface_pressure=101325.0,  # 1 ATM
            surface_temperature=temperature,  # From race_config or default
            surface_water=water,  # From race_config or default
            atmosphere=atmosphere,  # From race_config or default
            tectonic_activity=0.0,  # No tectonics (artificial)
            magnetic_field=1.0,  # Engineered shielding
            planet_type=PlanetType.DYSON_SPHERE,
            image_id="Sphereworld_Portrait.png",
            diameter_hexes=11.0,  # Multi-hex zone (11-hex diameter)
        )

        # Add to system and register with galaxy
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # === Finalize ===
        return self._finalize_superweapon(
            fleet=fleet,
            empire=empire,
            ship=ship,
            event_type=EventType.DYSON_SPHERE_CREATED,
            event_message=f"Dyson Sphere created in {system.name}",
            log_message=f"Dyson Sphere created in {system.name}",
            system_name=system.name,
        )

    def process_self_destruct(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy
    ) -> SuperweaponResult:
        """
        Process a SELF_DESTRUCT order.

        Removes the specified ships from the fleet.

        Args:
            fleet: Fleet with SELF_DESTRUCT order
            empire: Empire that owns the fleet
            galaxy: Galaxy (unused, for signature consistency)

        Returns:
            SuperweaponResult with success status.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.SELF_DESTRUCT:
            return SuperweaponResult(success=False, message="No SELF_DESTRUCT order")

        # Target is list of ship IDs
        ship_ids = order.target
        if not isinstance(ship_ids, list) or not ship_ids:
            fleet.pop_order()
            return SuperweaponResult(success=False, message="No ships specified")

        # Build ship lookup
        ships_by_id = {ship.id: ship for ship in fleet.ships}

        # Collect ships to remove
        ships_to_remove = []
        ship_names = []
        for ship_id in ship_ids:
            ship = ships_by_id.get(ship_id)
            if ship:
                ships_to_remove.append(ship)
                # Get name - ship.name always exists on ShipInstance
                name = ship.name if isinstance(ship.name, str) else str(ship_id)
                ship_names.append(name)

        # Remove ships
        for ship in ships_to_remove:
            fleet.remove_ship(ship)

        fleet.pop_order()

        # Check if fleet is now empty
        fleet_consumed = len(fleet.ships) == 0

        # Clean up empty fleet (SG-003 fix)
        if fleet_consumed:
            empire.remove_fleet(fleet)

        logger.info(f"Ships self-destructed: {', '.join(ship_names)}")
        log_event(
            EventType.SHIPS_SELF_DESTRUCTED,
            category=EventCategory.SUPERWEAPONS,
            empire_id=empire.id,
            message=f"{len(ships_to_remove)} ships self-destructed",
            fleet_id=fleet.id,
            ship_count=len(ships_to_remove),
            ship_names=ship_names,
        )

        return SuperweaponResult(
            success=True,
            fleet_consumed=fleet_consumed,
            message=f"{len(ships_to_remove)} ships self-destructed"
        )
