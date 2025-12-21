
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import unittest
import sys
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Game, WIDTH, HEIGHT
from designs import create_brick, create_interceptor

class TestOverlay(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = Game()
        # Mock screen for drawing
        self.game.screen = pygame.Surface((WIDTH, HEIGHT))

    def test_toggle_overlay(self):
        # Initial state - overlay is on battle_scene now
        self.assertFalse(self.game.battle_scene.show_overlay)
        
        # Manually toggle
        self.game.battle_scene.show_overlay = True
        self.assertTrue(self.game.battle_scene.show_overlay)
        
    def test_draw_overlay_no_crash(self):
        # Create a simple battle with design functions
        team1 = [create_brick(20000, 40000)]
        team2 = [create_interceptor(80000, 40000)]
        
        self.game.start_battle(team1, team2)
        self.game.battle_scene.show_overlay = True
        
        # Ensure we have ships
        self.assertTrue(len(self.game.battle_scene.ships) > 0)
        
        # Set a target for a ship to ensure line drawing triggers
        ship = self.game.battle_scene.ships[0]
        target = self.game.battle_scene.ships[1]
        ship.current_target = target
        
        # Call draw which calls draw_debug_overlay
        try:
            self.game.battle_scene.draw(self.game.screen)
        except Exception as e:
            self.fail(f"draw raised exception: {e}")

    def tearDown(self):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
