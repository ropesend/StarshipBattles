"""Tests for the rebuilt `RaceEnvironmentPanel` (PROJ-283 Phase 5).

The new panel iterates `FACTOR_REGISTRY`:
    * One `PreferenceRow` per scalar factor (7 rows)
    * One `PreferenceRow` per gas factor (10 rows, under "Atmosphere")
    * Two single-slider rows for `base_reproduction_rate` and `base_happiness`
    * A homeworld dropdown at the top
    * A live points-remaining label

Tests rely on heavy mocking of pygame_gui widgets — we don't need real
rendering, just verification that the right rows are constructed and
that `update_config` / `set_from_config` / `apply_homeworld_preset`
read/write the expected `race_config` attributes.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import (
    FACTOR_REGISTRY,
    iter_gas_factors,
    iter_scalar_factors,
)
from game.strategy.data.race_config import RaceConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_panel():
    p = MagicMock()
    # Panel rect — make it tall enough for ~17 rows
    p.get_relative_rect.return_value = pygame.Rect(0, 0, 800, 1200)
    return p


@pytest.fixture
def mock_manager():
    return MagicMock()


@pytest.fixture
def race_config():
    return RaceConfig(
        name="Test Race",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


def _make_panel(mock_panel, mock_manager, race_config):
    """Construct a `RaceEnvironmentPanel` with all the pygame_gui /
    pygame_gui-derived classes patched out.

    Each pygame_gui constructor call returns a fresh `MagicMock` so that
    `panel.reproduction_slider` and `panel.happiness_slider` (and the
    individual labels) are distinct instances — otherwise tests that
    inspect calls on one widget would see the most recent call on a
    shared mock.
    """
    from game.ui.panels import race_environment_panel as rep_module

    def _fresh_mock_class():
        m = MagicMock()
        m.side_effect = lambda *a, **kw: MagicMock()
        return m

    patches = [
        patch.object(rep_module, "UILabel", _fresh_mock_class()),
        patch.object(rep_module, "UIDropDownMenu", _fresh_mock_class()),
        patch.object(rep_module, "UIHorizontalSlider", _fresh_mock_class()),
        patch.object(rep_module, "PreferenceRow", _fresh_mock_class()),
        patch.object(rep_module, "create_section_header", MagicMock()),
    ]
    for p in patches:
        p.start()
    try:
        return rep_module.RaceEnvironmentPanel(
            panel=mock_panel,
            manager=mock_manager,
            race_config=race_config,
        )
    finally:
        for p in patches:
            p.stop()


# ---------------------------------------------------------------------------
# Construction: one row per registry factor
# ---------------------------------------------------------------------------


class TestPanelConstruction:
    def test_panel_has_row_for_every_scalar_factor(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        scalar_ids = {f.id for f in iter_scalar_factors()}
        assert scalar_ids.issubset(set(panel.preference_rows.keys()))

    def test_panel_has_row_for_every_gas_factor(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        gas_ids = {f.id for f in iter_gas_factors()}
        assert gas_ids.issubset(set(panel.preference_rows.keys()))

    def test_panel_has_17_total_rows(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        assert len(panel.preference_rows) == len(FACTOR_REGISTRY)

    def test_panel_has_reproduction_and_happiness_sliders(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        assert panel.reproduction_slider is not None
        assert panel.happiness_slider is not None

    def test_panel_has_homeworld_dropdown(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        assert panel.homeworld_dropdown is not None

    def test_panel_has_points_label(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        assert panel.points_label is not None


# ---------------------------------------------------------------------------
# update_config: PreferenceRow callback writes to race_config.preferences
# ---------------------------------------------------------------------------


class TestUpdateConfig:
    def test_update_config_reads_each_row_into_preferences(
        self, mock_panel, mock_manager, race_config,
    ):
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        panel = _make_panel(mock_panel, mock_manager, race_config)
        # Make every PreferenceRow.current_preference return a known
        # marker so update_config writes them into race_config.preferences.
        for fid, row in panel.preference_rows.items():
            factor = FACTOR_REGISTRY[fid]
            row.current_preference.return_value = EnvironmentalPreference(
                setpoint=factor.default_setpoint,
                tolerance=factor.default_tolerance + factor.step,  # 1 step deviation
                min_value=factor.min_value,
                max_value=factor.max_value,
                step=factor.step,
            )

        panel.update_config()

        # Every preference should now reflect the row's reported value.
        for fid in panel.preference_rows:
            factor = FACTOR_REGISTRY[fid]
            assert race_config.preferences[fid].tolerance == pytest.approx(
                factor.default_tolerance + factor.step
            )

    def test_update_config_reads_repro_and_happiness_sliders(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        panel.reproduction_slider.get_current_value.return_value = 0.05
        panel.happiness_slider.get_current_value.return_value = 0.7

        panel.update_config()

        assert race_config.base_reproduction_rate == pytest.approx(0.05)
        assert race_config.base_happiness == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# set_from_config: panel mirrors race_config state into rows + sliders
# ---------------------------------------------------------------------------


class TestSetFromConfig:
    def test_set_from_config_calls_set_preference_per_row(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        panel.set_from_config()
        for fid, row in panel.preference_rows.items():
            row.set_preference.assert_called()
            arg = row.set_preference.call_args.args[0]
            assert arg is race_config.preferences[fid]

    def test_set_from_config_writes_repro_and_happiness_sliders(
        self, mock_panel, mock_manager, race_config,
    ):
        race_config.base_reproduction_rate = 0.04
        race_config.base_happiness = 0.7
        panel = _make_panel(mock_panel, mock_manager, race_config)
        panel.set_from_config()
        panel.reproduction_slider.set_current_value.assert_called_with(0.04)
        panel.happiness_slider.set_current_value.assert_called_with(0.7)


# ---------------------------------------------------------------------------
# Homeworld preset application
# ---------------------------------------------------------------------------


class TestApplyHomeworldPreset:
    def test_apply_continental_overrides_relevant_factors(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)

        # Continental's preferences include gravity/temperature/water/...
        panel.apply_homeworld_preset("CONTINENTAL")

        # Race's gravity preference should now reflect Continental's setpoint.
        assert race_config.preferences["gravity"].setpoint == pytest.approx(9.81)
        assert race_config.homeworld_type == "CONTINENTAL"

    def test_apply_custom_does_not_mutate(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        original_gravity_setpoint = race_config.preferences["gravity"].setpoint
        panel.apply_homeworld_preset("(Custom)")
        assert race_config.preferences["gravity"].setpoint == original_gravity_setpoint


# ---------------------------------------------------------------------------
# Live points label
# ---------------------------------------------------------------------------


class TestPointsLabel:
    def test_update_points_display_calls_set_text(
        self, mock_panel, mock_manager, race_config,
    ):
        panel = _make_panel(mock_panel, mock_manager, race_config)
        panel.points_label.set_text.reset_mock()
        panel._update_points_display()
        panel.points_label.set_text.assert_called()
        text = panel.points_label.set_text.call_args.args[0]
        assert "100" in text or "Points" in text


# ---------------------------------------------------------------------------
# update_labels: cross-panel API contract + live slider-move refresh
# ---------------------------------------------------------------------------

# Regression tests for the crash
#   AttributeError: 'RaceEnvironmentPanel' object has no attribute 'update_labels'
# at race_setup_screen.py:546. The refactor in PROJ-283 Phase 5 dropped the
# method that sibling panels (Identity, Aptitudes) expose. Restoring it must
# also refresh per-row labels live — PreferenceRow.refresh_from_sliders is
# the widget-level method that reads sliders and updates labels + cost; the
# panel's update_labels fans that out to every row plus the bespoke
# reproduction/happiness single-slider rows.


class TestUpdateLabels:
    def _seed_numeric_sliders(self, panel):
        """Seed the repro/happiness slider mocks with numeric values so
        the panel's format-string formatters (`{:.1f}`, `{:.2f}`) don't
        trip on default `MagicMock` return values."""
        panel.reproduction_slider.get_current_value.return_value = 0.03
        panel.happiness_slider.get_current_value.return_value = 0.5

    def test_update_labels_exists_and_callable(
        self, mock_panel, mock_manager, race_config,
    ):
        """Bare contract: the method exists and doesn't raise.

        This is the test that would have caught the original crash.
        Sibling panels (`RaceIdentityPanel`, `RaceAptitudesPanel`) both
        expose `update_labels()`; the PROJ-283 Phase 5 rewrite dropped
        it here, breaking the cross-panel API.
        """
        panel = _make_panel(mock_panel, mock_manager, race_config)
        self._seed_numeric_sliders(panel)
        assert hasattr(panel, "update_labels")
        panel.update_labels()  # must not raise

    def test_update_labels_calls_refresh_from_sliders_on_every_row(
        self, mock_panel, mock_manager, race_config,
    ):
        """Each `PreferenceRow.refresh_from_sliders()` must be called
        exactly once. This is the method that re-renders each row's
        setpoint / tolerance / cost labels from current slider values
        AND fires the `on_change` callback, which in turn refreshes
        the points-remaining header.
        """
        panel = _make_panel(mock_panel, mock_manager, race_config)
        self._seed_numeric_sliders(panel)
        for row in panel.preference_rows.values():
            row.refresh_from_sliders.reset_mock()

        panel.update_labels()

        for fid, row in panel.preference_rows.items():
            row.refresh_from_sliders.assert_called_once(), (
                f"row {fid} was not refreshed"
            )

    def test_update_labels_refreshes_reproduction_and_happiness_labels(
        self, mock_panel, mock_manager, race_config,
    ):
        """The bespoke single-slider rows (reproduction + happiness) are
        NOT `PreferenceRow` instances and therefore need explicit label
        refresh from `update_labels()` — otherwise dragging those two
        sliders leaves their numeric labels stale."""
        panel = _make_panel(mock_panel, mock_manager, race_config)
        panel.reproduction_slider.get_current_value.return_value = 0.042
        panel.happiness_slider.get_current_value.return_value = 0.73
        panel.reproduction_label.set_text.reset_mock()
        panel.happiness_label.set_text.reset_mock()

        panel.update_labels()

        panel.reproduction_label.set_text.assert_called_once()
        panel.happiness_label.set_text.assert_called_once()
        # Happiness label reads `{value:.2f}`; reproduction uses
        # `_format_reproduction` which renders a percentage — assert
        # the value substring appears in each label call.
        happy_text = panel.happiness_label.set_text.call_args.args[0]
        assert "0.73" in happy_text
        repro_text = panel.reproduction_label.set_text.call_args.args[0]
        # 0.042 -> "4.2%" via _format_reproduction (rate * 100).
        assert "4.2" in repro_text

    def test_update_labels_is_idempotent(
        self, mock_panel, mock_manager, race_config,
    ):
        """Calling `update_labels()` repeatedly (as a user dragging a
        slider triggers many `UI_HORIZONTAL_SLIDER_MOVED` events per
        second would) must not raise — and each call re-invokes
        `refresh_from_sliders` on every row."""
        panel = _make_panel(mock_panel, mock_manager, race_config)
        self._seed_numeric_sliders(panel)
        for row in panel.preference_rows.values():
            row.refresh_from_sliders.reset_mock()

        panel.update_labels()
        panel.update_labels()
        panel.update_labels()

        for row in panel.preference_rows.values():
            assert row.refresh_from_sliders.call_count == 3
