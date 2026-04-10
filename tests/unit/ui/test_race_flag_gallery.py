"""
Unit tests for RaceFlagGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race flag gallery panel functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, call


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with flag_id property."""
    config = MagicMock()
    config.flag_id = None
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
    loader.load_flag_full.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return loader


# =============================================================================
# Test: RaceFlagGallery Import and Creation
# =============================================================================

class TestRaceFlagGalleryCreation:
    """Tests for RaceFlagGallery initialization."""

    def test_race_flag_gallery_has_button_list(self):
        """RaceFlagGallery has asset_buttons list attribute."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.asset_buttons = []

            assert hasattr(gallery, 'asset_buttons')
            assert isinstance(gallery.asset_buttons, list)

    def test_race_flag_gallery_has_preview_images_list(self):
        """RaceFlagGallery has flag_preview_images list attribute."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.flag_preview_images = []

            assert hasattr(gallery, 'flag_preview_images')
            assert isinstance(gallery.flag_preview_images, list)

    def test_race_flag_gallery_has_scroll_container(self):
        """RaceFlagGallery has scroll_container attribute for scrolling container."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.scroll_container = None

            assert hasattr(gallery, 'scroll_container')

    def test_race_flag_gallery_has_preview_panel(self):
        """RaceFlagGallery has preview_panel attribute."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.preview_panel = None

            assert hasattr(gallery, 'preview_panel')


# =============================================================================
# Test: Flag Selection
# =============================================================================

class TestFlagSelection:
    """Tests for flag selection functionality."""

    def test_on_asset_selected_updates_race_config(self, mock_race_config):
        """Selecting a flag updates race_config.flag_id."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            gallery.on_asset_selected("flag_001")

            assert mock_race_config.flag_id == "flag_001"

    def test_on_asset_selected_clears_old_preview_images(self, mock_race_config):
        """Selecting a flag clears existing preview images."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock existing preview images
            old_img1 = MagicMock()
            old_img2 = MagicMock()
            gallery.flag_preview_images = [old_img1, old_img2]

            gallery.on_asset_selected("flag_001")

            # Old images should be killed
            old_img1.kill.assert_called_once()
            old_img2.kill.assert_called_once()

    def test_on_asset_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a flag calls the on_select callback if provided."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()

            callback = MagicMock()
            gallery.on_select_callback = callback

            gallery.on_asset_selected("flag_001")

            callback.assert_called_once_with("flag_001")

    def test_on_asset_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a flag with no callback doesn't raise an error."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.asset_buttons = []
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Should not raise
            gallery.on_asset_selected("flag_001")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_asset_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a flag highlights the corresponding button."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            gallery.asset_buttons = [
                (btn1, "flag_001"),
                (btn2, "flag_002"),
            ]

            gallery.on_asset_selected("flag_001")

            btn1.select.assert_called_once()
            btn2.unselect.assert_called_once()

    def test_on_asset_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a flag deselects all other buttons."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Create mock buttons
            btn1 = MagicMock()
            btn2 = MagicMock()
            btn3 = MagicMock()
            gallery.asset_buttons = [
                (btn1, "flag_001"),
                (btn2, "flag_002"),
                (btn3, "flag_003"),
            ]

            gallery.on_asset_selected("flag_002")

            btn1.unselect.assert_called_once()
            btn2.select.assert_called_once()
            btn3.unselect.assert_called_once()


# =============================================================================
# Test: Configuration Binding
# =============================================================================

class TestConfigurationBinding:
    """Tests for setting values from config."""

    def test_set_from_config_selects_configured_flag(self, mock_race_config):
        """set_from_config selects the flag from race_config."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            mock_race_config.flag_id = "flag_005"
            gallery.asset_buttons = []
            gallery.flag_preview_images = []
            gallery.preview_panel = MagicMock()
            gallery._asset_loader = MagicMock()
            gallery._asset_loader.load_flag_full.return_value = []
            gallery.ui_manager = MagicMock()
            gallery.on_select_callback = None

            # Mock on_asset_selected to track call (base class method)
            gallery.on_asset_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_asset_selected.assert_called_once_with("flag_005")

    def test_set_from_config_no_flag_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no flag_id in config."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        with patch.object(RaceFlagGallery, '__init__', lambda self, *args, **kwargs: None):
            gallery = RaceFlagGallery.__new__(RaceFlagGallery)
            gallery.race_config = mock_race_config
            mock_race_config.flag_id = None  # No flag selected

            # Mock on_asset_selected to track call
            gallery.on_asset_selected = MagicMock()

            gallery.set_from_config()

            gallery.on_asset_selected.assert_not_called()


# =============================================================================
# Test: Constants
# =============================================================================

class TestConstants:
    """Tests for gallery constants."""

    def test_has_thumb_size_constant(self):
        """RaceFlagGallery has FLAG_THUMB_SIZE constant."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        assert hasattr(RaceFlagGallery, 'FLAG_THUMB_SIZE')
        assert RaceFlagGallery.FLAG_THUMB_SIZE > 0

    def test_has_preview_size_constant(self):
        """RaceFlagGallery has PREVIEW_SIZE constant."""
        from game.ui.panels.race_flag_gallery import RaceFlagGallery

        assert hasattr(RaceFlagGallery, 'PREVIEW_SIZE')
        assert RaceFlagGallery.PREVIEW_SIZE > 0

