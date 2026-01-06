"""Tests for Battle UI Overlay."""
import unittest
from unittest.mock import MagicMock, patch
import pygame
from game.core.constants import GameState
from game.core.input_handler import InputHandler

class MockGame:
    def __init__(self):
        self.state = GameState.MENU
        self.battle_scene = MagicMock()
        # Initialize attributes with concrete values for logic testing
        self.battle_scene.sim_paused = False
        self.battle_scene.show_overlay = False
        self.battle_scene.sim_speed_multiplier = 1.0

class TestOverlay(unittest.TestCase):

    def setUp(self):
        # pygame layout needs display initialized for event pump?
        # Headless mode handles this usually.
        # We patch display info anyway.
        self.patcher = patch('pygame.display.Info')
        self.mock_info = self.patcher.start()
        self.mock_info.return_value.current_w = 1920
        self.mock_info.return_value.current_h = 1080
        
        self.game = MockGame()

    def tearDown(self):
        if hasattr(self, 'patcher'):
            self.patcher.stop()

    def test_toggle_overlay(self):
        """Test that overlay toggles with 'O' key."""
        self.game.state = GameState.BATTLE
        self.game.battle_scene.show_overlay = False
        
        event_o = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_o)
        InputHandler.handle_keydown(self.game, event_o)
        
        self.assertTrue(self.game.battle_scene.show_overlay, "Overlay should toggle ON")
        
        InputHandler.handle_keydown(self.game, event_o)
        self.assertFalse(self.game.battle_scene.show_overlay, "Overlay should toggle OFF")

    def test_toggle_pause(self):
        """Test that pause toggles with SPACE key."""
        self.game.state = GameState.BATTLE
        self.game.battle_scene.sim_paused = False
        
        event_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        InputHandler.handle_keydown(self.game, event_space)
        
        self.assertTrue(self.game.battle_scene.sim_paused, "Pause should toggle ON")
        
        InputHandler.handle_keydown(self.game, event_space)
        self.assertFalse(self.game.battle_scene.sim_paused, "Pause should toggle OFF")

if __name__ == '__main__':
    unittest.main()
