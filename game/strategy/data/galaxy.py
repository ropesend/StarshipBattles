import random
import math
from enum import Enum, auto
from game.strategy.data.hex_math import HexCoord, hex_distance, hex_to_pixel, hex_ring, pixel_to_hex
from game.strategy.data.naming import NameRegistry
import os

from game.strategy.data.stars import StarGenerator, Star, StarType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planet_gen import PlanetGenerator

# Planet and PlanetType moved to game.strategy.data.planet

class WarpPoint:
    def __init__(self, destination_id, location):
        self.destination_id = destination_id
        self.location = location # HexCoord (Local to system)

    def to_dict(self) -> dict:
        """Serialize WarpPoint to dict."""
        from game.strategy.data.hex_math import hex_to_dict
        return {
            'destination_id': self.destination_id,
            'location': hex_to_dict(self.location)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WarpPoint':
        """Deserialize WarpPoint from dict."""
        from game.strategy.data.hex_math import hex_from_dict
        return cls(
            destination_id=data['destination_id'],
            location=hex_from_dict(data['location'])
        )

class StarSystem:
    def __init__(self, name, global_location, stars=None):
        self.name = name
        self.global_location = global_location # HexCoord
        self.stars = stars if stars else []
        self.warp_points = []
        self.planets = [] # List[Planet]

    @property
    def primary_star(self):
        return self.stars[0] if self.stars else None

    def add_warp_point(self, destination_id, location):
        self.warp_points.append(WarpPoint(destination_id, location))

    def __repr__(self):
        star_count = len(self.stars)
        p_name = self.primary_star.name if self.primary_star else "Empty"
        return f"System('{self.name}', Loc:{self.global_location}, Stars:{star_count}, Primary:{p_name})"

    def to_dict(self) -> dict:
        """Serialize StarSystem to dict."""
        from game.strategy.data.hex_math import hex_to_dict
        return {
            'name': self.name,
            'global_location': hex_to_dict(self.global_location),
            'stars': [star.to_dict() for star in self.stars],
            'warp_points': [wp.to_dict() for wp in self.warp_points],
            'planets': [planet.to_dict() for planet in self.planets]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StarSystem':
        """Deserialize StarSystem from dict."""
        from game.strategy.data.hex_math import hex_from_dict
        from game.strategy.data.stars import Star

        system = cls(
            name=data['name'],
            global_location=hex_from_dict(data['global_location']),
            stars=[Star.from_dict(s) for s in data.get('stars', [])]
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
        
        # Initialize Naming Registry
        data_path = os.path.join(os.getcwd(), 'data', 'StarSystemNames.YAML')
        self.naming = NameRegistry(data_path)
        self.star_generator = StarGenerator()
        self.planet_generator = PlanetGenerator()
        
    def add_system(self, system):
        """Add a system to the galaxy map."""
        self.systems[system.global_location] = system
        self.name_map[system.name] = system
        
    def get_system_by_name(self, name):
        """Get system by name."""
        return self.name_map.get(name)

    def get_system_of_object(self, obj):
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
    
    def register_planet(self, system, planet):
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
    
    def get_planet_by_id(self, planet_id):
        """O(1) lookup of planet by ID."""
        return self.planets_by_id.get(planet_id)
    
    def get_system_of_planet(self, planet):
        """O(1) reverse lookup: Planet -> StarSystem."""
        return self._planet_to_system.get(planet)
    
    def get_planets_at_global_hex(self, global_hex):
        """O(1) spatial lookup: get all planets at a global hex coordinate."""
        return self._global_hex_planets.get(global_hex, [])
    
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

    def generate_systems(self, count, min_dist=10):
        """
        Generate random systems ensuring minimum distance and assigning Star Types.
        """
        generated = []
        attempts = 0
        max_attempts = count * 1000 
        
        while len(generated) < count and attempts < max_attempts:
            attempts += 1
            
            q = random.randint(-self.radius, self.radius)
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            r = random.randint(r1, r2)
            
            coord = HexCoord(q, r)
            
            if coord in self.systems:
                continue
                
            valid = True
            for other_c in self.systems:
                if hex_distance(coord, other_c) < min_dist:
                    valid = False
                    break
            
            if valid:
                name = self.naming.get_system_name()
                
                # New Star Generation
                stars = self.star_generator.generate_system_stars(name)
                
                sys = StarSystem(name, coord, stars=stars)
                self.generate_planets(sys)
                self.add_system(sys)
                generated.append(sys)
                
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

    def generate_warp_lanes(self):
        """
        Generate warp lanes ensuring connectivity (MST) and adding density.
        """
        systems = list(self.systems.values())
        if len(systems) < 2:
            return

        # 1. Compute all possible edges with weights (distance)
        edges = []
        for i in range(len(systems)):
            for j in range(i + 1, len(systems)):
                dist = hex_distance(systems[i].global_location, systems[j].global_location)
                edges.append((dist, i, j))

        # Sort by distance (asc)
        edges.sort(key=lambda x: x[0])

        # 2. Kruskal's Algorithm for MST
        parent = list(range(len(systems)))
        def find(i):
            if parent[i] == i: return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        mst_edges = []
        for dist, i, j in edges:
            if union(i, j):
                mst_edges.append((i, j))
                self.create_vars_link(systems[i], systems[j])

        # 3. Add additional random edges to meet density
        for dist, i, j in edges:
            # Skip if already linked (MST covered it)
            s_i, s_j = systems[i], systems[j]
            already_linked = any(wp.destination_id == s_j.name for wp in s_i.warp_points)

            if already_linked:
                continue

            # Cap degree logic? "3 to 10 warp points"
            deg_i = len(s_i.warp_points)
            deg_j = len(s_j.warp_points)

            if deg_i >= 10 or deg_j >= 10:
                continue

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
            base_chance = 40.0 / (dist + 1) # Arbitrary tuning

            if deg_i < 3 or deg_j < 3:
                base_chance *= 3.0 # Boost to help them get up to min

            # Penalize bad angles
            if not valid_angles:
                # If degrees are decent (>3), strictly reject (or very low chance)
                # If degrees are low (<3), allow with penalty because "if it is necessary... that is ok"
                if deg_i > 3 and deg_j > 3:
                    continue
                else:
                    base_chance *= 0.1 # Severe penalty

            if random.random() < base_chance:
                self.create_vars_link(s_i, s_j)

    def to_dict(self) -> dict:
        """Serialize Galaxy to dict."""
        from game.strategy.data.hex_math import hex_to_dict

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
        from game.strategy.data.hex_math import hex_from_dict

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
