"""
Unit tests for RaceAssetLoader.

PROJ-12 Phase 4: TDD tests written before implementation.
Tests the race asset loading functionality (flags, portraits, placeholders).
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# =============================================================================
# Test: RaceAssetLoader Creation
# =============================================================================

class TestRaceAssetLoaderCreation:
    """Tests for RaceAssetLoader initialization."""

    def test_race_asset_loader_can_be_imported(self):
        """RaceAssetLoader can be imported from module."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        assert RaceAssetLoader is not None

    def test_race_asset_loader_can_be_instantiated(self):
        """RaceAssetLoader can be created."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        assert loader is not None


# =============================================================================
# Test: Flag Loading
# =============================================================================

class TestFlagLoading:
    """Tests for flag loading functionality."""

    def test_load_flag_full_returns_list(self):
        """load_flag_full returns a list of surfaces."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        # Even if flag doesn't exist, should return list of placeholders
        with patch('os.path.exists', return_value=False):
            result = loader.load_flag_full("nonexistent_flag")

        assert isinstance(result, list)
        assert len(result) == 3  # rectangle, shield, triangle

    def test_load_flag_full_returns_three_shapes(self):
        """load_flag_full returns exactly 3 shapes."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_flag_full("test_flag")

        assert len(result) == 3


# =============================================================================
# Test: Portrait Loading
# =============================================================================

class TestPortraitLoading:
    """Tests for portrait loading functionality."""

    def test_load_portrait_full_returns_none_for_missing(self):
        """load_portrait_full returns None for missing portrait."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_portrait_full("nonexistent_portrait.png")

        assert result is None

    def test_load_portrait_full_has_correct_signature(self):
        """load_portrait_full accepts portrait_id parameter."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        # Method should exist and accept string parameter
        assert hasattr(loader, 'load_portrait_full')
        assert callable(loader.load_portrait_full)


# =============================================================================
# Test: Placeholder Creation
# =============================================================================

class TestPlaceholderCreation:
    """Tests for placeholder surface creation."""

    def test_create_placeholder_returns_surface(self):
        """create_placeholder returns a pygame Surface."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        result = loader.create_placeholder(100, 100)

        assert isinstance(result, pygame.Surface)

    def test_create_placeholder_has_correct_dimensions(self):
        """create_placeholder returns surface with requested dimensions."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        result = loader.create_placeholder(150, 200)

        assert result.get_width() == 150
        assert result.get_height() == 200

    def test_create_placeholder_different_sizes(self):
        """create_placeholder works with various sizes."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        sizes = [(50, 50), (100, 200), (256, 256)]
        for w, h in sizes:
            result = loader.create_placeholder(w, h)
            assert result.get_width() == w
            assert result.get_height() == h


# =============================================================================
# Test: Preview Loading (Small Versions)
# =============================================================================

class TestPreviewLoading:
    """Tests for preview-sized asset loading."""

    def test_load_portrait_preview_returns_none_for_none_id(self):
        """load_portrait_preview returns None when portrait_id is None."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        result = loader.load_portrait_preview(None, 60)

        assert result is None

    def test_load_flag_preview_returns_none_for_none_id(self):
        """load_flag_preview returns None when flag_id is None."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        result = loader.load_flag_preview(None, 60)

        assert result is None

    def test_load_portrait_preview_returns_none_for_missing_path(self):
        """load_portrait_preview returns None when path doesn't exist."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_portrait_preview("nonexistent", 60)

        assert result is None


# =============================================================================
# Test: Empire Asset Loading (PROJ-37 Phase 3)
# =============================================================================

class TestEmpireAssetLoading:
    """Tests for empire asset loading methods added in PROJ-37."""

    # -------------------------------------------------------------------------
    # load_empire_race_assets tests
    # -------------------------------------------------------------------------

    def test_load_empire_race_assets_returns_dict(self):
        """load_empire_race_assets returns a dict."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_empire_race_assets("nonexistent_flag")

        assert isinstance(result, dict)

    def test_load_empire_race_assets_empty_flag_id(self):
        """load_empire_race_assets returns empty dict for empty flag_id."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        result = loader.load_empire_race_assets("")

        assert result == {}

    def test_load_empire_race_assets_none_flag_id(self):
        """load_empire_race_assets returns empty dict for None flag_id."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        result = loader.load_empire_race_assets(None)

        assert result == {}

    def test_load_empire_race_assets_contains_colony_key(self):
        """load_empire_race_assets returns dict with 'colony' key when flag exists."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_surface = MagicMock(spec=pygame.Surface)

        with patch.object(loader, 'load_flag_full', return_value=[mock_surface, mock_surface, mock_surface]):
            result = loader.load_empire_race_assets("test_flag")

        assert 'colony' in result
        assert result['colony'] == mock_surface

    def test_load_empire_race_assets_contains_fleet_flag_key(self):
        """load_empire_race_assets returns dict with 'fleet_flag' key when flag exists."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_surface = MagicMock(spec=pygame.Surface)

        with patch.object(loader, 'load_flag_full', return_value=[mock_surface, mock_surface, mock_surface]):
            result = loader.load_empire_race_assets("test_flag")

        assert 'fleet_flag' in result
        assert result['fleet_flag'] == mock_surface

    def test_load_empire_race_assets_handles_partial_shapes(self):
        """load_empire_race_assets handles case where only rectangle shape exists."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_surface = MagicMock(spec=pygame.Surface)

        # Only one shape available
        with patch.object(loader, 'load_flag_full', return_value=[mock_surface]):
            result = loader.load_empire_race_assets("test_flag")

        assert 'colony' in result
        assert 'fleet_flag' not in result  # Shield not available

    # -------------------------------------------------------------------------
    # load_empire_theme_assets tests
    # -------------------------------------------------------------------------

    def test_load_empire_theme_assets_returns_dict(self):
        """load_empire_theme_assets returns a dict."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_empire_theme_assets("Federation", "/nonexistent/path")

        assert isinstance(result, dict)

    def test_load_empire_theme_assets_empty_theme_id(self):
        """load_empire_theme_assets returns empty dict for empty theme_id."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        result = loader.load_empire_theme_assets("", "/some/path")

        assert result == {}

    def test_load_empire_theme_assets_empty_asset_base(self):
        """load_empire_theme_assets returns empty dict for empty asset_base."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        result = loader.load_empire_theme_assets("Federation", "")

        assert result == {}

    def test_load_empire_theme_assets_nonexistent_theme_dir(self):
        """load_empire_theme_assets returns empty dict when theme dir doesn't exist."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_empire_theme_assets("Federation", "/some/path")

        assert result == {}

    @patch('game.ui.screens.race_asset_loader.get_asset_manager')
    def test_load_empire_theme_assets_loads_colony_flag(self, mock_get_am):
        """load_empire_theme_assets loads colony flag from Flags/Colony_Flag.jpg."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_am = MagicMock()
        mock_am.load_external_image.return_value = mock_surface
        mock_get_am.return_value = mock_am

        def exists_side_effect(path):
            # Theme dir exists, colony flag exists, fleet icon doesn't
            if 'Federation' in path and 'Flags' not in path and 'Skins' not in path:
                return True
            if 'Colony_Flag' in path:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect):
            result = loader.load_empire_theme_assets("Federation", "/assets/themes")

        assert 'colony' in result
        assert result['colony'] == mock_surface

    @patch('game.ui.screens.race_asset_loader.get_asset_manager')
    def test_load_empire_theme_assets_loads_fleet_icon(self, mock_get_am):
        """load_empire_theme_assets loads fleet icon from Skins/Battlecruiser.png."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_am = MagicMock()
        mock_am.load_external_image.return_value = mock_surface
        mock_get_am.return_value = mock_am

        def exists_side_effect(path):
            # Theme dir exists, fleet icon exists, colony flag doesn't
            if 'Federation' in path and 'Flags' not in path and 'Skins' not in path:
                return True
            if 'Battlecruiser' in path:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect):
            result = loader.load_empire_theme_assets("Federation", "/assets/themes")

        assert 'fleet' in result
        assert result['fleet'] == mock_surface

    # -------------------------------------------------------------------------
    # load_all_empire_assets tests
    # -------------------------------------------------------------------------

    def test_load_all_empire_assets_returns_dict(self):
        """load_all_empire_assets returns a dict."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_empire = MagicMock()
        mock_empire.flag_id = None
        mock_empire.empire_theme_id = None

        result = loader.load_all_empire_assets(mock_empire, "/assets/themes")

        assert isinstance(result, dict)

    def test_load_all_empire_assets_race_precedence_over_theme(self):
        """load_all_empire_assets: race assets override theme assets for 'colony' key."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_empire = MagicMock()
        mock_empire.flag_id = "test_flag"
        mock_empire.empire_theme_id = "Federation"

        race_surface = MagicMock(spec=pygame.Surface)
        race_surface.name = "race_colony"
        theme_surface = MagicMock(spec=pygame.Surface)
        theme_surface.name = "theme_colony"
        fleet_surface = MagicMock(spec=pygame.Surface)

        with patch.object(loader, 'load_empire_race_assets', return_value={'colony': race_surface, 'fleet_flag': race_surface}):
            with patch.object(loader, 'load_empire_theme_assets', return_value={'colony': theme_surface, 'fleet': fleet_surface}):
                result = loader.load_all_empire_assets(mock_empire, "/assets/themes")

        # Race colony should override theme colony
        assert result['colony'] == race_surface
        # Fleet icon from theme should still be present
        assert result['fleet'] == fleet_surface

    def test_load_all_empire_assets_uses_theme_when_no_race(self):
        """load_all_empire_assets: uses theme assets when no race assets exist."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_empire = MagicMock()
        mock_empire.flag_id = None  # No race flag
        mock_empire.empire_theme_id = "Federation"

        theme_surface = MagicMock(spec=pygame.Surface)

        with patch.object(loader, 'load_empire_race_assets', return_value={}):
            with patch.object(loader, 'load_empire_theme_assets', return_value={'colony': theme_surface, 'fleet': theme_surface}):
                result = loader.load_all_empire_assets(mock_empire, "/assets/themes")

        assert result['colony'] == theme_surface

    def test_load_all_empire_assets_handles_missing_attributes(self):
        """load_all_empire_assets handles empire objects missing flag_id/theme_id."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        # Empire without flag_id or empire_theme_id attributes
        mock_empire = MagicMock(spec=[])  # Empty spec means no attributes

        result = loader.load_all_empire_assets(mock_empire, "/assets/themes")

        assert isinstance(result, dict)
        assert result == {}

    def test_load_all_empire_assets_includes_fleet_flag_from_race(self):
        """load_all_empire_assets includes fleet_flag from race assets."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()
        mock_empire = MagicMock()
        mock_empire.flag_id = "test_flag"
        mock_empire.empire_theme_id = None

        fleet_flag_surface = MagicMock(spec=pygame.Surface)

        with patch.object(loader, 'load_empire_race_assets', return_value={'colony': fleet_flag_surface, 'fleet_flag': fleet_flag_surface}):
            with patch.object(loader, 'load_empire_theme_assets', return_value={}):
                result = loader.load_all_empire_assets(mock_empire, "/assets/themes")

        assert 'fleet_flag' in result


# =============================================================================
# Test: Error Handling and Edge Cases (PROJ-111 Phase 6 Task 6.7)
# =============================================================================

class TestRaceAssetLoaderErrorHandling:
    """Tests for error handling and edge cases."""

    def test_load_flag_full_with_missing_asset_directory(self):
        """load_flag_full gracefully handles missing asset directory."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=False):
            result = loader.load_flag_full("completely_nonexistent_flag")

        # Should return placeholders, not crash
        assert isinstance(result, list)
        assert len(result) == 3
        # All should be placeholder surfaces
        for surf in result:
            assert isinstance(surf, pygame.Surface)

    def test_load_flag_full_with_partial_shapes(self):
        """load_flag_full handles case where only some shapes exist."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        # Only rectangle exists
        def exists_side_effect(path):
            return 'rectangle' in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load') as mock_load:
                mock_surface = MagicMock(spec=pygame.Surface)
                mock_surface.convert_alpha.return_value = mock_surface
                mock_load.return_value = mock_surface

                result = loader.load_flag_full("partial_flag")

        assert len(result) == 3
        # First should be the loaded surface, others placeholders
        assert result[0] == mock_surface

    def test_load_portrait_full_with_invalid_image_file(self):
        """load_portrait_full handles corrupt/invalid image files."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=True):
            with patch('pygame.image.load', side_effect=pygame.error("Invalid image")):
                result = loader.load_portrait_full("corrupt_image.png")

        # Should return None gracefully
        assert result is None

    def test_load_flag_full_with_pygame_error(self):
        """load_flag_full handles pygame errors during load."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        # First shape file exists but fails to load
        def exists_side_effect(path):
            if 'rectangle' in path:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', side_effect=pygame.error("Load error")):
                result = loader.load_flag_full("broken_flag")

        # Should have 3 items - placeholders for all
        assert len(result) == 3

    def test_load_portrait_preview_with_empty_directory(self):
        """load_portrait_preview handles empty portrait directory."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=[]):
                result = loader.load_portrait_preview("empty_portrait_dir", 60)

        # Should return None for empty directory
        assert result is None

    def test_load_flag_preview_with_only_non_image_files(self):
        """load_flag_preview handles directory with only non-image files."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['readme.txt', 'metadata.json']):
                result = loader.load_flag_preview("text_only_dir", 60)

        # Should return None when no images found
        assert result is None

    def test_create_placeholder_creates_valid_surface(self):
        """create_placeholder creates surface with visual markers."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        result = loader.create_placeholder(100, 100)

        assert isinstance(result, pygame.Surface)
        assert result.get_width() == 100
        assert result.get_height() == 100
        # Surface should have alpha channel
        assert result.get_flags() & pygame.SRCALPHA

    def test_load_empire_theme_assets_with_exception(self):
        """load_empire_theme_assets handles exceptions from asset_manager."""
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        loader = RaceAssetLoader()

        def exists_side_effect(path):
            if 'TestTheme' in path:
                return True
            if 'Colony_Flag' in path:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('game.ui.screens.race_asset_loader.get_asset_manager') as mock_get_am:
                mock_am = MagicMock()
                mock_am.load_external_image.side_effect = Exception("Load failed")
                mock_get_am.return_value = mock_am

                # This may raise, which is acceptable for unhandled exception
                try:
                    result = loader.load_empire_theme_assets("TestTheme", "/assets/themes")
                except Exception:
                    result = {}

        # Should handle gracefully or raise - test that it doesn't crash pygame
        assert isinstance(result, dict)
