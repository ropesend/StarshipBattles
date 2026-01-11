import unittest
import os
import tempfile
import yaml
from game.strategy.data.naming import NameRegistry
from game.strategy.data.galaxy import Galaxy, StarSystem, Planet, PlanetType

class TestNaming(unittest.TestCase):
    def setUp(self):
        # Create a temp yaml file for testing
        self.test_data = {
            "names": ["Alpha", "Beta", "Gamma", "Delta"]
        }
        self.fd, self.path = tempfile.mkstemp(suffix=".YAML")
        with os.fdopen(self.fd, 'w') as f:
            yaml.dump(self.test_data, f)
            
    def tearDown(self):
        os.remove(self.path)
        
    def test_load_and_shuffle(self):
        """Test that names are loaded and shuffled."""
        registry = NameRegistry(self.path)
        self.assertEqual(len(registry.available_names), 4)
        # Cannot easily test shuffle without seed control, but length is key.
        
    def test_unique_names(self):
        """Test that names are unique and exhausted correctly."""
        registry = NameRegistry(self.path)
        names = set()
        for _ in range(4):
            names.add(registry.get_system_name())
            
        self.assertEqual(len(names), 4)
        self.assertTrue("Alpha" in names)
        
        # Test fallback
        fallback = registry.get_system_name()
        self.assertTrue(fallback.startswith("Unknown-"))
        
    def test_roman_numerals(self):
        """Test Roman numeral conversion."""
        self.assertEqual(NameRegistry.to_roman(1), "I")
        self.assertEqual(NameRegistry.to_roman(2), "II")
        self.assertEqual(NameRegistry.to_roman(3), "III")
        self.assertEqual(NameRegistry.to_roman(4), "IV")
        self.assertEqual(NameRegistry.to_roman(5), "V")
        self.assertEqual(NameRegistry.to_roman(9), "IX")
        self.assertEqual(NameRegistry.to_roman(10), "X")
        
    def test_planet_naming_simple(self):
        """Test standard planet naming."""
        registry = NameRegistry(self.path)
        
        # Mock Planets
        # Planet(type, ring, location)
        p1 = Planet(PlanetType.TERRAN, 1, (0,0))
        p2 = Planet(PlanetType.GAS_GIANT, 3, (0,0))
        p3 = Planet(PlanetType.ICE_WORLD, 5, (0,0))
        
        planets = [p3, p1, p2] # Unsorted
        
        registry.name_planets("Sol", planets)
        
        # Should be sorted by distance
        # p1 (1) -> Sol I
        # p2 (3) -> Sol II
        # p3 (5) -> Sol III
        
        self.assertEqual(p1.name, "Sol I")
        self.assertEqual(p2.name, "Sol II")
        self.assertEqual(p3.name, "Sol III")
        
    def test_planet_naming_same_distance(self):
        """Test that planets at same distance get sequential numbers if locations differ."""
        registry = NameRegistry(self.path)
        
        # Two planets at ring 3, different locations
        p1 = Planet(PlanetType.TERRAN, 3, (1,0))
        p2 = Planet(PlanetType.TERRAN, 3, (0,1))
        
        planets = [p1, p2]
        registry.name_planets("Sol", planets)
        
        names = {p1.name, p2.name}
        self.assertEqual(names, {"Sol I", "Sol II"})
        
    def test_planet_naming_moons(self):
        """Test that planets at same distance AND location get suffix."""
        registry = NameRegistry(self.path)
        
        # Two planets at ring 3, SAME location
        # Simulate moon by having same location object
        loc = (2,2)
        p1 = Planet(PlanetType.TERRAN, 3, loc) # "Larger" (first in list/sort)
        p2 = Planet(PlanetType.BARREN, 3, loc) # "Smaller" (second)
        
        # Force order for test stability since we rely on list order for size proxy
        planets = [p1, p2]
        
        registry.name_planets("Sol", planets)
        
        self.assertEqual(p1.name, "Sol I") 
        self.assertEqual(p2.name, "Sol Ia")

if __name__ == '__main__':
    unittest.main()
