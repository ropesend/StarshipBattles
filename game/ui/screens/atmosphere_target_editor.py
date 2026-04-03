"""Atmosphere Target Editor — UI window for setting planet atmosphere targets.

Provides sliders and numeric display for each gas, plus a "Set to Species Ideal"
button that populates targets from the colony's species atmosphere preferences.
"""
import logging
import pygame
import pygame_gui
from pygame_gui.elements import (
    UIWindow, UIPanel, UILabel, UIButton, UIHorizontalSlider,
    UIScrollingContainer,
)
from typing import Dict, Optional, Callable

from game.strategy.data.race_config import GAS_NAME_TO_FORMULA, GAS_FORMULA_TO_NAME

logger = logging.getLogger(__name__)

# All possible gases in order
ALL_GASES = ["N2", "O2", "CO2", "H2O", "CH4", "H2", "He", "Ar", "NH3", "SO2"]

# Display names for gases
GAS_DISPLAY = {
    "N2": "Nitrogen",
    "O2": "Oxygen",
    "CO2": "Carbon Dioxide",
    "H2O": "Water Vapor",
    "CH4": "Methane",
    "H2": "Hydrogen",
    "He": "Helium",
    "Ar": "Argon",
    "NH3": "Ammonia",
    "SO2": "Sulfur Dioxide",
}

# Max slider value in Pa (150 kPa = ~1.5 atm)
MAX_SLIDER_PA = 150000.0


class AtmosphereTargetEditor(UIWindow):
    """Window for editing atmosphere modification targets on a planet."""

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet,
        on_apply_callback: Optional[Callable[[int, Dict[str, float]], None]] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        race_config=None,
    ):
        """Initialize atmosphere target editor.

        Args:
            rect: Window rectangle.
            manager: UI manager.
            planet: Planet object with atmosphere and atmosphere_target.
            on_apply_callback: Called with (planet_id, target_dict) when Apply clicked.
            on_close_callback: Called when window is closed.
            race_config: Optional RaceConfig for species ideal presets.
        """
        super().__init__(
            rect, manager,
            window_display_title=f"Atmosphere Target: {planet.name}",
            resizable=True,
        )

        self.planet = planet
        self.on_apply_callback = on_apply_callback
        self.on_close_callback = on_close_callback
        self.race_config = race_config

        # Determine which gases to show (present on planet + in target)
        current_atmo = getattr(planet, 'atmosphere', {})
        current_target = getattr(planet, 'atmosphere_target', {})
        self.gases = []
        for gas in ALL_GASES:
            if current_atmo.get(gas, 0) > 0 or current_target.get(gas, 0) > 0:
                self.gases.append(gas)
        # Always show the 6 main gases even if not present
        for gas in ["N2", "O2", "CO2", "H2O", "CH4", "H2"]:
            if gas not in self.gases:
                self.gases.append(gas)

        self.sliders: Dict[str, UIHorizontalSlider] = {}
        self.value_labels: Dict[str, UILabel] = {}
        self.current_labels: Dict[str, UILabel] = {}

        self._build_ui()

    def _build_ui(self):
        """Build the editor UI with sliders for each gas."""
        content_rect = self.get_container().get_rect()
        container_w = content_rect.width
        container_h = content_rect.height

        # Info header
        y = 10
        UILabel(
            pygame.Rect(10, y, container_w - 20, 25),
            text=f"Total Pressure: {sum(self.planet.atmosphere.values()):.0f} Pa",
            manager=self.ui_manager,
            container=self,
        )
        y += 30

        # Column headers
        UILabel(pygame.Rect(10, y, 120, 20), text="Gas", manager=self.ui_manager, container=self)
        UILabel(pygame.Rect(130, y, 70, 20), text="Current", manager=self.ui_manager, container=self)
        UILabel(pygame.Rect(200, y, container_w - 300, 20), text="Target (Pa)", manager=self.ui_manager, container=self)
        UILabel(pygame.Rect(container_w - 100, y, 90, 20), text="Value", manager=self.ui_manager, container=self)
        y += 25

        # Gas sliders
        current_target = getattr(self.planet, 'atmosphere_target', {})

        for gas in self.gases:
            current_pa = self.planet.atmosphere.get(gas, 0.0)
            target_pa = current_target.get(gas, current_pa)

            # Gas name
            display_name = GAS_DISPLAY.get(gas, gas)
            UILabel(
                pygame.Rect(10, y, 120, 22),
                text=display_name,
                manager=self.ui_manager,
                container=self,
            )

            # Current value label
            current_label = UILabel(
                pygame.Rect(130, y, 70, 22),
                text=f"{current_pa:.0f}",
                manager=self.ui_manager,
                container=self,
            )
            self.current_labels[gas] = current_label

            # Slider
            slider_w = container_w - 310
            slider = UIHorizontalSlider(
                pygame.Rect(200, y, slider_w, 22),
                start_value=target_pa,
                value_range=(0.0, MAX_SLIDER_PA),
                manager=self.ui_manager,
                container=self,
                click_increment=100.0,
            )
            self.sliders[gas] = slider

            # Target value label
            value_label = UILabel(
                pygame.Rect(container_w - 100, y, 90, 22),
                text=f"{target_pa:.0f} Pa",
                manager=self.ui_manager,
                container=self,
            )
            self.value_labels[gas] = value_label

            y += 28

        # Buttons at bottom
        btn_y = container_h - 50
        btn_w = 140

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
            text="Clear Target",
            manager=self.ui_manager,
            container=self,
        )

        self.btn_apply = UIButton(
            pygame.Rect(container_w - btn_w - 10, btn_y, btn_w, 35),
            text="Apply",
            manager=self.ui_manager,
            container=self,
        )

    def update(self, time_delta: float):
        """Update slider value labels."""
        super().update(time_delta)

        for gas, slider in self.sliders.items():
            if slider.has_moved_recently:
                val = slider.get_current_value()
                self.value_labels[gas].set_text(f"{val:.0f} Pa")

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle button clicks."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_apply:
                self._on_apply()
                return True
            elif event.ui_element == self.btn_species_ideal:
                self._set_species_ideal()
                return True
            elif event.ui_element == self.btn_match_current:
                self._set_match_current()
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

    def _on_apply(self):
        """Apply the current slider values as atmosphere target."""
        target = {}
        for gas, slider in self.sliders.items():
            val = slider.get_current_value()
            if val > 0:
                target[gas] = val

        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, target)

        self.kill()

    def _set_species_ideal(self):
        """Set sliders to the species' ideal atmosphere composition.

        Converts race atmosphere preferences (-100 to +100) into target Pa values.
        Positive preferences get proportional partial pressures targeting Earth-like total.
        """
        if self.race_config is None:
            return

        prefs = getattr(self.race_config, 'atmosphere_preferences', {})
        if not prefs:
            return

        # Target total pressure: 1 atm (101325 Pa) as a baseline
        target_total = 101325.0

        # Calculate proportional targets from preferences
        # Positive preferences get proportional allocation
        # Negative/zero preferences get 0
        positive_weights = {}
        for gas_name, score in prefs.items():
            if score > 0:
                formula = GAS_NAME_TO_FORMULA.get(gas_name)
                if formula:
                    positive_weights[formula] = score

        if not positive_weights:
            return

        total_weight = sum(positive_weights.values())

        for gas, slider in self.sliders.items():
            if gas in positive_weights:
                fraction = positive_weights[gas] / total_weight
                target_pa = fraction * target_total
                slider.set_current_value(target_pa)
                self.value_labels[gas].set_text(f"{target_pa:.0f} Pa")
            else:
                slider.set_current_value(0.0)
                self.value_labels[gas].set_text("0 Pa")

    def _set_match_current(self):
        """Set sliders to match current atmosphere (no change target)."""
        for gas, slider in self.sliders.items():
            current_pa = self.planet.atmosphere.get(gas, 0.0)
            slider.set_current_value(current_pa)
            self.value_labels[gas].set_text(f"{current_pa:.0f} Pa")

    def _clear_target(self):
        """Clear all target values (set all sliders to 0)."""
        for gas, slider in self.sliders.items():
            slider.set_current_value(0.0)
            self.value_labels[gas].set_text("0 Pa")
