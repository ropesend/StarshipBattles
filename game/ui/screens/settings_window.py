"""Settings window for the strategy screen.

Provides UI controls for user-configurable game settings.

PROJ-470 MOD-001 (Pattern #31): migrated from a bare ``UIWindow`` with a
manual close-callback to the ``StrategyModalWindow`` base class. The base
class auto-registers the window with the ``StrategyWindowManager`` on
construction (so ``has_modal_open()`` counts it and ``is_blocking`` blocks
background hover/click) and auto-deregisters in ``kill()``. The registrar
slot-cleanup ``on_close_callback`` is preserved and invoked from ``kill()``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame
from pygame_gui.elements import UIPanel, UILabel, UIHorizontalSlider, UIButton

from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.services.game_settings import GameSettings
import logging

if TYPE_CHECKING:
    import pygame_gui
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class SettingsWindow(StrategyModalWindow):
    """Modal settings window with sliders for game settings."""

    def __init__(
        self,
        rect: pygame.Rect,
        manager: "pygame_gui.UIManager",
        *,
        window_manager: "StrategyWindowManager | None",
        on_close_callback: Callable[[], None] | None = None,
    ):
        """Initialize the settings window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            window_manager: PROJ-313 StrategyWindowManager (or None outside the
                strategy screen). The base class registers/deregisters here.
            on_close_callback: Optional registrar slot-cleanup callback invoked
                from ``kill()``.
        """
        # ---- Stage 1: cheap state ----
        self.on_close_callback = on_close_callback
        self._settings = GameSettings()

        # ---- Stage 2: shell (StrategyModalWindow auto-registers) ----
        super().__init__(
            rect,
            manager,
            window_display_title="Settings",
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets (skipped under bypass_init) ----
        if getattr(self, "_window_init_bypassed", False):
            return

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
        """Invoke the registrar slot-cleanup callback, then delegate to
        ``StrategyModalWindow.kill()`` which deregisters from the window
        manager before tearing down the underlying window."""
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
