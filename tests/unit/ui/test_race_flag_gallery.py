"""
Unit tests for RaceFlagGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race flag gallery panel functionality.

PROJ-322 Task 5.5 (APC-001-F05): the legacy `RaceFlagGallery.__new__` +
`patch.object(__init__, ...)` blocks now route through the shared
`make_ui_widget` factory via `_bypass_init_gallery`.
"""

import pytest
from unittest.mock import MagicMock

from tests.fixtures.ui_widget_factory import make_ui_widget


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


def _bypass_init_gallery(race_config, *, asset_buttons=None, flag_preview_images=None):
    """Build a `RaceFlagGallery` via the shared `make_ui_widget` factory.

    Replaces the inline `__new__` + `patch.object(__init__, ...)` blocks
    that wired ~10 attrs per test. The factory calls real `__init__` →
    `BaseGallery.__init__` → `_create_content` → real disk
    `_discover_assets` (flags directory). Pygame_gui elements stay mocked
    so the only side effect is the disk scan.

    Tests then overwrite specific attrs (e.g. `gallery.asset_buttons = [...]`,
    `gallery.flag_preview_images = [...]`) for deterministic assertions.

    PROJ-322 Task 5.5 / APC-001-F05 (originally promoted from inline blocks
    in PROJ-323 Task 1.30).
    """
    from game.ui.panels.race_flag_gallery import RaceFlagGallery

    asset_loader = MagicMock()
    asset_loader.load_flag_full.return_value = []

    gallery = make_ui_widget(
        RaceFlagGallery,
        race_config=race_config,
        x=0,
        y=0,
        width=600,
        height=400,
        asset_loader=asset_loader,
    )
    # Override _create_content's auto-mocked attrs with the test's
    # explicit values (or empty lists by default).
    gallery.asset_buttons = asset_buttons if asset_buttons is not None else []
    gallery.flag_preview_images = (
        flag_preview_images if flag_preview_images is not None else []
    )
    return gallery


# =============================================================================
# Test: RaceFlagGallery Import and Creation
# =============================================================================

# =============================================================================
# Test: Flag Selection
# =============================================================================

class TestFlagSelection:
    """Tests for flag selection functionality."""

    def test_on_asset_selected_updates_race_config(self, mock_race_config):
        """Selecting a flag updates race_config.flag_id."""
        gallery = _bypass_init_gallery(mock_race_config)

        gallery.on_asset_selected("flag_001")

        assert mock_race_config.flag_id == "flag_001"

    def test_on_asset_selected_clears_old_preview_images(self, mock_race_config):
        """Selecting a flag clears existing preview images."""
        # Create mock existing preview images
        old_img1 = MagicMock()
        old_img2 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            flag_preview_images=[old_img1, old_img2],
        )

        gallery.on_asset_selected("flag_001")

        # Old images should be killed
        old_img1.kill.assert_called_once()
        old_img2.kill.assert_called_once()

    def test_on_asset_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a flag calls the on_select callback if provided."""
        gallery = _bypass_init_gallery(mock_race_config)

        callback = MagicMock()
        gallery.on_select_callback = callback

        gallery.on_asset_selected("flag_001")

        callback.assert_called_once_with("flag_001")

    def test_on_asset_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a flag with no callback doesn't raise an error."""
        gallery = _bypass_init_gallery(mock_race_config)

        # Should not raise
        gallery.on_asset_selected("flag_001")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_asset_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a flag highlights the corresponding button."""
        # Create mock buttons
        btn1 = MagicMock()
        btn2 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[(btn1, "flag_001"), (btn2, "flag_002")],
        )

        gallery.on_asset_selected("flag_001")

        btn1.select.assert_called_once()
        btn2.unselect.assert_called_once()

    def test_on_asset_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a flag deselects all other buttons."""
        btn1 = MagicMock()
        btn2 = MagicMock()
        btn3 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[
                (btn1, "flag_001"),
                (btn2, "flag_002"),
                (btn3, "flag_003"),
            ],
        )

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
        # Construct with no flag_id so _create_content's pre-select branch
        # doesn't run; THEN set the value the test wants.
        gallery = _bypass_init_gallery(mock_race_config)
        mock_race_config.flag_id = "flag_005"

        # Mock on_asset_selected to track call (base class method)
        gallery.on_asset_selected = MagicMock()

        gallery.set_from_config()

        gallery.on_asset_selected.assert_called_once_with("flag_005")

    def test_set_from_config_no_flag_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no flag_id in config."""
        gallery = _bypass_init_gallery(mock_race_config)
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


# =============================================================================
# Issue #11: cross-instance thumbnail cache + 256/ flag source
# =============================================================================


class TestIssue11FlagModuleCache:
    """Issue #11: ``_discover_assets`` must reuse decoded thumbnails
    across gallery instances via a module-level cache, eliminating the
    per-open filesystem scan + smoothscale on Setup Species reopen."""

    def test_discover_assets_uses_module_level_cache_across_instances(
        self, mock_race_config
    ):
        """Two gallery instances share thumbnails — second open does no
        filesystem scan."""
        from game.ui.panels import race_flag_gallery as rfg

        # Reset module cache so this test isn't polluted by other tests.
        rfg._clear_thumbnail_caches()

        gallery_a = _bypass_init_gallery(mock_race_config)
        first_pass = gallery_a._discover_assets()
        assert first_pass, "fixture expects flags directory to exist with content"

        # Patch scandir on the second build: if the cache is per-instance
        # (bug), the second gallery will call scandir again. With the
        # module cache fix, it must not.
        from unittest.mock import patch

        with patch("os.scandir") as mock_scandir:
            gallery_b = _bypass_init_gallery(mock_race_config)
            second_pass = gallery_b._discover_assets()
            mock_scandir.assert_not_called()

        assert second_pass is first_pass, (
            "Second gallery instance must return the SAME cached list, "
            "not a fresh decode."
        )

    def test_clear_thumbnail_caches_resets_module_state(self, mock_race_config):
        """The reset helper exists and lets tests/fixtures wipe state."""
        from game.ui.panels import race_flag_gallery as rfg

        gallery = _bypass_init_gallery(mock_race_config)
        gallery._discover_assets()  # populate cache

        rfg._clear_thumbnail_caches()

        # After reset, the next discover must actually hit disk again.
        from unittest.mock import patch

        with patch("os.scandir", wraps=__import__("os").scandir) as wrapped:
            gallery2 = _bypass_init_gallery(mock_race_config)
            gallery2._discover_assets()
            wrapped.assert_called()


class TestIssue11FlagReads256:
    """Issue #11: flag gallery must read ``256/rectangle.png`` directly
    (no 128→256 smoothscale upscale)."""

    def test_discover_assets_prefers_256_path(self, mock_race_config, tmp_path, monkeypatch):
        """If both 256/ and 128/ exist, the 256/ file is loaded directly
        (the 128/ file is NOT touched)."""
        from unittest.mock import patch, MagicMock

        from game.ui.panels import race_flag_gallery as rfg

        # Build a fake flags directory: one flag with both 128/ and 256/.
        processed = tmp_path / "Images" / "Flags" / "Processed"
        flag_dir = processed / "flag_x"
        (flag_dir / "128").mkdir(parents=True)
        (flag_dir / "256").mkdir(parents=True)
        (flag_dir / "128" / "rectangle.png").write_bytes(b"x")
        (flag_dir / "256" / "rectangle.png").write_bytes(b"x")

        monkeypatch.setattr(rfg.Paths, "ASSET_DIR", str(tmp_path))
        rfg._clear_thumbnail_caches()

        loaded_paths = []

        def fake_load(path):
            loaded_paths.append(path)
            surf = MagicMock()
            surf.convert_alpha.return_value = surf
            return surf

        with patch("pygame.image.load", side_effect=fake_load), patch(
            "pygame.transform.smoothscale", side_effect=lambda surf, _size: surf
        ):
            gallery = _bypass_init_gallery(mock_race_config)
            rfg._clear_thumbnail_caches()  # discard the production-scan cache
            gallery._asset_cache = None  # discard any instance cache from _bypass
            gallery._discover_assets()

        assert any("256" in p and "rectangle.png" in p for p in loaded_paths), (
            f"flag gallery must read 256/rectangle.png directly; "
            f"loaded paths were: {loaded_paths}"
        )
        assert not any(
            "128" in p and "rectangle.png" in p for p in loaded_paths
        ), (
            f"flag gallery must NOT read 128/rectangle.png when 256/ "
            f"is available; loaded paths were: {loaded_paths}"
        )

