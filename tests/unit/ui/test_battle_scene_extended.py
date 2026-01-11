
import unittest
import sys
import os

import pygame
from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, LayerType
import os
from unittest import mock
from game.ai.controller import STRATEGY_MANAGER
from game.core.registry import RegistryManager

class TestBattleSceneExtended(unittest.TestCase):
    """Test BattleScene simulation loop, victory conditions, and headless mode."""
    
        

    def setUp(self):
        # Note: pygame, registry, and data loading handled by conftest fixtures
        # initialize_ship_data() and load_components() are patched to be no-ops
        # because the reset_game_state fixture already loaded the data

        # AI Strategy Manager still needs to be loaded per-test
        test_data_path = os.path.join(os.getcwd(), "tests", "unit", "data")
        STRATEGY_MANAGER.load_data(
             test_data_path,
             targeting_file="test_targeting_policies.json",
             movement_file="test_movement_policies.json",
             strategy_file="test_combat_strategies.json"
        )

    def tearDown(self):
        """Cleanup pygame and global managers."""
        # Note: pygame and registry cleanup is handled by conftest fixtures
        # (pygame_display_reset and reset_game_state)
        # DO NOT call pygame.quit() here as it conflicts with session-level fixture

        # AI Strategy Manager should still be cleared
        STRATEGY_MANAGER.clear()

    def test_is_battle_over_victory(self):
        """Verify is_battle_over identifies when one team is eliminated."""
        scene = BattleScene(1000, 1000)
        
        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0, ship_class="Escort")
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1, ship_class="Escort")
        
        # Ensure they are fully equipped ships
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.OUTER)
            s.recalculate_stats()
        
        scene.start([ship1], [ship2])
        self.assertFalse(scene.is_battle_over(), "Battle should NOT be over at start with active ships")
        
        # Kill ship2
        ship2.is_alive = False
        self.assertTrue(scene.is_battle_over())
        self.assertEqual(scene.get_winner(), 0)

    def test_update_loop_tick_counter(self):
        """Verify update loop increments sim_tick_counter."""
        scene = BattleScene(1000, 1000)
        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0, ship_class="Escort")
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1, ship_class="Escort")
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.OUTER)
            s.recalculate_stats()
        
        scene.start([ship1], [ship2])
        
        self.assertEqual(scene.sim_tick_counter, 0)
        scene.update([])
        self.assertEqual(scene.sim_tick_counter, 1)

    def test_headless_mode_initialization(self):
        """Verify headless mode sets start time and skips camera fit."""
        scene = BattleScene(1000, 1000)
        # Mock camera to ensure fit_objects isn't called normally if fit_objects fails without screen
        scene.camera = mock.MagicMock()
        
        scene.start([], [], headless=True)
        self.assertTrue(scene.headless_mode)
        self.assertIsNotNone(scene.headless_start_time)
        
        scene.camera.fit_objects.assert_not_called()

    def test_process_beam_attack_logic(self):
        """Verify _process_beam_attack applies damage to target."""
        scene = BattleScene(1000, 1000)
        ship = Ship("Target", 0, 0, (255,255,255), team_id=1)
        ship.radius = 20
        # Mock take_damage
        ship.take_damage = mock.MagicMock()
        
        # Mock the ability that will be returned by get_ability
        mock_ability = mock.MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 25
        
        # Mock the component to return the mock ability
        mock_comp = mock.MagicMock()
        mock_comp.shots_hit = 0
        mock_comp.get_ability.return_value = mock_ability
        
        beam = {
            'type': 'beam',
            'damage': 25,
            'target': ship,
            'origin': pygame.math.Vector2(0,0),
            'direction': pygame.math.Vector2(1,0),
            'range': 100,
            'component': mock_comp
        }
        
        scene.engine.collision_system.process_beam_attack(beam, scene.engine.recent_beams)
        ship.take_damage.assert_called_with(25)

if __name__ == '__main__':
    unittest.main()
