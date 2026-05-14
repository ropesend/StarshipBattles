"""Galaxy entity registry module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles entity lifecycle management (planets, fleets, zones).

PROJ-372 Phase 3: switched from ``_galaxy: Galaxy`` back-pointer to
``_state: GalaxyState`` — services are now unit-testable without
constructing a real ``Galaxy()``.
"""
from typing import Optional, TYPE_CHECKING

from game.core.protocols import is_zone_occupant

if TYPE_CHECKING:
    from game.strategy.data.star_system import StarSystem
    from game.strategy.data.galaxy_state import GalaxyState
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet


class GalaxyEntityRegistry:
    """Entity lifecycle manager for Galaxy.

    Handles registration, unregistration, and lookup of:
    - Planets (with ID assignment and spatial indexing)
    - Fleets (with ID-based lookup + ID generation)
    - Zones (multi-hex objects like stars and Dyson Spheres)
    """

    def __init__(self, state: 'GalaxyState'):
        """Initialize with the Galaxy's state container.

        Args:
            state: GalaxyState instance shared with the Galaxy facade.
        """
        self._state = state

    # ---- System registration (PROJ-372 Phase 3: moved from Galaxy.add_system) ----

    def add_system(self, system: 'StarSystem') -> None:
        """Add a system to the galaxy map and register its zones / warp points."""
        self._state.systems[system.global_location] = system
        self._state.name_map[system.name] = system
        self._register_zones_from_system(system)
        self._rebuild_warp_point_index_for(system)

    def _register_zones_from_system(self, system: 'StarSystem') -> None:
        """PROJ-204: register every star and storm zone on a system."""
        for star in system.stars:
            self.register_zone(system, star)
        for storm in system.storms:
            self.register_zone(system, storm)

    def _rebuild_warp_point_index_for(self, system: 'StarSystem') -> None:
        """PROJ-204: index a system's warp points into the global table."""
        for wp in system.warp_points:
            global_hex = system.global_location + wp.location
            self._state.global_hex_warp_points[global_hex] = system

    def rebuild_all_warp_point_indices(self) -> None:
        """PROJ-204: clear + rebuild the global warp index over all systems."""
        self._state.global_hex_warp_points.clear()
        for system in self._state.systems.values():
            self._rebuild_warp_point_index_for(system)

    # ---- Planet registry ----

    def _index_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Index a planet in all galaxy lookups (shared by register/restore).

        Args:
            system: StarSystem containing the planet.
            planet: Planet to index (must have id already set).
        """
        self._state.planets_by_id[planet.id] = planet
        self._state.planet_to_system[planet] = system

        global_hex = system.global_location + planet.location
        self._state.global_hex_planets.setdefault(global_hex, []).append(planet)

        # Register zone if planet has multi-hex footprint (PROJ-139)
        if planet.radius_hexes > 0:
            self.register_zone(system, planet)

    def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet, assign next ID, and update indexes."""
        planet.id = self._state.next_planet_id
        self._state.next_planet_id += 1
        self._index_planet(system, planet)

    def restore_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet whose ID is already set (deserialization path)."""
        self._index_planet(system, planet)

    def get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """O(1) lookup of planet by ID."""
        return self._state.planets_by_id.get(planet_id)

    def unregister_planet(self, planet: 'Planet') -> None:
        """Remove a planet from all galaxy indexes and its parent system."""
        self._state.planets_by_id.pop(planet.id, None)
        system = self._state.planet_to_system.pop(planet, None)

        if system is not None:
            if planet.radius_hexes > 0:
                self.unregister_zone(system, planet)

            global_hex = system.global_location + planet.location
            if global_hex in self._state.global_hex_planets:
                planets_at_hex = self._state.global_hex_planets[global_hex]
                if planet in planets_at_hex:
                    planets_at_hex.remove(planet)
                if not planets_at_hex:
                    del self._state.global_hex_planets[global_hex]

            if planet in system.planets:
                system.planets.remove(planet)

    # ---- Fleet registry ----

    def get_next_fleet_id(self) -> int:
        """Generate globally unique sequential fleet ID.

        All empires share one counter to prevent ID collisions in the
        galaxy-wide fleets_by_id registry.
        """
        fleet_id = self._state.next_fleet_id
        self._state.next_fleet_id += 1
        return fleet_id

    def register_fleet(self, fleet: 'Fleet') -> None:
        """Register a fleet for O(1) lookup by ID."""
        self._state.fleets_by_id[fleet.id] = fleet

    def unregister_fleet(self, fleet: 'Fleet') -> None:
        """Remove a fleet from the registry."""
        self._state.fleets_by_id.pop(fleet.id, None)

    def get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """O(1) lookup of fleet by ID."""
        return self._state.fleets_by_id.get(fleet_id)

    # ---- Zone registry ----

    def register_zone(self, system: 'StarSystem', obj) -> None:
        """Register a multi-hex zone object (star, Dyson Sphere) in the index."""
        if not is_zone_occupant(obj):
            return
        # Use id() because Star objects are not hashable.
        self._state.zone_to_system[id(obj)] = system
        for local_hex in obj.occupied_hexes:
            global_hex = system.global_location + local_hex
            zones = self._state.global_hex_zones.setdefault(global_hex, [])
            if obj not in zones:
                zones.append(obj)

    def unregister_zone(self, system: 'StarSystem', obj) -> None:
        """Remove a multi-hex zone object from the zone index."""
        if not is_zone_occupant(obj):
            return
        self._state.zone_to_system.pop(id(obj), None)
        for local_hex in obj.occupied_hexes:
            global_hex = system.global_location + local_hex
            if global_hex in self._state.global_hex_zones:
                zone_list = self._state.global_hex_zones[global_hex]
                if obj in zone_list:
                    zone_list.remove(obj)
                if not zone_list:
                    del self._state.global_hex_zones[global_hex]
