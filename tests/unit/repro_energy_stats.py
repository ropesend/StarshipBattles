import unittest
import sys
import os
import pygame
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, Component, LayerType
from game.core.registry import RegistryManager
from ship_stats import ShipStatsCalculator

class TestEnergyRepro(unittest.TestCase):
    def setUp(self):
        pygame.init()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "game.simulation.components.component.json"))

    def test_keys(self):
        print("DEBUG: Checking Component Registry Keys")
        comps = RegistryManager.instance().components
        if 'laser_cannon' in comps:
            data = comps['laser_cannon'].data
            print(f"DEBUG: Laser Keys: {list(data.keys())}")
            print(f"DEBUG: Laser energy_cost value in data: {data.get('energy_cost')}")
            print(f"DEBUG: Laser energy_cost type in data: {type(data.get('energy_cost'))}")
            
            laser = create_component('laser_cannon')
            print(f"DEBUG: Created Laser energy_cost attr: {getattr(laser, 'energy_cost', 'MISSING')}")
        else:
            print("ERROR: laser_cannon missing")

        if 'generator' in comps:
            data = comps['generator'].data
            print(f"DEBUG: Generator Keys: {list(data.keys())}")
            print(f"DEBUG: Generator energy_generation value in data: {data.get('energy_generation')}")
            
            gen = create_component('generator')
            print(f"DEBUG: Created Gen energy_generation_rate attr: {getattr(gen, 'energy_generation_rate', 'MISSING')}")

if __name__ == '__main__':
    unittest.main()
