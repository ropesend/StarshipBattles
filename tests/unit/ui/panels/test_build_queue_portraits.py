"""Tests for BuildQueuePortraitLoader resource icon loading.

PROJ-79: Added tests for resource icon loading method.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pygame


@pytest.fixture
def mock_pygame_init():
    """Initialize pygame for Surface creation."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_design_library():
    """Create mock DesignLibrary."""
    library = Mock()
    library.scan_designs.return_value = []
    return library


@pytest.fixture
def mock_session():
    """Create mock session with player_empire."""
    session = Mock()
    session.player_empire = Mock()
    session.player_empire.empire_theme_id = "Federation"
    return session


@pytest.fixture
def portrait_loader(mock_design_library, mock_session):
    """Create BuildQueuePortraitLoader with mocks."""
    from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
    return BuildQueuePortraitLoader(mock_design_library, mock_session)


class TestResourceIconLoading:
    """Tests for load_resource_icons() method."""

    def test_load_resource_icons_returns_all_five_resources(
        self, portrait_loader, mock_pygame_init
    ):
        """load_resource_icons returns dict with all 5 resource types."""
        icons = portrait_loader.load_resource_icons(icon_size=20)

        assert isinstance(icons, dict)
        assert len(icons) == 8
        expected_resources = ["metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo"]
        for resource in expected_resources:
            assert resource in icons

    def test_load_resource_icons_returns_surfaces(
        self, portrait_loader, mock_pygame_init
    ):
        """load_resource_icons returns pygame.Surface for each resource."""
        icons = portrait_loader.load_resource_icons(icon_size=20)

        for resource, surface in icons.items():
            assert isinstance(surface, pygame.Surface), f"{resource} should be Surface"

    def test_load_resource_icons_respects_icon_size(
        self, portrait_loader, mock_pygame_init
    ):
        """load_resource_icons scales icons to requested size."""
        # Test with custom size
        icons = portrait_loader.load_resource_icons(icon_size=32)

        for resource, surface in icons.items():
            assert surface.get_width() == 32, f"{resource} width should be 32"
            assert surface.get_height() == 32, f"{resource} height should be 32"

    def test_load_resource_icons_default_size_is_20(
        self, portrait_loader, mock_pygame_init
    ):
        """load_resource_icons uses 20 as default icon size."""
        icons = portrait_loader.load_resource_icons()

        for resource, surface in icons.items():
            assert surface.get_width() == 20, f"{resource} default width should be 20"
            assert surface.get_height() == 20, f"{resource} default height should be 20"

    def test_load_resource_icons_fallback_on_missing_file(
        self, mock_design_library, mock_session, mock_pygame_init
    ):
        """load_resource_icons creates fallback surfaces when files missing."""
        from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader

        # Patch pygame.image.load to raise FileNotFoundError
        with patch('pygame.image.load', side_effect=FileNotFoundError("not found")):
            loader = BuildQueuePortraitLoader(mock_design_library, mock_session)
            icons = loader.load_resource_icons(icon_size=20)

            # Should still return all 5 resources with fallback surfaces
            assert len(icons) == 8
            for resource, surface in icons.items():
                assert isinstance(surface, pygame.Surface)
                assert surface.get_width() == 20
                assert surface.get_height() == 20


class TestResourcePortraitConstants:
    """Tests for resource portrait constants."""

    def test_resource_portrait_files_has_all_resources(self):
        """RESOURCE_PORTRAIT_FILES contains all 5 resources."""
        from game.ui.panels.build_queue_portraits import RESOURCE_PORTRAIT_FILES

        expected = ["metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo"]
        for resource in expected:
            assert resource in RESOURCE_PORTRAIT_FILES

    def test_resource_fallback_colors_has_all_resources(self):
        """RESOURCE_FALLBACK_COLORS contains all 5 resources."""
        from game.ui.panels.build_queue_portraits import RESOURCE_FALLBACK_COLORS

        expected = ["metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo"]
        for resource in expected:
            assert resource in RESOURCE_FALLBACK_COLORS

    def test_resource_fallback_colors_are_valid_rgb(self):
        """RESOURCE_FALLBACK_COLORS contains valid RGB tuples."""
        from game.ui.panels.build_queue_portraits import RESOURCE_FALLBACK_COLORS

        for resource, color in RESOURCE_FALLBACK_COLORS.items():
            assert isinstance(color, tuple), f"{resource} color should be tuple"
            assert len(color) == 3, f"{resource} color should have 3 components"
            for component in color:
                assert 0 <= component <= 255, f"{resource} color component out of range"
