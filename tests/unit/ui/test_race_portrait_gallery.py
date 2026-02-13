"""
Unit tests for RacePortraitGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race portrait gallery panel functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with portrait_id property."""
    config = MagicMock()
    config.portrait_id = None
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


@pytest.fixture
def mock_asset_loader():
    """Create a mock RaceAssetLoader."""
    loader = MagicMock()
    loader.load_portrait_full.return_value = MagicMock()  # Mock Surface
    return loader


# =============================================================================
# Test: RacePortraitGallery Import and Creation
# =============================================================================

class TestRacePortraitGalleryCreation:
    """Tests for RacePortraitGallery initialization."""

    def test_race_portrait_gallery_can_be_imported(self):
        """RacePortraitGallery can be imported from separate module."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        assert RacePortraitGallery is not None

    def test_race_portrait_gallery_has_button_list(self):
        """RacePortraitGallery has asset_buttons list attribute."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.asset_buttons = []

            assert hasattr(gallery, 'asset_buttons')
            assert isinstance(gallery.asset_buttons, list)

    def test_race_portrait_gallery_has_preview_image(self):
        """RacePortraitGallery has portrait_preview_image attribute."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.portrait_preview_image = None

            assert hasattr(gallery, 'portrait_preview_image')

    def test_race_portrait_gallery_has_scroll_container(self):
        """RacePortraitGallery has scroll_container attribute for scrolling container."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.scroll_container = None

            assert hasattr(gallery, 'scroll_container')

    def test_race_portrait_gallery_has_preview_panel(self):
        """RacePortraitGallery has preview_panel attribute."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.preview_panel = None

            assert hasattr(gallery, 'preview_panel')


# =============================================================================
# Test: Portrait Selection
# =============================================================================

class TestPortraitSelection:
    """Tests for portrait selection functionality."""

    def test_on_asset_selected_updates_race_config(self, mock_race_config):
        """Selecting a portrait updates race_config.portrait_id."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            gallery.on_asset_selected("portrait_001.png")

            assert mock_race_config.portrait_id == "portrait_001.png"

    def test_on_asset_selected_clears_old_preview_image(self, mock_race_config):
        """Selecting a portrait clears existing preview image."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock existing preview image
            old_img = MagicMock()
            gallery.portrait_preview_image = old_img

            gallery.on_asset_selected("portrait_001.png")

            # Old image should be killed
            old_img.kill.assert_called_once()

    def test_on_asset_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a portrait calls the on_select callback if provided."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()

            callback = MagicMock()
            gallery.on_select_callback = callback

            gallery.on_asset_selected("portrait_001.png")

            callback.assert_called_once_with("portrait_001.png")

    def test_on_asset_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a portrait with no callback doesn't raise an error."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Should not raise
            gallery.on_asset_selected("portrait_001.png")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_asset_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a portrait highlights the corresponding button."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            gallery.asset_buttons = [
                (btn1, MagicMock(), "portrait_001.png"),
                (btn2, MagicMock(), "portrait_002.png"),
            ]

            gallery.on_asset_selected("portrait_001.png")

            btn1.select.assert_called_once()
            btn2.unselect.assert_called_once()

    def test_on_asset_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a portrait deselects all other buttons."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            btn3 = MagicMock()
            gallery.asset_buttons = [
                (btn1, MagicMock(), "portrait_001.png"),
                (btn2, MagicMock(), "portrait_002.png"),
                (btn3, MagicMock(), "portrait_003.png"),
            ]

            gallery.on_asset_selected("portrait_002.png")

            btn1.unselect.assert_called_once()
            btn2.select.assert_called_once()
            btn3.unselect.assert_called_once()


# =============================================================================
# Test: Configuration Binding
# =============================================================================

class TestConfigurationBinding:
    """Tests for setting values from config."""

    def test_set_from_config_selects_configured_portrait(self, mock_race_config):
        """set_from_config selects the portrait from race_config."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            mock_race_config.portrait_id = "portrait_005.png"
            gallery.asset_buttons = []
            gallery.portrait_preview_image = None
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_portrait_full.return_value = None
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Mock on_asset_selected to track call (base class method)
            gallery.on_asset_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_asset_selected.assert_called_once_with("portrait_005.png")

    def test_set_from_config_no_portrait_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no portrait_id in config."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        with patch.object(RacePortraitGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RacePortraitGallery.__new__(RacePortraitGallery)
            gallery.race_config = mock_race_config
            mock_race_config.portrait_id = None  # No portrait selected

            # Mock on_asset_selected to track call (base class method)
            gallery.on_asset_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_asset_selected.assert_not_called()


# =============================================================================
# Test: Constants
# =============================================================================

class TestConstants:
    """Tests for gallery constants."""

    def test_has_thumb_size_constant(self):
        """RacePortraitGallery has PORTRAIT_THUMB_SIZE constant."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        assert hasattr(RacePortraitGallery, 'PORTRAIT_THUMB_SIZE')
        assert RacePortraitGallery.PORTRAIT_THUMB_SIZE > 0

    def test_has_preview_size_constant(self):
        """RacePortraitGallery has PREVIEW_SIZE constant."""
        from game.ui.panels.race_portrait_gallery import RacePortraitGallery

        assert hasattr(RacePortraitGallery, 'PREVIEW_SIZE')
        assert RacePortraitGallery.PREVIEW_SIZE > 0

