import random
import math
from enum import Enum, auto
from game.strategy.data.hex_math import HexCoord, hex_distance, hex_to_pixel, hex_ring, pixel_to_hex
from game.strategy.data.naming import NameRegistry
import os

class StarType(Enum):
    # Name, Radius (px relative), Color (RGB), Weight
    BLUE_GIANT = (12, (100, 100, 255), 5)
    WHITE_DWARF = (4, (220, 220, 255), 10)
    YELLOW_MAIN = (8, (255, 255, 0), 40) # Sol-like
    ORANGE_DWARF = (7, (255, 165, 0), 25)
    RED_DWARF = (6, (255, 60, 60), 20)
    
    def __init__(self, radius, color, weight):
        self.radius = radius
        self.color = color
        self.probability_weight = weight

class PlanetType(Enum):
    # Name, Min Orbit Ring (int), Max Orbit Ring (int), Color (RGB)
    # Rings 1-3: Inner/Hot
    # Rings 4-9: Habitable/Temperate
    # Rings 10+: Outer/Cold
    LAVA = (1, 3, (255, 100, 0))
    BARREN = (1, 15, (150, 150, 150))
    TERRAN = (4, 9, (0, 200, 200)) # Rare, Goldilocks
    GAS_GIANT = (8, 20, (200, 150, 100))
    ICE_WORLD = (12, 25, (100, 200, 255))
    ASTEROID_FIELD = (3, 20, (100, 100, 100))
    
    def __init__(self, min_ring, max_ring, color):
        self.min_ring = min_ring
        self.max_ring = max_ring
        self.color = color

class Planet:
    def __init__(self, planet_type, orbit_distance, location):
        self.planet_type = planet_type
        self.orbit_distance = orbit_distance # Int (Ring number)
        self.location = location # HexCoord (Local to system, 0,0 is star)
        self.name = f"Planet-{orbit_distance}"
        
        # Empire Management
        self.owner_id = None # int or None
        self.construction_queue = [] # List of (item_name, turns_remaining)

    def add_production(self, item_name, turns):
        self.construction_queue.append([item_name, turns])

class WarpPoint:
    def __init__(self, destination_id, location):
        self.destination_id = destination_id
        self.location = location # HexCoord (Local to system)

class StarSystem:
    def __init__(self, name, global_location, star_type=None):
        self.name = name
        self.global_location = global_location # HexCoord
        self.star_type = star_type
        self.warp_points = []
        self.planets = [] # List[Planet]
        
    def add_warp_point(self, destination_id, location):
        self.warp_points.append(WarpPoint(destination_id, location))
        
    def __repr__(self):
        star_name = self.star_type.name if self.star_type else 'Unk'
        return f"System('{self.name}', {self.global_location}, {star_name}, Planets: {len(self.planets)})"

class Galaxy:
    # ... (__init__, add_system, generate_planets remain unchanged, only create_vars_link changes)
    def __init__(self, radius=100):
        self.radius = radius
        self.systems = {} # keys: HexCoord, values: StarSystem
        self.name_map = {} # keys: str (name), values: StarSystem
        
        # Initialize Naming Registry
        # Assuming run from root of repo
        data_path = os.path.join(os.getcwd(), 'data', 'StarSystemNames.YAML')
        self.naming = NameRegistry(data_path)
        
    def add_system(self, system):
        """Add a system to the galaxy map."""
        self.systems[system.global_location] = system
        self.name_map[system.name] = system
        
    def get_system_by_name(self, name):
        """Get system by name."""
        return self.name_map.get(name)
    
    def generate_planets(self, system):
        # ... (same as before)
        """Generate planets for a system based on its star type."""
        # Hex Grid placement
        # 1. Determine number of planets
        base_count = random.randint(1, 8)
        if system.star_type == StarType.RED_DWARF:
             base_count = random.randint(0, 5)
        elif system.star_type == StarType.BLUE_GIANT:
             base_count = random.randint(0, 4)
             
        # 2. Pick occupied rings
        occupied_rings = set()
        
        # 3. Generate
        for _ in range(base_count):
            p_type = random.choice(list(PlanetType))
            
            # Constraints
            if p_type == PlanetType.LAVA and system.star_type == StarType.BLUE_GIANT:
                continue
                
            # Pick a ring
            ring = -1
            for attempt in range(10):
                r = random.randint(p_type.min_ring, p_type.max_ring)
                if r not in occupied_rings:
                    ring = r
                    break
            
            if ring == -1:
                continue 
                
            occupied_rings.add(ring)
            
            # Pick a spot on the ring
            ring_hexes = hex_ring(ring)
            if not ring_hexes:
                continue
                
            loc = random.choice(ring_hexes)
            
            planet = Planet(p_type, ring, loc)
            system.planets.append(planet)
            
        system.planets.sort(key=lambda p: p.orbit_distance)
        self.naming.name_planets(system.name, system.planets)

    def generate_systems(self, count, min_dist=10):
        # ... (same as before)
        """
        Generate random systems ensuring minimum distance and assigning Star Types.
        """
        generated = []
        attempts = 0
        max_attempts = count * 1000 
        
        star_types = list(StarType)
        weights = [st.probability_weight for st in star_types]
        
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
                s_type = random.choices(star_types, weights=weights, k=1)[0]
                sys = StarSystem(name, coord, star_type=s_type)
                self.generate_planets(sys)
                self.add_system(sys)
                generated.append(sys)
                
        return generated

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
        # Target ~25 Hexes out
        WARP_HEX_DIST = 25
        
        # We want the resulting HexCoord to have a distance of approx 25.
        # hex_to_pixel(size=1) scales x by 1.5.
        # So we project ~37.5 units in 'pixel space' of size 1.0.
        projection_dist = WARP_HEX_DIST * 1.5
        
        # For A -> B
        local_ax = math.cos(angle_a_to_b) * projection_dist
        local_ay = math.sin(angle_a_to_b) * projection_dist
        loc_a = pixel_to_hex(local_ax, local_ay, 1.0)
        
        # For B -> A
        local_bx = math.cos(angle_b_to_a) * projection_dist
        local_by = math.sin(angle_b_to_a) * projection_dist
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
                
            # If degree is low, boost chance
            base_chance = 40.0 / (dist + 1) # Arbitrary tuning
            
            if deg_i < 3 or deg_j < 3:
                base_chance *= 3.0 # Boost to help them get up to min
            
            if random.random() < base_chance:
                self.create_vars_link(s_i, s_j)
