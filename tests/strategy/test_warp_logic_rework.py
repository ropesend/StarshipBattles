import pytest
import math
from game.strategy.data.hex_math import HexCoord, hex_distance, hex_to_pixel
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.data.stars import Star

class TestWarpLogicRework:
    
    @pytest.fixture
    def galaxy(self):
        return Galaxy(radius=1000)

    def test_warp_distance_scaling(self, galaxy):
        """
        Verify that warp points generated for larger stars are placed further away 
        than those for smaller stars.
        """
        # Create a small star system (Diam = 1)
        small_sys = StarSystem("Small", HexCoord(0,0))
        small_star = Star(
            name="Small A", mass=0.5, diameter_hexes=1.0, 
            temperature=3000, luminosity=0.1, spectrum=None, 
            star_type=None, color=(255,100,100), age=1e9
        )
        small_sys.stars = [small_star]
        
        # Create a large star system (Diam = 10)
        large_sys = StarSystem("Large", HexCoord(100,0))
        large_star = Star(
            name="Large A", mass=50.0, diameter_hexes=10.0, 
            temperature=30000, luminosity=1000, spectrum=None, 
            star_type=None, color=(100,100,255), age=1e7
        )
        large_sys.stars = [large_star]
        
        # We need to mock _calculate_warp_distance or call create_vars_link and measure
        # Since we are testing black box behavior of integration, let's link them to a dummy
        
        dummy_1 = StarSystem("Dummy1", HexCoord(0, 50)) # 50 hexes away from small
        dummy_2 = StarSystem("Dummy2", HexCoord(100, 50)) # 50 hexes away from large
        
        # Link 
        galaxy.create_vars_link(small_sys, dummy_1)
        galaxy.create_vars_link(large_sys, dummy_2)
        
        # Measure Small Star Warp Dist
        assert len(small_sys.warp_points) == 1
        wp_small = small_sys.warp_points[0]
        dist_small = hex_distance(HexCoord(0,0), wp_small.location)
        
        # Measure Large Star Warp Dist
        assert len(large_sys.warp_points) == 1
        wp_large = large_sys.warp_points[0]
        dist_large = hex_distance(HexCoord(0,0), wp_large.location)
        
        # Check assertions
        # Expected base ~15 + 1.5*Diam
        # Small: ~16.5
        # Large: ~30.0
        print(f"Small Dist: {dist_small}, Large Dist: {dist_large}")
        assert dist_large > dist_small + 5 # Gap should be significant

    def test_angle_clearance_calculation(self, galaxy):
        """
        Verify the _is_angle_clear logic (helper to be implemented).
        We will test this by adding warp points and checking if hypothetically adding another
        would return True/False correctly.
        """
        # System at 0,0
        center = StarSystem("Center", HexCoord(0,0))
        
        # Add a warp point at 0 degrees (East) -> (10, 0)
        # Using hexes, (10, 0) is roughly 0 degrees.
        center.add_warp_point("EastTarget", HexCoord(10, 0))
        
        # We need to access the internal helper or simulate logic. 
        # Since the interface is protected, we can test it directly or via side effects.
        # Let's test the helper directly as it will be a method on Galaxy class.
        
        if not hasattr(galaxy, '_is_angle_clear'):
             pytest.skip("_is_angle_clear not implemented yet")
             
        # Target at 10 degrees (very close)
        # 10 degrees in radians ~ 0.17
        angle_fail = 0.1
        assert galaxy._is_angle_clear(center, angle_fail, threshold_deg=30) == False
        
        # Target at 90 degrees (clear)
        angle_pass = math.pi / 2
        assert galaxy._is_angle_clear(center, angle_pass, threshold_deg=30) == True

    def test_min_distance_constraint(self, galaxy):
        """Verify warp points respect minimum distance regardless of star size."""
        # Extremely tiny star
        micro_sys = StarSystem("Micro", HexCoord(0,0))
        micro_star = Star(
            name="Micro", mass=0.1, diameter_hexes=0.1, # Tiny
            temperature=3000, luminosity=0.01, spectrum=None, star_type=None, color=(0,0,0), age=1
        )
        micro_sys.stars = [micro_star]
        
        dummy = StarSystem("Target", HexCoord(20, 0))
        galaxy.create_vars_link(micro_sys, dummy)
        
        wp = micro_sys.warp_points[0]
        dist = hex_distance(HexCoord(0,0), wp.location)
        assert dist >= 10
