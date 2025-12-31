import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, initialize_ship_data
from components import load_components, create_component, LayerType
from ship_stats import ShipStatsCalculator

class TestShieldRepro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))

    def setUp(self):
        self.ship = Ship("ShieldRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.calculator = ShipStatsCalculator(self.ship.vehicle_classes if hasattr(self.ship, 'vehicle_classes') else {})

    def test_shield_regen_cost(self):
        # 1. create ShieldRegen
        regen = create_component('shield_regen')
        # Expect 2.0 from json
        print(f"DEBUG: Initial Energy Cost: {getattr(regen, 'energy_cost', 'MISSING')}")
        
        self.ship.add_component(regen, LayerType.INNER)
        self.ship.recalculate_stats()
        
        print(f"DEBUG: Post-Recalc Energy Cost: {getattr(regen, 'energy_cost', 'MISSING')}")
        
        self.assertEqual(regen.energy_cost, 2.0, "Energy cost should persist as 2.0")

if __name__ == '__main__':
    unittest.main()
