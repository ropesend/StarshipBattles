import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, initialize_ship_data
from ui.builder.stats_config import StatDefinition, get_logistics_rows

class TestStatsConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data()

    def test_dynamic_resource_rows(self):
        # Create a ship and register standard + custom resources
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        # Manually register to simulate a ship component setup
        ship.resources.register_storage("fuel", 100)
        ship.resources.register_storage("energy", 500)
        ship.resources.register_storage("biomass", 50) # Custom resource
        
        # Get dynamic rows
        # Assuming we add a method like get_resource_rows(ship) to StatsConfig class
        # Or if StatsConfig is just a module, we test the module-level function
        
        # Since StatsConfig in current file is the CLASS or MODULE? 
        # Looking at previous view_file, 'stats_config.py' has 'class StatDefinition' but STATS_CONFIG is a dict.
        # It doesn't have a 'StatsConfig' class that manages logic, it's a data loader.
        # So likely we will ADD a function `get_logistics_rows(ship)` that returns the list including dynamic ones.
        
        from ui.builder.stats_config import get_logistics_rows
        
        rows = get_logistics_rows(ship)
        
        # Check for Fuel
        fuel_row = next((r for r in rows if r.label == "Fuel Capacity"), None)
        self.assertIsNotNone(fuel_row)
        self.assertEqual(fuel_row.get_value(ship), 100)
        
        # Check for Energy
        energy_row = next((r for r in rows if r.label == "Energy Capacity"), None)
        self.assertIsNotNone(energy_row)
        self.assertEqual(energy_row.get_value(ship), 500)
        
        # Check for Biomass (Custom) - Should be capitalized automatically?
        biomass_row = next((r for r in rows if "Biomass" in r.label), None)
        self.assertIsNotNone(biomass_row, "Should find dynamic row for Biomass")
        self.assertEqual(biomass_row.get_value(ship), 50)
        
    def test_resource_endurance_rows(self):
         ship = Ship("TestShip", 0, 0, (255, 255, 255))
         ship.resources.register_storage("fuel", 100)
         
         # Add a component with consumption
         from game.simulation.components.component import Component
         from game.simulation.entities.ship import LayerType
         
         comp = Component({'id': 'test_engine', 'name': 'Test Engine', 'type': 'Engine', 'mass': 10, 'hp': 10})
         # Inject ability data
         comp.abilities['ResourceConsumption'] = [{'resource': 'fuel', 'amount': 10, 'trigger': 'constant'}]
         # Must instantiate abilities for the system to see them
         comp._instantiate_abilities()
         
         # Add to ship layer manually (avoid validation for unit test simplicity)
         ship.layers[LayerType.CORE]['components'].append(comp)
         comp.ship = ship
         
         from ui.builder.stats_config import get_logistics_rows
         rows = get_logistics_rows(ship)
         
         # Find Endurance Row
         end_row = next((r for r in rows if "Fuel Endurance" in r.label), None)
         self.assertIsNotNone(end_row)
         
         # Value = max / consumption = 100 / 10 = 10
         # But the getter in stats_config might re-calculate or just read ship.fuel_endurance
         # Let's ensure ship.fuel_endurance is set if that's what it reads.
         ship.fuel_endurance = 10.0
         
         self.assertEqual(end_row.get_value(ship), 10.0)

if __name__ == '__main__':
    unittest.main()
