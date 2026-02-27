"""Galaxy entity registry module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles entity lifecycle management (planets, fleets, zones).
"""
from typing import Optional, TYPE_CHECKING

from game.core.protocols import is_zone_occupant

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet
    from game.core.hex_math import HexCoord


class GalaxyEntityRegistry:
    """Entity lifecycle manager for Galaxy.

    Handles registration, unregistration, and lookup of:
    - Planets (with ID assignment and spatial indexing)
    - Fleets (with ID-based lookup)
    - Zones (multi-hex objects like stars and Dyson Spheres)
    """

    def __init__(self, galaxy: 'Galaxy'):
        """Initialize the entity registry.

        Args:
            galaxy: Galaxy instance for shared state access.
        """
        self._galaxy = galaxy

    def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet with the galaxy, assigning ID and updating indexes.

        Args:
            system: StarSystem containing the planet.
            planet: Planet to register.
        """
        # Assign unique ID
        planet.id = self._galaxy._next_planet_id
        self._galaxy._next_planet_id += 1

        # Add to ID registry
        self._galaxy.planets_by_id[planet.id] = planet

        # Add to reverse lookup
        self._galaxy._planet_to_system[planet] = system

        # Add to spatial index (global hex)
        global_hex = system.global_location + planet.location
        if global_hex not in self._galaxy._global_hex_planets:
            self._galaxy._global_hex_planets[global_hex] = []
        self._galaxy._global_hex_planets[global_hex].append(planet)

        # Register zone if planet has multi-hex footprint (PROJ-139)
        if planet.diameter_hexes > 0:
            self.register_zone(system, planet)

    def restore_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet with pre-existing ID (for deserialization).

        Unlike register_planet(), this does NOT assign a new ID.
        The planet.id must already be set (from Planet.from_dict()).

        Args:
            system: StarSystem containing the planet.
            planet: Planet to register (must have id already set).
        """
        # Add to ID registry (preserving existing ID)
        self._galaxy.planets_by_id[planet.id] = planet

        # Add to reverse lookup
        self._galaxy._planet_to_system[planet] = system

        # Add to spatial index (global hex)
        global_hex = system.global_location + planet.location
        if global_hex not in self._galaxy._global_hex_planets:
            self._galaxy._global_hex_planets[global_hex] = []
        self._galaxy._global_hex_planets[global_hex].append(planet)

        # Register zone if planet has multi-hex footprint (PROJ-139)
        if planet.diameter_hexes > 0:
            self.register_zone(system, planet)

    def get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """O(1) lookup of planet by ID.

        Args:
            planet_id: Planet ID to find.

        Returns:
            Planet if found, None otherwise.
        """
        return self._galaxy.planets_by_id.get(planet_id)

    def unregister_planet(self, planet: 'Planet') -> None:
        """Remove a planet from all galaxy indexes and its parent system.

        Args:
            planet: The planet to unregister.
        """
        # Remove from ID registry
        self._galaxy.planets_by_id.pop(planet.id, None)

        # Get system before removing from lookup
        system = self._galaxy._planet_to_system.pop(planet, None)

        # Remove from spatial index and zone registry
        if system is not None:
            # Unregister zone if planet has multi-hex footprint (PROJ-139)
            if planet.diameter_hexes > 0:
                self.unregister_zone(system, planet)

            global_hex = system.global_location + planet.location
            if global_hex in self._galaxy._global_hex_planets:
                planets_at_hex = self._galaxy._global_hex_planets[global_hex]
                if planet in planets_at_hex:
                    planets_at_hex.remove(planet)
                # Clean up empty list
                if not planets_at_hex:
                    del self._galaxy._global_hex_planets[global_hex]

            # Remove from system's planets list
            if planet in system.planets:
                system.planets.remove(planet)

    def register_fleet(self, fleet: 'Fleet') -> None:
        """Register a fleet for O(1) lookup by ID.

        Args:
            fleet: Fleet object to register.
        """
        self._galaxy.fleets_by_id[fleet.id] = fleet

    def unregister_fleet(self, fleet: 'Fleet') -> None:
        """Remove a fleet from the registry.

        Args:
            fleet: Fleet object to unregister.
        """
        self._galaxy.fleets_by_id.pop(fleet.id, None)

    def get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """O(1) lookup of fleet by ID.

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        return self._galaxy.fleets_by_id.get(fleet_id)

    def register_zone(self, system: 'StarSystem', obj) -> None:
        """Register a multi-hex zone object (star, Dyson Sphere) in the zone index.

        Args:
            system: The StarSystem containing the object.
            obj: Object with an occupied_hexes property (IZoneOccupant).
        """
        if not is_zone_occupant(obj):
            return
        # Register in zone-to-system reverse lookup (PROJ-179: O(1) lookup)
        # Use id() because Star objects are not hashable
        self._galaxy._zone_to_system[id(obj)] = system
        for local_hex in obj.occupied_hexes:
            global_hex = system.global_location + local_hex
            if global_hex not in self._galaxy._global_hex_zones:
                self._galaxy._global_hex_zones[global_hex] = []
            if obj not in self._galaxy._global_hex_zones[global_hex]:
                self._galaxy._global_hex_zones[global_hex].append(obj)

    def unregister_zone(self, system: 'StarSystem', obj) -> None:
        """Remove a multi-hex zone object from the zone index.

        Args:
            system: The StarSystem containing the object.
            obj: Object with an occupied_hexes property (IZoneOccupant).
        """
        if not is_zone_occupant(obj):
            return
        # Remove from zone-to-system reverse lookup (PROJ-179: O(1) lookup)
        self._galaxy._zone_to_system.pop(id(obj), None)
        for local_hex in obj.occupied_hexes:
            global_hex = system.global_location + local_hex
            if global_hex in self._galaxy._global_hex_zones:
                zone_list = self._galaxy._global_hex_zones[global_hex]
                if obj in zone_list:
                    zone_list.remove(obj)
                if not zone_list:
                    del self._galaxy._global_hex_zones[global_hex]
