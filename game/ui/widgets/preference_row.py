"""Reusable UI row for one habitability factor (PROJ-283 Phase 5).

Renders:

    [factor.display_name]  Setpoint: [slider] [value]  Tolerance: [slider] [±value]  [cost]

Used by `RaceEnvironmentPanel` to lay out one row per factor in
`FACTOR_REGISTRY`. Adding a new factor to the registry surfaces a row
here automatically — no panel-side change required.

Display conventions:
    * Slider value is the raw factor value (m/s² for gravity, Pa for
      gases, fraction for water, etc.).
    * Display labels apply `factor.display_scale`:
        gravity: × 1/9.81 → "g"
        pressure / gas: × 0.001 → "kPa"
        water: × 100 → "%"
        temperature: × 1.0 → "K"
        tectonic: × 1.0 → "fraction"
        magnetic: × 1.0 → "earth_equiv"
    * Cost label shows the per-axis cost contribution (NOT total budget):
      `2^|round((tol - default_tolerance) / step)| - 1`.

Callback contract:
    * `on_change` receives `(factor_id, EnvironmentalPreference)` whenever
      `refresh_from_sliders()` is called and either slider moved.
    * Caller is responsible for writing the new preference into
      `RaceConfig.preferences[factor_id]`.
"""
from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

import pygame
from pygame_gui.elements import UIHorizontalSlider, UILabel

from game.strategy.data.environmental_preference import EnvironmentalPreference

if TYPE_CHECKING:
    from game.strategy.data.habitability_factors import HabitabilityFactor


# Layout constants (in px). Single row of 30 px height by default.
_NAME_WIDTH = 140
# PROJ-293: 60 → 90 to give breathing room for "101.3 kPa" (which previously
# overflowed by 3 px) and any future factor with a slightly longer
# display_unit + 2 decimals (e.g. "±50.00 abcde").
_SETPOINT_LABEL_WIDTH = 90
_TOLERANCE_LABEL_WIDTH = 90
_COST_WIDTH = 50
_SLIDER_HEIGHT = 22
_LABEL_HEIGHT = 22
_GAP = 6


class PreferenceRow:
    """One row of the race environment panel; renders a single factor."""

    def __init__(
        self,
        factor: "HabitabilityFactor",
        preference: EnvironmentalPreference,
        manager,
        container,
        rect: pygame.Rect,
        on_change: Optional[Callable[[str, EnvironmentalPreference], None]] = None,
    ) -> None:
        self.factor = factor
        self._on_change = on_change
        self._build_widgets(preference, manager, container, rect)

    # ------------------------------------------------------------------ #
    # Static helpers (also exposed for tests + budget-display callers)    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def format_value(factor: "HabitabilityFactor", raw_value: float) -> str:
        """Render a raw factor value in its display unit.

        PROJ-293: Display formatting is data-driven via `factor.display_unit`
        and `factor.display_precision`. To add a new factor with a custom
        display, set those fields in the registry — no UI code change required.

        Convention: percent unit is glued to the number ("50%"); all other
        non-empty units take a separating space ("1.0 g"); empty unit
        produces a bare number ("0.30").
        """
        scaled = raw_value * factor.display_scale
        text = f"{scaled:.{factor.display_precision}f}"
        if factor.display_unit == "%":
            return f"{text}%"
        if factor.display_unit:
            return f"{text} {factor.display_unit}"
        return text

    @staticmethod
    def calculate_factor_cost(
        factor: "HabitabilityFactor", preference: EnvironmentalPreference,
    ) -> int:
        """Per-factor budget cost. Mirrors `RacePointBudget._exponential_cost`
        applied to one factor's tolerance deviation. Setpoint is free."""
        steps = abs(round((preference.tolerance - factor.default_tolerance) / factor.step))
        if steps <= 0:
            return 0
        return (1 << steps) - 1

    # ------------------------------------------------------------------ #
    # Widget construction                                                 #
    # ------------------------------------------------------------------ #

    def _build_widgets(
        self,
        preference: EnvironmentalPreference,
        manager,
        container,
        rect: pygame.Rect,
    ) -> None:
        """Place the four labels and two sliders into `rect`."""
        x = rect.x
        y = rect.y

        # Name label
        self.name_label = UILabel(
            relative_rect=pygame.Rect(x, y, _NAME_WIDTH, _LABEL_HEIGHT),
            text=self.factor.display_name,
            manager=manager,
            container=container,
        )
        x += _NAME_WIDTH + _GAP

        # Compute remaining width split between two slider+label groups
        # plus the cost label at the right edge.
        cost_label_x = rect.x + rect.width - _COST_WIDTH
        sliders_total = (
            cost_label_x - x
            - _SETPOINT_LABEL_WIDTH - _TOLERANCE_LABEL_WIDTH - _GAP * 3
        )
        slider_width = max(60, sliders_total // 2)

        # Setpoint slider + value label
        self.setpoint_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(x, y, slider_width, _SLIDER_HEIGHT),
            start_value=preference.setpoint,
            value_range=(self.factor.min_value, self.factor.max_value),
            manager=manager,
            container=container,
            click_increment=self.factor.step,
        )
        x += slider_width + _GAP

        self.setpoint_label = UILabel(
            relative_rect=pygame.Rect(x, y, _SETPOINT_LABEL_WIDTH, _LABEL_HEIGHT),
            text=self.format_value(self.factor, preference.setpoint),
            manager=manager,
            container=container,
        )
        x += _SETPOINT_LABEL_WIDTH + _GAP

        # Tolerance slider + value label
        # Tolerance can range from `step` (one cost-step minimum) up to
        # the full axis span; the cost curve handles the rest.
        max_tolerance = max(
            self.factor.default_tolerance * 10,
            self.factor.max_value - self.factor.min_value,
        )
        self.tolerance_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(x, y, slider_width, _SLIDER_HEIGHT),
            start_value=preference.tolerance,
            value_range=(self.factor.step, max_tolerance),
            manager=manager,
            container=container,
            click_increment=self.factor.step,
        )
        x += slider_width + _GAP

        self.tolerance_label = UILabel(
            relative_rect=pygame.Rect(x, y, _TOLERANCE_LABEL_WIDTH, _LABEL_HEIGHT),
            text=f"±{self.format_value(self.factor, preference.tolerance)}",
            manager=manager,
            container=container,
        )

        # Cost label at the far right
        self.cost_label = UILabel(
            relative_rect=pygame.Rect(cost_label_x, y, _COST_WIDTH, _LABEL_HEIGHT),
            text=f"{self.calculate_factor_cost(self.factor, preference)}p",
            manager=manager,
            container=container,
        )

    # ------------------------------------------------------------------ #
    # Slider read / refresh                                               #
    # ------------------------------------------------------------------ #

    def current_preference(self) -> EnvironmentalPreference:
        """Build a fresh `EnvironmentalPreference` from the current
        slider values. Raw slider values are stored as-is; cost
        calculation rounds to the nearest step internally, so explicit
        snapping here would introduce display drift between the slider
        position and the persisted preference."""
        return EnvironmentalPreference(
            setpoint=self.setpoint_slider.get_current_value(),
            tolerance=self.tolerance_slider.get_current_value(),
            min_value=self.factor.min_value,
            max_value=self.factor.max_value,
            step=self.factor.step,
        )

    def refresh_from_sliders(self) -> None:
        """Read both sliders, update the value/cost labels, and fire
        `on_change` with the freshly built preference. Call this from
        the host panel's slider-changed handler."""
        pref = self.current_preference()
        self.setpoint_label.set_text(self.format_value(self.factor, pref.setpoint))
        self.tolerance_label.set_text(
            f"±{self.format_value(self.factor, pref.tolerance)}"
        )
        self.cost_label.set_text(f"{self.calculate_factor_cost(self.factor, pref)}p")
        if self._on_change is not None:
            self._on_change(self.factor.id, pref)

    def set_preference(self, preference: EnvironmentalPreference) -> None:
        """External setter — used when applying a homeworld preset."""
        self.setpoint_slider.set_current_value(preference.setpoint)
        self.tolerance_slider.set_current_value(preference.tolerance)
        self.setpoint_label.set_text(self.format_value(self.factor, preference.setpoint))
        self.tolerance_label.set_text(
            f"±{self.format_value(self.factor, preference.tolerance)}"
        )
        self.cost_label.set_text(
            f"{self.calculate_factor_cost(self.factor, preference)}p"
        )

    def owns_event(self, event) -> bool:
        """True if the event refers to one of this row's sliders."""
        ui_element = getattr(event, "ui_element", None)
        return ui_element in (self.setpoint_slider, self.tolerance_slider)
