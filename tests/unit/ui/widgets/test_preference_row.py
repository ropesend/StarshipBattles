"""Tests for `PreferenceRow` (PROJ-283 Phase 5).

`PreferenceRow` is a reusable UI row that renders one habitability factor:

    [factor.display_name]  Setpoint: [slider] [value]  Tolerance: [slider] [±value]  [cost]

Both sliders honour the factor's `min_value`, `max_value`, and `step`.
Slider value labels are scaled by `factor.display_scale` (Pa → kPa for
pressures, m/s² → g for gravity, fraction → percent for water).

The row owns no `RaceConfig` reference — its `EnvironmentalPreference`
is read on demand. When a slider changes, the row builds a fresh
preference and fires `on_change(factor.id, new_pref)` so the caller can
write into `RaceConfig.preferences[factor.id]`.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import get_factor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_manager():
    return MagicMock()


@pytest.fixture
def mock_container():
    return MagicMock()


@pytest.fixture
def gravity_factor():
    return get_factor("gravity")


@pytest.fixture
def gravity_pref(gravity_factor):
    return EnvironmentalPreference(
        setpoint=gravity_factor.default_setpoint,
        tolerance=gravity_factor.default_tolerance,
        min_value=gravity_factor.min_value,
        max_value=gravity_factor.max_value,
        step=gravity_factor.step,
    )


@pytest.fixture
def gas_o2_factor():
    return get_factor("gas.O2")


@pytest.fixture
def gas_o2_pref(gas_o2_factor):
    return EnvironmentalPreference(
        setpoint=gas_o2_factor.default_setpoint,
        tolerance=gas_o2_factor.default_tolerance,
        min_value=gas_o2_factor.min_value,
        max_value=gas_o2_factor.max_value,
        step=gas_o2_factor.step,
    )


def _patch_widgets():
    """Returns a context-managed pair of patches for the two pygame_gui
    widget classes the row constructs."""
    return (
        patch('game.ui.widgets.preference_row.UIHorizontalSlider'),
        patch('game.ui.widgets.preference_row.UILabel'),
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestPreferenceRowConstruction:
    def test_constructs_for_scalar_factor(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p as MockLabel:
            MockSlider.return_value = MagicMock()
            MockLabel.return_value = MagicMock()
            row = PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
            )
            # Two sliders (setpoint + tolerance) constructed
            assert MockSlider.call_count == 2
            # Four labels: name, setpoint value, tolerance value, cost
            assert MockLabel.call_count == 4
            assert row.factor is gravity_factor

    def test_constructs_for_gas_factor(
        self, mock_manager, mock_container, gas_o2_factor, gas_o2_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p:
            MockSlider.return_value = MagicMock()
            row = PreferenceRow(
                factor=gas_o2_factor,
                preference=gas_o2_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
            )
            assert row.factor.id == "gas.O2"

    def test_setpoint_slider_uses_factor_bounds(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        """Setpoint slider's value_range must come from
        `(factor.min_value, factor.max_value)` so the user can place
        their setpoint anywhere on the legal axis."""
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p:
            MockSlider.return_value = MagicMock()
            PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
            )
            # First slider call = setpoint slider
            _, kwargs = MockSlider.call_args_list[0]
            assert kwargs["value_range"] == (gravity_factor.min_value, gravity_factor.max_value)
            assert kwargs["start_value"] == gravity_pref.setpoint

    def test_tolerance_slider_starts_at_pref_tolerance(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p:
            MockSlider.return_value = MagicMock()
            PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
            )
            # Second slider call = tolerance slider
            _, kwargs = MockSlider.call_args_list[1]
            assert kwargs["start_value"] == gravity_pref.tolerance


# ---------------------------------------------------------------------------
# Display scaling
# ---------------------------------------------------------------------------


class TestDisplayScaling:
    def test_pressure_value_displayed_in_kpa(
        self, mock_manager, mock_container, gas_o2_factor,
    ):
        """Gas factors store Pa internally; the value label should show kPa
        (display_scale = 0.001)."""
        from game.ui.widgets.preference_row import PreferenceRow

        # Setpoint of 101325 Pa should render as "101.3 kPa"
        pref = EnvironmentalPreference(
            setpoint=101325.0,
            tolerance=gas_o2_factor.default_tolerance,
            min_value=gas_o2_factor.min_value,
            max_value=gas_o2_factor.max_value,
            step=gas_o2_factor.step,
        )

        from game.ui.widgets.preference_row import PreferenceRow
        formatted = PreferenceRow.format_value(gas_o2_factor, 101325.0)
        assert "101.3" in formatted
        assert "kPa" in formatted

    def test_gravity_value_displayed_in_g(self, gravity_factor):
        from game.ui.widgets.preference_row import PreferenceRow

        # 9.81 m/s² × (1/9.81) = 1.0 g
        formatted = PreferenceRow.format_value(gravity_factor, 9.81)
        assert "1.0" in formatted
        assert "g" in formatted.lower()

    def test_water_value_displayed_as_percent(self):
        from game.ui.widgets.preference_row import PreferenceRow

        water = get_factor("water")
        # 0.5 fraction × 100 = 50%
        formatted = PreferenceRow.format_value(water, 0.5)
        assert "50" in formatted
        assert "%" in formatted

    def test_temperature_value_displayed_in_kelvin(self):
        from game.ui.widgets.preference_row import PreferenceRow

        temp = get_factor("temperature")
        # display_scale = 1.0, unit "K"
        formatted = PreferenceRow.format_value(temp, 293.0)
        assert "293" in formatted
        assert "K" in formatted


# ---------------------------------------------------------------------------
# on_change callback
# ---------------------------------------------------------------------------


class TestOnChangeCallback:
    def test_setpoint_change_fires_callback_with_factor_id_and_pref(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p:
            mock_setpoint = MagicMock()
            mock_tolerance = MagicMock()
            mock_setpoint.get_current_value.return_value = 12.0
            mock_tolerance.get_current_value.return_value = gravity_pref.tolerance
            MockSlider.side_effect = [mock_setpoint, mock_tolerance]

            on_change = MagicMock()
            row = PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
                on_change=on_change,
            )
            # Simulate the user moving the setpoint slider, then telling
            # the row to refresh from its sliders.
            row.refresh_from_sliders()

            on_change.assert_called_once()
            factor_id, new_pref = on_change.call_args.args
            assert factor_id == "gravity"
            assert isinstance(new_pref, EnvironmentalPreference)
            assert new_pref.setpoint == 12.0
            assert new_pref.tolerance == gravity_pref.tolerance

    def test_tolerance_change_fires_callback(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p:
            mock_setpoint = MagicMock()
            mock_tolerance = MagicMock()
            mock_setpoint.get_current_value.return_value = gravity_pref.setpoint
            mock_tolerance.get_current_value.return_value = gravity_pref.tolerance + gravity_factor.step
            MockSlider.side_effect = [mock_setpoint, mock_tolerance]

            on_change = MagicMock()
            row = PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
                on_change=on_change,
            )
            row.refresh_from_sliders()

            on_change.assert_called_once()
            _, new_pref = on_change.call_args.args
            assert new_pref.tolerance == gravity_pref.tolerance + gravity_factor.step


# ---------------------------------------------------------------------------
# Cost label
# ---------------------------------------------------------------------------


class TestCostLabel:
    def test_default_tolerance_costs_zero(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        # default tolerance ⇒ 0 cost
        cost = PreferenceRow.calculate_factor_cost(gravity_factor, gravity_pref)
        assert cost == 0

    def test_one_step_tighter_costs_one(
        self, mock_manager, mock_container, gravity_factor,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        pref = EnvironmentalPreference(
            setpoint=gravity_factor.default_setpoint,
            tolerance=gravity_factor.default_tolerance - gravity_factor.step,
            min_value=gravity_factor.min_value,
            max_value=gravity_factor.max_value,
            step=gravity_factor.step,
        )
        cost = PreferenceRow.calculate_factor_cost(gravity_factor, pref)
        assert cost == 1

    def test_three_steps_costs_seven(self, gravity_factor):
        from game.ui.widgets.preference_row import PreferenceRow

        pref = EnvironmentalPreference(
            setpoint=gravity_factor.default_setpoint,
            tolerance=gravity_factor.default_tolerance + 3 * gravity_factor.step,
            min_value=gravity_factor.min_value,
            max_value=gravity_factor.max_value,
            step=gravity_factor.step,
        )
        cost = PreferenceRow.calculate_factor_cost(gravity_factor, pref)
        assert cost == 7  # 2^3 - 1

    def test_setpoint_change_does_not_cost(self, gravity_factor):
        """Setpoint is free regardless of where it sits in the axis range."""
        from game.ui.widgets.preference_row import PreferenceRow

        pref = EnvironmentalPreference(
            setpoint=20.0,  # far from default 9.81
            tolerance=gravity_factor.default_tolerance,
            min_value=gravity_factor.min_value,
            max_value=gravity_factor.max_value,
            step=gravity_factor.step,
        )
        cost = PreferenceRow.calculate_factor_cost(gravity_factor, pref)
        assert cost == 0


class TestCostLabelLiveUpdate:
    def test_cost_label_text_updates_on_tolerance_slider_move(
        self, mock_manager, mock_container, gravity_factor, gravity_pref,
    ):
        from game.ui.widgets.preference_row import PreferenceRow

        slider_p, label_p = _patch_widgets()
        with slider_p as MockSlider, label_p as MockLabel:
            mock_setpoint = MagicMock()
            mock_tolerance = MagicMock()
            mock_setpoint.get_current_value.return_value = gravity_pref.setpoint
            # Tighten by one step -> 1 point cost
            mock_tolerance.get_current_value.return_value = (
                gravity_pref.tolerance - gravity_factor.step
            )
            MockSlider.side_effect = [mock_setpoint, mock_tolerance]
            # Track the label instances so we can identify the cost label
            labels = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            MockLabel.side_effect = labels

            row = PreferenceRow(
                factor=gravity_factor,
                preference=gravity_pref,
                manager=mock_manager,
                container=mock_container,
                rect=pygame.Rect(0, 0, 800, 30),
            )
            row.refresh_from_sliders()

            # The cost label is the row's `cost_label` attribute; check
            # set_text was called with a string containing "1".
            assert row.cost_label is not None
            calls = [c.args[0] for c in row.cost_label.set_text.call_args_list]
            assert any("1" in text for text in calls), (
                f"Expected cost label to show '1'; got calls {calls}"
            )
