import unittest
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star, Spectrum, StarType
from game.strategy.data.hex_math import HexCoord

class TestRadiation(unittest.TestCase):
    
    def setUp(self):
        # Create a mock star with uniform spectrum for easy math
        self.flat_spec = Spectrum(100, 100, 100, 100, 100, 100, 100, 100, 100)
        self.star = Star(
            name="Test Star",
            mass=1.0,
            diameter_hexes=1.0,
            temperature=5000,
            luminosity=1.0,
            spectrum=self.flat_spec,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 255),
            age=1.0,
            location=HexCoord(0,0)
        )
        
    def test_falloff_distance_1(self):
        # At distance 1 (adjacent), factor should be 1/1^3 = 1.0
        target = HexCoord(1, 0) # 1 hex away
        result = calculate_incident_radiation(target, [self.star])
        
        self.assertAlmostEqual(result.gamma_ray, 100.0)
        self.assertAlmostEqual(result.red, 100.0)
        
    def test_falloff_distance_2(self):
        # At distance 2, factor should be 1/2^2.1 = 1/4.287 = 0.23325
        target = HexCoord(2, 0) # 2 hexes away
        result = calculate_incident_radiation(target, [self.star])
        
        # 100 * (1 / 2**2.1) = 23.325824788
        self.assertAlmostEqual(result.gamma_ray, 23.3258248)
        
    def test_falloff_distance_10(self):
        # At distance 10, factor should be 1/10^2.1 = 1/125.89 = 0.007943
        target = HexCoord(10, 0)
        result = calculate_incident_radiation(target, [self.star])
        
        # 100 * (1 / 10**2.1) = 0.79432823
        self.assertAlmostEqual(result.gamma_ray, 0.7943282)
        
    def test_clamping(self):
        # At distance 0 (inside star), should clamp to 1.0
        target = HexCoord(0, 0)
        result = calculate_incident_radiation(target, [self.star])
        
        self.assertAlmostEqual(result.gamma_ray, 100.0)
        
    def test_additive_measure(self):
        # Two stars at same location (0,0)
        target = HexCoord(1, 0)
        result = calculate_incident_radiation(target, [self.star, self.star])
        
        # Should be double (200.0)
        self.assertAlmostEqual(result.gamma_ray, 200.0)

if __name__ == '__main__':
    unittest.main()
