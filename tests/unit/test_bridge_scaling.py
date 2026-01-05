
import unittest
import sys
import os
import math

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.simulation.components.component import Component, load_components
from game.core.registry import RegistryManager

class MockShip:
    def __init__(self, max_mass):
        self.max_mass_budget = max_mass

class TestBridgeScaling(unittest.TestCase):
    def setUp(self):
        # Load components to ensure Bridge is available
        # But we can also just manually load the json if we want to be independent of global loading
        # For this test, let's try to load the actual definition from file to ensure we test the file edits.
        load_components("data/components.json")
        self.bridge_def = RegistryManager.instance().components.get("bridge")
        
    def test_bridge_scaling_1000(self):
        # Base case: 1000 mass
        # Sqrt(1) = 1
        # Mass = 50 * 1 = 50
        # HP = 200 * 1 = 200
        # Crew = ceil(5 * 1) = 5
        
        comp = self.bridge_def.clone()
        ship = MockShip(1000)
        comp.ship = ship
        
        comp.recalculate_stats()
        
        self.assertAlmostEqual(comp.mass, 50.0)
        self.assertEqual(comp.max_hp, 200)
        self.assertEqual(comp.abilities['CrewRequired'], 5)

    def test_bridge_scaling_4000(self):
        # 4000 mass -> scale = sqrt(4) = 2
        # Mass = 50 * 2 = 100
        # HP = 200 * 2 = 400
        # Crew = ceil(5 * 2) = 10
        
        comp = self.bridge_def.clone()
        ship = MockShip(4000)
        comp.ship = ship
        
        comp.recalculate_stats()
        
        self.assertAlmostEqual(comp.mass, 100.0)
        self.assertEqual(comp.max_hp, 400)
        self.assertEqual(comp.abilities['CrewRequired'], 10)

    def test_bridge_scaling_odd(self):
        # 2000 mass -> scale = sqrt(2) = 1.4142...
        # Mass = 50 * 1.414 = 70.71...
        # HP = 200 * 1.414 = 282.84... -> int(282)
        # Crew = ceil(5 * 1.414) = ceil(7.07) = 8
        
        scale = math.sqrt(2000 / 1000)
        
        comp = self.bridge_def.clone()
        ship = MockShip(2000)
        comp.ship = ship
        
        comp.recalculate_stats()
        
        self.assertAlmostEqual(comp.mass, 50 * scale)
        self.assertEqual(comp.max_hp, int(200 * scale))
        self.assertEqual(comp.abilities['CrewRequired'], math.ceil(5 * scale)) 
        self.assertEqual(comp.abilities['CrewRequired'], 8)

if __name__ == '__main__':
    unittest.main()
