"""
Unit tests for RaceDescriptionPanel.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race description panel functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with description properties."""
    config = MagicMock()
    config.bio_description = "Test biological description"
    config.socio_description = "Test sociological description"
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


# =============================================================================
# Test: RaceDescriptionPanel Import and Creation
# =============================================================================

class TestRaceDescriptionPanelCreation:
    """Tests for RaceDescriptionPanel initialization."""

    def test_race_description_panel_has_text_box_references(self):
        """RaceDescriptionPanel has expected text box reference attributes."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.bio_text_box = None
            panel.bio_char_label = None
            panel.socio_text_box = None
            panel.socio_char_label = None

            assert hasattr(panel, 'bio_text_box')
            assert hasattr(panel, 'bio_char_label')
            assert hasattr(panel, 'socio_text_box')
            assert hasattr(panel, 'socio_char_label')

    def test_race_description_panel_has_max_length_constant(self):
        """RaceDescriptionPanel has MAX_LENGTH constant."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        assert hasattr(RaceDescriptionPanel, 'MAX_LENGTH')
        assert RaceDescriptionPanel.MAX_LENGTH == 500


# =============================================================================
# Test: Character Count Updates
# =============================================================================

class TestCharacterCountUpdates:
    """Tests for character count label updates."""

    def test_update_char_counts_updates_bio_label(self):
        """update_char_counts updates biological description character count."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)

            panel.bio_text_box = MagicMock()
            panel.bio_text_box.get_text.return_value = "Test text"  # 9 chars
            panel.bio_char_label = MagicMock()

            panel.socio_text_box = None
            panel.socio_char_label = None

            panel.update_char_counts()

            panel.bio_char_label.set_text.assert_called_with("9/500")

    def test_update_char_counts_updates_socio_label(self):
        """update_char_counts updates sociological description character count."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)

            panel.bio_text_box = None
            panel.bio_char_label = None

            panel.socio_text_box = MagicMock()
            panel.socio_text_box.get_text.return_value = "A longer test text"  # 18 chars
            panel.socio_char_label = MagicMock()

            panel.update_char_counts()

            panel.socio_char_label.set_text.assert_called_with("18/500")

    def test_update_char_counts_handles_empty_text(self):
        """update_char_counts handles empty text correctly."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)

            panel.bio_text_box = MagicMock()
            panel.bio_text_box.get_text.return_value = ""
            panel.bio_char_label = MagicMock()

            panel.socio_text_box = MagicMock()
            panel.socio_text_box.get_text.return_value = ""
            panel.socio_char_label = MagicMock()

            panel.update_char_counts()

            panel.bio_char_label.set_text.assert_called_with("0/500")
            panel.socio_char_label.set_text.assert_called_with("0/500")


# =============================================================================
# Test: Configuration Updates
# =============================================================================

class TestConfigurationUpdates:
    """Tests for updating RaceConfig from panel values."""

    def test_update_config_reads_bio_text_box(self, mock_race_config):
        """update_config reads biological description from text box."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config

            panel.bio_text_box = MagicMock()
            panel.bio_text_box.get_text.return_value = "New bio description"
            panel.socio_text_box = None

            panel.update_config()

            assert mock_race_config.bio_description == "New bio description"

    def test_update_config_reads_socio_text_box(self, mock_race_config):
        """update_config reads sociological description from text box."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config

            panel.bio_text_box = None
            panel.socio_text_box = MagicMock()
            panel.socio_text_box.get_text.return_value = "New socio description"

            panel.update_config()

            assert mock_race_config.socio_description == "New socio description"

    def test_update_config_enforces_max_length(self, mock_race_config):
        """update_config enforces 500 character limit."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config

            # Create text longer than 500 chars
            long_text = "A" * 600

            panel.bio_text_box = MagicMock()
            panel.bio_text_box.get_text.return_value = long_text
            panel.socio_text_box = MagicMock()
            panel.socio_text_box.get_text.return_value = long_text

            panel.update_config()

            assert len(mock_race_config.bio_description) == 500
            assert len(mock_race_config.socio_description) == 500


# =============================================================================
# Test: Loading from Config
# =============================================================================

class TestLoadingFromConfig:
    """Tests for setting panel values from RaceConfig."""

    def test_set_from_config_updates_bio_text_box(self, mock_race_config):
        """set_from_config updates biological text box from config."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config
            mock_race_config.bio_description = "Loaded bio text"

            panel.bio_text_box = MagicMock()
            panel.bio_char_label = MagicMock()
            panel.socio_text_box = None
            panel.socio_char_label = None

            panel.set_from_config()

            panel.bio_text_box.set_text.assert_called_with("Loaded bio text")

    def test_set_from_config_updates_socio_text_box(self, mock_race_config):
        """set_from_config updates sociological text box from config."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config
            mock_race_config.socio_description = "Loaded socio text"

            panel.bio_text_box = None
            panel.bio_char_label = None
            panel.socio_text_box = MagicMock()
            panel.socio_char_label = MagicMock()

            panel.set_from_config()

            panel.socio_text_box.set_text.assert_called_with("Loaded socio text")

    def test_set_from_config_handles_empty_descriptions(self, mock_race_config):
        """set_from_config handles empty/None descriptions."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config
            mock_race_config.bio_description = ""
            mock_race_config.socio_description = None

            panel.bio_text_box = MagicMock()
            panel.bio_char_label = MagicMock()
            panel.socio_text_box = MagicMock()
            panel.socio_char_label = MagicMock()

            panel.set_from_config()

            panel.bio_text_box.set_text.assert_called_with("")
            panel.socio_text_box.set_text.assert_called_with("")

    def test_set_from_config_updates_char_counts(self, mock_race_config):
        """set_from_config calls update_char_counts after setting text."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        with patch.object(RaceDescriptionPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceDescriptionPanel.__new__(RaceDescriptionPanel)
            panel.race_config = mock_race_config

            panel.bio_text_box = MagicMock()
            panel.bio_text_box.get_text.return_value = "test"
            panel.bio_char_label = MagicMock()
            panel.socio_text_box = MagicMock()
            panel.socio_text_box.get_text.return_value = "test"
            panel.socio_char_label = MagicMock()

            panel.set_from_config()

            # Should update char counts after setting text
            panel.bio_char_label.set_text.assert_called()
            panel.socio_char_label.set_text.assert_called()
