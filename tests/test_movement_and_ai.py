
import unittest
from unittest.mock import MagicMock
import pygame
import os
import sys

# Ensure imports work from project root
sys.path.append(os.getcwd())

from ship import Ship
from battle import BattleScene
from ai import AIController
from components import LayerType, COMPONENT_REGISTRY, load_components, load_modifiers

class TestMovementAndAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Load data once
        base_path = os.getcwd() 
        if not os.path.exists(os.path.join(base_path, "data", "components.json")):
             base_path = os.path.dirname(os.getcwd())
             
        comp_path = os.path.join(base_path, "data", "components.json")
        mod_path = os.path.join(base_path, "data", "modifiers.json")
        
        if os.path.exists(comp_path):
            load_components(comp_path)
        if os.path.exists(mod_path):
            load_modifiers(mod_path)

    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), 0)
        self.ship.ship_class = "Escort"

    def get_component_clone(self, id):
        if id in COMPONENT_REGISTRY:
            return COMPONENT_REGISTRY[id].clone()
        return None

    def test_derelict_status_logic(self):
        """
        Verify strict requirements for a ship to NOT be derelict.
        """
        s = self.ship
        
        # 1. Empty ship -> Derelict
        s.recalculate_stats()
        self.assertTrue(s.is_derelict, "Empty ship should be derelict")

        # 2. Add Bridge only -> Derelict
        bridge = self.get_component_clone("bridge")
        s.add_component(bridge, LayerType.CORE)
        s.recalculate_stats()
        self.assertTrue(s.is_derelict, "Ship with only bridge should be derelict")
        
        # 3. Add Generator -> Derelict
        gen = self.get_component_clone("generator")
        s.add_component(gen, LayerType.CORE)
        s.recalculate_stats()
        self.assertTrue(s.is_derelict, "Ship with only bridge+gen should be derelict")
        
        # 4. Add Engines + Life + Crew + Fuel -> Not Derelict
        engine = self.get_component_clone("standard_engine")
        s.add_component(engine, LayerType.OUTER)
        
        ls = self.get_component_clone("life_support")
        s.add_component(ls, LayerType.INNER)
        
        quart = self.get_component_clone("crew_quarters")
        s.add_component(quart, LayerType.INNER)

        tank = self.get_component_clone("fuel_tank")
        s.add_component(tank, LayerType.INNER)
        
        s.recalculate_stats()
        self.assertFalse(s.is_derelict, "Fully equipped ship should NOT be derelict")
        self.assertGreater(s.total_thrust, 0)

    def test_ai_target_acquisition_long_range(self):
        """
        Regression Test: Ensure AI can target enemies at very long range.
        """
        attacker = self.ship
        attacker.ai_strategy = "max_weapons_range"
        attacker.position = pygame.math.Vector2(0, 0)
        
        target = Ship("Target", 50000, 0, (255,0,0), 1)
        target.ship_class = "Escort"
        target.mass = 1000 
        
        mock_grid = MagicMock()
        mock_grid.query_radius.return_value = [target]
        
        ai = AIController(attacker, mock_grid, 1)
        
        found_target = ai.find_target()
        
        self.assertIsNotNone(found_target, "AI failed to acquire long-range target")
        self.assertEqual(found_target, target)

    def test_ai_thrust_command_generation(self):
        """
        Verify AI issues thrust commands when it has a valid target ahead.
        """
        attacker = self.ship
        attacker.add_component(self.get_component_clone("bridge"), LayerType.CORE)
        attacker.add_component(self.get_component_clone("standard_engine"), LayerType.OUTER)
        attacker.add_component(self.get_component_clone("generator"), LayerType.CORE)
        attacker.add_component(self.get_component_clone("life_support"), LayerType.INNER)
        attacker.add_component(self.get_component_clone("crew_quarters"), LayerType.INNER)
        attacker.add_component(self.get_component_clone("fuel_tank"), LayerType.INNER)
        attacker.recalculate_stats()
        
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0 
        
        target = Ship("Target", 500, 0, (255,0,0), 1)
        target.mass = 100
        
        mock_grid = MagicMock()
        mock_grid.query_radius.return_value = [target]
        
        ai = AIController(attacker, mock_grid, 1)
        
        # 1. Find target
        attacker.current_target = ai.find_target()
        self.assertEqual(attacker.current_target, target)
        
        # 2. Update AI
        attacker.is_thrusting = False
        ai.update()
        
        self.assertTrue(attacker.is_thrusting, "AI did not set is_thrusting despite valid target ahead")

if __name__ == '__main__':
    unittest.main()
