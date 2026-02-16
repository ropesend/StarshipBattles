"""Main menu scene implementing IScene protocol."""

from typing import Callable, Dict, Any, List, Tuple
import os
import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from game.core.paths import Paths
from game.core.protocols import IScene


class MenuScene:
    """
    Main menu scene implementing IScene protocol.

    Manages the main menu UI with pygame_gui buttons and optional
    overlay dialogs (new game setup, load menu, race setup).
    """

    # Background color for menu
    BG_COLOR = (20, 20, 30)

    def __init__(
        self,
        width: int,
        height: int,
        button_config: List[Tuple[str, Callable[[], None]]],
    ):
        """
        Initialize the menu scene.

        Args:
            width: Screen width
            height: Screen height
            button_config: List of (button_text, callback) tuples
        """
        self.width = width
        self.height = height
        self.button_config = button_config

        # Create UI manager for menu buttons (use same theme as strategy/workshop)
        theme_path = os.path.join(Paths.DATA_DIR, 'builder_theme.json')
        self.ui_manager = pygame_gui.UIManager(
            (width, height),
            theme_path=theme_path if os.path.exists(theme_path) else None
        )
        self.ui_manager.preload_fonts([
            {'name': 'noto_sans', 'point_size': 14, 'style': 'bold', 'antialiased': 1}
        ])

        # Button tracking
        self.buttons: List[UIButton] = []
        self._button_callbacks: Dict[UIButton, Callable[[], None]] = {}

        # Create buttons
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create menu buttons from config."""
        # Clear old buttons
        for btn in self.buttons:
            btn.kill()
        self.buttons.clear()
        self._button_callbacks.clear()

        for i, (text, callback) in enumerate(self.button_config):
            btn = UIButton(
                relative_rect=pygame.Rect(
                    self.width // 2 - 100,
                    self.height // 2 - 320 + i * 70,
                    200, 50
                ),
                text=text,
                manager=self.ui_manager
            )
            self.buttons.append(btn)
            self._button_callbacks[btn] = callback

    def handle_event(self, event: Any) -> None:
        """Handle pygame events."""
        self.ui_manager.process_events(event)

        # Check for button presses
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            callback = self._button_callbacks.get(event.ui_element)
            if callback:
                callback()

    def update(self, dt: float) -> None:
        """Update menu UI."""
        self.ui_manager.update(dt)

    def draw(self, screen: Any) -> None:
        """Draw menu to screen."""
        screen.fill(self.BG_COLOR)
        self.ui_manager.draw_ui(screen)

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self.width = width
        self.height = height
        self.ui_manager.set_window_resolution((width, height))
        self._create_buttons()

    def get_ui_manager(self) -> pygame_gui.UIManager:
        """Get the UI manager for overlay dialogs."""
        return self.ui_manager
