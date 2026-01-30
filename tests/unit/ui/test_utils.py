"""
Tests for game.ui.utils module.

PROJ-44 Task 1.2: Extract Window Rect Creation Helper
PROJ-44 Task 1.3: Extract Image Scaling Utility
"""
import pytest
import pygame
from unittest.mock import MagicMock


class TestCreateCenteredRect:
    """Tests for create_centered_rect helper function."""

    def test_creates_pygame_rect(self):
        """Should return a pygame.Rect instance."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(200, 100, 800, 600)

        assert isinstance(result, pygame.Rect)

    def test_centers_horizontally(self):
        """Rect should be centered horizontally."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(200, 100, 800, 600)

        # Center X should be at 400 (screen_width / 2)
        # Rect left should be at 300 (400 - 100)
        assert result.centerx == 400
        assert result.left == 300

    def test_centers_vertically(self):
        """Rect should be centered vertically."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(200, 100, 800, 600)

        # Center Y should be at 300 (screen_height / 2)
        # Rect top should be at 250 (300 - 50)
        assert result.centery == 300
        assert result.top == 250

    def test_preserves_dimensions(self):
        """Rect should have the requested width and height."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(200, 100, 800, 600)

        assert result.width == 200
        assert result.height == 100

    def test_large_window_on_small_screen(self):
        """Should handle window larger than screen (negative offsets)."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(1000, 800, 800, 600)

        # Should still center, even if offscreen
        assert result.centerx == 400
        assert result.centery == 300
        assert result.left == -100  # (800 - 1000) // 2
        assert result.top == -100   # (600 - 800) // 2

    def test_odd_dimensions_round_down(self):
        """Integer division should round down for odd differences."""
        from game.ui.utils import create_centered_rect

        result = create_centered_rect(201, 101, 800, 600)

        # (800 - 201) // 2 = 299
        assert result.left == 299
        # (600 - 101) // 2 = 249
        assert result.top == 249


class TestCalculateShipImageScale:
    """Tests for calculate_ship_image_scale helper (PROJ-44 Task 1.3)."""

    def test_basic_scaling(self):
        """Basic scale calculation with default parameters."""
        from game.ui.utils import calculate_ship_image_scale

        # 100x100 image, target 200px = scale factor 2.0
        result = calculate_ship_image_scale((100, 100), 200)

        assert result == 2.0

    def test_with_visible_size(self):
        """Scale based on visible_size instead of image size."""
        from game.ui.utils import calculate_ship_image_scale

        # Image is 200x200 but visible content is only 100x100
        # Target 200 / visible 100 = scale 2.0
        result = calculate_ship_image_scale((200, 200), 200, visible_size=100)

        assert result == 2.0

    def test_with_manual_scale(self):
        """Manual scale multiplier is applied."""
        from game.ui.utils import calculate_ship_image_scale

        # Base scale would be 2.0, manual scale 1.5 = 3.0
        result = calculate_ship_image_scale((100, 100), 200, manual_scale=1.5)

        assert result == 3.0

    def test_visible_size_fallback(self):
        """Falls back to max(image_size) when visible_size is None."""
        from game.ui.utils import calculate_ship_image_scale

        # Image is 200x100, max is 200, target 400 = scale 2.0
        result = calculate_ship_image_scale((200, 100), 400, visible_size=None)

        assert result == 2.0

    def test_handles_zero_visible_size(self):
        """Handles visible_size of 0 without division error."""
        from game.ui.utils import calculate_ship_image_scale

        # visible_size=0 should fall back to image dimensions
        result = calculate_ship_image_scale((100, 50), 200, visible_size=0)

        # Falls back to max(100, 50) = 100, target 200 = scale 2.0
        assert result == 2.0


class TestScaleAndRotateImage:
    """Tests for scale_and_rotate_image helper (PROJ-44 Task 1.3)."""

    def test_scale_only(self):
        """Scaling without rotation."""
        from game.ui.utils import scale_and_rotate_image

        # Create a 10x10 surface
        surface = pygame.Surface((10, 10))

        result = scale_and_rotate_image(surface, 2.0)

        assert result.get_width() == 20
        assert result.get_height() == 20

    def test_scale_down(self):
        """Scaling down works correctly."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((100, 100))

        result = scale_and_rotate_image(surface, 0.5)

        assert result.get_width() == 50
        assert result.get_height() == 50

    def test_zero_scale_returns_original(self):
        """Zero scale returns original image."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((10, 10))

        result = scale_and_rotate_image(surface, 0)

        assert result.get_size() == (10, 10)

    def test_negative_scale_returns_original(self):
        """Negative scale returns original image."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((10, 10))

        result = scale_and_rotate_image(surface, -1.0)

        assert result.get_size() == (10, 10)

    def test_with_rotation(self):
        """Scale and rotation combined."""
        from game.ui.utils import scale_and_rotate_image

        # Create rectangular surface to see rotation effect
        surface = pygame.Surface((20, 10))

        result = scale_and_rotate_image(surface, 1.0, rotation=90)

        # After 90 degree rotation, dimensions swap
        # Note: pygame.transform.rotate may add padding
        assert result.get_height() >= 20  # Original width becomes height
        assert result.get_width() >= 10   # Original height becomes width
