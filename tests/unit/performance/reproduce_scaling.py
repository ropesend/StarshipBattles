import sys
import os
import unittest
import pygame

# Pattern I: Save original path and handle robust root discovery
original_path = sys.path.copy()
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from game.simulation.components.component import load_components, create_component, load_modifiers
from game.core.registry import RegistryManager
import json

class TestComponentScaling(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Ensure clean state
        RegistryManager.instance().clear()
        
        # Load data using robust paths
        load_components(os.path.join(ROOT_DIR, "data", "components.json"))
        load_modifiers(os.path.join(ROOT_DIR, "data", "modifiers.json"))

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()
        # Restore sys.path
        global original_path
        sys.path = original_path.copy()
        super().tearDown()

    def test_crew_scaling(self):
        # Create Crew Quarters
        cq = create_component("crew_quarters")
        self.assertIsNotNone(cq, "Crew Quarters should exist")
        
        # New Ability System: Access via get_ability
        initial_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Initial Crew Capacity: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        res = cq.add_modifier("simple_size_mount", 2.0)
        self.assertTrue(res, "Should successfully add modifier")

        scaled_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Scaled Crew Capacity (x2): {scaled_capacity}")

        self.assertEqual(scaled_capacity, initial_capacity * 2, "Crew Capacity should scale linearly with size")

    def test_life_support_scaling(self):
        # Create Life Support
        ls = create_component("life_support")
        self.assertIsNotNone(ls, "Life Support should exist")
        
        initial_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Initial Life Support: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        ls.add_modifier("simple_size_mount", 2.0)

        scaled_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Scaled Life Support (x2): {scaled_capacity}")

        self.assertEqual(scaled_capacity, initial_capacity * 2, "Life Support should scale linearly with size")

if __name__ == '__main__':
    unittest.main()
