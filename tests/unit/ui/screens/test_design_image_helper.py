"""
Tests for design_image_helper module.

Tests the extracted image loading utilities for design thumbnails.
"""
import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock


class TestLoadPortraitThumbnail:
    """Tests for load_portrait_thumbnail function."""

    def setup_method(self):
        """Initialize pygame display for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def teardown_method(self):
        """Clean up pygame."""
        pygame.quit()

    def test_returns_surface_when_no_files_exist(self):
        """Returns a pygame.Surface placeholder when no files exist."""
        from game.ui.screens.design_image_helper import load_portrait_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.vehicle_type = "Ship"
        design.design_id = "test_design"

        with patch('os.path.exists', return_value=False):
            result = load_portrait_thumbnail(design)

        assert isinstance(result, pygame.Surface)

    def test_placeholder_has_correct_dimensions(self):
        """Placeholder surface has correct dimensions (size x size)."""
        from game.ui.screens.design_image_helper import load_portrait_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.vehicle_type = "Ship"
        design.design_id = "test_design"

        with patch('os.path.exists', return_value=False):
            result = load_portrait_thumbnail(design, size=75)

        assert result.get_width() == 75
        assert result.get_height() == 75

    def test_logs_warning_when_file_exists_but_load_fails(self):
        """Logs warning when file exists but pygame.image.load fails."""
        from game.ui.screens.design_image_helper import load_portrait_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.vehicle_type = "Ship"
        design.design_id = "test_design"

        # First path exists but fails to load, rest don't exist
        def exists_side_effect(path):
            return "Cruiser_Portrait.jpg" in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', side_effect=pygame.error("Load failed")):
                with patch('game.ui.screens.design_image_helper.log_warning') as mock_warning:
                    result = load_portrait_thumbnail(design)

        assert mock_warning.called
        assert isinstance(result, pygame.Surface)  # Falls back to placeholder

    def test_different_vehicle_types_produce_different_placeholder_colors(self):
        """Different vehicle types produce different placeholder colors."""
        from game.ui.screens.design_image_helper import load_portrait_thumbnail

        def make_design(vehicle_type):
            design = Mock()
            design.theme_id = "Federation"
            design.ship_class = "Test"
            design.vehicle_type = vehicle_type
            design.design_id = f"test_{vehicle_type}"
            return design

        with patch('os.path.exists', return_value=False):
            ship_surface = load_portrait_thumbnail(make_design("Ship"))
            fighter_surface = load_portrait_thumbnail(make_design("Fighter"))
            satellite_surface = load_portrait_thumbnail(make_design("Satellite"))
            complex_surface = load_portrait_thumbnail(make_design("Planetary Complex"))

        # Get a sample pixel from each (avoiding text area by checking corner)
        # The gradient starts at top, so check a pixel near the top
        ship_color = ship_surface.get_at((2, 2))[:3]
        fighter_color = fighter_surface.get_at((2, 2))[:3]
        satellite_color = satellite_surface.get_at((2, 2))[:3]
        complex_color = complex_surface.get_at((2, 2))[:3]

        # All should be different
        colors = [ship_color, fighter_color, satellite_color, complex_color]
        unique_colors = set(colors)
        assert len(unique_colors) == 4, f"Expected 4 unique colors, got {len(unique_colors)}: {colors}"

    def test_loads_and_scales_image_when_file_exists(self):
        """Successfully loads and scales image when file exists."""
        from game.ui.screens.design_image_helper import load_portrait_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.vehicle_type = "Ship"
        design.design_id = "test_design"

        # Create a mock image surface
        mock_img = pygame.Surface((100, 100))
        mock_img.fill((255, 0, 0))

        def exists_side_effect(path):
            return "Cruiser_Portrait.jpg" in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', return_value=mock_img):
                result = load_portrait_thumbnail(design, size=50)

        assert result.get_width() == 50
        assert result.get_height() == 50


class TestLoadTopdownThumbnail:
    """Tests for load_topdown_thumbnail function."""

    def setup_method(self):
        """Initialize pygame display for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def teardown_method(self):
        """Clean up pygame."""
        pygame.quit()

    def test_returns_none_when_no_skin_file_found(self):
        """Returns None when no skin file found."""
        from game.ui.screens.design_image_helper import load_topdown_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.design_id = "test_design"

        with patch('os.path.exists', return_value=False):
            result = load_topdown_thumbnail(design)

        assert result is None

    def test_returns_surface_when_skin_file_found(self):
        """Returns a Surface when skin file is found and valid."""
        from game.ui.screens.design_image_helper import load_topdown_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.design_id = "test_design"

        # Create a mock image surface with visible content
        mock_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Draw a visible rectangle in the center
        pygame.draw.rect(mock_img, (255, 0, 0, 255), (25, 25, 50, 50))

        def exists_side_effect(path):
            return "Cruiser.png" in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', return_value=mock_img):
                result = load_topdown_thumbnail(design, target_height=50)

        assert isinstance(result, pygame.Surface)
        assert result.get_height() == 50

    def test_logs_warning_when_file_exists_but_load_fails(self):
        """Logs warning when file exists but load fails."""
        from game.ui.screens.design_image_helper import load_topdown_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.design_id = "test_design"

        def exists_side_effect(path):
            return "Cruiser.png" in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', side_effect=pygame.error("Load failed")):
                with patch('game.ui.screens.design_image_helper.log_warning') as mock_warning:
                    result = load_topdown_thumbnail(design)

        assert mock_warning.called
        assert result is None

    def test_returns_none_for_fully_transparent_image(self):
        """Returns None when image is fully transparent."""
        from game.ui.screens.design_image_helper import load_topdown_thumbnail

        design = Mock()
        design.theme_id = "Federation"
        design.ship_class = "Cruiser"
        design.design_id = "test_design"

        # Create fully transparent image
        mock_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Don't draw anything - fully transparent

        def exists_side_effect(path):
            return "Cruiser.png" in path

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('pygame.image.load', return_value=mock_img):
                result = load_topdown_thumbnail(design)

        assert result is None


class TestGetVisibleBoundingBox:
    """Tests for _get_visible_bounding_box function."""

    def setup_method(self):
        """Initialize pygame display for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def teardown_method(self):
        """Clean up pygame."""
        pygame.quit()

    def test_fully_transparent_surface_returns_none(self):
        """Fully transparent surface returns None."""
        from game.ui.screens.design_image_helper import _get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Don't draw anything - fully transparent

        result = _get_visible_bounding_box(surface)

        assert result is None

    def test_surface_with_visible_pixels_returns_correct_bounding_box(self):
        """Surface with visible pixels returns correct bounding box."""
        from game.ui.screens.design_image_helper import _get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Draw a rectangle from (10, 20) to (60, 80)
        pygame.draw.rect(surface, (255, 0, 0, 255), (10, 20, 50, 60))

        result = _get_visible_bounding_box(surface)

        assert result is not None
        min_x, min_y, max_x, max_y = result
        assert min_x == 10
        assert min_y == 20
        assert max_x == 60  # 10 + 50
        assert max_y == 80  # 20 + 60

    def test_single_visible_pixel_returns_1x1_bounding_box(self):
        """Single visible pixel returns 1x1 bounding box."""
        from game.ui.screens.design_image_helper import _get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Set a single pixel at (50, 50) with full opacity
        surface.set_at((50, 50), (255, 0, 0, 255))

        result = _get_visible_bounding_box(surface)

        assert result is not None
        min_x, min_y, max_x, max_y = result
        assert min_x == 50
        assert min_y == 50
        assert max_x == 51  # min_x + 1
        assert max_y == 51  # min_y + 1
        assert (max_x - min_x) == 1
        assert (max_y - min_y) == 1

    def test_ignores_nearly_transparent_pixels(self):
        """Ignores pixels with alpha <= 10."""
        from game.ui.screens.design_image_helper import _get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Set nearly transparent pixels (should be ignored)
        surface.set_at((0, 0), (255, 0, 0, 5))
        surface.set_at((99, 99), (255, 0, 0, 10))
        # Set one visible pixel
        surface.set_at((50, 50), (255, 0, 0, 255))

        result = _get_visible_bounding_box(surface)

        assert result is not None
        min_x, min_y, max_x, max_y = result
        # Should only find the visible pixel at (50, 50)
        assert min_x == 50
        assert min_y == 50
        assert max_x == 51
        assert max_y == 51
