
import unittest
from unittest.mock import MagicMock, patch
import pygame
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, VEHICLE_CLASSES
from components import Component

class TestValidationWarnings(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Ensure 'Frigate' exists
        if "Frigate" not in VEHICLE_CLASSES:
             VEHICLE_CLASSES["Frigate"] = {"max_mass": 2000, "hull_mass": 100}

        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Frigate")
        
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
        engine = self.create_comp(id="engine", fuel_cost=10, type="Engine")
        # Ensure attribute is set (Standard Engine class might map it, generic Component maps all data keys)
        
        self.ship.add_component(engine, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Fuel Storage" in w for w in warnings), f"Expected 'Needs Fuel Storage', got {warnings}")
        
        # Add Fuel Tank
        tank = self.create_comp(id="tank", resource_type="fuel", type="Tank", capacity=100)
        self.ship.add_component(tank, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Fuel Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

    def test_ammo_warning(self):
        # Add Railgun requiring ammo
        gun = self.create_comp(id="railgun", ammo_cost=1, type="ProjectileWeapon")
        self.ship.add_component(gun, LayerType.OUTER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Ammo Storage" in w for w in warnings), f"Expected 'Needs Ammo Storage', got {warnings}")
        
        # Add Ordnance Tank
        tank = self.create_comp(id="ammo_tank", resource_type="ammo", type="Tank", capacity=100)
        self.ship.add_component(tank, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Ammo Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

    def test_energy_warning_direct_cost(self):
        # Add Laser requiring energy
        laser = self.create_comp(id="laser", energy_cost=5, type="BeamWeapon")
        self.ship.add_component(laser, LayerType.OUTER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Energy Storage" in w for w in warnings), f"Expected 'Needs Energy Storage', got {warnings}")
        
        # Add Battery
        battery = self.create_comp(id="battery", resource_type="energy", type="Tank", capacity=1000)
        self.ship.add_component(battery, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Energy Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

    def test_energy_warning_ability_cost(self):
        # Add Shield requiring regen energy via Ability
        shield = self.create_comp(id="shield", type="ShieldRegenerator", abilities={"EnergyConsumption": 2.0})
        self.ship.add_component(shield, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertTrue(any("Needs Energy Storage" in w for w in warnings), f"Expected 'Needs Energy Storage', got {warnings}")
        
        # Add Generator (which counts as Energy Source in our rule if type=Generator or provides EnergyGeneration)
        # Note: In our rule, type="Generator" sets has_energy_gen=True. But Wait...
        # The rule checked: `if needs_energy_storage and not has_energy_storage`.
        # `has_energy_storage` is set if resource_type == 'energy'.
        # Does Generator provide storage? Usually not. Batteries do.
        # My rule implemented: "Needs Energy Storage" if missing.
        # The prompt said: "Examples are anything the uses energy should need a battery".
        # So a Generator alone might NOT be enough if I strictly enforce "Storage".
        # But `components.json` Generator has `resource_type`? No.
        # If I add a Generator, does it silence the warning?
        # My implementation: `if resource_type == 'energy': has_energy_storage = True`.
        # Generator usually generates.
        # Let's check `components.json` for Generator.
        # It has `energy_generation` but no `capacity`.
        # So strictly, it doesn't provide storage.
        # But maybe I should allow Generator to satisfy?
        # The Prompt: "anything the uses energy should need a battery ... I may create a different energy storage component".
        # It seems distinct from generation.
        # So checking strictly for storage (capacity > 0) is correct per prompt "Need a battery".
        
        # So let's add a Battery.
        battery = self.create_comp(id="battery", resource_type="energy", type="Tank", capacity=100)
        self.ship.add_component(battery, LayerType.INNER)
        
        warnings = self.ship.get_validation_warnings()
        self.assertFalse(any("Needs Energy Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}")

if __name__ == '__main__':
    unittest.main()
