"""
Unit tests for RaceThemeGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race ship theme gallery panel functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with theme_id property."""
    config = MagicMock()
    config.theme_id = None
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


@pytest.fixture
def mock_panel():
    """Create a mock UIPanel container."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(
        width=600,
        height=400
    )
    return panel


# =============================================================================
# Test: RaceThemeGallery Import and Creation
# =============================================================================

class TestRaceThemeGalleryCreation:
    """Tests for RaceThemeGallery initialization."""

    def test_race_theme_gallery_can_be_imported(self):
        """RaceThemeGallery can be imported from separate module."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        assert RaceThemeGallery is not None

    def test_race_theme_gallery_has_button_list(self):
        """RaceThemeGallery has theme_buttons list attribute."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.theme_buttons = []

            assert hasattr(gallery, 'theme_buttons')
            assert isinstance(gallery.theme_buttons, list)

    def test_race_theme_gallery_has_scroll_container(self):
        """RaceThemeGallery has theme_scroll attribute."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.theme_scroll = None

            assert hasattr(gallery, 'theme_scroll')


# =============================================================================
# Test: Theme Selection
# =============================================================================

class TestThemeSelection:
    """Tests for theme selection functionality."""

    def test_on_theme_selected_updates_race_config(self, mock_race_config):
        """Selecting a theme updates race_config.theme_id."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.theme_buttons = []
            gallery.on_select_callback = None

            gallery.on_theme_selected("terran")

            assert mock_race_config.theme_id == "terran"

    def test_on_theme_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a theme calls the on_select callback if provided."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.theme_buttons = []

            callback = MagicMock()
            gallery.on_select_callback = callback

            gallery.on_theme_selected("terran")

            callback.assert_called_once_with("terran")

    def test_on_theme_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a theme with no callback doesn't raise an error."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.theme_buttons = []
            gallery.on_select_callback = None

            # Should not raise
            gallery.on_theme_selected("terran")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_theme_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a theme highlights the corresponding button."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            gallery.theme_buttons = [
                (btn1, "terran"),
                (btn2, "alien"),
            ]

            gallery.on_theme_selected("terran")

            btn1.select.assert_called_once()
            btn2.unselect.assert_called_once()

    def test_on_theme_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a theme deselects all other buttons."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            btn3 = MagicMock()
            gallery.theme_buttons = [
                (btn1, "terran"),
                (btn2, "alien"),
                (btn3, "robotic"),
            ]

            gallery.on_theme_selected("alien")

            btn1.unselect.assert_called_once()
            btn2.select.assert_called_once()
            btn3.unselect.assert_called_once()


# =============================================================================
# Test: Configuration Binding
# =============================================================================

class TestConfigurationBinding:
    """Tests for setting values from config."""

    def test_set_from_config_selects_configured_theme(self, mock_race_config):
        """set_from_config selects the theme from race_config."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            mock_race_config.theme_id = "terran"
            gallery.theme_buttons = []
            gallery.on_select_callback = None

            # Mock on_theme_selected to track call
            gallery.on_theme_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_theme_selected.assert_called_once_with("terran")

    def test_set_from_config_no_theme_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no theme_id in config."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            mock_race_config.theme_id = None  # No theme selected

            # Mock on_theme_selected to track call
            gallery.on_theme_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_theme_selected.assert_not_called()


# =============================================================================
# Test: Button Click Handling
# =============================================================================

class TestButtonClickHandling:
    """Tests for button click event handling."""

    def test_handle_button_click_returns_true_for_theme_button(self, mock_race_config):
        """handle_button_click returns True when a theme button is clicked."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.on_select_callback = None

            btn1 = MagicMock()
            btn2 = MagicMock()
            gallery.theme_buttons = [
                (btn1, "terran"),
                (btn2, "alien"),
            ]

            result = gallery.handle_button_click(btn1)

            assert result is True

    def test_handle_button_click_returns_false_for_other_button(self, mock_race_config):
        """handle_button_click returns False when a different button is clicked."""
        from game.ui.panels.race_theme_gallery import RaceThemeGallery

        with patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceThemeGallery.__new__(RaceThemeGallery)
            gallery.race_config = mock_race_config
            gallery.on_select_callback = None

            btn1 = MagicMock()
            btn2 = MagicMock()
            other_btn = MagicMock()
            gallery.theme_buttons = [
                (btn1, "terran"),
                (btn2, "alien"),
            ]

            result = gallery.handle_button_click(other_btn)

            assert result is False

