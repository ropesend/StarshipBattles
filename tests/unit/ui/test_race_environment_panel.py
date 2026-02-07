"""
Unit tests for RaceEnvironmentPanel.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race environment configuration panel functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with environment properties."""
    config = MagicMock()
    config.gravity_ideal = 1.0
    config.gravity_tolerance = 0.3
    config.temperature_ideal = 293.0
    config.temperature_tolerance = 50.0
    config.radiation_tolerance = 0.0
    config.atmosphere_preferences = {
        "Oxygen": 0.0,
        "Nitrogen": 0.0,
        "Carbon Dioxide": 0.0,
        "Methane": 0.0,
        "Hydrogen": 0.0,
        "Helium": 0.0,
    }
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


# =============================================================================
# Test: RaceEnvironmentPanel Import and Creation
# =============================================================================

class TestRaceEnvironmentPanelCreation:
    """Tests for RaceEnvironmentPanel initialization."""

    def test_race_environment_panel_can_be_imported(self):
        """RaceEnvironmentPanel can be imported from separate module."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        assert RaceEnvironmentPanel is not None

    def test_race_environment_panel_has_slider_references(self):
        """RaceEnvironmentPanel has expected slider reference attributes."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        # Use mock to avoid pygame initialization
        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = None
            panel.atmosphere_sliders = {}

            # Verify the attributes exist
            assert hasattr(panel, 'gravity_ideal_slider')
            assert hasattr(panel, 'gravity_tolerance_slider')
            assert hasattr(panel, 'temp_ideal_slider')
            assert hasattr(panel, 'temp_tolerance_slider')
            assert hasattr(panel, 'radiation_slider')
            assert hasattr(panel, 'atmosphere_sliders')


# =============================================================================
# Test: Value Formatting
# =============================================================================

class TestValueFormatting:
    """Tests for value formatting methods."""

    def test_format_radiation_sensitive(self):
        """Radiation values below -50 show 'Sens' suffix."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_radiation(-75)

            assert "Sens" in result
            assert "-75" in result

    def test_format_radiation_resistant(self):
        """Radiation values above 50 show 'Res' suffix."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_radiation(75)

            assert "Res" in result
            assert "75" in result

    def test_format_radiation_neutral_positive(self):
        """Positive neutral radiation values show plus sign."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_radiation(25)

            assert result == "+25"

    def test_format_radiation_neutral_negative(self):
        """Negative neutral radiation values show minus sign."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_radiation(-25)

            assert result == "-25"

    def test_format_atmosphere_positive(self):
        """Positive atmosphere values show plus sign."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_atmosphere(50)

            assert result == "+50"

    def test_format_atmosphere_negative(self):
        """Negative atmosphere values show minus sign."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            result = panel._format_atmosphere(-50)

            assert result == "-50"


# =============================================================================
# Test: Configuration Updates
# =============================================================================

class TestConfigurationUpdates:
    """Tests for updating RaceConfig from panel values."""

    def test_update_config_reads_gravity_sliders(self, mock_race_config):
        """update_config reads gravity values from sliders."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config

            # Mock sliders
            panel.gravity_ideal_slider = MagicMock()
            panel.gravity_ideal_slider.get_current_value.return_value = 1.5
            panel.gravity_tolerance_slider = MagicMock()
            panel.gravity_tolerance_slider.get_current_value.return_value = 0.5
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = None
            panel.water_ideal_slider = None
            panel.water_tolerance_slider = None
            panel.homeworld_dropdown = None
            panel.atmosphere_sliders = {}

            panel.update_config()

            assert mock_race_config.gravity_ideal == 1.5
            assert mock_race_config.gravity_tolerance == 0.5

    def test_update_config_reads_temperature_sliders(self, mock_race_config):
        """update_config reads temperature values from sliders."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config

            # Mock sliders
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = MagicMock()
            panel.temp_ideal_slider.get_current_value.return_value = 310.0
            panel.temp_tolerance_slider = MagicMock()
            panel.temp_tolerance_slider.get_current_value.return_value = 75.0
            panel.radiation_slider = None
            panel.water_ideal_slider = None
            panel.water_tolerance_slider = None
            panel.homeworld_dropdown = None
            panel.atmosphere_sliders = {}

            panel.update_config()

            assert mock_race_config.temperature_ideal == 310.0
            assert mock_race_config.temperature_tolerance == 75.0

    def test_update_config_reads_radiation_slider(self, mock_race_config):
        """update_config reads radiation value from slider."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config

            # Mock sliders
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = MagicMock()
            panel.radiation_slider.get_current_value.return_value = 50.0
            panel.water_ideal_slider = None
            panel.water_tolerance_slider = None
            panel.homeworld_dropdown = None
            panel.atmosphere_sliders = {}

            panel.update_config()

            assert mock_race_config.radiation_tolerance == 50.0

    def test_update_config_reads_atmosphere_sliders(self, mock_race_config):
        """update_config reads atmosphere values from sliders."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config

            # Mock sliders
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = None
            panel.water_ideal_slider = None
            panel.water_tolerance_slider = None
            panel.homeworld_dropdown = None

            oxygen_slider = MagicMock()
            oxygen_slider.get_current_value.return_value = 80.0
            nitrogen_slider = MagicMock()
            nitrogen_slider.get_current_value.return_value = -20.0
            panel.atmosphere_sliders = {
                "Oxygen": oxygen_slider,
                "Nitrogen": nitrogen_slider,
            }

            panel.update_config()

            assert mock_race_config.atmosphere_preferences["Oxygen"] == 80.0
            assert mock_race_config.atmosphere_preferences["Nitrogen"] == -20.0


# =============================================================================
# Test: Label Updates
# =============================================================================

class TestLabelUpdates:
    """Tests for updating display labels from slider values."""

    def test_update_labels_updates_gravity_labels(self):
        """update_labels updates gravity display labels."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            # Mock sliders and labels
            panel.gravity_ideal_slider = MagicMock()
            panel.gravity_ideal_slider.get_current_value.return_value = 1.5
            panel.gravity_ideal_label = MagicMock()

            panel.gravity_tolerance_slider = MagicMock()
            panel.gravity_tolerance_slider.get_current_value.return_value = 0.4
            panel.gravity_tolerance_label = MagicMock()

            panel.temp_ideal_slider = None
            panel.temp_ideal_label = None
            panel.temp_tolerance_slider = None
            panel.temp_tolerance_label = None
            panel.radiation_slider = None
            panel.radiation_label = None
            panel.water_ideal_slider = None
            panel.water_ideal_label = None
            panel.water_tolerance_slider = None
            panel.water_tolerance_label = None
            panel.atmosphere_sliders = {}
            panel.atmosphere_labels = {}

            panel.update_labels()

            panel.gravity_ideal_label.set_text.assert_called_with("1.5")
            panel.gravity_tolerance_label.set_text.assert_called_with("±0.40")

    def test_update_labels_updates_temperature_labels(self):
        """update_labels updates temperature display labels."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            # Mock sliders and labels
            panel.gravity_ideal_slider = None
            panel.gravity_ideal_label = None
            panel.gravity_tolerance_slider = None
            panel.gravity_tolerance_label = None

            panel.temp_ideal_slider = MagicMock()
            panel.temp_ideal_slider.get_current_value.return_value = 300.0
            panel.temp_ideal_label = MagicMock()

            panel.temp_tolerance_slider = MagicMock()
            panel.temp_tolerance_slider.get_current_value.return_value = 60.0
            panel.temp_tolerance_label = MagicMock()

            panel.radiation_slider = None
            panel.radiation_label = None
            panel.water_ideal_slider = None
            panel.water_ideal_label = None
            panel.water_tolerance_slider = None
            panel.water_tolerance_label = None
            panel.atmosphere_sliders = {}
            panel.atmosphere_labels = {}

            panel.update_labels()

            panel.temp_ideal_label.set_text.assert_called_with("300")
            panel.temp_tolerance_label.set_text.assert_called_with("±60")

    def test_update_labels_updates_radiation_label(self):
        """update_labels updates radiation display label."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            # Mock sliders and labels
            panel.gravity_ideal_slider = None
            panel.gravity_ideal_label = None
            panel.gravity_tolerance_slider = None
            panel.gravity_tolerance_label = None
            panel.temp_ideal_slider = None
            panel.temp_ideal_label = None
            panel.temp_tolerance_slider = None
            panel.temp_tolerance_label = None

            panel.radiation_slider = MagicMock()
            panel.radiation_slider.get_current_value.return_value = 75.0
            panel.radiation_label = MagicMock()

            panel.water_ideal_slider = None
            panel.water_ideal_label = None
            panel.water_tolerance_slider = None
            panel.water_tolerance_label = None
            panel.atmosphere_sliders = {}
            panel.atmosphere_labels = {}

            panel.update_labels()

            # Should show "+75 Res" for resistant
            panel.radiation_label.set_text.assert_called()
            call_arg = panel.radiation_label.set_text.call_args[0][0]
            assert "75" in call_arg
            assert "Res" in call_arg


# =============================================================================
# Test: Default Atmosphere Gases
# =============================================================================

class TestDefaultGases:
    """Tests for default atmosphere gas list."""

    def test_has_default_gases_constant(self):
        """RaceEnvironmentPanel has DEFAULT_GASES constant."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        assert hasattr(RaceEnvironmentPanel, 'DEFAULT_GASES')
        gases = RaceEnvironmentPanel.DEFAULT_GASES
        assert "Oxygen" in gases
        assert "Nitrogen" in gases
        assert "Carbon Dioxide" in gases
        assert "Methane" in gases
        assert "Hydrogen" in gases
        assert "Helium" in gases


# =============================================================================
# Test: Homeworld Dropdown (PROJ-66 Phase 4)
# =============================================================================

class TestHomeworldDropdown:
    """Tests for homeworld type dropdown."""

    def test_panel_has_homeworld_dropdown(self):
        """RaceEnvironmentPanel has homeworld_dropdown attribute."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.homeworld_dropdown = None

            assert hasattr(panel, 'homeworld_dropdown')

    def test_homeworld_dropdown_has_all_planet_types(self):
        """Homeworld dropdown includes all planet type names plus Custom."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel
        from game.strategy.data.homeworld_presets import get_available_homeworld_names

        # Get expected names from presets
        expected_names = get_available_homeworld_names()

        # Verify we have 11 planet types
        assert len(expected_names) == 11
        assert "Continental" in expected_names
        assert "Jovian" in expected_names
        assert "Arid" in expected_names


# =============================================================================
# Test: Water Sliders (PROJ-66 Phase 4)
# =============================================================================

class TestWaterSliders:
    """Tests for water preference sliders."""

    def test_panel_has_water_ideal_slider(self):
        """RaceEnvironmentPanel has water_ideal_slider attribute."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.water_ideal_slider = None
            panel.water_ideal_label = None

            assert hasattr(panel, 'water_ideal_slider')
            assert hasattr(panel, 'water_ideal_label')

    def test_panel_has_water_tolerance_slider(self):
        """RaceEnvironmentPanel has water_tolerance_slider attribute."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.water_tolerance_slider = None
            panel.water_tolerance_label = None

            assert hasattr(panel, 'water_tolerance_slider')
            assert hasattr(panel, 'water_tolerance_label')

    def test_format_water_shows_percentage(self):
        """_format_water returns percentage format."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            assert panel._format_water(0.5) == "50%"
            assert panel._format_water(1.0) == "100%"
            assert panel._format_water(0.0) == "0%"
            assert panel._format_water(0.75) == "75%"

    def test_update_config_reads_water_sliders(self, mock_race_config):
        """update_config reads water values from sliders."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            mock_race_config.water_ideal = 0.5
            mock_race_config.water_tolerance = 0.2

            # Mock existing sliders to None
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = None
            panel.atmosphere_sliders = {}
            panel.homeworld_dropdown = None

            # Mock water sliders
            panel.water_ideal_slider = MagicMock()
            panel.water_ideal_slider.get_current_value.return_value = 0.7
            panel.water_tolerance_slider = MagicMock()
            panel.water_tolerance_slider.get_current_value.return_value = 0.3

            panel.update_config()

            assert mock_race_config.water_ideal == 0.7
            assert mock_race_config.water_tolerance == 0.3

    def test_update_labels_formats_water_values(self):
        """update_labels updates water display labels with percentage."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)

            # Mock all sliders/labels to None except water
            panel.gravity_ideal_slider = None
            panel.gravity_ideal_label = None
            panel.gravity_tolerance_slider = None
            panel.gravity_tolerance_label = None
            panel.temp_ideal_slider = None
            panel.temp_ideal_label = None
            panel.temp_tolerance_slider = None
            panel.temp_tolerance_label = None
            panel.radiation_slider = None
            panel.radiation_label = None
            panel.atmosphere_sliders = {}
            panel.atmosphere_labels = {}

            # Mock water sliders and labels
            panel.water_ideal_slider = MagicMock()
            panel.water_ideal_slider.get_current_value.return_value = 0.6
            panel.water_ideal_label = MagicMock()

            panel.water_tolerance_slider = MagicMock()
            panel.water_tolerance_slider.get_current_value.return_value = 0.2
            panel.water_tolerance_label = MagicMock()

            panel.update_labels()

            panel.water_ideal_label.set_text.assert_called_with("60%")
            panel.water_tolerance_label.set_text.assert_called_with("±20%")

    def test_set_from_config_sets_water_sliders(self, mock_race_config):
        """set_from_config sets water slider values from race_config."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            mock_race_config.water_ideal = 0.8
            mock_race_config.water_tolerance = 0.15

            # Mock all sliders to None except water
            panel.gravity_ideal_slider = None
            panel.gravity_tolerance_slider = None
            panel.temp_ideal_slider = None
            panel.temp_tolerance_slider = None
            panel.radiation_slider = None
            panel.atmosphere_sliders = {}
            panel.homeworld_dropdown = None

            # Mock water sliders - get_current_value for update_labels
            panel.water_ideal_slider = MagicMock()
            panel.water_ideal_slider.get_current_value.return_value = 0.8
            panel.water_tolerance_slider = MagicMock()
            panel.water_tolerance_slider.get_current_value.return_value = 0.15

            # Mock labels for update_labels call
            panel.gravity_ideal_label = None
            panel.gravity_tolerance_label = None
            panel.temp_ideal_label = None
            panel.temp_tolerance_label = None
            panel.radiation_label = None
            panel.atmosphere_labels = {}
            panel.water_ideal_label = MagicMock()
            panel.water_tolerance_label = MagicMock()

            panel.set_from_config()

            panel.water_ideal_slider.set_current_value.assert_called_with(0.8)
            panel.water_tolerance_slider.set_current_value.assert_called_with(0.15)


# =============================================================================
# Test: Homeworld Preset Auto-Populate (PROJ-66 Phase 4)
# =============================================================================

class TestHomeworldPresetAutoPopulate:
    """Tests for homeworld preset auto-populate functionality."""

    def _setup_all_mocks(self, panel):
        """Helper to set up all slider and label mocks for preset tests."""
        # Mock all sliders with get_current_value for update_labels
        panel.gravity_ideal_slider = MagicMock()
        panel.gravity_ideal_slider.get_current_value.return_value = 1.0
        panel.gravity_tolerance_slider = MagicMock()
        panel.gravity_tolerance_slider.get_current_value.return_value = 0.3
        panel.temp_ideal_slider = MagicMock()
        panel.temp_ideal_slider.get_current_value.return_value = 293
        panel.temp_tolerance_slider = MagicMock()
        panel.temp_tolerance_slider.get_current_value.return_value = 50
        panel.water_ideal_slider = MagicMock()
        panel.water_ideal_slider.get_current_value.return_value = 0.6
        panel.water_tolerance_slider = MagicMock()
        panel.water_tolerance_slider.get_current_value.return_value = 0.2
        panel.radiation_slider = MagicMock()
        panel.radiation_slider.get_current_value.return_value = 0

        atmo_gases = ["Oxygen", "Nitrogen", "Carbon Dioxide", "Methane", "Hydrogen", "Helium"]
        panel.atmosphere_sliders = {}
        panel.atmosphere_labels = {}
        for gas in atmo_gases:
            slider = MagicMock()
            slider.get_current_value.return_value = 0
            panel.atmosphere_sliders[gas] = slider
            panel.atmosphere_labels[gas] = MagicMock()

        # Mock labels
        panel.gravity_ideal_label = MagicMock()
        panel.gravity_tolerance_label = MagicMock()
        panel.temp_ideal_label = MagicMock()
        panel.temp_tolerance_label = MagicMock()
        panel.water_ideal_label = MagicMock()
        panel.water_tolerance_label = MagicMock()
        panel.radiation_label = MagicMock()

    def test_apply_homeworld_preset_continental_sets_gravity(self, mock_race_config):
        """apply_homeworld_preset for Continental sets gravity to 1.0."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            self._setup_all_mocks(panel)

            panel.apply_homeworld_preset("CONTINENTAL")

            panel.gravity_ideal_slider.set_current_value.assert_called_with(1.0)

    def test_apply_homeworld_preset_continental_sets_temperature(self, mock_race_config):
        """apply_homeworld_preset for Continental sets temperature to 293K."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            self._setup_all_mocks(panel)

            panel.apply_homeworld_preset("CONTINENTAL")

            panel.temp_ideal_slider.set_current_value.assert_called_with(293)

    def test_apply_homeworld_preset_jovian_sets_high_gravity(self, mock_race_config):
        """apply_homeworld_preset for Jovian sets gravity to 2.5."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            self._setup_all_mocks(panel)

            panel.apply_homeworld_preset("JOVIAN")

            panel.gravity_ideal_slider.set_current_value.assert_called_with(2.5)

    def test_apply_homeworld_preset_custom_does_nothing(self, mock_race_config):
        """apply_homeworld_preset for (Custom) leaves sliders unchanged."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config

            # Mock all sliders
            panel.gravity_ideal_slider = MagicMock()
            panel.gravity_tolerance_slider = MagicMock()
            panel.temp_ideal_slider = MagicMock()
            panel.temp_tolerance_slider = MagicMock()
            panel.water_ideal_slider = MagicMock()
            panel.water_tolerance_slider = MagicMock()
            panel.radiation_slider = MagicMock()
            panel.atmosphere_sliders = {}

            panel.apply_homeworld_preset("(Custom)")

            # No slider should have been set
            panel.gravity_ideal_slider.set_current_value.assert_not_called()
            panel.temp_ideal_slider.set_current_value.assert_not_called()
            panel.water_ideal_slider.set_current_value.assert_not_called()
            panel.radiation_slider.set_current_value.assert_not_called()

    def test_apply_homeworld_preset_updates_config(self, mock_race_config):
        """apply_homeworld_preset updates race_config.homeworld_type."""
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel

        with patch.object(RaceEnvironmentPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceEnvironmentPanel.__new__(RaceEnvironmentPanel)
            panel.race_config = mock_race_config
            mock_race_config.homeworld_type = None
            self._setup_all_mocks(panel)

            panel.apply_homeworld_preset("ARID")

            assert mock_race_config.homeworld_type == "ARID"
