"""
Battle input handling for keyboard commands.

Provides centralized keyboard input routing for battle mode.
Decouples input logic from the main Game class for testability.
"""
import pygame
from game.core.constants import GameState


# Speed multiplier constants for simulation time control
# These control how fast the battle simulation runs relative to real-time
MIN_SPEED_MULTIPLIER = 0.00390625  # 1/256 - minimum slow-motion speed for detailed observation
MAX_SPEED_MULTIPLIER = 16.0        # 16x - maximum fast-forward speed for quick resolution
NORMAL_SPEED = 1.0                 # 1x - real-time simulation speed
UI_PAUSE_SPEED = 100.0             # 100x - instant updates when UI is paused (menu open, etc.)


class BattleInputHandler:
    """
    Handles keyboard input for Battle mode.

    Provides static methods for routing keyboard events during battle simulation.
    Manages speed control, pause, and overlay toggles.
    """

    @staticmethod
    def handle_keydown(game, event):
        """
        Route keyboard events to the appropriate handler based on game state.

        Currently only handles BATTLE state keyboard shortcuts. Other states
        (MAIN_MENU, BUILDER, etc.) handle their own input through pygame_gui.

        Args:
            game: The main Game instance containing current state and scenes
            event: pygame.KEYDOWN event to process
        """
        if game.state == GameState.BATTLE:
            BattleInputHandler._handle_battle_keydown(game, event)

    @staticmethod
    def _handle_battle_keydown(game, event):
        """
        Handle keyboard shortcuts during battle simulation.

        Keybindings:
            O       - Toggle overlay display (ship stats, targeting lines)
            SPACE   - Pause/unpause simulation
            COMMA   - Slow down simulation (halve speed, min 1/256x)
            PERIOD  - Speed up simulation (double speed, max 16x)
            M       - Reset to normal speed (1x real-time)
            SLASH   - Set UI pause speed (100x for instant resolution)

        Args:
            game: The main Game instance
            event: pygame.KEYDOWN event to process
        """
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
