import pytest
from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint

class TestGalaxyGen:
    def test_galaxy_init(self):
        g = Galaxy(radius=1000)
        assert g.radius == 1000
        assert len(g.systems) == 0

    def test_add_system(self):
        g = Galaxy(radius=100)
        coord = HexCoord(0, 0)
        sys = StarSystem(name="Sol", global_location=coord)
        g.add_system(sys)
        assert len(g.systems) == 1
        assert g.systems[coord] == sys

    def test_generation_constraints_min_distance(self):
        """Verify that generated systems obey the minimum distance rule."""
        g = Galaxy(radius=2000)
        # Try to generate 5 systems with min distance 101
        # Use a fixed seed in implementation if possible, or just checks
        systems = g.generate_systems(count=5, min_dist=101)
        
        assert len(systems) == 5
        assert len(g.systems) == 5
        
        # Check all pairs
        coords = list(g.systems.keys())
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = hex_distance(coords[i], coords[j])
                assert d >= 101, f"Systems at {coords[i]} and {coords[j]} are too close: {d}"

    def test_warp_point_linking(self):
        """Verify warp points capture target direction."""
        g = Galaxy(radius=1000)
        
        # Manually place two systems
        s1 = StarSystem("Alpha", HexCoord(0, 0))
        s2 = StarSystem("Beta", HexCoord(100, 0)) # East direction
        g.add_system(s1)
        g.add_system(s2)
        
        # Link them
        g.create_vars_link(s1, s2)
        
        # Check s1 has warp to s2
        assert len(s1.warp_points) == 1
        wp = s1.warp_points[0]
        assert wp.destination_id == "Beta"
        
        # Check orientation 
        # s2 is East of s1 (positive q, r=0)
        # Warp point should be on the East edge of s1's local grid
        assert isinstance(wp.location, HexCoord)
        # Check rough direction: q should be positive, r near 0?
        # WARP_DIST is 30 hexes approx.
        assert wp.location.q > 0 
        assert abs(wp.location.r) < 10 # Should be somewhat aligned east

    def test_graph_connectivity(self):
        """Verify that the generated galaxy is fully connected (no isolated islands)."""
        g = Galaxy(radius=1000)
        g.generate_systems(count=20, min_dist=50)
        g.generate_warp_lanes() # New explicit step or auto? User request implies part of generation.
        # Assuming generate_systems might need to call lanes, or separate.
        # Let's say we call generating lanes manually for tested control.
        
        # BFS Traversal
        if not g.systems:
            return
            
        start_node = next(iter(g.systems.values()))
        visited = {start_node.name}
        queue = [start_node]
        
        while queue:
            current = queue.pop(0)
            for wp in current.warp_points:
                # O(N) lookup for target obj, irrelevant for test size
                target = next((s for s in g.systems.values() if s.name == wp.destination_id), None)
                if target and target.name not in visited:
                    visited.add(target.name)
                    queue.append(target)
        
        assert len(visited) == len(g.systems), f"Graph not connected! Visited {len(visited)}/{len(g.systems)}"

    def test_minimum_warp_points(self):
        """Verify every star has at least 1 warp point."""
        g = Galaxy(radius=1000)
        g.generate_systems(count=10, min_dist=50)
        g.generate_warp_lanes()
        
        for sys in g.systems.values():
            assert len(sys.warp_points) >= 1, f"System {sys.name} has no warp points!"
