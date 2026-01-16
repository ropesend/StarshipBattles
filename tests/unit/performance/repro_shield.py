import unittest
import pygame

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, LayerType
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.registry import RegistryManager
from game.core.constants import ROOT_DIR, COMPONENTS_FILE

class TestShieldRepro(unittest.TestCase):

    def setUp(self):
        pygame.init()
        # Ensure clean state
        RegistryManager.instance().clear()

        initialize_ship_data(ROOT_DIR)
        load_components(COMPONENTS_FILE)
        self.ship = Ship("ShieldRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.calculator = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()

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
