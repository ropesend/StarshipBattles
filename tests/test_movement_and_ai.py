
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
from ship import Ship, initialize_ship_data
from battle import BattleScene
from ai import AIController
from components import LayerType, COMPONENT_REGISTRY, load_components, load_modifiers

class TestMovementAndAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Initialize vehicle class definitions FIRST (required for layer configs)
        initialize_ship_data()
        # Load data once
        base_path = os.getcwd() 
        if not os.path.exists(os.path.join(base_path, "data", "components.json")):
             base_path = os.path.dirname(os.getcwd())
             
        comp_path = os.path.join(base_path, "data", "components.json")
        mod_path = os.path.join(base_path, "data", "modifiers.json")
        
        if os.path.exists(comp_path):
            load_components(comp_path)
        if os.path.exists(mod_path):
            cls.mod_path = mod_path
            load_modifiers(mod_path)

    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser")

    def get_component_clone(self, id):
        if id in COMPONENT_REGISTRY:
            return COMPONENT_REGISTRY[id].clone()
        return None

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
        # Build a valid ship with all required components
        # Bridge (CORE) - CommandAndControl
        bridge = self.get_component_clone("bridge")
        attacker.add_component(bridge, LayerType.CORE)
        
        # Generator (CORE)
        gen = self.get_component_clone("generator")
        attacker.add_component(gen, LayerType.CORE)
        
        # Engine (OUTER) - CombatPropulsion
        engine = self.get_component_clone("standard_engine")
        attacker.add_component(engine, LayerType.OUTER)
        
        # Fuel (INNER) - FuelStorage
        fuel = self.get_component_clone("fuel_tank")
        attacker.add_component(fuel, LayerType.INNER)
        
        # Life Support + Crew for operational ship (need multiple for Cruiser crew requirements)
        for _ in range(4):
            ls = self.get_component_clone("life_support")
            attacker.add_component(ls, LayerType.INNER)
            cq = self.get_component_clone("crew_quarters")
            attacker.add_component(cq, LayerType.INNER)
        
        attacker.recalculate_stats()
        
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.update(1/60.0) 
        
        # Attacker is already configured as Cruiser in setUp
        
        target = Ship("Test", 500, 0, (255,0,0), team_id=1, ship_class="Cruiser")
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
