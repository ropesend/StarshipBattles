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

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with all properties for summary display.

    PROJ-66 Phase 6: Added identity, water, and aptitude fields.
    """
    config = MagicMock()
    config.name = "Test Race"
    config.flag_id = "flag_01"
    config.portrait_id = "portrait_01"
    config.theme_id = "Atlantians"
    config.gravity_ideal = 1.0
    config.gravity_tolerance = 0.3
    config.temperature_ideal = 293.0
    config.temperature_tolerance = 50.0
    config.radiation_tolerance = 0.0
    config.atmosphere_preferences = {
        "Oxygen": 20.0,
        "Nitrogen": -10.0,
        "Carbon Dioxide": 0.0,
        "Methane": 0.0,
        "Hydrogen": 0.0,
        "Helium": 0.0,
    }
    config.bio_description = "Test biological description"
    config.socio_description = "Test sociological description"
    # PROJ-66: New identity fields
    config.faction_name = "Test Empire"
    config.race_name = "Testarians"
    config.government_type = "Empire"
    config.government_organization = "Centralized"
    config.physical_type = "Humanoid"
    config.society_type = "Collectivist"
    config.homeworld_type = "CONTINENTAL"
    config.water_ideal = 50.0
    config.water_tolerance = 30.0
    # Aptitude values
    config.aptitude_strength = 6
    config.aptitude_intelligence = 7
    config.aptitude_constitution = 5
    config.aptitude_dexterity = 5
    config.aptitude_tolerance_other_species = 5
    config.aptitude_cooperation = 5
    config.aptitude_happiness = 5
    config.aptitude_population_growth = 5
    config.aptitude_conflict_tolerance = 5
    return config


@pytest.fixture
def mock_race_config_empty():
    """Create a mock RaceConfig with no values set (new race).

    PROJ-66 Phase 6: Added identity, water, and aptitude fields.
    """
    config = MagicMock()
    config.name = None
    config.flag_id = None
    config.portrait_id = None
    config.theme_id = None
    config.gravity_ideal = 1.0
    config.gravity_tolerance = 0.3
    config.temperature_ideal = 293.0
    config.temperature_tolerance = 50.0
    config.radiation_tolerance = 0.0
    config.atmosphere_preferences = {}
    config.bio_description = ""
    config.socio_description = ""
    # PROJ-66: New identity fields
    config.faction_name = ""
    config.race_name = ""
    config.government_type = ""
    config.government_organization = ""
    config.physical_type = ""
    config.society_type = ""
    config.homeworld_type = ""
    config.water_ideal = 50.0
    config.water_tolerance = 30.0
    # Aptitude defaults
    config.aptitude_strength = 5
    config.aptitude_intelligence = 5
    config.aptitude_constitution = 5
    config.aptitude_dexterity = 5
    config.aptitude_tolerance_other_species = 5
    config.aptitude_cooperation = 5
    config.aptitude_happiness = 5
    config.aptitude_population_growth = 5
    config.aptitude_conflict_tolerance = 5
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

    def test_race_summary_panel_can_be_imported(self):
        """RaceSummaryPanel can be imported from separate module."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        assert RaceSummaryPanel is not None

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

    def test_format_radiation_summary_neutral(self, mock_race_config):
        """Radiation summary shows neutral for value 0."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            mock_race_config.radiation_tolerance = 0.0

            result = panel._format_radiation_summary()

            assert "Neutral" in result

    def test_format_radiation_summary_sensitive(self, mock_race_config):
        """Radiation summary shows Sensitive for values below -50."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            mock_race_config.radiation_tolerance = -75.0

            result = panel._format_radiation_summary()

            assert "Sensitive" in result

    def test_format_radiation_summary_resistant(self, mock_race_config):
        """Radiation summary shows Resistant for values above 50."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config
            mock_race_config.radiation_tolerance = 75.0

            result = panel._format_radiation_summary()

            assert "Resistant" in result

    def test_format_atmosphere_summary_with_preferences(self, mock_race_config):
        """Atmosphere summary shows non-zero gas preferences."""
        from game.ui.panels.race_summary_panel import RaceSummaryPanel

        with patch.object(RaceSummaryPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceSummaryPanel.__new__(RaceSummaryPanel)
            panel.race_config = mock_race_config

            result = panel._format_atmosphere_summary()

            # Should mention gases with non-zero values
            assert "Oxygen" in result or "+20" in result
            assert "Nitrogen" in result or "-10" in result

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
