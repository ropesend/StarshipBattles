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
        

if __name__ == '__main__':
    unittest.main()
