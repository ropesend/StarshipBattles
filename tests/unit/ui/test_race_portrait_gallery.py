"""
Unit tests for RacePortraitGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race portrait gallery panel functionality.

PROJ-322 Task 5.1 (APC-001-F01): the legacy `RacePortraitGallery.__new__` +
`patch.object(__init__, ...)` blocks have been replaced with the shared
`make_ui_widget` factory routed through a module-scope `_bypass_init_gallery`
helper. The factory does run `_create_content` which discovers real portrait
files on disk; the tests still assert against test-controlled mock attrs by
re-assigning `gallery.asset_buttons` / `gallery.preview_panel` /
`gallery.portrait_preview_image` post-construction.
"""

import pytest
from unittest.mock import MagicMock

from tests.fixtures.ui_widget_factory import make_ui_widget


def _bypass_init_gallery(race_config=None, asset_loader=None):
    """Build a `RacePortraitGallery` via the shared `make_ui_widget` factory.

    Replaces the inline `__new__` + `patch.object(__init__, ...)` blocks
    that wired ~10 attrs per test. The factory calls real `__init__` which
    delegates to `BaseGallery.__init__` → `_create_content` → real disk
    `_discover_assets`. With pygame_gui elements mocked the only side
    effect is the disk scan; production attrs (`race_config`, `ui_manager`,
    `panel`, `asset_buttons`, `preview_panel`, `scroll_container`,
    `_asset_loader`, `on_select_callback`) are all populated.

    Tests then overwrite specific attrs (e.g. `gallery.asset_buttons = []`,
    `gallery.preview_panel = MagicMock()`) before calling the production
    method under test.

    PROJ-322 Task 5.1 / APC-001-F01.
    """
    if race_config is None:
        race_config = MagicMock()
        race_config.portrait_id = None
    if asset_loader is None:
        asset_loader = MagicMock()
        asset_loader.load_portrait_full.return_value = None
    from game.ui.panels.race_portrait_gallery import RacePortraitGallery

    return make_ui_widget(
        RacePortraitGallery,
        race_config=race_config,
        x=0,
        y=0,
        width=600,
        height=400,
        asset_loader=asset_loader,
    )


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

    def test_race_portrait_gallery_has_button_list(self):
        """RacePortraitGallery has asset_buttons list attribute."""
        gallery = _bypass_init_gallery()

        assert hasattr(gallery, 'asset_buttons')
        assert isinstance(gallery.asset_buttons, list)

    def test_race_portrait_gallery_has_preview_image(self):
        """RacePortraitGallery has portrait_preview_image attribute."""
        gallery = _bypass_init_gallery()

        assert hasattr(gallery, 'portrait_preview_image')

    def test_race_portrait_gallery_has_scroll_container(self):
        """RacePortraitGallery has scroll_container attribute for scrolling container."""
        gallery = _bypass_init_gallery()

        assert hasattr(gallery, 'scroll_container')

    def test_race_portrait_gallery_has_preview_panel(self):
        """RacePortraitGallery has preview_panel attribute."""
        gallery = _bypass_init_gallery()

        assert hasattr(gallery, 'preview_panel')


# =============================================================================
# Test: Portrait Selection
# =============================================================================

class TestPortraitSelection:
    """Tests for portrait selection functionality."""

    def test_on_asset_selected_updates_race_config(self, mock_race_config):
        """Selecting a portrait updates race_config.portrait_id."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        # Reset asset_buttons + preview_image to deterministic values; the
        # factory's _create_content populated them with mocks based on the
        # real portrait files on disk.
        gallery.asset_buttons = []
        gallery.portrait_preview_image = None

        gallery.on_asset_selected("portrait_001.png")

        assert mock_race_config.portrait_id == "portrait_001.png"

    def test_on_asset_selected_clears_old_preview_image(self, mock_race_config):
        """Selecting a portrait clears existing preview image."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        gallery.asset_buttons = []
        # Create mock existing preview image (replacing whatever
        # _create_content put there)
        old_img = MagicMock()
        gallery.portrait_preview_image = old_img

        gallery.on_asset_selected("portrait_001.png")

        # Old image should be killed
        old_img.kill.assert_called_once()

    def test_on_asset_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a portrait calls the on_select callback if provided."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        gallery.asset_buttons = []
        gallery.portrait_preview_image = None

        callback = MagicMock()
        gallery.on_select_callback = callback

        gallery.on_asset_selected("portrait_001.png")

        callback.assert_called_once_with("portrait_001.png")

    def test_on_asset_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a portrait with no callback doesn't raise an error."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        gallery.asset_buttons = []
        gallery.portrait_preview_image = None

        # Should not raise
        gallery.on_asset_selected("portrait_001.png")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_asset_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a portrait highlights the corresponding button."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        gallery.portrait_preview_image = None

        # Create mock buttons (overwriting whatever _create_content built)
        btn1 = MagicMock()
        btn2 = MagicMock()
        gallery.asset_buttons = [
            (btn1, "portrait_001.png"),
            (btn2, "portrait_002.png"),
        ]

        gallery.on_asset_selected("portrait_001.png")

        btn1.select.assert_called_once()
        btn2.unselect.assert_called_once()

    def test_on_asset_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a portrait deselects all other buttons."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        gallery.portrait_preview_image = None

        # Create mock buttons
        btn1 = MagicMock()
        btn2 = MagicMock()
        btn3 = MagicMock()
        gallery.asset_buttons = [
            (btn1, "portrait_001.png"),
            (btn2, "portrait_002.png"),
            (btn3, "portrait_003.png"),
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
        # Construct with no portrait_id so _create_content's pre-select
        # branch doesn't run; THEN set the value the test wants to assert.
        gallery = _bypass_init_gallery(race_config=mock_race_config)
        mock_race_config.portrait_id = "portrait_005.png"
        gallery.asset_buttons = []
        gallery.portrait_preview_image = None

        # Mock on_asset_selected to track call (base class method)
        gallery.on_asset_selected = MagicMock()

        gallery.set_from_config()

        gallery.on_asset_selected.assert_called_once_with("portrait_005.png")

    def test_set_from_config_no_portrait_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no portrait_id in config."""
        gallery = _bypass_init_gallery(race_config=mock_race_config)
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


# =============================================================================
# Issue #11: cross-instance thumbnail cache
# =============================================================================


class TestIssue11PortraitModuleCache:
    """Issue #11: ``_discover_assets`` must reuse decoded thumbnails
    across gallery instances via a module-level cache, eliminating the
    per-open filesystem scan + 2048→256 smoothscale on dialog reopen."""

    def test_discover_assets_uses_module_level_cache_across_instances(self):
        """Two gallery instances share thumbnails — second open does no
        filesystem scan."""
        from unittest.mock import patch

        from game.ui.panels import race_portrait_gallery as rpg

        rpg._clear_thumbnail_caches()

        gallery_a = _bypass_init_gallery()
        first_pass = gallery_a._discover_assets()
        assert first_pass, "fixture expects portraits directory to have content"

        with patch("os.scandir") as mock_scandir:
            gallery_b = _bypass_init_gallery()
            second_pass = gallery_b._discover_assets()
            mock_scandir.assert_not_called()

        assert second_pass is first_pass

    def test_clear_thumbnail_caches_resets_module_state(self):
        """The reset helper exists and lets tests/fixtures wipe state."""
        from unittest.mock import patch

        from game.ui.panels import race_portrait_gallery as rpg
        import os as os_mod

        gallery = _bypass_init_gallery()
        gallery._discover_assets()

        rpg._clear_thumbnail_caches()

        with patch("os.scandir", wraps=os_mod.scandir) as wrapped:
            gallery2 = _bypass_init_gallery()
            gallery2._discover_assets()
            wrapped.assert_called()

