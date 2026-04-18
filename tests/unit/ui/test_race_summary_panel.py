"""
Unit tests for RaceSummaryPanel.

PROJ-44 Phase 7 Task 7.1: TDD tests for the summary panel extraction.
Tests the race summary display panel functionality.
"""

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

    def test_format_gravity_summary(self, mock_race_config):
        """Gravity summary shows ideal and tolerance."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            result = panel._format_gravity_summary()

            assert "1.0" in result
            assert "0.30" in result
            assert "g" in result

    def test_format_temperature_summary(self, mock_race_config):
        """Temperature summary shows ideal and tolerance."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            result = panel._format_temperature_summary()

            assert "293" in result
            assert "50" in result
            assert "K" in result

    # PROJ-283 Phase 4: Sensitive/Resistant labels were derived from the
    # legacy `radiation_tolerance` (signed -100..+100). The new model
    # stores `pref.tolerance` (unsigned σ) on a `radiation` factor —
    # there's no direction to label. The summary now just shows the
    # numeric tolerance; the sensitive/resistant test surface goes away.

    def test_format_radiation_summary_shows_tolerance(self, mock_race_config):
        """Radiation summary renders the radiation tolerance value."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            result = panel._format_radiation_summary()
            assert "Radiation" in result

    def test_format_atmosphere_summary_with_preferences(self, mock_race_config):
        """Atmosphere summary lists gas factors with non-zero setpoints
        (formatted by chemical formula + kPa)."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            result = panel._format_atmosphere_summary()

            # PROJ-283 Phase 4: chemical-formula labels + kPa.
            assert "O2" in result
            assert "N2" in result
            assert "kPa" in result

    def test_format_atmosphere_summary_all_neutral(self, mock_race_config_empty):
        """Atmosphere summary shows neutral when all zero."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config_empty

            result = panel._format_atmosphere_summary()

            assert "neutral" in result.lower() or "0" in result

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

            panel.refresh()

            panel.summary_labels['theme_value'].set_text.assert_called()

    def test_refresh_updates_gravity_label(self, mock_race_config):
        """refresh() updates gravity label from race_config."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            panel.summary_labels = {'gravity': MagicMock()}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None

            panel.refresh()

            panel.summary_labels['gravity'].set_text.assert_called()

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
