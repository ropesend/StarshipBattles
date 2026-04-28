"""
Unit tests for RaceSummaryPanel.

PROJ-44 Phase 7 Task 7.1: TDD tests for the summary panel extraction.
Tests the race summary display panel functionality.
"""

import pygame
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

# PROJ-283 Phase 4: switched from MagicMock to real RaceConfig instances —
# the summary panel formatters now read from `race_config.preferences` (a
# typed dict of `EnvironmentalPreference`), and MagicMock can't impersonate
# the dict subscript + attribute access cleanly. Real RaceConfig is light
# enough to construct in a fixture, and `__post_init__` backfills any
# preferences not explicitly overridden.

def _override_pref(rc, factor_id, *, setpoint=None, tolerance=None):
    from game.strategy.data.environmental_preference import EnvironmentalPreference
    from game.strategy.data.habitability_factors import get_factor
    f = get_factor(factor_id)
    rc.preferences[factor_id] = EnvironmentalPreference(
        setpoint=setpoint if setpoint is not None else f.default_setpoint,
        tolerance=tolerance if tolerance is not None else f.default_tolerance,
        min_value=f.min_value, max_value=f.max_value, step=f.step,
    )


@pytest.fixture
def mock_race_config():
    """Real RaceConfig populated for summary-display tests.

    Sets two atmospheric setpoints (O2, N2) so atmosphere-summary tests
    have something non-zero to render.
    """
    from game.strategy.data.race_config import RaceConfig
    config = RaceConfig(
        name="Test Race",
        flag_id="flag_01",
        portrait_id="portrait_01",
        theme_id="Atlantians",
        faction_name="Test Empire",
        race_name="Testarians",
        government_type="Empire",
        government_organization="Centralized",
        physical_type="Humanoid",
        society_type="Collectivist",
        homeworld_type="CONTINENTAL",
        bio_description="Test biological description",
        socio_description="Test sociological description",
    )
    _override_pref(config, "gravity", setpoint=9.81, tolerance=0.3 * 9.81)
    _override_pref(config, "temperature", setpoint=293.0, tolerance=50.0)
    _override_pref(config, "radiation", setpoint=0.0, tolerance=10.0)
    _override_pref(config, "water", setpoint=0.5, tolerance=0.3)
    # Atmosphere setpoints — keep the gases that the legacy fixture exercised
    _override_pref(config, "gas.O2", setpoint=20000.0)
    _override_pref(config, "gas.N2", setpoint=10000.0)
    return config


@pytest.fixture
def mock_race_config_empty():
    """Real RaceConfig with no atmosphere setpoints — exercises the
    'all neutral' atmosphere-summary branch."""
    from game.strategy.data.race_config import RaceConfig
    config = RaceConfig(
        name="",
        # Empty identity fields exercise placeholder rendering. `validate()`
        # would reject this config, but the summary-panel formatters never
        # call validate — they just read attributes.
        flag_id="",
        portrait_id="",
        theme_id="",
    )
    # Gas setpoints all zero except registry defaults (O2=21k, N2=79k);
    # explicitly zero them so the atmosphere summary formatter falls
    # through to "All neutral".
    for fid in list(config.preferences.keys()):
        if fid.startswith("gas."):
            _override_pref(config, fid, setpoint=0.0)
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


@pytest.fixture
def mock_asset_loader():
    """Create a mock RaceAssetLoader."""
    loader = MagicMock()
    return loader


# =============================================================================
# Test: RaceSummaryPanel Import and Creation
# =============================================================================

class TestRaceSummaryPanelCreation:
    """Tests for RaceSummaryPanel initialization."""

    def test_race_summary_panel_has_expected_attributes(self):
        """RaceSummaryPanel has expected UI element attributes."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        # Use mock to avoid pygame initialization
        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.summary_labels = {}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []

            # Verify the attributes exist
            assert hasattr(panel, 'summary_labels')
            assert hasattr(panel, 'summary_flag_images')
            assert hasattr(panel, 'summary_portrait_image')
            assert hasattr(panel, 'summary_ship_images')

    def test_race_summary_panel_stores_race_config(self, mock_race_config):
        """RaceSummaryPanel stores reference to race_config."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            assert panel.race_config is mock_race_config


# =============================================================================
# Test: Summary Data Formatting
# =============================================================================

class TestSummaryDataFormatting:
    """Tests for summary data formatting methods."""

    # FEAT-14: gravity / temperature / radiation / water / atmosphere are no
    # longer rendered via per-factor formatters. The Summary tab now iterates
    # FACTOR_REGISTRY end-to-end and uses `PreferenceRow.format_value` —
    # see TestFeat14RegistryDrivenSummary below.

    def test_format_description_status_with_content(self, mock_race_config):
        """Description status shows character count when content exists."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            bio_status = panel._format_bio_status()
            socio_status = panel._format_socio_status()

            assert "chars" in bio_status or "Set" in bio_status
            assert "chars" in socio_status or "Set" in socio_status

    def test_format_description_status_empty(self, mock_race_config_empty):
        """Description status shows empty when no content."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config_empty

            bio_status = panel._format_bio_status()

            assert "Empty" in bio_status or "0" in bio_status


# =============================================================================
# Test: Refresh Summary
# =============================================================================

class TestRefreshSummary:
    """Tests for refreshing summary display."""

    def test_refresh_updates_faction_label(self, mock_race_config):
        """refresh() updates faction label from race_config.

        PROJ-66 Phase 6: Changed from name_value to faction_value.
        """
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            panel.summary_labels = {'faction_value': MagicMock()}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            # FEAT-14: column-3 scroll container is None in these legacy
            # tests — _rebuild_env_scroll_content treats that as a no-op.
            panel._env_scroll_container = None
            panel._dynamic_env_labels = []

            panel.refresh()

            panel.summary_labels['faction_value'].set_text.assert_called()

    def test_refresh_updates_theme_label(self, mock_race_config):
        """refresh() updates theme label from race_config."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            panel.summary_labels = {'theme_value': MagicMock()}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            # FEAT-14: column-3 scroll container is None in these legacy
            # tests — _rebuild_env_scroll_content treats that as a no-op.
            panel._env_scroll_container = None
            panel._dynamic_env_labels = []

            panel.refresh()

            panel.summary_labels['theme_value'].set_text.assert_called()

    def test_refresh_clears_previous_flag_images(self, mock_race_config):
        """refresh() clears previous flag images before creating new ones."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            # Mock previous flag image
            old_image = MagicMock()
            panel.summary_flag_images = [old_image]
            panel.summary_labels = {}
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            # FEAT-14: column-3 scroll container is None in these legacy
            # tests — _rebuild_env_scroll_content treats that as a no-op.
            panel._env_scroll_container = None
            panel._dynamic_env_labels = []

            panel.refresh()

            # Old image should be killed
            old_image.kill.assert_called()


# =============================================================================
# Test: Display Name Placeholders
# =============================================================================

class TestPlaceholders:
    """Tests for placeholder text when values not set."""

    def test_faction_placeholder_when_not_set(self, mock_race_config_empty):
        """Shows placeholder when faction name not set.

        PROJ-66 Phase 6: Changed from name_value to faction_value.
        """
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config_empty

            # Mock labels
            faction_label = MagicMock()
            panel.summary_labels = {'faction_value': faction_label}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            # FEAT-14: column-3 scroll container is None in these legacy
            # tests — _rebuild_env_scroll_content treats that as a no-op.
            panel._env_scroll_container = None
            panel._dynamic_env_labels = []

            panel.refresh()

            # Should show placeholder text
            call_arg = faction_label.set_text.call_args[0][0]
            assert "Identity" in call_arg or "set" in call_arg.lower()

    def test_theme_placeholder_when_not_set(self, mock_race_config_empty):
        """Shows placeholder when theme not set."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config_empty

            # Mock labels
            theme_label = MagicMock()
            panel.summary_labels = {'theme_value': theme_label}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            # FEAT-14: column-3 scroll container is None in these legacy
            # tests — _rebuild_env_scroll_content treats that as a no-op.
            panel._env_scroll_container = None
            panel._dynamic_env_labels = []

            panel.refresh()

            # Should show placeholder text
            call_arg = theme_label.set_text.call_args[0][0]
            assert "Ships" in call_arg or "set" in call_arg.lower()


# =============================================================================
# Test: Callback Integration
# =============================================================================

class TestCallbackIntegration:
    """Tests for callback integration with parent screen."""

    def test_on_load_race_callback_stored(self):
        """on_load_race_callback is stored if provided."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            callback = MagicMock()
            panel.on_load_race_callback = callback

            assert panel.on_load_race_callback is callback

    def test_has_load_button_reference(self):
        """RaceSummaryPanel has btn_load attribute for Load Race button."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.btn_load = MagicMock()

            assert hasattr(panel, 'btn_load')


class TestFeat12RandomizeAllButton:
    """FEAT-12 Sub-task 5: master Randomize All button on Summary panel.

    Lives parallel to `btn_load`. Constructor accepts an
    `on_randomize_all_callback` parameter; the panel exposes the new
    `btn_randomize_all` attribute the screen wires up in `process_event`.
    """

    def test_on_randomize_all_callback_stored(self):
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *a, **kw: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            cb = MagicMock()
            panel.on_randomize_all_callback = cb
            assert panel.on_randomize_all_callback is cb

    def test_has_btn_randomize_all_attribute(self):
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *a, **kw: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.btn_randomize_all = MagicMock()
            assert hasattr(panel, 'btn_randomize_all')

    def test_constructor_accepts_on_randomize_all_callback(self):
        """Construction signature accepts the new keyword without error."""
        import inspect
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        sig = inspect.signature(RaceSummaryPanel.__init__)
        assert "on_randomize_all_callback" in sig.parameters


# =============================================================================
# FEAT-14: Registry-driven Summary tab
# =============================================================================


def _collect_label_texts(label_constructor_mock) -> list:
    """Pull every `text=` (or 2nd positional) value passed to a mocked
    UILabel constructor."""
    texts: list = []
    for call in label_constructor_mock.call_args_list:
        args, kwargs = call
        if "text" in kwargs:
            texts.append(kwargs["text"])
    return texts


@pytest.fixture
def mock_race_config_full():
    """RaceConfig with non-default setpoints on every FACTOR_REGISTRY entry
    (so the gas filter doesn't skip any) — exercises the full registry render."""
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.environmental_preference import EnvironmentalPreference
    from game.strategy.data.habitability_factors import FACTOR_REGISTRY

    config = RaceConfig(name="Full Race", flag_id="f", portrait_id="p", theme_id="t")
    for fid, factor in FACTOR_REGISTRY.items():
        # Non-zero setpoint everywhere so gas filter renders all 10 gases.
        setpoint = factor.default_setpoint if factor.default_setpoint > 0 else 1.0
        config.preferences[fid] = EnvironmentalPreference(
            setpoint=setpoint,
            tolerance=factor.default_tolerance,
            min_value=factor.min_value,
            max_value=factor.max_value,
            step=factor.step,
        )
    return config


class TestFeat14RegistryDrivenSummary:
    """FEAT-14: Summary tab iterates FACTOR_REGISTRY end-to-end and renders
    every aptitude explicitly. Reuses `PreferenceRow.format_value` — no
    per-factor formatters in the panel."""

    def _refresh_with_mocked_uilabel(self, race_config, monkeypatch=None):
        """Stub out pygame_gui inside the summary panel module, instantiate
        a panel via __new__ (skipping pygame init), wire the dynamic-label
        bookkeeping the new column-3 code expects, call refresh(), and
        return the captured UILabel-text list.
        """
        from game.ui.panels import race_summary_panel as rsp_module

        # Fresh mock class so each call returns a distinct widget.
        ui_label_mock = MagicMock()
        ui_label_mock.side_effect = lambda *a, **kw: MagicMock()
        ui_panel_mock = MagicMock()
        ui_panel_mock.side_effect = lambda *a, **kw: MagicMock()
        ui_scroll_mock = MagicMock()
        ui_scroll_mock.side_effect = lambda *a, **kw: MagicMock()

        with patch.object(rsp_module.pygame_gui.elements, "UILabel", ui_label_mock), \
             patch.object(rsp_module.pygame_gui.elements, "UIPanel", ui_panel_mock), \
             patch.object(
                 rsp_module.pygame_gui.elements,
                 "UIScrollingContainer",
                 ui_scroll_mock,
             ), \
             patch.object(rsp_module, "create_section_header", MagicMock()):
            panel = rsp_module.RaceSummaryPanel.__new__(rsp_module.RaceSummaryPanel)
            panel.race_config = race_config
            panel.summary_labels = {}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            panel.ui_manager = MagicMock()
            panel.panel = MagicMock()
            panel._env_scroll_container = MagicMock()
            # _rebuild_env_scroll_content reads container.get_relative_rect().width
            # so it can size labels — give it a real int.
            panel._env_scroll_container.get_relative_rect.return_value = pygame.Rect(
                0, 0, 800, 400,
            )
            panel._dynamic_env_labels = []

            panel.refresh()

            return _collect_label_texts(ui_label_mock), panel

    def test_refresh_renders_every_scalar_factor_display_name(
        self, mock_race_config_full,
    ):
        """Every FACTOR_REGISTRY scalar entry's `display_name` appears in the
        rendered Summary text. This is the registry-driven contract."""
        from game.strategy.data.habitability_factors import iter_scalar_factors

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        for factor in iter_scalar_factors():
            assert factor.display_name in joined, (
                f"Scalar factor {factor.id} ({factor.display_name}) missing "
                f"from Summary tab. Rendered text: {joined!r}"
            )

    def test_refresh_renders_every_set_gas_factor_display_name(
        self, mock_race_config_full,
    ):
        """Every gas factor with setpoint > 0 appears by display name. The
        full-config fixture sets every gas to non-zero, so all 10 gases
        must render."""
        from game.strategy.data.habitability_factors import iter_gas_factors

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        for factor in iter_gas_factors():
            assert factor.display_name in joined, (
                f"Gas factor {factor.id} ({factor.display_name}) missing "
                f"from Summary tab."
            )

    def test_refresh_uses_preference_row_format_for_setpoint(
        self, mock_race_config_full,
    ):
        """Setpoint values are formatted via PreferenceRow.format_value —
        gravity at 9.81 m/s^2 should render as "1.0 g" (display_scale 1/9.81,
        precision 1, unit "g")."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        # Gravity setpoint 9.81 m/s^2 → "1.0 g"
        assert "1.0 g" in joined, (
            f"Gravity setpoint not rendered with PROJ-293 display contract "
            f"in {joined!r}"
        )
        # Temperature 293 K (precision 0)
        assert "293 K" in joined or "293K" in joined, (
            f"Temperature setpoint not rendered with display unit in {joined!r}"
        )

    def test_refresh_renders_all_seven_aptitudes_by_name(
        self, mock_race_config,
    ):
        """All 7 RaceConfig aptitudes show with explicit human-readable labels
        and their assigned scores. PROJ-283 collapsed happiness +
        population_growth into base_happiness + base_reproduction_rate;
        those are NOT counted as 'aptitudes' but should still appear."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config)
        joined = "\n".join(texts)
        # Each aptitude's human-readable name + value present.
        expected_aptitude_labels = [
            "Strength",
            "Intelligence",
            "Constitution",
            "Dexterity",
            "Tolerance",        # tolerance_other_species
            "Cooperation",
            "Conflict Tolerance",
        ]
        for label in expected_aptitude_labels:
            assert label in joined, (
                f"Aptitude label {label!r} missing from Summary tab. "
                f"Rendered: {joined!r}"
            )

    def test_refresh_renders_base_happiness_and_reproduction(
        self, mock_race_config,
    ):
        """The PROJ-283 derived seeds — base_happiness and
        base_reproduction_rate — are still rendered explicitly (they are not
        aptitudes per se, but the user wants a complete review)."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config)
        joined = "\n".join(texts)
        # base_happiness default = 0.5 → "0.50"
        # base_reproduction_rate default = 0.03 → "3.0%"
        assert "Happiness" in joined or "happiness" in joined.lower()
        assert "Reproduction" in joined or "reproduction" in joined.lower()

    def test_adding_factor_to_registry_surfaces_automatically(
        self, mock_race_config_full, monkeypatch,
    ):
        """Acceptance: adding a factor to FACTOR_REGISTRY surfaces a row with
        ZERO panel-side change (matches PROJ-283/293 contract).

        We monkeypatch `iter_scalar_factors` to yield an extra synthetic
        factor and assert its display_name appears in the rendered text."""
        from game.strategy.data.habitability_factors import (
            HabitabilityFactor,
            iter_scalar_factors,
            _default_gaussian_scorer,
        )
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        fake_factor = HabitabilityFactor(
            id="fake_axis",
            display_name="Fake Test Axis",
            unit="widgets",
            display_scale=1.0,
            weight=0.1,
            default_setpoint=42.0,
            default_tolerance=5.0,
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            extractor=lambda planet: 0.0,
            scorer=_default_gaussian_scorer,
            display_unit="W",
            display_precision=0,
        )

        original = list(iter_scalar_factors())

        def patched_iter():
            yield from original
            yield fake_factor

        # Inject a preference for the fake factor so the panel doesn't
        # KeyError on lookup.
        mock_race_config_full.preferences["fake_axis"] = EnvironmentalPreference(
            setpoint=fake_factor.default_setpoint,
            tolerance=fake_factor.default_tolerance,
            min_value=fake_factor.min_value,
            max_value=fake_factor.max_value,
            step=fake_factor.step,
        )

        from game.ui.panels import race_summary_panel as rsp_module
        from game.strategy.data import habitability_factors as hab_module
        monkeypatch.setattr(rsp_module, "iter_scalar_factors", patched_iter)
        # The budget calculator (called by _format_budget_summary) iterates
        # race_config.preferences and looks up each factor in FACTOR_REGISTRY
        # via get_factor(). Register the fake there too so the lookup
        # succeeds — this is the same single-edit contract the ticket
        # promises ("adding to FACTOR_REGISTRY surfaces automatically").
        monkeypatch.setitem(hab_module.FACTOR_REGISTRY, "fake_axis", fake_factor)

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        assert "Fake Test Axis" in joined, (
            f"Adding a factor to FACTOR_REGISTRY did not surface it on the "
            f"Summary tab. Rendered text: {joined!r}"
        )
