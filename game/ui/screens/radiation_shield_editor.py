"""Radiation Shield Editor -- UI window for setting planet radiation shielding targets.

Provides a single slider for setting a target radiation shielding level (0.0 to 2.0),
with displays for the planet's natural magnetic field and current shielding.
Includes Auto, Clear, and Apply buttons.
"""
from __future__ import annotations

import logging
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UILabel, UIButton, UIHorizontalSlider
from typing import Optional, Callable, Any

from game.ui.screens.species_selector_mixin import (
    build_species_selector, get_selected_race_id, load_race_config,
)

logger = logging.getLogger(__name__)

# Slider range
MIN_SHIELDING = 0.0
MAX_SHIELDING = 2.0


class RadiationShieldEditor(UIWindow):
    """Window for editing radiation shielding target on a planet."""

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet,
        on_apply_callback: Optional[Callable[[int, Optional[float]], None]] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        race_config=None,
    ):
        """Initialize radiation shield editor.

        Args:
            rect: Window rectangle.
            manager: UI manager.
            planet: Planet object with magnetic_field and radiation_shielding attributes.
            on_apply_callback: Called with (planet_id, shielding_target) when Apply clicked.
                shielding_target is None when clearing, otherwise a float 0.0-2.0.
            on_close_callback: Called when window is closed.
            race_config: Optional RaceConfig; reads `preferences["radiation"].setpoint` for the auto-shielding default.
        """
        super().__init__(
            rect, manager,
            window_display_title=f"Radiation Shield: {planet.name}",
            resizable=False,
        )

        self.planet = planet
        self.on_apply_callback = on_apply_callback
        self.on_close_callback = on_close_callback
        self.race_config = race_config
        self._species_dropdown = None
        self._default_race_id = None

        self.magnetic_field = getattr(planet, 'magnetic_field', 0.0)
        self.current_shielding = getattr(planet, 'radiation_shielding', 0.0)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the editor UI with species selector, info labels, slider, and buttons."""
        content_rect = self.get_container().get_rect()
        container_w = content_rect.width
        container_h = content_rect.height

        y = 10

        # Species selector (shown only if multiple species on planet)
        self._species_dropdown, widgets, y, self._default_race_id = build_species_selector(
            self.planet, self, self.ui_manager, y, container_w,
        )

        # Natural magnetic field display
        self.lbl_field = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Natural Field: {self.magnetic_field:.2f}",
            manager=self.ui_manager,
            container=self,
        )
        y += 28

        # Current shielding display
        self.lbl_current = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Current Shielding: {self.current_shielding:.2f}",
            manager=self.ui_manager,
            container=self,
        )
        y += 28

        # Target shielding display
        initial_target = self.current_shielding
        self.lbl_target = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Target Shielding: {initial_target:.2f}",
            manager=self.ui_manager,
            container=self,
        )
        y += 35

        # Slider
        slider_w = container_w - 20
        self.slider = UIHorizontalSlider(
            pygame.Rect(10, y, slider_w, 25),
            start_value=initial_target,
            value_range=(MIN_SHIELDING, MAX_SHIELDING),
            manager=self.ui_manager,
            container=self,
            click_increment=0.01,
        )
        y += 30

        # Slider range labels
        UILabel(
            pygame.Rect(10, y, 60, 20),
            text=f"{MIN_SHIELDING:.1f}",
            manager=self.ui_manager,
            container=self,
        )
        UILabel(
            pygame.Rect(container_w - 70, y, 60, 20),
            text=f"{MAX_SHIELDING:.1f}",
            manager=self.ui_manager,
            container=self,
        )

        # Buttons at bottom
        btn_y = container_h - 50
        btn_w = 120

        self.btn_auto = UIButton(
            pygame.Rect(10, btn_y, btn_w, 35),
            text="Auto",
            manager=self.ui_manager,
            container=self,
        )

        self.btn_clear = UIButton(
            pygame.Rect(10 + btn_w + 10, btn_y, btn_w, 35),
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
            self.lbl_target.set_text(f"Target Shielding: {val:.2f}")

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle button clicks and window close."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_apply:
                self._on_apply()
                return True
            elif event.ui_element == self.btn_auto:
                self._set_auto()
                return True
            elif event.ui_element == self.btn_clear:
                self._clear_target()
                return True

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self:
                if self.on_close_callback:
                    self.on_close_callback()
                return True

        return handled

    def _on_apply(self) -> None:
        """Apply the current slider value as radiation shielding target."""
        shielding = self.slider.get_current_value()

        logger.info(
            "Applying shielding target for planet %s: %.2f",
            self.planet.name, shielding,
        )

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, shielding)

        self.kill()

    def _set_auto(self) -> None:
        """Set the slider to the selected species' preferred shielding level.

        PROJ-283 Phase 4: the radiation factor's `setpoint` is the
        race's ideal `radiation_shielding` value (the registry default
        is 0, "doesn't care"). Just write that to the slider — no
        threshold-vs-magnetic-field arithmetic needed; the new model
        decouples shielding preference from magnetic field (magnetic is
        its own factor).
        """
        rc = self._get_active_race_config()
        if rc is None:
            return

        rad_pref = rc.preferences.get("radiation")
        if rad_pref is None:
            return

        clamped = max(MIN_SHIELDING, min(MAX_SHIELDING, rad_pref.setpoint))
        self.slider.set_current_value(clamped)
        self.lbl_target.set_text(f"Target Shielding: {clamped:.2f}")
        logger.debug(
            "Auto shielding: setpoint=%.3f, field=%.3f, clamped=%.3f",
            rad_pref.setpoint, self.magnetic_field, clamped,
        )

    def _get_active_race_config(self) -> Any:
        """Get the race config for the currently selected species."""
        if self._species_dropdown is not None:
            race_id = get_selected_race_id(self._species_dropdown)
            if race_id:
                rc = load_race_config(race_id)
                if rc:
                    return rc
        if self._default_race_id:
            rc = load_race_config(self._default_race_id)
            if rc:
                return rc
        return self.race_config

    def _clear_target(self) -> None:
        """Clear shielding target (apply None)."""
        logger.info("Clearing shielding target for planet %s", self.planet.name)

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, None)

        self.kill()
