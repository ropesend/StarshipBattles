
import unittest
import pygame
import sys
import os
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from game.simulation.entities.ship import Ship, LayerType, VEHICLE_CLASSES, load_vehicle_classes
from game.simulation.components.component import load_components, create_component

class TestBug08FuelValidation(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        
        # Load REAL components
        load_components("data/components.json")
        # Load REAL vehicle classes
        load_vehicle_classes("data/vehicleclasses.json")

    def test_class_requirements_fuel_storage_failure(self):
        """
        Reproduction of BUG-08: "Needs Fuel Storage" warning despite Fuel Tank presence.
        """
        # Create a Fighter (Medium) which we know requires 'fuel' -> 'FuelStorage'
        # based on previous inspection of vehicleclasses.json
        ship = Ship("Test Fighter", 0, 0, (255, 255, 255), ship_class="Fighter (Medium)")
        
        # Verify it has the requirement (Sanity Check)
        class_def = VEHICLE_CLASSES.get("Fighter (Medium)", {})
        reqs = class_def.get('requirements', {})
        self.assertIn("fuel", reqs, "Test Setup Failure: Fighter (Medium) should have a fuel requirement")
        
        # Add Fuel Tank (provides 'ResourceStorage' for 'fuel')
        tank = create_component("fuel_tank")
        self.assertIsNotNone(tank, "Failed to create 'fuel_tank'")
        
        ship.add_component(tank, LayerType.CORE)
        

        # Force Recalculate
        ship.recalculate_stats()
        
        # Debugging
        print(f"FuelStorage Total: {ship.get_ability_total('FuelStorage')}")
        print(f"ResourceStorage Total: {ship.get_ability_total('ResourceStorage')}")
        
        # Check Missing Requirements
        missing = ship.get_missing_requirements()
        print(f"Missing Requirements: {missing}")
        
        # Check for FuelStorage warning
        has_fuel_error = any("FuelStorage" in m for m in missing)
        
        # ASSERT: Should NOT have fuel error if working correctly.
        # This will FAIL if bug is present (Red State).
        self.assertFalse(has_fuel_error, f"Validation Failure: Ship incorrectly reports missing FuelStorage despite having Fuel Tank! Missing: {missing}")
        
if __name__ == '__main__':
    unittest.main()
