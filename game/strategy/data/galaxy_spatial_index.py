"""Galaxy spatial query module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
Handles spatial queries for locating systems and entities.

PROJ-372 Phase 3: switched from ``_galaxy: Galaxy`` back-pointer to
``_state: GalaxyState``.
"""
from typing import Any, List, Optional, TYPE_CHECKING

from game.core.protocols import is_planet, is_zone_occupant

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.galaxy_state import GalaxyState
    from game.strategy.data.planet import Planet


class GalaxySpatialIndex:
    """Spatial query handler for Galaxy.

    All lookups are O(1) using GalaxyState's pre-built indexes.
    """

    def __init__(self, state: 'GalaxyState'):
        """Initialize with the Galaxy's state container."""
        self._state = state

    def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
        """Find the system containing a Fleet (by its global location).

        Auto-routes Planet objects to ``get_system_of_planet`` (planets
        have local coordinates, not global).
        """
        # PROJ-382 Phase 2 (Pattern #2): use TypeGuard instead of importing
        # the concrete strategy.data.Planet class for runtime narrowing.
        if is_planet(obj):
            return self.get_system_of_planet(obj)

        if not hasattr(obj, 'location'):
            return None

        if obj.location in self._state.systems:
            return self._state.systems[obj.location]

        return None

    def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
        """O(1) reverse lookup: Planet -> StarSystem."""
        return self._state.planet_to_system.get(planet)

    def get_planets_at_global_hex(self, global_hex: 'HexCoord') -> List['Planet']:
        """O(1) spatial lookup: planets at a global hex coordinate."""
        return self._state.global_hex_planets.get(global_hex, [])

    def get_planet_global_hex(self, planet: 'Planet') -> Optional['HexCoord']:
        """O(1) lookup: get the global hex coordinate of a planet."""
        system = self._state.planet_to_system.get(planet)
        if system:
            return system.global_location + planet.location
        return None

    def get_zones_at_global_hex(self, global_hex: 'HexCoord') -> list:
        """O(1) spatial lookup: zone objects at a global hex."""
        return self._state.global_hex_zones.get(global_hex, [])

    def get_system_at_location(self, location: 'HexCoord') -> Optional['StarSystem']:
        """Find the star system containing a given global hex location.

        O(1) lookup using spatial indexes. Checks (in order): system
        global_location, planets, zones, warp points.
        """
        if location in self._state.systems:
            return self._state.systems[location]

        planets = self._state.global_hex_planets.get(location, [])
        if planets:
            return self._state.planet_to_system.get(planets[0])

        zones = self._state.global_hex_zones.get(location, [])
        if zones:
            return self._state.zone_to_system.get(id(zones[0]))

        wp_system = self._state.global_hex_warp_points.get(location)
        if wp_system:
            return wp_system

        return None

    def get_all_fleets_in_system(self, system: 'StarSystem', empires: List) -> List[tuple]:
        """Find all fleets from all empires at any hex within a system.

        Checks the system's global_location plus all planet, star, and
        warp point local offsets.
        """
        system_hexes = {system.global_location}

        for planet in system.planets:
            system_hexes.add(system.global_location + planet.location)

        for star in system.stars:
            system_hexes.add(system.global_location + star.location)
            if is_zone_occupant(star):
                for local_hex in star.occupied_hexes:
                    system_hexes.add(system.global_location + local_hex)

        for planet in system.planets:
            if planet.radius_hexes > 0:
                for local_hex in planet.occupied_hexes:
                    system_hexes.add(system.global_location + local_hex)

        for wp in system.warp_points:
            system_hexes.add(system.global_location + wp.location)

        result = []
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location in system_hexes:
                    result.append((empire, fleet))

        return result
