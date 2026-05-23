"""Gravity Target Editor -- UI window for setting planet gravity targets.

Provides a single slider for setting a target surface gravity in g-units,
with conversion to m/s^2 for storage. Includes Species Ideal (with species
dropdown for multi-species planets), Match Current, Clear, and Apply buttons.

PROJ-458 Phase 3: retrofitted with the Pattern #33 two-stage UIWindow
bypass-init shape.
"""
from __future__ import annotations

import logging
import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIButton, UIHorizontalSlider
from typing import Any, Optional, Callable, Protocol, TYPE_CHECKING

from game.ui.screens.species_selector_mixin import build_species_selector
from game.ui.screens.planet_target_editor_base import PlanetTargetEditor

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class GravityTargetEditorUiBuilder(Protocol):
    """Stage-2 widget-tree builder for :class:`GravityTargetEditor`."""

    def build(self, window: "GravityTargetEditor") -> None: ...


class DefaultGravityTargetEditorUiBuilder:
    """Thin wrapper around the editor's existing ``_build_ui()`` method."""

    def build(self, window: "GravityTargetEditor") -> None:
        window._build_ui()

# Conversion factor
G_TO_MS2 = 9.81

# Slider range in g-units
MIN_GRAVITY_G = 0.1
MAX_GRAVITY_G = 3.0


class GravityTargetEditor(PlanetTargetEditor):
    """Window for editing gravity modification target on a planet.

    PROJ-313: Migrated to StrategyModalWindow base class.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet,
        *,
        window_manager: "StrategyWindowManager",
        on_apply_callback: Optional[Callable[[int, Optional[float]], None]] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        race_config=None,
        ui_builder: Optional[GravityTargetEditorUiBuilder] = None,
    ):
        # Stage 1 — pure-Python state + UI-builder seam.
        self.planet = planet
        self.on_apply_callback = on_apply_callback
        self.on_close_callback = on_close_callback
        self.race_config = race_config
        self._species_dropdown = None
        self._default_race_id = None

        self.current_g = getattr(planet, 'surface_gravity', 0.0) / G_TO_MS2

        self._ui_builder: GravityTargetEditorUiBuilder = (
            ui_builder or DefaultGravityTargetEditorUiBuilder()
        )

        # Bypass guard — type(self) so subclass flags win.
        if getattr(type(self), "bypass_init", False):
            self.ui_manager = manager
            self._window_init_bypassed = True
            object.__setattr__(self, "_rect", rect)
            return

        # Stage 2 — heavy widget tree.
        super().__init__(
            rect, manager,
            window_display_title=f"Gravity Target: {planet.name}",
            resizable=False,
            window_manager=window_manager,
        )
        self._window_init_bypassed = False
        self._ui_builder.build(self)

    def _build_ui(self) -> None:
        """Build the editor UI with species selector, gravity slider, and buttons."""
        content_rect = self.get_container().get_rect()
        container_w = content_rect.width
        container_h = content_rect.height

        y = 10

        # Species selector (shown only if multiple species on planet)
        self._species_dropdown, widgets, y, self._default_race_id = build_species_selector(
            self.planet, self, self.ui_manager, y, container_w,
        )

        # Current gravity display
        self.lbl_current = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Current: {self.current_g:.2f} g",
            manager=self.ui_manager,
            container=self,
        )
        y += 30

        # Target gravity display
        initial_target = self.current_g
        self.lbl_target = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Target: {initial_target:.2f} g",
            manager=self.ui_manager,
            container=self,
        )
        y += 35

        # Slider
        slider_w = container_w - 20
        self.slider = UIHorizontalSlider(
            pygame.Rect(10, y, slider_w, 25),
            start_value=initial_target,
            value_range=(MIN_GRAVITY_G, MAX_GRAVITY_G),
            manager=self.ui_manager,
            container=self,
            click_increment=0.01,
        )
        y += 30

        # Slider range labels
        UILabel(
            pygame.Rect(10, y, 60, 20),
            text=f"{MIN_GRAVITY_G} g",
            manager=self.ui_manager,
            container=self,
        )
        UILabel(
            pygame.Rect(container_w - 70, y, 60, 20),
            text=f"{MAX_GRAVITY_G} g",
            manager=self.ui_manager,
            container=self,
        )

        # Buttons at bottom
        btn_y = container_h - 50
        btn_w = 120

        self.btn_species_ideal = UIButton(
            pygame.Rect(10, btn_y, btn_w, 35),
            text="Species Ideal",
            manager=self.ui_manager,
            container=self,
        )

        self.btn_match_current = UIButton(
            pygame.Rect(10 + btn_w + 10, btn_y, btn_w, 35),
            text="Match Current",
            manager=self.ui_manager,
            container=self,
        )

        self.btn_clear = UIButton(
            pygame.Rect(10 + (btn_w + 10) * 2, btn_y, btn_w, 35),
            text="Clear",
            manager=self.ui_manager,
            container=self,
        )

        self.btn_apply = UIButton(
            pygame.Rect(container_w - btn_w - 10, btn_y, btn_w, 35),
            text="Apply",
            manager=self.ui_manager,
            container=self,
        )

    def update(self, time_delta: float) -> None:
        """Update the target label when the slider moves."""
        super().update(time_delta)

        if self.slider.has_moved_recently:
            val = self.slider.get_current_value()
            self.lbl_target.set_text(f"Target: {val:.2f} g")

    def _button_handlers(self) -> dict[UIButton, Callable[[], None]]:
        return {
            self.btn_apply: self._on_apply,
            self.btn_species_ideal: self._set_species_ideal,
            self.btn_match_current: self._set_match_current,
            self.btn_clear: self._clear_target,
        }

    def _on_apply(self) -> None:
        """Apply the current slider value as gravity target (converted to m/s^2)."""
        gravity_g = self.slider.get_current_value()
        gravity_ms2 = gravity_g * G_TO_MS2

        logger.info(
            "Applying gravity target for planet %s: %.2f g (%.2f m/s^2)",
            self.planet.name, gravity_g, gravity_ms2,
        )

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, gravity_ms2)

        self.kill()

    def _set_species_ideal(self) -> None:
        """Set slider to the selected species' ideal gravity."""
        rc = self._get_active_race_config()
        if rc is None:
            return

        # PROJ-283 Phase 4: read setpoint from registry-driven preferences
        # (registry stores gravity in m/s², slider is in g).
        gravity_pref = rc.preferences.get("gravity")
        if gravity_pref is None:
            return
        ideal_g = gravity_pref.setpoint / 9.81

        clamped = max(MIN_GRAVITY_G, min(MAX_GRAVITY_G, ideal_g))
        self.slider.set_current_value(clamped)
        self.lbl_target.set_text(f"Target: {clamped:.2f} g")
        logger.debug("Set gravity to species ideal: %.2f g", clamped)


    def _set_match_current(self) -> None:
        """Set slider to match current planet gravity."""
        clamped = max(MIN_GRAVITY_G, min(MAX_GRAVITY_G, self.current_g))
        self.slider.set_current_value(clamped)
        self.lbl_target.set_text(f"Target: {clamped:.2f} g")
        logger.debug("Set gravity to match current: %.2f g", clamped)

    def _clear_target(self) -> None:
        """Clear gravity target (apply None)."""
        logger.info("Clearing gravity target for planet %s", self.planet.name)

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, None)

        self.kill()
