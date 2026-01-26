
import sys
import os
sys.path.append(os.getcwd())
import unittest
from game.simulation.components.component import load_components, create_component, load_modifiers, MODIFIER_REGISTRY
import json

class TestComponentScaling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load data
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")

    def test_crew_scaling(self):
        # Create Crew Quarters
        cq = create_component("crew_quarters")
        self.assertIsNotNone(cq, "Crew Quarters should exist")
        
        initial_capacity = cq.crew_capacity
        print(f"Initial Crew Capacity: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        # We need to manually add modifier as if it was in the builder or loaded
        # modifiers.json has id "simple_size_mount"
        res = cq.add_modifier("simple_size_mount", 2.0)
        self.assertTrue(res, "Should successfully add modifier")

        scaled_capacity = cq.crew_capacity
        print(f"Scaled Crew Capacity (x2): {scaled_capacity}")

        self.assertEqual(scaled_capacity, initial_capacity * 2, "Crew Capacity should scale linearly with size")

    def test_life_support_scaling(self):
        # Create Life Support
        ls = create_component("life_support")
        self.assertIsNotNone(ls, "Life Support should exist")
        
        initial_capacity = ls.life_support_capacity
        print(f"Initial Life Support: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        ls.add_modifier("simple_size_mount", 2.0)

        scaled_capacity = ls.life_support_capacity
        print(f"Scaled Life Support (x2): {scaled_capacity}")

        self.assertEqual(scaled_capacity, initial_capacity * 2, "Life Support should scale linearly with size")

if __name__ == '__main__':
    unittest.main()
