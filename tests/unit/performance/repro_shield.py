import unittest
import sys
import os
import pygame

# Pattern I: Save original path and handle robust root discovery
original_path = sys.path.copy()
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, LayerType
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.registry import RegistryManager

class TestShieldRepro(unittest.TestCase):

    def setUp(self):
        pygame.init()
        # Ensure clean state
        RegistryManager.instance().clear()
        
        base_dir = ROOT_DIR
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
        self.ship = Ship("ShieldRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.calculator = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()
        # Restore sys.path
        global original_path
        sys.path = original_path.copy()
        super().tearDown()

    def test_shield_regen_cost(self):
        # 1. create ShieldRegen
        regen = create_component('shield_regen')
        # Expect 2.0 from json
        # ability_instances should have ResourceConsumption
        cons = regen.get_ability('ResourceConsumption')
        val = cons.amount if cons else 'MISSING'
        print(f"DEBUG: Initial Energy Cost: {val}")
        
        self.ship.add_component(regen, LayerType.INNER)
        self.ship.recalculate_stats()
        
        cons = regen.get_ability('ResourceConsumption')
        val = cons.amount if cons else 'MISSING'
        print(f"DEBUG: Post-Recalc Energy Cost: {val}")
        
        self.assertEqual(val, 2.0, "Energy cost should persist as 2.0")

if __name__ == '__main__':
    unittest.main()
