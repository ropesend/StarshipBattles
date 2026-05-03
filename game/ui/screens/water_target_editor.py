"""Water Target Editor -- UI window for setting planet water coverage targets.

Provides a single slider for setting a target water coverage level (0.0 to 1.0),
displayed as a percentage. Includes Species Ideal, Match Current, Clear, and
Apply buttons.
"""
from __future__ import annotations

import logging
import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIButton, UIHorizontalSlider
from typing import Optional, Callable, Any, TYPE_CHECKING

from game.ui.screens.species_selector_mixin import build_species_selector
from game.ui.screens.planet_target_editor_base import PlanetTargetEditor

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)

# Slider range (fraction)
MIN_WATER = 0.0
MAX_WATER = 1.0


class WaterTargetEditor(PlanetTargetEditor):
    """Window for editing water coverage target on a planet.

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
    ):
        """Initialize water target editor.

        Args:
            rect: Window rectangle.
            manager: UI manager.
            planet: Planet object with surface_water attribute (0.0 to 1.0).
            window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
            on_apply_callback: Called with (planet_id, water_target) when Apply clicked.
                water_target is None when clearing, otherwise a float 0.0-1.0.
            on_close_callback: Called when window is closed.
            race_config: Optional RaceConfig; reads `preferences["water"].setpoint` (0.0 to 1.0) for the species-ideal default.
        """
        super().__init__(
            rect, manager,
            window_display_title=f"Water Target: {planet.name}",
            resizable=False,
            window_manager=window_manager,
        )

        self.planet = planet
        self.on_apply_callback = on_apply_callback
        self.on_close_callback = on_close_callback
        self.race_config = race_config
        self._species_dropdown = None
        self._default_race_id = None

        self.current_water = getattr(planet, 'surface_water', 0.0)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the editor UI with species selector, water slider, and buttons."""
        content_rect = self.get_container().get_rect()
        container_w = content_rect.width
        container_h = content_rect.height

        y = 10

        # Species selector (shown only if multiple species on planet)
        self._species_dropdown, widgets, y, self._default_race_id = build_species_selector(
            self.planet, self, self.ui_manager, y, container_w,
        )

        # Current water display
        self.lbl_current = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Current: {self.current_water * 100:.1f}%",
            manager=self.ui_manager,
            container=self,
        )
        y += 30

        # Target water display
        initial_target = self.current_water
        self.lbl_target = UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Target: {initial_target * 100:.1f}%",
            manager=self.ui_manager,
            container=self,
        )
        y += 35

        # Slider
        slider_w = container_w - 20
        self.slider = UIHorizontalSlider(
            pygame.Rect(10, y, slider_w, 25),
            start_value=initial_target,
            value_range=(MIN_WATER, MAX_WATER),
            manager=self.ui_manager,
            container=self,
            click_increment=0.01,
        )
        y += 30

        # Slider range labels
        UILabel(
            pygame.Rect(10, y, 60, 20),
            text="0%",
            manager=self.ui_manager,
            container=self,
        )
        UILabel(
            pygame.Rect(container_w - 70, y, 60, 20),
            text="100%",
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
            self.lbl_target.set_text(f"Target: {val * 100:.1f}%")

    def _button_handlers(self):
        return {
            self.btn_apply: self._on_apply,
            self.btn_species_ideal: self._set_species_ideal,
            self.btn_match_current: self._set_match_current,
            self.btn_clear: self._clear_target,
        }

    def _on_apply(self) -> None:
        """Apply the current slider value as water coverage target."""
        water_level = self.slider.get_current_value()

        logger.info(
            "Applying water target for planet %s: %.1f%%",
            self.planet.name, water_level * 100,
        )

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, water_level)

        self.kill()

    def _set_species_ideal(self) -> None:
        """Set slider to the selected species' ideal water coverage."""
        rc = self._get_active_race_config()
        if rc is None:
            return

        # PROJ-283 Phase 4: read setpoint from registry-driven preferences.
        water_pref = rc.preferences.get("water")
        if water_pref is None:
            return
        ideal = water_pref.setpoint

        clamped = max(MIN_WATER, min(MAX_WATER, ideal))
        self.slider.set_current_value(clamped)
        self.lbl_target.set_text(f"Target: {clamped * 100:.1f}%")
        logger.debug("Set water to species ideal: %.1f%%", clamped * 100)


    def _set_match_current(self) -> None:
        """Set slider to match current planet water coverage."""
        clamped = max(MIN_WATER, min(MAX_WATER, self.current_water))
        self.slider.set_current_value(clamped)
        self.lbl_target.set_text(f"Target: {clamped * 100:.1f}%")
        logger.debug("Set water to match current: %.1f%%", clamped * 100)

    def _clear_target(self) -> None:
        """Clear water target (apply None)."""
        logger.info("Clearing water target for planet %s", self.planet.name)

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, None)

        self.kill()
