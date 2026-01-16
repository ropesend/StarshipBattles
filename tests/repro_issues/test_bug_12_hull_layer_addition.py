import unittest
import pygame
from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
from game.simulation.components.component import load_components, create_component
from game.core.registry import RegistryManager
from game.core.constants import ROOT_DIR, COMPONENTS_FILE

class TestBug12HullAddition(unittest.TestCase):
    """Reproduction test for BUG-12: Component Addition to Hull Layer."""

    def setUp(self):
        pygame.init()
        # Set up registry and data
        initialize_ship_data(ROOT_DIR)
        load_components(COMPONENTS_FILE)
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()

    def test_prevent_non_hull_addition_to_hull_layer(self):
        """Verify that non-hull components cannot be added to the HULL layer."""
        # 'armor_plate' is definitely not a hull component
        comp = create_component('armor_plate')
        self.assertIsNotNone(comp)
        
        # This SHOULD return False and not add the component
        res = self.ship.add_component(comp, LayerType.HULL)
        
        self.assertFalse(res, "Should NOT be able to add armor_plate to HULL layer")
        self.assertNotIn(comp, self.ship.layers[LayerType.HULL]['components'], 
                        "Component should not be present in HULL layer list")

    def test_prevent_any_addition_to_hull_layer_in_builder(self):
        """Verify that even 'bridge' or 'engine' cannot be added to HULL layer."""
        for comp_id in ['bridge', 'standard_engine']:
            comp = create_component(comp_id)
            res = self.ship.add_component(comp, LayerType.HULL)
            self.assertFalse(res, f"Should NOT be able to add {comp_id} to HULL layer")
            self.assertNotIn(comp, self.ship.layers[LayerType.HULL]['components'])

if __name__ == '__main__':
    unittest.main()
