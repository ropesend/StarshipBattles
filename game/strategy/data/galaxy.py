import random
from enum import Enum, auto
from typing import Any, Dict, List, Optional, TYPE_CHECKING
# hex_to_pixel/pixel_to_hex: Used for geometric calculations (angles, distances),
# not rendering. These convert hex coords to/from Cartesian for trigonometry.
from game.core.hex_math import HexCoord, hex_to_dict, hex_from_dict
from game.core.validation_helpers import require_keys, validate_positive
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
import logging
from game.strategy.data.naming import NameRegistry
import os

from game.strategy.data.stars import StarGenerator, Star
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.storm import Storm
from game.strategy.data.planet_gen import PlanetGenerator
from game.strategy.generation.planet_image_registry import PlanetImageRegistry
from game.strategy.generation.storm_generator import StormGenerator
from game.strategy.data.galaxy_warp_generator import GalaxyWarpGenerator
from game.strategy.data.galaxy_system_generator import GalaxySystemGenerator
from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry
from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex
from game.core.json_utils import load_json

if TYPE_CHECKING:
    from game.strategy.generation.placement_strategies import ISystemPlacementStrategy
    from game.strategy.generation.region_classifier import RegionClassifier
    from game.strategy.data.fleet import Fleet


class WarpPoint:
    def __init__(self, destination_id, location):
        self.destination_id = destination_id
        self.location = location # HexCoord (Local to system)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize WarpPoint to dict."""
        return {
            'destination_id': self.destination_id,
            'location': hex_to_dict(self.location)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WarpPoint':
        """Deserialize WarpPoint from dict.

        Raises:
            PersistenceException: If required keys missing or location is malformed.
        """
        require_keys(data, ['destination_id', 'location'], 'WarpPoint')

        try:
            location = hex_from_dict(data['location'])
        except (KeyError, TypeError) as e:
            raise PersistenceException(
                f"WarpPoint: invalid location format - {type(e).__name__}: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": "WarpPoint",
                    "field": "location",
                    "value": data.get('location'),
                    "error": str(e),
                }
            ) from e

        return cls(
            destination_id=data['destination_id'],
            location=location
        )

class StarSystem:
    def __init__(self, name, global_location, stars=None, region_id=None):
        self.name = name
        self.global_location = global_location # HexCoord
        self.stars = stars if stars else []
        self.warp_points = []
        self.planets = [] # List[Planet]
        self.storms = []  # List[Storm] - environmental hazards (PROJ-189)
        self.region_id = region_id  # Optional[int] - which arm/cluster this belongs to

    @property
    def primary_star(self):
        return self.stars[0] if self.stars else None

    def add_warp_point(self, destination_id, location):
        self.warp_points.append(WarpPoint(destination_id, location))

    def __repr__(self):
        star_count = len(self.stars)
        p_name = self.primary_star.name if self.primary_star else "Empty"
        return f"System('{self.name}', Loc:{self.global_location}, Stars:{star_count}, Primary:{p_name})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize StarSystem to dict."""
        result = {
            'name': self.name,
            'global_location': hex_to_dict(self.global_location),
            'stars': [star.to_dict() for star in self.stars],
            'warp_points': [wp.to_dict() for wp in self.warp_points],
            'planets': [planet.to_dict() for planet in self.planets],
            'storms': [s.to_dict() for s in self.storms]
        }
        if self.region_id is not None:
            result['region_id'] = self.region_id
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'StarSystem':
        """Deserialize StarSystem from dict.

        Raises:
            PersistenceException: If required keys missing.

        Note:
            Invalid children (stars, planets, warp points) are skipped with
            a warning log to allow resilient degradation.
        """
        from game.core.json_utils import deserialize_list

        require_keys(data, ['name', 'global_location'], 'StarSystem')
        parent_name = f"StarSystem '{data['name']}'"

        # Deserialize stars with error isolation
        stars = deserialize_list(
            data.get('stars', []), Star.from_dict, 'star', parent_name
        )

        system = cls(
            name=data['name'],
            global_location=hex_from_dict(data['global_location']),
            stars=stars,
            region_id=data.get('region_id')
        )

        # Deserialize warp points with error isolation
        system.warp_points = deserialize_list(
            data.get('warp_points', []), WarpPoint.from_dict, 'warp point', parent_name
        )

        # Deserialize planets with error isolation
        system.planets = deserialize_list(
            data.get('planets', []), Planet.from_dict, 'planet', parent_name
        )

        # Deserialize storms with error isolation (PROJ-189)
        system.storms = deserialize_list(
            data.get('storms', []), Storm.from_dict, 'storm', parent_name
        )

        return system

class Galaxy:
    def __init__(self, radius=100):
        self.radius = radius
        self.systems = {} # keys: HexCoord, values: StarSystem
        self.name_map = {} # keys: str (name), values: StarSystem
        
        # Entity Registries (Issue #1 fix: proper IDs instead of id())
        self._next_planet_id = 1
        self.planets_by_id = {}  # int -> Planet
        
        # Spatial Indexes (Issue #2 fix: O(1) lookups instead of O(n²))
        self._planet_to_system = {}    # Planet -> StarSystem
        self._global_hex_planets = {}  # HexCoord -> List[Planet]

        # Zone Registry (PROJ-139 Phase 2: multi-hex object lookup)
        self._global_hex_zones = {}    # HexCoord -> List[object] (stars, Dyson Spheres)
        self._zone_to_system = {}      # object -> StarSystem (PROJ-179: O(1) zone lookup)

        # Warp Point Index (PROJ-179 Phase 2: O(1) warp point lookup)
        self._global_hex_warp_points = {}  # HexCoord -> StarSystem

        # Fleet Registry (PROJ-87 Phase 6: O(1) fleet lookup)
        self.fleets_by_id = {}  # int -> Fleet
        
        # Initialize Naming Registry
        data_path = os.path.join(os.getcwd(), 'data', 'StarSystemNames.YAML')
        self.naming = NameRegistry(data_path)
        self.star_generator = StarGenerator()
        self.image_registry = PlanetImageRegistry()
        self.planet_generator = PlanetGenerator(self.image_registry)

        # Load storm definitions and create storm generator (PROJ-189)
        storms_path = os.path.join(os.getcwd(), 'data', 'storms.json')
        storm_defs = load_json(storms_path, default={})
        self.storm_generator = StormGenerator(storm_defs) if storm_defs else None

        # Internal delegates (PROJ-173 Phase 2)
        self._warp_gen = GalaxyWarpGenerator()
        self._sys_gen = GalaxySystemGenerator(
            self.star_generator, self.planet_generator, self.naming, self.image_registry,
            storm_generator=self.storm_generator
        )
        self._registry = GalaxyEntityRegistry(self)
        self._spatial = GalaxySpatialIndex(self)
        
    def add_system(self, system):
        """Add a system to the galaxy map."""
        self.systems[system.global_location] = system
        self.name_map[system.name] = system
        # PROJ-204: Shared zone and warp point registration
        self._register_zones_from_system(system)
        self._rebuild_warp_point_index(system)

    def _register_zones_from_system(self, system: 'StarSystem') -> None:
        """Register all star and storm zones from a system.

        PROJ-204 Phase 2: Consolidates duplicated zone registration (CQ-26).

        Args:
            system: The StarSystem whose zones to register.
        """
        for star in system.stars:
            self.register_zone(system, star)
        for storm in system.storms:
            self.register_zone(system, storm)

    def _rebuild_warp_point_index(self, system: 'StarSystem') -> None:
        """Add warp points from a system to the global hex index.

        PROJ-204 Phase 2: Consolidates duplicated warp point indexing (CQ-27).

        Args:
            system: The StarSystem whose warp points to index.
        """
        for wp in system.warp_points:
            global_hex = system.global_location + wp.location
            self._global_hex_warp_points[global_hex] = system

    def _rebuild_all_warp_point_indices(self) -> None:
        """Rebuild the warp point index for all systems.

        PROJ-204 Phase 2: Consolidates full rebuild after warp generation (CQ-27).
        Call after bulk warp point changes (e.g., generate_warp_lanes).
        """
        self._global_hex_warp_points.clear()
        for system in self.systems.values():
            self._rebuild_warp_point_index(system)

    def get_system_by_name(self, name: str) -> Optional['StarSystem']:
        """Get system by name."""
        return self.name_map.get(name)

    def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
        """Find the system containing a Fleet (by its global location).

        Facade method delegating to GalaxySpatialIndex.

        Auto-routes Planet objects to get_system_of_planet(). Planets have
        local coordinates relative to their system, not global coordinates.

        Args:
            obj: Object with a 'location' attribute (global HexCoord).

        Returns:
            StarSystem or None.
        """
        return self._spatial.get_system_of_object(obj)
    
    def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet with the galaxy, assigning ID and updating indexes.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            system: StarSystem containing the planet.
            planet: Planet to register.
        """
        self._registry.register_planet(system, planet)

    def get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """O(1) lookup of planet by ID.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            planet_id: Planet ID to find.

        Returns:
            Planet if found, None otherwise.
        """
        return self._registry.get_planet_by_id(planet_id)
    
    def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
        """O(1) reverse lookup: Planet -> StarSystem.

        Facade method delegating to GalaxySpatialIndex.

        Args:
            planet: Planet to find system for.

        Returns:
            StarSystem containing the planet, or None if not registered.
        """
        return self._spatial.get_system_of_planet(planet)

    def get_planets_at_global_hex(self, global_hex: 'HexCoord') -> List['Planet']:
        """O(1) spatial lookup: get all planets at a global hex coordinate.

        Facade method delegating to GalaxySpatialIndex.

        Args:
            global_hex: Global HexCoord to query.

        Returns:
            List of planets at this hex, or empty list.
        """
        return self._spatial.get_planets_at_global_hex(global_hex)

    def get_planet_global_hex(self, planet: 'Planet') -> Optional['HexCoord']:
        """O(1) lookup: get the global hex coordinate of a planet.

        Facade method delegating to GalaxySpatialIndex.

        Args:
            planet: Planet to get location for.

        Returns:
            Global HexCoord of the planet, or None if planet not registered.
        """
        return self._spatial.get_planet_global_hex(planet)

    # --- Zone Registry Methods (PROJ-139 Phase 2: multi-hex zones) ---
    # Facade methods delegating to GalaxyEntityRegistry

    def register_zone(self, system: 'StarSystem', obj) -> None:
        """Register a multi-hex zone object (star, Dyson Sphere) in the zone index.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            system: The StarSystem containing the object.
            obj: Object with an occupied_hexes property (IZoneOccupant).
        """
        self._registry.register_zone(system, obj)

    def unregister_zone(self, system: 'StarSystem', obj) -> None:
        """Remove a multi-hex zone object from the zone index.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            system: The StarSystem containing the object.
            obj: Object with an occupied_hexes property (IZoneOccupant).
        """
        self._registry.unregister_zone(system, obj)

    def get_zones_at_global_hex(self, global_hex: 'HexCoord') -> list:
        """O(1) spatial lookup: get all zone objects at a global hex.

        Facade method delegating to GalaxySpatialIndex.

        Args:
            global_hex: Global HexCoord to query.

        Returns:
            List of zone objects (stars, Dyson Spheres) at this hex, or empty list.
        """
        return self._spatial.get_zones_at_global_hex(global_hex)

    # --- Fleet Registry Methods (PROJ-87 Phase 6) ---
    # Facade methods delegating to GalaxyEntityRegistry

    def register_fleet(self, fleet: 'Fleet') -> None:
        """Register a fleet for O(1) lookup by ID.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            fleet: Fleet object to register.
        """
        self._registry.register_fleet(fleet)

    def unregister_fleet(self, fleet: 'Fleet') -> None:
        """Remove a fleet from the registry.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            fleet: Fleet object to unregister.
        """
        self._registry.unregister_fleet(fleet)

    def get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """O(1) lookup of fleet by ID.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        return self._registry.get_fleet_by_id(fleet_id)

    def unregister_planet(self, planet: 'Planet') -> None:
        """Remove a planet from all galaxy indexes and its parent system.

        Facade method delegating to GalaxyEntityRegistry.

        Args:
            planet: The planet to unregister.
        """
        self._registry.unregister_planet(planet)

    def remove_warp_link(self, system_a_name: str, system_b_name: str) -> None:
        """Remove warp points connecting two systems.

        Removes warp points from both systems that link to each other.
        Handles missing systems gracefully.

        Args:
            system_a_name: Name of the first system.
            system_b_name: Name of the second system.
        """
        system_a = self.name_map.get(system_a_name)
        system_b = self.name_map.get(system_b_name)

        if system_a is not None:
            # Remove from warp point index (PROJ-179: O(1) lookup)
            for wp in system_a.warp_points:
                if wp.destination_id == system_b_name:
                    global_hex = system_a.global_location + wp.location
                    self._global_hex_warp_points.pop(global_hex, None)
            system_a.warp_points = [
                wp for wp in system_a.warp_points
                if wp.destination_id != system_b_name
            ]

        if system_b is not None:
            # Remove from warp point index (PROJ-179: O(1) lookup)
            for wp in system_b.warp_points:
                if wp.destination_id == system_a_name:
                    global_hex = system_b.global_location + wp.location
                    self._global_hex_warp_points.pop(global_hex, None)
            system_b.warp_points = [
                wp for wp in system_b.warp_points
                if wp.destination_id != system_a_name
            ]

    def get_system_at_location(self, location: 'HexCoord') -> Optional['StarSystem']:
        """Find the star system containing a given global hex location.

        Facade method delegating to GalaxySpatialIndex.

        Checks if the location is:
        - At a system's global_location
        - At a planet within a system
        - At a star within a system
        - At a warp point within a system

        Args:
            location: Global HexCoord to search for.

        Returns:
            StarSystem if location is within a system, None if in deep space.
        """
        return self._spatial.get_system_at_location(location)

    def get_all_fleets_in_system(self, system: 'StarSystem', empires: List) -> List[tuple]:
        """Find all fleets from all empires at any hex within a system.

        Facade method delegating to GalaxySpatialIndex.

        Checks the system's global_location plus all planet, star, and
        warp point local offsets.

        Args:
            system: The StarSystem to search within.
            empires: List of Empire objects to search.

        Returns:
            List of (empire, fleet) tuples for all fleets in the system.
        """
        return self._spatial.get_all_fleets_in_system(system, empires)

    def generate_planets(self, system: 'StarSystem') -> None:
        """Generate planets for a system based on its star type.

        Facade method delegating to GalaxySystemGenerator.

        Args:
            system: StarSystem to generate planets for.
        """
        self._sys_gen.generate_planets(self, system)

    def generate_systems(
        self,
        count: int,
        min_dist: int = 10,
        placement_strategy: Optional['ISystemPlacementStrategy'] = None,
        rng: Optional[random.Random] = None
    ) -> List['StarSystem']:
        """Generate star systems ensuring minimum distance and assigning Star Types.

        Facade method delegating to GalaxySystemGenerator.

        Args:
            count: Number of systems to generate.
            min_dist: Minimum distance between systems in hex units.
            placement_strategy: Strategy for placing systems. If None, uses
                RandomPlacementStrategy for uniform random placement.
            rng: Random number generator for deterministic generation.
                If None, uses global random state.

        Returns:
            List of generated StarSystem objects.
        """
        return self._sys_gen.generate_systems(
            self, count, min_dist, placement_strategy, rng
        )

    def create_vars_link(self, sys_a: 'StarSystem', sys_b: 'StarSystem') -> None:
        """Create a warp link between two systems.

        Facade method delegating to GalaxyWarpGenerator.

        Args:
            sys_a: First system.
            sys_b: Second system.
        """
        # Track warp point count before to detect new additions
        wp_count_a = len(sys_a.warp_points)
        wp_count_b = len(sys_b.warp_points)

        self._warp_gen.create_warp_link(sys_a, sys_b)

        # Register any newly created warp points (PROJ-179: O(1) lookup)
        if len(sys_a.warp_points) > wp_count_a:
            wp = sys_a.warp_points[-1]  # Most recently added
            global_hex = sys_a.global_location + wp.location
            self._global_hex_warp_points[global_hex] = sys_a
        if len(sys_b.warp_points) > wp_count_b:
            wp = sys_b.warp_points[-1]
            global_hex = sys_b.global_location + wp.location
            self._global_hex_warp_points[global_hex] = sys_b

    def generate_warp_lanes(
        self,
        k_neighbors: int = 20,
        region_classifier: 'Optional[RegionClassifier]' = None,
        inter_region_mode: str = 'normal'
    ) -> None:
        """Generate warp lanes ensuring connectivity (MST) and adding density.

        Uses spatial indexing with k-nearest neighbors for O(n*k) performance
        instead of O(n²) all-pairs computation.

        Facade method delegating to GalaxyWarpGenerator.

        Args:
            k_neighbors: Number of nearest neighbors to consider per system.
                         Higher values = more edges to consider, slower but
                         potentially better connectivity. Default 20.
            region_classifier: Optional RegionClassifier for region-aware
                         warp lane generation. If provided, inter-region
                         connections are penalized based on inter_region_mode.
            inter_region_mode: How to handle inter-region connections:
                         - 'normal': No region restrictions (default)
                         - 'limited': Allow 1-2 inter-region links per region pair
                         - 'minimal': Only allow MST-required inter-region links
        """
        self._warp_gen.generate_warp_lanes(
            self, k_neighbors, region_classifier, inter_region_mode
        )
        # PROJ-204: Rebuild warp point index after generation
        self._rebuild_all_warp_point_indices()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Galaxy to dict."""
        # Convert systems dict (HexCoord keys -> dict keys)
        systems_list = []
        for coord, system in self.systems.items():
            systems_list.append({
                'coord': hex_to_dict(coord),
                'system': system.to_dict()
            })

        return {
            'radius': self.radius,
            'systems': systems_list,
            '_next_planet_id': self._next_planet_id
        }

    @classmethod
    def from_dict(cls, data: dict, naming_data_path: str = None) -> 'Galaxy':
        """
        Deserialize Galaxy from dict.

        Args:
            data: Saved galaxy data
            naming_data_path: Path to StarSystemNames.YAML (optional)

        Returns:
            Reconstructed Galaxy with all indexes rebuilt

        Raises:
            PersistenceException: If required keys missing or radius is not positive.

        Note:
            Invalid systems are skipped with a warning log to allow
            resilient degradation.
        """
        logger = logging.getLogger(__name__)
        require_keys(data, ['radius'], 'Galaxy')
        validate_positive(data['radius'], 'radius', 'Galaxy')

        # Create empty galaxy
        galaxy = cls(radius=data['radius'])

        # Restore planet ID counter
        galaxy._next_planet_id = data.get('_next_planet_id', 1)

        # Deserialize systems with error isolation
        for i, sys_entry in enumerate(data.get('systems', [])):
            try:
                # Validate system entry structure
                if 'coord' not in sys_entry:
                    raise PersistenceException(
                        f"Galaxy: system entry {i} missing 'coord'",
                        code=ErrorCode.CORRUPT_DATA.value,
                        context={"source": "Galaxy", "index": i, "missing_key": "coord"}
                    )
                if 'system' not in sys_entry:
                    raise PersistenceException(
                        f"Galaxy: system entry {i} missing 'system'",
                        code=ErrorCode.CORRUPT_DATA.value,
                        context={"source": "Galaxy", "index": i, "missing_key": "system"}
                    )

                coord = hex_from_dict(sys_entry['coord'])
                system = StarSystem.from_dict(sys_entry['system'])
            except (PersistenceException, KeyError, TypeError, ValueError) as e:
                logger.warning(f"Galaxy: skipping invalid system at index {i}: {e}")
                continue

            # Add to galaxy maps
            galaxy.systems[coord] = system
            galaxy.name_map[system.name] = system

            # PROJ-204: Shared zone and warp point registration
            galaxy._register_zones_from_system(system)
            galaxy._rebuild_warp_point_index(system)

            # Restore planet registrations (preserves existing IDs from saved data)
            for planet in system.planets:
                galaxy._registry.restore_planet(system, planet)

        return galaxy
