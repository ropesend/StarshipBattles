"""Strategy menu dropdown panel.

Provides a dropdown menu panel with game management options:
Save Game, Load Game, Settings, Controls, Quit to Menu, Quit Game.
"""

import pygame
import pygame_gui
import pygame_gui.elements
from typing import Callable, Optional


# Menu option identifiers
MENU_SAVE_GAME = "save_game"
MENU_LOAD_GAME = "load_game"
MENU_SETTINGS = "settings"
MENU_CONTROLS = "controls"
MENU_QUIT_TO_MENU = "quit_to_menu"
MENU_QUIT_GAME = "quit_game"

# Layout constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 35
BUTTON_GAP = 5
PANEL_PADDING = 10
BUTTON_COUNT = 6
PANEL_WIDTH = BUTTON_WIDTH + 2 * PANEL_PADDING
PANEL_HEIGHT = BUTTON_COUNT * BUTTON_HEIGHT + (BUTTON_COUNT + 1) * BUTTON_GAP + 2 * PANEL_PADDING

# Button definitions: (label, option_id)
MENU_BUTTONS = [
    ("Save Game", MENU_SAVE_GAME),
    ("Load Game", MENU_LOAD_GAME),
    ("Settings", MENU_SETTINGS),
    ("Controls", MENU_CONTROLS),
    ("Quit to Menu", MENU_QUIT_TO_MENU),
    ("Quit Game", MENU_QUIT_GAME),
]


class StrategyMenuPanel(pygame_gui.elements.UIPanel):
    """Dropdown menu panel for strategy view game management options.

    Displays a vertical list of buttons for game management actions.
    Calls the provided callback with the option identifier when a button is pressed.

    Args:
        relative_rect: Panel position and size.
        manager: The pygame_gui UIManager.
        on_option_callback: Called with option string when a menu button is pressed.
    """

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        on_option_callback: Callable[[str], None],
    ):
        super().__init__(
            relative_rect,
            starting_height=2,
            manager=manager,
        )

        self.on_option_callback = on_option_callback
        self._option_buttons: dict[pygame_gui.elements.UIButton, str] = {}

        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create the menu option buttons inside the panel."""
        for i, (label, option_id) in enumerate(MENU_BUTTONS):
            y = PANEL_PADDING + i * (BUTTON_HEIGHT + BUTTON_GAP)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(PANEL_PADDING, y, BUTTON_WIDTH, BUTTON_HEIGHT),
                text=label,
                manager=self.ui_manager,
                container=self,
            )
            self._option_buttons[button] = option_id

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process UI events, dispatching button presses to the callback.

        Args:
            event: The pygame event to process.

        Returns:
            True if the event was consumed by this panel.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            option = self._option_buttons.get(event.ui_element)
            if option is not None:
                self.on_option_callback(option)
                return True
        return super().process_event(event)

    def get_option_buttons(self) -> dict[pygame_gui.elements.UIButton, str]:
        """Return the mapping of buttons to option identifiers.

        Useful for testing.
        """
        return dict(self._option_buttons)
