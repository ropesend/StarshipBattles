import pytest
import math
from unittest.mock import patch

from game.core.hex_math import HexCoord, hex_distance, hex_to_pixel
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem, WarpPoint
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
        # Create a small star system (radius = 1)
        small_sys = StarSystem("Small", HexCoord(0,0))
        small_star = Star(
            name="Small A", mass=0.5, radius_hexes=1,
            temperature=3000, luminosity=0.1, spectrum=None,
            star_type=None, color=(255,100,100), age=1e9
        )
        small_sys.stars = [small_star]

        # Create a large star system (radius = 5)
        large_sys = StarSystem("Large", HexCoord(100,0))
        large_star = Star(
            name="Large A", mass=50.0, radius_hexes=5,
            temperature=30000, luminosity=1000, spectrum=None,
            star_type=None, color=(100,100,255), age=1e7
        )
        large_sys.stars = [large_star]
        
        # We need to mock _calculate_warp_distance or call create_vars_link and measure
        # Since we are testing black box behavior of integration, let's link them to a dummy
        
        dummy_1 = StarSystem("Dummy1", HexCoord(0, 50)) # 50 hexes away from small
        dummy_2 = StarSystem("Dummy2", HexCoord(100, 50)) # 50 hexes away from large
        
        # Link with deterministic jitter so the scaling assertion is about
        # star radius, not the process-wide RNG state inherited from prior tests.
        with patch("game.strategy.data.galaxy_warp_generator.random.uniform", return_value=0.0):
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
        
        # Expected base ~15 + 1.5*Diam
        # Small: ~16.5, Large: ~30.0
        assert dist_large > dist_small + 5, f"Gap should be significant: Small={dist_small}, Large={dist_large}"

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
        # Test the helper directly via the warp generator delegate.

        # Target at 10 degrees (very close)
        # 10 degrees in radians ~ 0.17
        angle_fail = 0.1
        assert galaxy._warp_gen._is_angle_clear(center, angle_fail, threshold_deg=30) is False

        # Target at 90 degrees (clear)
        angle_pass = math.pi / 2
        assert galaxy._warp_gen._is_angle_clear(center, angle_pass, threshold_deg=30) is True

    def test_min_distance_constraint(self, galaxy):
        """Verify warp points respect minimum distance regardless of star size."""
        # Extremely tiny star
        micro_sys = StarSystem("Micro", HexCoord(0,0))
        micro_star = Star(
            name="Micro", mass=0.1, radius_hexes=1, # Tiny (minimum is 1)
            temperature=3000, luminosity=0.01, spectrum=None, star_type=None, color=(0,0,0), age=1
        )
        micro_sys.stars = [micro_star]
        
        dummy = StarSystem("Target", HexCoord(20, 0))
        galaxy.create_vars_link(micro_sys, dummy)
        
        wp = micro_sys.warp_points[0]
        dist = hex_distance(HexCoord(0,0), wp.location)
        assert dist >= 10
