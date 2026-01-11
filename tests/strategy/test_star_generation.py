
import unittest
from game.strategy.data.stars import StarGenerator, StarType, Star

class TestStarGeneration(unittest.TestCase):
    def setUp(self):
        self.generator = StarGenerator()

    def test_star_mass_distribution(self):
        """Verify that mass distribution generally follows expectations."""
        masses = []
        for _ in range(1000):
            masses.append(self.generator._generate_mass(is_primary=True))
            
        # Check median ~1.0
        masses.sort()
        median = masses[500]
        print(f"Median Mass: {median}")
        self.assertTrue(0.5 < median < 2.0, f"Median mass {median} should be near 1.0")
        
        # Check range
        self.assertTrue(min(masses) >= 0.1)
        self.assertTrue(max(masses) <= 100.0)

    def test_multi_star_probabilities(self):
        """Verify generation of multiple stars."""
        counts = {1:0, 2:0, 3:0, 4:0}
        n = 2000
        for i in range(n):
            stars = self.generator.generate_system_stars(f"Sys-{i}")
            c = len(stars)
            if c in counts: counts[c] += 1
            
            # Check hierarchy
            primary = stars[0]
            for companion in stars[1:]:
                # Primary should be more massive (or at least generated first and primary logic holds)
                # My generator logic enforces companions are generated with primary_mass cap?
                # Actually _generate_mass loops until < primary_mass.
                self.assertGreaterEqual(primary.mass, companion.mass * 0.99, "Primary should be ~largest")
                
                # Check distances
                # Primary is at 0,0,0
                # Companion location magnitude should be > primary radius
                # hex_distance between (0,0) and companion.location
                from game.strategy.data.hex_math import hex_distance, HexCoord
                dist = hex_distance(HexCoord(0,0), companion.location)
                
                self.assertGreater(dist, primary.diameter_hexes, "Companion inside primary?")

        print(f"Counts: {counts}")
        # Approx 10% binary -> ~200
        # Wide tolerance because random
        self.assertTrue(150 < counts[2] < 250, "Binary count deviation")
        
    def test_physical_properties(self):
        """Check mapping of mass to radius/hexes."""
        seen_giants = False
        seen_dwarfs = False
        
        for i in range(100):
            stars = self.generator.generate_system_stars(f"Sys-{i}")
            for star in stars:
                if star.star_type in (StarType.RED_GIANT, StarType.BLUE_GIANT):
                    seen_giants = True
                    self.assertGreater(star.diameter_hexes, 2.0)
                if star.star_type == StarType.RED_DWARF:
                    seen_dwarfs = True
                    self.assertLessEqual(star.diameter_hexes, 3.0)
                    
                # Check Spectrum
                spec = star.spectrum
                self.assertIsNotNone(spec)
                total = spec.get_total_output()
                self.assertGreater(total, 0)
                
                # Verify 9 bands are present and non-negative
                self.assertGreaterEqual(spec.gamma_ray, 0)
                self.assertGreaterEqual(spec.xray, 0)
                self.assertGreaterEqual(spec.ultraviolet, 0)
                self.assertGreaterEqual(spec.blue, 0)
                self.assertGreaterEqual(spec.green, 0)
                self.assertGreaterEqual(spec.red, 0)
                self.assertGreaterEqual(spec.infrared, 0)
                self.assertGreaterEqual(spec.microwave, 0)
                self.assertGreaterEqual(spec.radio, 0)
                
        self.assertTrue(seen_giants, "Should have seen at least one giant")
        self.assertTrue(seen_dwarfs, "Should have seen at least one dwarf")

if __name__ == '__main__':
    unittest.main()
