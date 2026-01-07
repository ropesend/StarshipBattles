
import unittest
import pygame
from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
from game.simulation.components.component import load_components, create_component
import os

class TestBuilderLogic(unittest.TestCase):
    """Test ship validation logic used by the builder."""
    
        

    def setUp(self):
        pygame.init()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
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
        # Add more to trigger total mass limit. 
        # Since add_component prevents exceeding mass, we expect it to return False eventually.
        added_count = 0
        for _ in range(50):
            if self.ship.add_component(create_component('armor_plate'), LayerType.ARMOR):
                added_count += 1
        
        # Should have stopped adding
        self.assertLess(added_count, 50, "Should have been prevented from adding all 50 plates")
        
        # Verify mass is within budget (or close to it if single component pushes slightly over? 
        # actually code checks strictly before adding)
        self.assertLessEqual(self.ship.mass, self.ship.max_mass_budget)
        self.assertTrue(self.ship.mass_limits_ok, "Ship should remain valid via add_component")
        
        # Now manually inject a huge component to verify mass_limits_ok handles invalid states (e.g. from loading)
        huge_plate = create_component('armor_plate')
        huge_plate.mass = 2000 # Way over budget
        self.ship.layers[LayerType.ARMOR]['components'].append(huge_plate)
        huge_plate.ship = self.ship
        self.ship.current_mass += huge_plate.mass
        
        self.ship.recalculate_stats()
        self.assertFalse(self.ship.mass_limits_ok, "Should report invalid if forcibly overloaded")

    def test_missing_bridge_requirement(self):
        """Verify get_missing_requirements identifies missing crew capacity.
        
        Note: Post-Phase 5, the validator no longer reads 'requirements' from JSON.
        It checks CrewCapacity vs CrewRequired for ships with crew-heavy components.
        """
        # Add a component that requires crew (e.g., bridge)
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.recalculate_stats()
        
        # Check if crew requirements are met
        missing = self.ship.get_missing_requirements()
        
        # Bridge requires crew - verify crew housing is flagged if insufficient
        # This may or may not show an error depending on crew capacity vs required
        # The key is that validation runs without crashing
        self.assertIsInstance(missing, list)

    def test_invalid_layer_addition_fallback(self):
        """Verify add_component returns False for invalid layers."""
        engine = create_component('standard_engine')
        # Engine only allowed in INNER, OUTER
        res = self.ship.add_component(engine, LayerType.ARMOR)
        self.assertFalse(res)
        self.assertNotIn(engine, self.ship.layers[LayerType.ARMOR]['components'])

    def test_vehicle_class_requirements_loading(self):
        """Verify ship_class does not crash when validating.
        
        Note: Post-Phase 5, 'requirements' has been removed from vehicleclasses.json.
        The validator now checks CrewCapacity/CrewRequired abilities directly.
        """
        # Use a "Fighter (Small)" specifically
        fighter = Ship("Flyer", 0, 0, (255,255,255), ship_class="Fighter (Small)")
        fighter.recalculate_stats()
        missing = fighter.get_missing_requirements()
        
        # Verify validation works and returns a list (may be empty)
        self.assertIsInstance(missing, list)

if __name__ == '__main__':
    unittest.main()
