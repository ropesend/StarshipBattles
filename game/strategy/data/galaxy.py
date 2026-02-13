import random
import math
from enum import Enum, auto
from typing import Any, Dict, List, Optional, TYPE_CHECKING
# hex_to_pixel/pixel_to_hex: Used for geometric calculations (angles, distances),
# not rendering. These convert hex coords to/from Cartesian for trigonometry.
from game.core.hex_math import HexCoord, hex_distance, hex_to_pixel, hex_ring, pixel_to_hex
from game.strategy.data.naming import NameRegistry
import os

from game.strategy.data.stars import StarGenerator, Star, StarType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planet_gen import PlanetGenerator
from game.strategy.generation.planet_image_registry import PlanetImageRegistry

if TYPE_CHECKING:
    from game.strategy.generation.placement_strategies import ISystemPlacementStrategy
    from game.strategy.generation.region_classifier import RegionClassifier
    from game.strategy.data.fleet import Fleet

# Planet and PlanetType moved to game.strategy.data.planet

class WarpPoint:
    def __init__(self, destination_id, location):
        self.destination_id = destination_id
        self.location = location # HexCoord (Local to system)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize WarpPoint to dict."""
        from game.core.hex_math import hex_to_dict
        return {
            'destination_id': self.destination_id,
            'location': hex_to_dict(self.location)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WarpPoint':
        """Deserialize WarpPoint from dict."""
        from game.core.hex_math import hex_from_dict
        return cls(
            destination_id=data['destination_id'],
            location=hex_from_dict(data['location'])
        )

class StarSystem:
    def __init__(self, name, global_location, stars=None, region_id=None):
        self.name = name
        self.global_location = global_location # HexCoord
        self.stars = stars if stars else []
        self.warp_points = []
        self.planets = [] # List[Planet]
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
        from game.core.hex_math import hex_to_dict
        result = {
            'name': self.name,
            'global_location': hex_to_dict(self.global_location),
            'stars': [star.to_dict() for star in self.stars],
            'warp_points': [wp.to_dict() for wp in self.warp_points],
            'planets': [planet.to_dict() for planet in self.planets]
        }
        if self.region_id is not None:
            result['region_id'] = self.region_id
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'StarSystem':
        """Deserialize StarSystem from dict."""
        from game.core.hex_math import hex_from_dict
        from game.strategy.data.stars import Star

        system = cls(
            name=data['name'],
            global_location=hex_from_dict(data['global_location']),
            stars=[Star.from_dict(s) for s in data.get('stars', [])],
            region_id=data.get('region_id')
        )

        # Deserialize warp points
        system.warp_points = [WarpPoint.from_dict(wp) for wp in data.get('warp_points', [])]

        # Deserialize planets
        system.planets = [Planet.from_dict(p) for p in data.get('planets', [])]

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

        # Fleet Registry (PROJ-87 Phase 6: O(1) fleet lookup)
        self.fleets_by_id = {}  # int -> Fleet
        
        # Initialize Naming Registry
        data_path = os.path.join(os.getcwd(), 'data', 'StarSystemNames.YAML')
        self.naming = NameRegistry(data_path)
        self.star_generator = StarGenerator()
        self.image_registry = PlanetImageRegistry()
        self.planet_generator = PlanetGenerator(self.image_registry)
        
    def add_system(self, system):
        """Add a system to the galaxy map."""
        self.systems[system.global_location] = system
        self.name_map[system.name] = system
        
    def get_system_by_name(self, name: str) -> Optional['StarSystem']:
        """Get system by name."""
        return self.name_map.get(name)

    def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
        """
        Find the system containing a given object (Fleet, Planet, etc).

        Args:
            obj: Object with a 'location' attribute (HexCoord).

        Returns:
            StarSystem or None.
        """
        if not hasattr(obj, 'location'):
            return None
            
        # Optimization: Map logic handles global hexes?
        # StarSystem.global_location is standard.
        # Check if object is AT a system location.
        if obj.location in self.systems:
            return self.systems[obj.location]
            
        # If object is a planet, it might be in a system's list but location is relative?
        # Standard: Fleet location is GLOBAL. Planet location is RELATIVE to System?
        # Wait, previous code: collision check used `(system.global_location + p.location)`.
        # so Planet.location is relative.
        # But Fleet.location is global.
        
        # If obj is Fleet:
        # It is strictly at a global hex.
        # If that hex matches a system's global hex, it is "at the system".
        # If it is in deep space, it returns None?
        # The calling code says: "Find Uncolonized Planets at Fleet Location". 
        # So it expects that if a fleet is at (X,Y) and there is a system at (X,Y), 
        # then we return that system.
        
        if obj.location in self.systems:
            return self.systems[obj.location]
            
        return None
    
    def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet with the galaxy, assigning ID and updating indexes."""
        # Assign unique ID
        planet.id = self._next_planet_id
        self._next_planet_id += 1
        
        # Add to ID registry
        self.planets_by_id[planet.id] = planet
        
        # Add to reverse lookup
        self._planet_to_system[planet] = system
        
        # Add to spatial index (global hex)
        global_hex = system.global_location + planet.location
        if global_hex not in self._global_hex_planets:
            self._global_hex_planets[global_hex] = []
        self._global_hex_planets[global_hex].append(planet)
    
    def get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """O(1) lookup of planet by ID."""
        return self.planets_by_id.get(planet_id)
    
    def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
        """O(1) reverse lookup: Planet -> StarSystem."""
        return self._planet_to_system.get(planet)
    
    def get_planets_at_global_hex(self, global_hex: HexCoord) -> List['Planet']:
        """O(1) spatial lookup: get all planets at a global hex coordinate."""
        return self._global_hex_planets.get(global_hex, [])

    # --- Fleet Registry Methods (PROJ-87 Phase 6) ---

    def register_fleet(self, fleet) -> None:
        """Register a fleet for O(1) lookup by ID.

        Args:
            fleet: Fleet object to register.
        """
        self.fleets_by_id[fleet.id] = fleet

    def unregister_fleet(self, fleet) -> None:
        """Remove a fleet from the registry.

        Args:
            fleet: Fleet object to unregister.
        """
        self.fleets_by_id.pop(fleet.id, None)

    def get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """O(1) lookup of fleet by ID.

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        return self.fleets_by_id.get(fleet_id)

    def unregister_planet(self, planet: 'Planet') -> None:
        """Remove a planet from all galaxy indexes and its parent system.

        Args:
            planet: The planet to unregister.
        """
        # Remove from ID registry
        self.planets_by_id.pop(planet.id, None)

        # Get system before removing from lookup
        system = self._planet_to_system.pop(planet, None)

        # Remove from spatial index
        if system is not None:
            global_hex = system.global_location + planet.location
            if global_hex in self._global_hex_planets:
                planets_at_hex = self._global_hex_planets[global_hex]
                if planet in planets_at_hex:
                    planets_at_hex.remove(planet)
                # Clean up empty list
                if not planets_at_hex:
                    del self._global_hex_planets[global_hex]

            # Remove from system's planets list
            if planet in system.planets:
                system.planets.remove(planet)

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
            system_a.warp_points = [
                wp for wp in system_a.warp_points
                if wp.destination_id != system_b_name
            ]

        if system_b is not None:
            system_b.warp_points = [
                wp for wp in system_b.warp_points
                if wp.destination_id != system_a_name
            ]

    def get_system_at_location(self, location: HexCoord) -> Optional['StarSystem']:
        """Find the star system containing a given global hex location.

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
        # Direct system location check (fast path)
        if location in self.systems:
            return self.systems[location]

        # Check if location is within a system (at a planet, star, or warp point)
        for sys_location, system in self.systems.items():
            # Check planets
            for planet in system.planets:
                if sys_location + planet.location == location:
                    return system

            # Check stars
            for star in system.stars:
                if hasattr(star, 'location') and sys_location + star.location == location:
                    return system

            # Check warp points
            for wp in system.warp_points:
                if sys_location + wp.location == location:
                    return system

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

        # Add star locations
        for star in system.stars:
            if hasattr(star, 'location'):
                system_hexes.add(system.global_location + star.location)

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

    def generate_planets(self, system):
        """Generate planets for a system based on its star type."""
        # Use new Planet Generator
        if not system.stars: return
        
        system.planets = self.planet_generator.generate_system_bodies(system.name, system.stars)
        
        # Sort by distance, then mass (descending) for consistent ordering
        system.planets.sort(key=lambda p: (p.orbit_distance, -p.mass))
        
        # Register all planets with the galaxy
        for planet in system.planets:
            self.register_planet(system, planet)

    def generate_systems(
        self,
        count: int,
        min_dist: int = 10,
        placement_strategy: Optional['ISystemPlacementStrategy'] = None,
        rng: Optional[random.Random] = None
    ) -> List['StarSystem']:
        """
        Generate star systems ensuring minimum distance and assigning Star Types.

        Args:
            count: Number of systems to generate
            min_dist: Minimum distance between systems in hex units
            placement_strategy: Strategy for placing systems. If None, uses
                RandomPlacementStrategy for uniform random placement.
            rng: Random number generator for deterministic generation.
                If None, uses global random state.

        Returns:
            List of generated StarSystem objects
        """
        # Import here to avoid circular dependency
        from game.strategy.generation.placement_strategies import RandomPlacementStrategy
        from game.strategy.data.spatial_index import SpatialIndex

        if placement_strategy is None:
            placement_strategy = RandomPlacementStrategy()

        generated: List[StarSystem] = []

        # Build spatial index ONCE for efficient distance checks
        # This avoids O(n²) complexity from rebuilding on every placement
        spatial_index = SpatialIndex(cell_size=max(min_dist, 500))
        existing_coords = set(self.systems.keys())
        for coord in existing_coords:
            spatial_index.add(coord, None)

        # Track consecutive failures to detect saturation
        consecutive_failures = 0
        max_consecutive_failures = 10  # Stop after 10 consecutive failed placements

        while len(generated) < count:
            # Use strategy to sample a valid location
            coord = placement_strategy.sample_location(
                radius=self.radius,
                existing_systems=existing_coords,
                min_dist=min_dist,
                rng=rng,
                spatial_index=spatial_index
            )

            if coord is None:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    # Galaxy is saturated, can't place more systems
                    break
                continue

            # Reset failure counter on success
            consecutive_failures = 0

            # Create the system
            name = self.naming.get_system_name()
            stars = self.star_generator.generate_system_stars(name)

            sys = StarSystem(name, coord, stars=stars)
            self.generate_planets(sys)
            self.add_system(sys)
            generated.append(sys)

            # Update spatial index and existing coords incrementally
            spatial_index.add(coord, None)
            existing_coords.add(coord)

        return generated

    def _calculate_warp_distance(self, system):
        """
        Calculate the distance for a warp point based on the primary star's size.
        Formula: Base (15) + (Star Diameter * 1.5) + Random(-2 to 5)
        Min Distance: 10
        """
        star_diam = 1.0
        if system.primary_star:
            star_diam = system.primary_star.diameter_hexes
            
        base_dist = 15.0
        scaled_dist = base_dist + (star_diam * 1.5)
        jitter = random.uniform(-2.0, 5.0)
        
        total_dist = scaled_dist + jitter
        return max(10.0, total_dist)

    def _is_angle_clear(self, system, target_angle_rad, threshold_deg=30):
        """
        Check if a target angle is clear of existing warp lines.
        Returns True if the angle difference to all existing lines is >= threshold.
        """
        if not system.warp_points:
            return True
            
        threshold_rad = math.radians(threshold_deg)
        
        for wp in system.warp_points:
            # Calculate angle of existing WP
            # We need to convert hex location to angle relative to system center (0,0)
            # Local hex coords are relative to system center.
            wx, wy = hex_to_pixel(wp.location, 1.0)
            existing_angle = math.atan2(wy, wx)
            
            diff = abs(target_angle_rad - existing_angle)
            # Normalize to 0-PI
            while diff > math.pi:
                diff -= 2 * math.pi
            diff = abs(diff)
            
            if diff < threshold_rad:
                return False
                
        return True

    def create_vars_link(self, sys_a, sys_b):
        """Create a warp link between two systems."""
        for wp in sys_a.warp_points:
            if wp.destination_id == sys_b.name:
                return 
                
        # 1. Determine direction in Global Map
        ax, ay = hex_to_pixel(sys_a.global_location, 1.0)
        bx, by = hex_to_pixel(sys_b.global_location, 1.0)
        
        angle_a_to_b = math.atan2(by - ay, bx - ax)
        angle_b_to_a = math.atan2(ay - by, ax - bx)
        
        # 2. Place Warp Point at System Edge (Local Map)
        
        dist_a = self._calculate_warp_distance(sys_a)
        dist_b = self._calculate_warp_distance(sys_b)
        
        # hex_to_pixel(size=1) scales x by 1.5.
        
        # For A -> B
        projection_dist_a = dist_a * 1.5
        local_ax = math.cos(angle_a_to_b) * projection_dist_a
        local_ay = math.sin(angle_a_to_b) * projection_dist_a
        loc_a = pixel_to_hex(local_ax, local_ay, 1.0)
        
        # For B -> A
        projection_dist_b = dist_b * 1.5
        local_bx = math.cos(angle_b_to_a) * projection_dist_b
        local_by = math.sin(angle_b_to_a) * projection_dist_b
        loc_b = pixel_to_hex(local_bx, local_by, 1.0)
        
        sys_a.add_warp_point(sys_b.name, loc_a)
        sys_b.add_warp_point(sys_a.name, loc_b)

    def _build_edge_candidates(
        self,
        systems: List['StarSystem'],
        spatial_index,
        k_neighbors: int
    ) -> List[tuple]:
        """Build sorted (dist, i, j) edge list using k-nearest neighbors.

        Computes edges via k-nearest neighbor queries on the spatial index,
        deduplicates, calculates distances, and returns sorted by distance.

        Args:
            systems: Ordered list of star systems (index = system ID).
            spatial_index: SpatialIndex populated with system coordinates.
            k_neighbors: Number of nearest neighbors to consider per system.

        Returns:
            List of (distance, i, j) tuples sorted by distance ascending.
        """
        edge_set = set()  # Avoid duplicates
        for i, sys in enumerate(systems):
            neighbors = spatial_index.get_k_nearest(
                sys.global_location,
                k=k_neighbors,
                exclude_coord=sys.global_location
            )
            for neighbor_coord, j in neighbors:
                if i < j:
                    edge_set.add((i, j))
                else:
                    edge_set.add((j, i))

        # Convert to edge list with distances
        edges = []
        for i, j in edge_set:
            dist = hex_distance(systems[i].global_location, systems[j].global_location)
            edges.append((dist, i, j))

        # Sort by distance (asc)
        edges.sort(key=lambda x: x[0])
        return edges

    def _apply_mst_edges(
        self,
        systems: List['StarSystem'],
        edges: List[tuple]
    ) -> None:
        """Apply Kruskal's MST algorithm to ensure full connectivity.

        Uses union-find with path compression to build a minimum spanning
        tree over the edge candidates. Creates warp links for all MST edges.

        Args:
            systems: Ordered list of star systems (index = system ID).
            edges: Sorted list of (distance, i, j) edge tuples.
        """
        parent = list(range(len(systems)))

        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        for dist, i, j in edges:
            if union(i, j):
                self.create_vars_link(systems[i], systems[j])

    def _should_add_density_edge(
        self,
        s_i: 'StarSystem',
        s_j: 'StarSystem',
        dist: float,
        region_classifier: 'Optional[RegionClassifier]',
        inter_region_mode: str,
        inter_region_links: dict
    ) -> bool:
        """Evaluate whether a single density edge candidate should be added.

        Checks degree caps, existing links, region constraints, angle
        validation, and probability calculation. Consumes one random.random()
        call for candidates that pass all pre-checks.

        Args:
            s_i: Source system.
            s_j: Destination system.
            dist: Distance between the two systems.
            region_classifier: Optional RegionClassifier for region filtering.
            inter_region_mode: Region connection mode ('normal', 'limited', 'minimal').
            inter_region_links: Mutable dict tracking inter-region link counts.

        Returns:
            True if the edge should be created, False otherwise.
        """
        # Skip if already linked (MST covered it)
        already_linked = any(wp.destination_id == s_j.name for wp in s_i.warp_points)
        if already_linked:
            return False

        # Cap degree logic: "3 to 10 warp points"
        deg_i = len(s_i.warp_points)
        deg_j = len(s_j.warp_points)

        if deg_i >= 10 or deg_j >= 10:
            return False

        # Check region constraints
        if region_classifier and inter_region_mode != 'normal':
            region_i = s_i.region_id
            region_j = s_j.region_id

            if region_i is not None and region_j is not None and region_i != region_j:
                # This is an inter-region edge
                if inter_region_mode == 'minimal':
                    # Only MST edges allowed between regions
                    return False
                elif inter_region_mode == 'limited':
                    # Allow limited inter-region links
                    region_pair = (min(region_i, region_j), max(region_i, region_j))
                    current_count = inter_region_links.get(region_pair, 0)
                    if current_count >= 2:
                        return False

        # Check Angle Preference
        # Calculate intended angle for both
        ax, ay = hex_to_pixel(s_i.global_location, 1.0)
        bx, by = hex_to_pixel(s_j.global_location, 1.0)
        angle_i_to_j = math.atan2(by - ay, bx - ax)
        angle_j_to_i = math.atan2(ay - by, ax - bx)

        # If angles are bad, reduce chance drastically or skip
        # Preference: "prefer to have at least 30 degrees... if necessary... ok"
        valid_angles = True
        if not self._is_angle_clear(s_i, angle_i_to_j, threshold_deg=30):
            valid_angles = False
        if not self._is_angle_clear(s_j, angle_j_to_i, threshold_deg=30):
            valid_angles = False

        # If degree is low, boost chance
        base_chance = 40.0 / (dist + 1)  # Arbitrary tuning

        if deg_i < 3 or deg_j < 3:
            base_chance *= 3.0  # Boost to help them get up to min

        # Penalize bad angles
        if not valid_angles:
            # If degrees are decent (>3), strictly reject (or very low chance)
            # If degrees are low (<3), allow with penalty because "if it is necessary... that is ok"
            if deg_i > 3 and deg_j > 3:
                return False
            else:
                base_chance *= 0.1  # Severe penalty

        return random.random() < base_chance

    def _add_density_edges(
        self,
        systems: List['StarSystem'],
        edges: List[tuple],
        region_classifier: 'Optional[RegionClassifier]',
        inter_region_mode: str
    ) -> None:
        """Add additional random edges beyond the MST to meet density targets.

        Iterates all edge candidates, evaluates each with
        _should_add_density_edge, creates warp links for accepted edges,
        and tracks inter-region link counts.

        Args:
            systems: Ordered list of star systems (index = system ID).
            edges: Sorted list of (distance, i, j) edge tuples.
            region_classifier: Optional RegionClassifier for region filtering.
            inter_region_mode: Region connection mode ('normal', 'limited', 'minimal').
        """
        # Track inter-region links for 'limited' mode
        inter_region_links = {}  # (min_region, max_region) -> count

        for dist, i, j in edges:
            s_i, s_j = systems[i], systems[j]

            if self._should_add_density_edge(
                s_i, s_j, dist,
                region_classifier, inter_region_mode, inter_region_links
            ):
                self.create_vars_link(s_i, s_j)

                # Track inter-region link
                if region_classifier and inter_region_mode == 'limited':
                    region_i = s_i.region_id
                    region_j = s_j.region_id
                    if region_i is not None and region_j is not None and region_i != region_j:
                        region_pair = (min(region_i, region_j), max(region_i, region_j))
                        inter_region_links[region_pair] = inter_region_links.get(region_pair, 0) + 1

    def generate_warp_lanes(
        self,
        k_neighbors: int = 20,
        region_classifier: 'Optional[RegionClassifier]' = None,
        inter_region_mode: str = 'normal'
    ):
        """
        Generate warp lanes ensuring connectivity (MST) and adding density.

        Uses spatial indexing with k-nearest neighbors for O(n*k) performance
        instead of O(n²) all-pairs computation.

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
        from game.strategy.data.spatial_index import SpatialIndex

        systems = list(self.systems.values())
        if len(systems) < 2:
            return

        # Build spatial index for efficient neighbor lookup
        spatial_index = SpatialIndex(cell_size=500)
        for i, sys in enumerate(systems):
            spatial_index.add(sys.global_location, i)

        # 1. Build sorted edge candidates via k-nearest neighbors
        edges = self._build_edge_candidates(systems, spatial_index, k_neighbors)

        # 2. Apply MST for guaranteed connectivity
        self._apply_mst_edges(systems, edges)

        # 3. Add density edges beyond MST
        self._add_density_edges(systems, edges, region_classifier, inter_region_mode)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Galaxy to dict."""
        from game.core.hex_math import hex_to_dict

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
        """
        from game.core.hex_math import hex_from_dict

        # Create empty galaxy
        galaxy = cls(radius=data['radius'])

        # Restore planet ID counter
        galaxy._next_planet_id = data.get('_next_planet_id', 1)

        # Deserialize systems
        for sys_entry in data.get('systems', []):
            coord = hex_from_dict(sys_entry['coord'])
            system = StarSystem.from_dict(sys_entry['system'])

            # Add to galaxy maps
            galaxy.systems[coord] = system
            galaxy.name_map[system.name] = system

            # Rebuild indexes for all planets in this system
            for planet in system.planets:
                # Add to ID registry
                galaxy.planets_by_id[planet.id] = planet

                # Add to reverse lookup
                galaxy._planet_to_system[planet] = system

                # Add to spatial index (global hex)
                global_hex = system.global_location + planet.location
                if global_hex not in galaxy._global_hex_planets:
                    galaxy._global_hex_planets[global_hex] = []
                galaxy._global_hex_planets[global_hex].append(planet)

        return galaxy
