"""Race Environment Panel — registry-driven UI (PROJ-283 Phase 5).

Iterates `FACTOR_REGISTRY` and renders one `PreferenceRow` per factor:
    * 7 scalar rows (gravity / temperature / water / pressure / tectonic /
      magnetic / radiation) under a "Surface" section
    * 10 gas rows under an "Atmosphere" section

Plus:
    * Live points-remaining label at the top
    * Homeworld preset dropdown
    * `base_reproduction_rate` and `base_happiness` single-slider rows

Adding a new habitability axis requires zero changes to this file —
adding an entry to `FACTOR_REGISTRY` surfaces a row automatically.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIDropDownMenu, UIHorizontalSlider, UILabel

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import (
    iter_gas_factors,
    iter_scalar_factors,
)
from game.strategy.data.homeworld_presets import (
    apply_preset_to_config,
    get_preset_for_planet_type,
    get_preset_id_from_name,
    load_homeworld_presets,
)
from game.ui.utils import create_section_header
from game.ui.widgets.preference_row import PreferenceRow

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


# Layout constants
_ROW_HEIGHT = 28
_ROW_GAP = 4
_SECTION_GAP = 12
_PADDING = 10

# Reproduction-rate slider bounds (mirror `RacePointBudget` floor/cap).
_REPRO_MIN = 0.005   # 0.5% (floor)
_REPRO_MAX = 0.10    # 10%

# Happiness seed slider bounds.
_HAPPINESS_MIN = 0.0
_HAPPINESS_MAX = 1.0


class RaceEnvironmentPanel:
    """Registry-driven environment panel."""

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: "RaceConfig",
    ) -> None:
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config

        # Widgets populated in `_create_content`
        self.points_label: Optional[UILabel] = None
        self.homeworld_dropdown: Optional[UIDropDownMenu] = None
        self.reproduction_slider: Optional[UIHorizontalSlider] = None
        self.reproduction_label: Optional[UILabel] = None
        self.happiness_slider: Optional[UIHorizontalSlider] = None
        self.happiness_label: Optional[UILabel] = None

        # `factor_id -> PreferenceRow`. Order preserved by `FACTOR_REGISTRY`.
        self.preference_rows: Dict[str, PreferenceRow] = {}

        self._create_content()

    # ------------------------------------------------------------------ #
    # Layout                                                              #
    # ------------------------------------------------------------------ #

    def _create_content(self) -> None:
        panel_rect = self.panel.get_relative_rect()
        panel_width = panel_rect.width - 2 * _PADDING
        y = _PADDING

        y = self._create_points_label(y, panel_width)
        y += _ROW_GAP
        y = self._create_homeworld_dropdown(y, panel_width)
        y += _SECTION_GAP

        y = self._create_repro_and_happiness(y, panel_width)
        y += _SECTION_GAP

        # Surface section
        create_section_header(
            "Surface", y, panel_width, self.ui_manager, self.panel,
            height=_ROW_HEIGHT,
        )
        y += _ROW_HEIGHT + _ROW_GAP
        y = self._create_factor_rows(iter_scalar_factors(), y, panel_width)
        y += _SECTION_GAP

        # Atmosphere section
        create_section_header(
            "Atmosphere", y, panel_width, self.ui_manager, self.panel,
            height=_ROW_HEIGHT,
        )
        y += _ROW_HEIGHT + _ROW_GAP
        y = self._create_factor_rows(iter_gas_factors(), y, panel_width)

    def _create_points_label(self, y: int, width: int) -> int:
        self.points_label = UILabel(
            relative_rect=pygame.Rect(_PADDING, y, width, _ROW_HEIGHT),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#points_display",
        )
        self._update_points_display()
        return y + _ROW_HEIGHT

    def _create_homeworld_dropdown(self, y: int, width: int) -> int:
        presets = load_homeworld_presets()
        options = [preset["name"] for preset in presets.values()]
        options.append("(Custom)")
        starting_option = "(Custom)"
        if self.race_config.homeworld_type:
            preset = presets.get(self.race_config.homeworld_type)
            if preset:
                starting_option = preset["name"]
        self.homeworld_dropdown = UIDropDownMenu(
            options_list=options,
            starting_option=starting_option,
            relative_rect=pygame.Rect(_PADDING, y, width, _ROW_HEIGHT),
            manager=self.ui_manager,
            container=self.panel,
        )
        return y + _ROW_HEIGHT

    def _create_repro_and_happiness(self, y: int, width: int) -> int:
        # Reproduction-rate row
        UILabel(
            relative_rect=pygame.Rect(_PADDING, y, 200, _ROW_HEIGHT),
            text="Base reproduction rate:",
            manager=self.ui_manager,
            container=self.panel,
        )
        slider_w = max(120, width - 360)
        self.reproduction_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(_PADDING + 210, y, slider_w, _ROW_HEIGHT - 4),
            start_value=self.race_config.base_reproduction_rate,
            value_range=(_REPRO_MIN, _REPRO_MAX),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.01,
        )
        self.reproduction_label = UILabel(
            relative_rect=pygame.Rect(_PADDING + 210 + slider_w + 5, y, 80, _ROW_HEIGHT),
            text=self._format_reproduction(self.race_config.base_reproduction_rate),
            manager=self.ui_manager,
            container=self.panel,
        )
        y += _ROW_HEIGHT + _ROW_GAP

        # Happiness row
        UILabel(
            relative_rect=pygame.Rect(_PADDING, y, 200, _ROW_HEIGHT),
            text="Base happiness (seed):",
            manager=self.ui_manager,
            container=self.panel,
        )
        self.happiness_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(_PADDING + 210, y, slider_w, _ROW_HEIGHT - 4),
            start_value=self.race_config.base_happiness,
            value_range=(_HAPPINESS_MIN, _HAPPINESS_MAX),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.05,
        )
        self.happiness_label = UILabel(
            relative_rect=pygame.Rect(_PADDING + 210 + slider_w + 5, y, 80, _ROW_HEIGHT),
            text=f"{self.race_config.base_happiness:.2f}",
            manager=self.ui_manager,
            container=self.panel,
        )
        y += _ROW_HEIGHT
        return y

    def _create_factor_rows(self, factors_iter, y: int, width: int) -> int:
        for factor in factors_iter:
            preference = self.race_config.preferences[factor.id]
            row = PreferenceRow(
                factor=factor,
                preference=preference,
                manager=self.ui_manager,
                container=self.panel,
                rect=pygame.Rect(_PADDING, y, width, _ROW_HEIGHT),
                on_change=self._on_row_change,
            )
            self.preference_rows[factor.id] = row
            y += _ROW_HEIGHT + _ROW_GAP
        return y

    # ------------------------------------------------------------------ #
    # Slider read / write                                                 #
    # ------------------------------------------------------------------ #

    def update_config(self) -> None:
        """Read every row + repro/happiness slider into `race_config`."""
        for factor_id, row in self.preference_rows.items():
            self.race_config.preferences[factor_id] = row.current_preference()
        if self.reproduction_slider is not None:
            self.race_config.base_reproduction_rate = (
                self.reproduction_slider.get_current_value()
            )
        if self.happiness_slider is not None:
            self.race_config.base_happiness = (
                self.happiness_slider.get_current_value()
            )
        self._update_points_display()

    def update_labels(self) -> None:
        """Refresh every factor row + repro/happiness labels from the
        current slider positions.

        Cross-panel API contract — sibling panels (`RaceIdentityPanel`,
        `RaceAptitudesPanel`) both expose `update_labels()`; the host
        screen's slider-move handler calls it on all three.

        Each `PreferenceRow.refresh_from_sliders()` re-reads its sliders,
        updates the setpoint / tolerance / cost labels, and fires the
        `on_change` callback — which writes the fresh preference back
        into `race_config` and re-renders the points-remaining header.
        The reproduction + happiness labels are refreshed in place
        since those are bespoke single-slider rows (not `PreferenceRow`
        instances).
        """
        for row in self.preference_rows.values():
            row.refresh_from_sliders()
        if self.reproduction_slider is not None and self.reproduction_label is not None:
            self.reproduction_label.set_text(
                self._format_reproduction(self.reproduction_slider.get_current_value())
            )
        if self.happiness_slider is not None and self.happiness_label is not None:
            self.happiness_label.set_text(
                f"{self.happiness_slider.get_current_value():.2f}"
            )

    def set_from_config(self) -> None:
        """Push every preference + repro/happiness back into the UI."""
        for factor_id, row in self.preference_rows.items():
            row.set_preference(self.race_config.preferences[factor_id])
        if self.reproduction_slider is not None:
            self.reproduction_slider.set_current_value(
                self.race_config.base_reproduction_rate
            )
        if self.reproduction_label is not None:
            self.reproduction_label.set_text(
                self._format_reproduction(self.race_config.base_reproduction_rate)
            )
        if self.happiness_slider is not None:
            self.happiness_slider.set_current_value(self.race_config.base_happiness)
        if self.happiness_label is not None:
            self.happiness_label.set_text(f"{self.race_config.base_happiness:.2f}")
        self._update_points_display()

    def _on_row_change(
        self, factor_id: str, new_pref: EnvironmentalPreference,
    ) -> None:
        """Callback fired by `PreferenceRow.refresh_from_sliders`. Writes
        the row's reported preference back into `race_config` and refreshes
        the points label."""
        self.race_config.preferences[factor_id] = new_pref
        self._update_points_display()

    # ------------------------------------------------------------------ #
    # Homeworld presets                                                   #
    # ------------------------------------------------------------------ #

    def apply_homeworld_preset(self, planet_type_name: str) -> None:
        """Apply a preset (or '(Custom)' = no-op) to the race config and
        refresh the relevant rows."""
        if planet_type_name == "(Custom)":
            return
        preset = get_preset_for_planet_type(planet_type_name)
        if preset is None:
            return
        apply_preset_to_config(preset, self.race_config)
        self.set_from_config()

    def handle_dropdown_change(self, event) -> bool:
        """Wire dropdown change events through to `apply_homeworld_preset`.
        Returns True if this panel handled the event."""
        if (
            self.homeworld_dropdown is not None
            and getattr(event, "ui_element", None) is self.homeworld_dropdown
        ):
            selected = self.homeworld_dropdown.selected_option
            if isinstance(selected, tuple):
                selected = selected[0]
            preset_id = get_preset_id_from_name(selected)
            self.apply_homeworld_preset(preset_id if preset_id else selected)
            return True
        return False

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _update_points_display(self) -> None:
        if self.points_label is None:
            return
        try:
            from game.strategy.data.race_point_budget import RacePointBudget
            budget = RacePointBudget()
            remaining = budget.get_remaining_points(self.race_config)
            total = budget.total_budget
            env_cost = budget.calculate_preferences_cost(self.race_config)
            self.points_label.set_text(
                f"Points: {remaining} / {total} remaining  |  Environment cost: {env_cost}"
            )
        except Exception as e:  # Intentional broad catch: the points label is non-critical UI; any failure (missing race attribute, bad budget config, etc.) blanks the label rather than crashing the panel.
            logger.warning("Failed to update points display: %s", e)
            self.points_label.set_text("")

    @staticmethod
    def _format_reproduction(rate: float) -> str:
        return f"{rate * 100:.1f}%"
