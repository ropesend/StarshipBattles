"""Galaxy spatial query module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles spatial queries for locating systems and entities.
"""
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.data.planet import Planet
    from game.core.hex_math import HexCoord


class GalaxySpatialIndex:
    """Spatial query handler for Galaxy.

    Handles all spatial lookups:
    - Finding systems at locations
    - Finding all fleets within a system
    - Planet and zone location lookups
    - Object-to-system reverse lookups
    """

    def __init__(self, galaxy: 'Galaxy'):
        """Initialize the spatial index.

        Args:
            galaxy: Galaxy instance for shared state access.
        """
        self._galaxy = galaxy

    def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
        """Find the system containing a Fleet (by its global location).

        Auto-routes Planet objects to get_system_of_planet(). Planets have
        local coordinates relative to their system, not global coordinates.

        Args:
            obj: Object with a 'location' attribute (global HexCoord).

        Returns:
            StarSystem or None.
        """
        # Auto-route planets to the correct lookup method (PROJ-184)
        from game.strategy.data.planet import Planet
        if isinstance(obj, Planet):
            return self.get_system_of_planet(obj)

        if not hasattr(obj, 'location'):
            return None

        # If object location matches a system's global_location
        if obj.location in self._galaxy.systems:
            return self._galaxy.systems[obj.location]

        return None

    def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
        """O(1) reverse lookup: Planet -> StarSystem.

        Args:
            planet: Planet to find system for.

        Returns:
            StarSystem containing the planet, or None if not registered.
        """
        return self._galaxy._planet_to_system.get(planet)

    def get_planets_at_global_hex(self, global_hex: 'HexCoord') -> List['Planet']:
        """O(1) spatial lookup: get all planets at a global hex coordinate.

        Args:
            global_hex: Global HexCoord to query.

        Returns:
            List of planets at this hex, or empty list.
        """
        return self._galaxy._global_hex_planets.get(global_hex, [])

    def get_planet_global_hex(self, planet: 'Planet') -> Optional['HexCoord']:
        """O(1) lookup: get the global hex coordinate of a planet.

        Args:
            planet: Planet to get location for.

        Returns:
            Global HexCoord of the planet, or None if planet not registered.
        """
        system = self._galaxy._planet_to_system.get(planet)
        if system:
            return system.global_location + planet.location
        return None

    def get_zones_at_global_hex(self, global_hex: 'HexCoord') -> list:
        """O(1) spatial lookup: get all zone objects at a global hex.

        Args:
            global_hex: Global HexCoord to query.

        Returns:
            List of zone objects (stars, Dyson Spheres) at this hex, or empty list.
        """
        return self._galaxy._global_hex_zones.get(global_hex, [])

    def get_system_at_location(self, location: 'HexCoord') -> Optional['StarSystem']:
        """Find the star system containing a given global hex location.

        O(1) lookup using spatial indexes. Checks if the location is:
        - At a system's global_location
        - At a planet within a system
        - At a zone (star, Dyson Sphere) within a system
        - At a warp point within a system

        Args:
            location: Global HexCoord to search for.

        Returns:
            StarSystem if location is within a system, None if in deep space.
        """
        # O(1) direct system lookup
        if location in self._galaxy.systems:
            return self._galaxy.systems[location]

        # O(1) planet lookup
        planets = self._galaxy._global_hex_planets.get(location, [])
        if planets:
            return self._galaxy._planet_to_system.get(planets[0])

        # O(1) zone lookup (stars, Dyson Spheres)
        zones = self._galaxy._global_hex_zones.get(location, [])
        if zones:
            # Use id() because zone objects (Star, Planet) may not be hashable
            return self._galaxy._zone_to_system.get(id(zones[0]))

        # O(1) warp point lookup
        wp_system = self._galaxy._global_hex_warp_points.get(location)
        if wp_system:
            return wp_system

        return None

    def get_all_fleets_in_system(self, system: 'StarSystem', empires: List) -> List[tuple]:
        """Find all fleets from all empires at any hex within a system.

        Checks the system's global_location plus all planet, star, and
        warp point local offsets.

        Args:
            system: The StarSystem to search within.
            empires: List of Empire objects to search.

        Returns:
            List of (empire, fleet) tuples for all fleets in the system.
        """
        # Build set of all valid hexes in the system
        system_hexes = {system.global_location}

        # Add planet locations
        for planet in system.planets:
            system_hexes.add(system.global_location + planet.location)

        # Add star locations and star zone hexes (PROJ-139)
        for star in system.stars:
            if hasattr(star, 'location'):
                system_hexes.add(system.global_location + star.location)
            # Add star zone hexes
            if hasattr(star, 'occupied_hexes'):
                for local_hex in star.occupied_hexes:
                    system_hexes.add(system.global_location + local_hex)

        # Add planet zone hexes for Dyson Spheres (PROJ-139)
        for planet in system.planets:
            diameter = getattr(planet, 'diameter_hexes', 0)
            if isinstance(diameter, (int, float)) and diameter > 0:
                for local_hex in planet.occupied_hexes:
                    system_hexes.add(system.global_location + local_hex)

        # Add warp point locations
        for wp in system.warp_points:
            system_hexes.add(system.global_location + wp.location)

        # Find all fleets at any of these hexes
        result = []
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location in system_hexes:
                    result.append((empire, fleet))

        return result
