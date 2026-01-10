import unittest
from unittest.mock import MagicMock, patch
import pygame
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager
from game.simulation.components.component import Component

class TestBug03Validation(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Ensure 'Cruiser' exists
        classes = RegistryManager.instance().vehicle_classes
        if "Cruiser" not in classes:
             classes["Cruiser"] = {"max_mass": 16000, "default_hull_id": "hull_cruiser"}

        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser")
        
        self.base_data = {
            "id": "test_comp",
            "name": "Test Comp",
            "type": "Component",
            "mass": 10,
            "hp": 10,
            "allowed_layers": ["INNER", "OUTER", "CORE"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": {}
        }

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()

    def create_comp(self, **kwargs):
        data = self.base_data.copy()
        data.update(kwargs)
        return Component(data)

    def test_fuel_warning_persistence_with_wrong_resource(self):
        """
        Verify that adding Energy Storage does NOT resolve Fuel Storage warning.
        Ref: BUG-03
        """
        # 1. Add Engine requiring fuel
        engine_abilities = {
            "ResourceConsumption": [{"resource": "fuel", "amount": 10, "trigger": "constant"}]
        }
        engine = self.create_comp(id="engine", type="Engine", abilities=engine_abilities)
        
        self.ship.add_component(engine, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Fuel Storage" in w for w in warnings), 
                       f"Pre-condition: Expected 'Needs Fuel Storage', got {warnings}")
        
        # 2. Add Battery (Energy Storage) - Should NOT fix fuel
        battery_abilities = {
            "ResourceStorage": [{"resource": "energy", "amount": 1000}]
        }
        battery = self.create_comp(id="battery", type="Tank", abilities=battery_abilities)
        self.ship.add_component(battery, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        
        # If the bug exists (validation is loose), the warning will be gone.
        self.assertTrue(any("Needs Fuel Storage" in w for w in warnings), 
                       f"BUG REPRO: 'Needs Fuel Storage' warning disappeared after adding Energy Storage! Warnings: {warnings}")

    def test_ammo_warning_persistence_with_wrong_resource(self):
        """
        Verify that adding Fuel Storage does NOT resolve Ammo Storage warning.
        """
        # 1. Add Railgun requiring ammo
        gun_abilities = {
            "ResourceConsumption": [{"resource": "ammo", "amount": 1, "trigger": "activation"}]
        }
        gun = self.create_comp(id="railgun", type="ProjectileWeapon", abilities=gun_abilities)
        self.ship.add_component(gun, LayerType.OUTER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Ammo Storage" in w for w in warnings), 
                       f"Pre-condition: Expected 'Needs Ammo Storage', got {warnings}")
        
        # 2. Add Fuel Tank - Should NOT fix ammo
        tank_abilities = {
            "ResourceStorage": [{"resource": "fuel", "amount": 100}]
        }
        tank = self.create_comp(id="tank", type="Tank", abilities=tank_abilities)
        self.ship.add_component(tank, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        
        self.assertTrue(any("Needs Ammo Storage" in w for w in warnings), 
                       f"BUG REPRO: 'Needs Ammo Storage' warning disappeared after adding Fuel Storage! Warnings: {warnings}")

if __name__ == '__main__':
    unittest.main()
