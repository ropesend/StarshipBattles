"""Tests for BattleScene logic."""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pygame



from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import create_component, load_components
from game.core.registry import RegistryManager

class TestBattleScene(unittest.TestCase):


    def setUp(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        # Mocking display set_mode to avoid window creation but we might need it for sprites?
        # Actually BattleScene uses pygame.display functionality potentially.
        # Let's verify if headless needs it.
        # pygame.display.set_mode = MagicMock() 
        # Using a dummy mode is safer for headless
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        initialize_ship_data()
        load_components("data/components.json")
        # Patch BattleInterface to avoid UI overhead
        with patch('game.ui.screens.battle_screen.BattleInterface') as MockUI:
            self.scene = BattleScene(800, 600)
            self.scene.ui = MockUI.return_value
            self.scene.ui.show_overlay = False

        # Create basic ships
        self.ship1 = Ship("Hero", 0, 0, (0, 0, 255))
        self.ship1.add_component(create_component('bridge'), LayerType.CORE)
        self.ship1.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship1.add_component(create_component('life_support'), LayerType.CORE)
        self.ship1.add_component(create_component('standard_engine'), LayerType.OUTER) # Add engine
        self.ship1.recalculate_stats()
        
        self.ship2 = Ship("Villain", 1000, 0, (255, 0, 0))
        self.ship2.add_component(create_component('bridge'), LayerType.CORE)
        self.ship2.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship2.add_component(create_component('life_support'), LayerType.CORE)
        self.ship2.add_component(create_component('standard_engine'), LayerType.OUTER) # Add engine
        self.ship2.recalculate_stats()

    def tearDown(self):
        """Cleanup pygame and registry."""
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        pygame.quit()
        RegistryManager.instance().clear()

    def test_start_initialization(self):
        """Test battle initialization."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        
        self.assertEqual(len(self.scene.ships), 2)
        self.assertEqual(len(self.scene.ai_controllers), 2)
        self.assertEqual(self.ship1.team_id, 0)
        self.assertEqual(self.ship2.team_id, 1)
        self.assertEqual(self.scene.sim_tick_counter, 0)
        
    def test_battle_over_condition(self):
        """Test win/loss detection."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        
        
        # Both alive
        self.assertFalse(self.scene.is_battle_over())
        
        # Kill one
        self.ship2.is_alive = False
        self.assertTrue(self.scene.is_battle_over())
        
        # Winner should be team 0
        self.assertEqual(self.scene.get_winner(), 0)

    def test_update_increment_sim_tick(self):
        """Test simulation tick counter increases."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        self.scene.update([])
        self.assertEqual(self.scene.sim_tick_counter, 1)

    def test_projectile_registration(self):
        """Test that fired projectiles are registered in scene."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        
        # Mock projectile
        proj = MagicMock()
        proj.type = 'projectile'
        proj.is_alive = True
        proj.position = pygame.Vector2(0,0)
        proj.velocity = pygame.Vector2(10,0)
        proj.damage = 10
        proj.team_id = 0
        
        # Configure ship to fire this projectile
        self.ship1.comp_trigger_pulled = True
        
        # We must mock fire_weapons to return our projectile
        # But Ship.fire_weapons is a method on the instance.
        # We can patch it on the instance or class.
        with patch.object(self.ship1, 'fire_weapons', return_value=[proj]):
            self.scene.update([])
        
        self.assertIn(proj, self.scene.projectiles)
    
    def test_projectile_cleanup(self):
        """Test dead projectiles are removed."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        
        proj = MagicMock()
        proj.type = 'projectile'
        proj.is_alive = False # Already dead
        proj.position = pygame.Vector2(0,0)
        proj.velocity = pygame.Vector2(0,0)
        
        self.scene.projectiles.append(proj)
        self.scene.update([])
        
        self.assertNotIn(proj, self.scene.projectiles)

if __name__ == '__main__':
    unittest.main()
