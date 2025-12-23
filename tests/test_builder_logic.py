
import unittest
import pygame
from ship import Ship, initialize_ship_data, LayerType
from components import load_components, create_component
import os

class TestBuilderLogic(unittest.TestCase):
    """Test ship validation logic used by the builder."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.ship = Ship("BuilderTarget", 0, 0, (255,255,255), ship_class="Escort")

    def test_mass_limit_validation(self):
        """Verify mass_limits_ok is false if mass exceeds budget or layer limits."""
        # Escort mass budget is 1000.
        # Layer limit for OUTER is 50%.
        # 8 plates * 30 mass = 240. (within 1000 and within 50%)
        for _ in range(8):
            self.ship.add_component(create_component('armor_plate'), LayerType.ARMOR)
        
        self.ship.recalculate_stats()
        # ARMOR limit is 30%. 240 / 1000 = 0.24 (OK)
        self.assertTrue(self.ship.mass_limits_ok)
        
        # Add a lot more to trigger TOTAL mass limit
        for _ in range(50):
            # Use batteries to spread mass if needed, but ARMOR is fine for total mass check
            self.ship.add_component(create_component('armor_plate'), LayerType.ARMOR)
        
        self.ship.recalculate_stats()
        self.assertGreater(self.ship.mass, self.ship.max_mass_budget)
        self.assertFalse(self.ship.mass_limits_ok)

    def test_missing_bridge_requirement(self):
        """Verify get_missing_requirements identifies missing command capability."""
        self.ship.recalculate_stats()
        missing = self.ship.get_missing_requirements()
        # Escort should need Command And Control
        self.assertTrue(any("Command And Control" in m for m in missing))
        
        # Add bridge
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.recalculate_stats()
        missing = self.ship.get_missing_requirements()
        self.assertFalse(any("Command And Control" in m for m in missing))

    def test_invalid_layer_addition_fallback(self):
        """Verify add_component returns False for invalid layers."""
        engine = create_component('standard_engine')
        # Engine only allowed in INNER, OUTER
        res = self.ship.add_component(engine, LayerType.ARMOR)
        self.assertFalse(res)
        self.assertNotIn(engine, self.ship.layers[LayerType.ARMOR]['components'])

    def test_vehicle_class_requirements_loading(self):
        """Verify ship_class affects requirements."""
        # Use a "Fighter (Small)" specifically
        fighter = Ship("Flyer", 0, 0, (255,255,255), ship_class="Fighter (Small)")
        fighter.recalculate_stats()
        missing = fighter.get_missing_requirements()
        
        # Should have requirements
        self.assertTrue(len(missing) > 0)

if __name__ == '__main__':
    unittest.main()
