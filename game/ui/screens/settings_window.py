"""Settings window for the strategy screen.

Provides UI controls for user-configurable game settings.

PROJ-470 MOD-001 (Pattern #31): migrated from a bare ``UIWindow`` with a
manual close-callback to the ``StrategyModalWindow`` base class. The base
class auto-registers the window with the ``StrategyWindowManager`` on
construction (so ``has_modal_open()`` counts it and ``is_blocking`` blocks
background hover/click) and auto-deregisters in ``kill()``. The registrar
slot-cleanup ``on_close_callback`` is preserved and invoked from ``kill()``.

PROJ-458 Phase 1: retrofitted with the Pattern #33 two-stage bypass-init
shape — Stage 1 pure-Python state + ``ui_builder`` seam above the bypass
guard, Stage 2 ``super().__init__`` + widget tree below. Production never
sets ``bypass_init``; tests use the ``bypass_init`` context manager from
``tests/fixtures/ui_widget_factory.py``.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Protocol

import pygame
from pygame_gui.elements import UILabel, UIHorizontalSlider, UIButton

from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.services.game_settings import GameSettings

if TYPE_CHECKING:
    import pygame_gui
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class SettingsWindowUiBuilder(Protocol):
    """Stage-2 widget-tree builder for :class:`SettingsWindow`.

    Pattern #33 retrofit seam: production instantiates
    :class:`DefaultSettingsWindowUiBuilder` by default; tests may
    inject a no-op builder under ``bypass_init`` so widget
    construction is skipped entirely.
    """

    def build(self, window: "SettingsWindow") -> None:
        """Populate widget slots on ``window`` using the real pygame_gui
        widget tree."""
        ...


class DefaultSettingsWindowUiBuilder:
    """Real pygame_gui widget tree builder for production paths."""

    def build(self, window: "SettingsWindow") -> None:
        rect = window.rect
        manager = window.ui_manager
        settings = window._settings

        y = 20
        width = rect.width - 40

        # --- Display Section ---
        UILabel(
            relative_rect=pygame.Rect(20, y, width, 25),
            text="DISPLAY",
            manager=manager,
            container=window,
        )
        y += 35

        # Background Brightness
        UILabel(
            relative_rect=pygame.Rect(20, y, 180, 25),
            text="Background Brightness:",
            manager=manager,
            container=window,
        )
        window._brightness_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(200, y, width - 260, 25),
            start_value=settings.background_brightness,
            value_range=(0.0, 1.0),
            manager=manager,
            container=window,
        )
        window._brightness_label = UILabel(
            relative_rect=pygame.Rect(width - 40, y, 60, 25),
            text=f"{settings.background_brightness:.0%}",
            manager=manager,
            container=window,
        )
        y += 50

        # --- Buttons ---
        window._btn_reset = UIButton(
            relative_rect=pygame.Rect(20, y, 120, 30),
            text="Reset Defaults",
            manager=manager,
            container=window,
        )
        window._btn_close = UIButton(
            relative_rect=pygame.Rect(width - 80, y, 100, 30),
            text="Close",
            manager=manager,
            container=window,
        )


class SettingsWindow(StrategyModalWindow):
    """Modal settings window with sliders for game settings."""

    def __init__(
        self,
        rect: pygame.Rect,
        manager: "pygame_gui.UIManager",
        *,
        window_manager: "StrategyWindowManager | None",
        on_close_callback: Callable[[], None] | None = None,
        ui_builder: SettingsWindowUiBuilder | None = None,
    ):
        """Initialize the settings window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            window_manager: PROJ-313 StrategyWindowManager (or None outside the
                strategy screen). The base class registers/deregisters here.
            on_close_callback: Optional registrar slot-cleanup callback invoked
                from ``kill()``.
            ui_builder: Optional Stage-2 widget builder. Production
                supplies :class:`DefaultSettingsWindowUiBuilder`; tests
                inject a no-op builder under ``bypass_init``.
        """
        # ---- Stage 1: cheap state + ui-builder seam ----
        self.on_close_callback = on_close_callback
        self._settings = GameSettings()
        self._ui_builder: SettingsWindowUiBuilder = (
            ui_builder or DefaultSettingsWindowUiBuilder()
        )

        # ---- Stage 2: shell (StrategyModalWindow auto-registers and
        # sets ``_window_init_bypassed`` for tests under bypass_init) ----
        super().__init__(
            rect,
            manager,
            window_display_title="Settings",
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets (skipped under bypass_init) ----
        if getattr(self, "_window_init_bypassed", False):
            return

        self._ui_builder.build(self)

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
