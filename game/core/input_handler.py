
import pygame
from game.core.constants import GameState


# Speed multiplier constants for simulation
# Min: 1/256 (very slow motion), Max: 16x (fast forward), Pause UI uses 100x
MIN_SPEED_MULTIPLIER = 0.00390625  # 1/256 - minimum slow-motion speed
MAX_SPEED_MULTIPLIER = 16.0        # Maximum fast-forward speed
NORMAL_SPEED = 1.0                 # Real-time speed
UI_PAUSE_SPEED = 100.0             # Speed used by pause/UI mode for instant updates


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
            scene.sim_speed_multiplier = max(MIN_SPEED_MULTIPLIER, scene.sim_speed_multiplier / 2.0)
        elif key == pygame.K_PERIOD:
            scene.sim_speed_multiplier = min(MAX_SPEED_MULTIPLIER, scene.sim_speed_multiplier * 2.0)
        elif key == pygame.K_m:
            scene.sim_speed_multiplier = NORMAL_SPEED
        elif key == pygame.K_SLASH:
            scene.sim_speed_multiplier = UI_PAUSE_SPEED
