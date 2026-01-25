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
