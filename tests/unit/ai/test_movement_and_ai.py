import unittest
from unittest.mock import MagicMock
import pygame

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.ui.screens.battle_scene import BattleScene
from game.ai.controller import AIController, StrategyManager
from game.simulation.components.component import LayerType, load_components, load_modifiers
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir


class TestMovementAndAI(unittest.TestCase):

    def setUp(self):
        pygame.init()
        # Initialize vehicle class definitions FIRST (required for layer configs)
        initialize_ship_data()

        data_dir = get_data_dir()
        unit_test_data_dir = get_unit_test_data_dir()

        # Load components and modifiers
        comp_path = data_dir / "components.json"
        mod_path = data_dir / "modifiers.json"

        if comp_path.exists():
            load_components(str(comp_path))
        if mod_path.exists():
            self.mod_path = str(mod_path)
            load_modifiers(str(mod_path))

        manager = StrategyManager.instance()
        manager.load_data(
            str(unit_test_data_dir),
            targeting_file="test_targeting_policies.json",
            movement_file="test_movement_policies.json",
            strategy_file="test_combat_strategies.json"
        )
        manager._loaded = True
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser")

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()
        StrategyManager.instance().clear()
        super().tearDown()

    def get_component_clone(self, id):
        comps = RegistryManager.instance().components
        if id in comps:
            return comps[id].clone()
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
