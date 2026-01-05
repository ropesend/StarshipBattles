
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

class TestValidationWarnings(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Ensure 'Cruiser' exists
        if "Cruiser" not in RegistryManager.instance().vehicle_classes:
             RegistryManager.instance().vehicle_classes["Cruiser"] = {"max_mass": 16000, "hull_mass": 400}

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

    def create_comp(self, **kwargs):
        data = self.base_data.copy()
        data.update(kwargs)
        return Component(data)

    def test_fuel_warning(self):
        # Add Engine requiring fuel
        engine_abilities = {
            "ResourceConsumption": [{"resource": "fuel", "amount": 10, "trigger": "constant"}]
        }
        engine = self.create_comp(id="engine", type="Engine", abilities=engine_abilities)
        
        self.ship.add_component(engine, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Fuel Storage" in w for w in warnings), f"Expected 'Needs Fuel Storage', got {warnings}")
        
        # Add Fuel Tank
        tank_abilities = {
            "ResourceStorage": [{"resource": "fuel", "amount": 100}]
        }
        tank = self.create_comp(id="tank", type="Tank", abilities=tank_abilities)
        self.ship.add_component(tank, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Fuel Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

    def test_ammo_warning(self):
        # Add Railgun requiring ammo
        gun_abilities = {
            "ResourceConsumption": [{"resource": "ammo", "amount": 1, "trigger": "activation"}]
        }
        gun = self.create_comp(id="railgun", type="ProjectileWeapon", abilities=gun_abilities)
        self.ship.add_component(gun, LayerType.OUTER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Ammo Storage" in w for w in warnings), f"Expected 'Needs Ammo Storage', got {warnings}")
        
        # Add Ordnance Tank
        tank_abilities = {
            "ResourceStorage": [{"resource": "ammo", "amount": 100}]
        }
        tank = self.create_comp(id="ammo_tank", type="Tank", abilities=tank_abilities)
        self.ship.add_component(tank, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Ammo Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

    def test_energy_warning(self):
        # Add Laser requiring energy
        laser_abilities = {
            "ResourceConsumption": [{"resource": "energy", "amount": 5, "trigger": "activation"}]
        }
        laser = self.create_comp(id="laser", type="BeamWeapon", abilities=laser_abilities)
        self.ship.add_component(laser, LayerType.OUTER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Energy Storage" in w for w in warnings), f"Expected 'Needs Energy Storage', got {warnings}")
        
        # Add Battery
        battery_abilities = {
            "ResourceStorage": [{"resource": "energy", "amount": 1000}]
        }
        battery = self.create_comp(id="battery", type="Tank", abilities=battery_abilities)
        self.ship.add_component(battery, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Energy Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

if __name__ == '__main__':
    unittest.main()
