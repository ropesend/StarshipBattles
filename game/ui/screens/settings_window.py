"""Settings window for the strategy screen.

Provides UI controls for user-configurable game settings.
"""
import pygame
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIHorizontalSlider, UIButton

from game.ui.services.game_settings import GameSettings
import logging

logger = logging.getLogger(__name__)


class SettingsWindow(UIWindow):
    """Modal settings window with sliders for game settings."""

    def __init__(self, rect, manager, on_close_callback=None):
        """Initialize the settings window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            on_close_callback: Called when window is closed.
        """
        super().__init__(rect, manager, window_display_title="Settings")

        self.on_close_callback = on_close_callback
        self._settings = GameSettings()

        y = 20
        width = rect.width - 40

        # --- Display Section ---
        UILabel(
            relative_rect=pygame.Rect(20, y, width, 25),
            text="DISPLAY",
            manager=manager,
            container=self,
        )
        y += 35

        # Background Brightness
        UILabel(
            relative_rect=pygame.Rect(20, y, 180, 25),
            text="Background Brightness:",
            manager=manager,
            container=self,
        )
        self._brightness_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(200, y, width - 260, 25),
            start_value=self._settings.background_brightness,
            value_range=(0.0, 1.0),
            manager=manager,
            container=self,
        )
        self._brightness_label = UILabel(
            relative_rect=pygame.Rect(width - 40, y, 60, 25),
            text=f"{self._settings.background_brightness:.0%}",
            manager=manager,
            container=self,
        )
        y += 50

        # --- Buttons ---
        self._btn_reset = UIButton(
            relative_rect=pygame.Rect(20, y, 120, 30),
            text="Reset Defaults",
            manager=manager,
            container=self,
        )
        self._btn_close = UIButton(
            relative_rect=pygame.Rect(width - 80, y, 100, 30),
            text="Close",
            manager=manager,
            container=self,
        )

    def process_event(self, event) -> bool:
        handled = super().process_event(event)

        if event.type == pygame.event.custom_type() or not hasattr(event, 'ui_element'):
            return handled

        from pygame_gui import UI_BUTTON_PRESSED
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self._btn_close:
                self.kill()
                return True
            if event.ui_element == self._btn_reset:
                self._settings.reset_to_defaults()
                self._brightness_slider.set_current_value(self._settings.background_brightness)
                self._brightness_label.set_text(f"{self._settings.background_brightness:.0%}")
                return True

        return handled

    def update(self, time_delta: float) -> None:
        super().update(time_delta)

        # Sync slider to settings (live preview)
        if self._brightness_slider.has_moved_recently:
            value = self._brightness_slider.get_current_value()
            self._settings.background_brightness = value
            self._brightness_label.set_text(f"{value:.0%}")

    def kill(self) -> None:
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
