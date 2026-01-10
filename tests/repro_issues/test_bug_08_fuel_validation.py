import unittest
import pygame
import pytest

from game.simulation.entities.ship import Ship, LayerType, load_vehicle_classes
from game.core.registry import RegistryManager
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
        Validation test: Verify ResourceStorage ability is correctly aggregated.
        
        Note: Post-Phase 5, 'requirements' has been removed from vehicleclasses.json.
        This test verifies the ability aggregation mechanism works correctly.
        Fuel tanks use 'ResourceStorage' ability, not 'FuelStorage'.
        """
        # Create a Cruiser (has enough mass budget for fuel tank)
        ship = Ship("Test Cruiser", 0, 0, (255, 255, 255), ship_class="Cruiser")
        
        # Add Fuel Tank (provides 'ResourceStorage' ability for 'fuel')
        tank = create_component("fuel_tank")
        self.assertIsNotNone(tank, "Failed to create 'fuel_tank'")
        
        # Use INNER layer which is appropriate for fuel tanks
        success = ship.add_component(tank, LayerType.INNER)
        self.assertTrue(success, "Failed to add fuel tank to ship")

        # Force Recalculate
        ship.recalculate_stats()
        
        # Verify ResourceStorage ability is correctly aggregated
        # Check the resource registry for max fuel
        fuel_max = ship.resources.get_max_value('fuel')
        print(f"Max Fuel: {fuel_max}")
        
        # Fuel tank should provide fuel storage
        self.assertGreater(fuel_max, 0, "Fuel tank should provide fuel storage")
        
        # Validation should work without errors
        missing = ship.get_missing_requirements()
        print(f"Missing Requirements: {missing}")
        self.assertIsInstance(missing, list)
        
if __name__ == '__main__':
    unittest.main()
