
import pygame
from game.core.constants import GameState

class InputHandler:
    """
    Handles input events for the Game class.
    Decouples input logic from the main application to allow for isolated testing.
    """
    
    @staticmethod
    def handle_keydown(game, event):
        """Handle key press events."""
        if game.state == GameState.BATTLE:
            InputHandler._handle_battle_keydown(game, event)

    @staticmethod
    def _handle_battle_keydown(game, event):
        scene = game.battle_scene
        key = event.key
        
        if key == pygame.K_o:
            scene.show_overlay = not scene.show_overlay
        elif key == pygame.K_SPACE:
            scene.sim_paused = not scene.sim_paused
        elif key == pygame.K_COMMA:
            scene.sim_speed_multiplier = max(0.00390625, scene.sim_speed_multiplier / 2.0)
        elif key == pygame.K_PERIOD:
             scene.sim_speed_multiplier = min(16.0, scene.sim_speed_multiplier * 2.0)
        elif key == pygame.K_m:
             scene.sim_speed_multiplier = 1.0
        elif key == pygame.K_SLASH:
            scene.sim_speed_multiplier = 100.0
