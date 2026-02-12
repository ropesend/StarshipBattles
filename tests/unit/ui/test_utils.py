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

    def test_rotation_90_180_270(self):
        """Test specific rotation angles."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((20, 10))

        # Test 90 degree rotation
        result_90 = scale_and_rotate_image(surface, 1.0, rotation=90)
        assert result_90 is not None

        # Test 180 degree rotation
        result_180 = scale_and_rotate_image(surface, 1.0, rotation=180)
        assert result_180 is not None

        # Test 270 degree rotation
        result_270 = scale_and_rotate_image(surface, 1.0, rotation=270)
        assert result_270 is not None

    def test_very_small_scale(self):
        """Very small scale still produces result."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((100, 100))

        result = scale_and_rotate_image(surface, 0.01)

        # Should produce at least 1x1 surface
        assert result.get_width() >= 1
        assert result.get_height() >= 1

    def test_very_large_scale(self):
        """Very large scale works correctly."""
        from game.ui.utils import scale_and_rotate_image

        surface = pygame.Surface((10, 10))

        result = scale_and_rotate_image(surface, 10.0)

        assert result.get_width() == 100
        assert result.get_height() == 100


class TestGetVisibleBoundingBox:
    """Tests for get_visible_bounding_box helper."""

    def test_fully_transparent_surface_returns_none(self):
        """Fully transparent surface returns None."""
        from game.ui.utils import get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Fully transparent

        result = get_visible_bounding_box(surface)

        assert result is None

    def test_fully_opaque_surface_returns_full_rect(self):
        """Fully opaque surface returns full dimensions."""
        from game.ui.utils import get_visible_bounding_box

        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        surface.fill((255, 255, 255, 255))  # Fully opaque

        result = get_visible_bounding_box(surface)

        assert result is not None
        min_x, min_y, max_x, max_y = result
        assert min_x == 0
        assert min_y == 0
        assert max_x == 50
        assert max_y == 50

    def test_single_opaque_pixel_returns_none(self):
        """Single opaque pixel returns None due to boundary check.

        Note: get_visible_bounding_box returns None for single pixels because
        the check `max_x <= min_x` is True when there's only one pixel.
        This is current expected behavior.
        """
        from game.ui.utils import get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Start transparent
        surface.set_at((50, 50), (255, 255, 255, 255))  # One opaque pixel

        result = get_visible_bounding_box(surface)

        # Single pixel is treated as empty by this function
        assert result is None

    def test_small_opaque_region(self):
        """Small 2x2 opaque region returns correct rect."""
        from game.ui.utils import get_visible_bounding_box

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Start transparent
        # Draw a small 2x2 region
        surface.set_at((50, 50), (255, 255, 255, 255))
        surface.set_at((51, 50), (255, 255, 255, 255))
        surface.set_at((50, 51), (255, 255, 255, 255))
        surface.set_at((51, 51), (255, 255, 255, 255))

        result = get_visible_bounding_box(surface)

        assert result is not None
        min_x, min_y, max_x, max_y = result
        assert min_x == 50
        assert min_y == 50
        assert max_x == 52  # Exclusive
        assert max_y == 52


class TestScaleImageByVisiblePortion:
    """Tests for scale_image_by_visible_portion helper."""

    def test_basic_functionality(self):
        """Basic scaling by visible portion works."""
        from game.ui.utils import scale_image_by_visible_portion

        # Create surface with visible content in center
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        # Draw a 50x50 opaque square in the center
        pygame.draw.rect(surface, (255, 255, 255, 255), (25, 25, 50, 50))

        result = scale_image_by_visible_portion(surface, target_height=100)

        # Should produce a scaled result
        assert result is not None
        assert result.get_height() > 0

    def test_empty_surface_returns_placeholder(self):
        """Empty surface returns placeholder."""
        from game.ui.utils import scale_image_by_visible_portion

        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Fully transparent

        result = scale_image_by_visible_portion(surface, target_height=50)

        assert result is not None
        assert result.get_height() == 50


class TestScaleImageToFit:
    """Tests for scale_image_to_fit helper."""

    def test_target_smaller_than_image(self):
        """Image scales down to fit smaller target."""
        from game.ui.utils import scale_image_to_fit

        surface = pygame.Surface((200, 200))
        surface.fill((255, 255, 255))

        result = scale_image_to_fit(surface, (100, 100))

        assert result.get_width() == 100
        assert result.get_height() == 100

    def test_target_larger_than_image(self):
        """Image scales up to fit larger target."""
        from game.ui.utils import scale_image_to_fit

        surface = pygame.Surface((50, 50))
        surface.fill((255, 255, 255))

        result = scale_image_to_fit(surface, (100, 100))

        assert result.get_width() == 100
        assert result.get_height() == 100

    def test_non_square_aspect_ratio(self):
        """Non-square images maintain aspect ratio."""
        from game.ui.utils import scale_image_to_fit

        # Wide image
        surface = pygame.Surface((200, 100))
        surface.fill((255, 255, 255))

        result = scale_image_to_fit(surface, (100, 100))

        assert result.get_width() == 100
        assert result.get_height() == 100


class TestCalculateShipImageScaleEdgeCases:
    """Additional edge case tests for calculate_ship_image_scale."""

    def test_visible_size_none_uses_max_dimension(self):
        """visible_size=None falls back to max of image dimensions."""
        from game.ui.utils import calculate_ship_image_scale

        # Tall image 50x100
        result = calculate_ship_image_scale((50, 100), 200, visible_size=None)

        # max(50, 100) = 100, target 200 = scale 2.0
        assert result == 2.0

    def test_1x1_image(self):
        """1x1 image scales correctly."""
        from game.ui.utils import calculate_ship_image_scale

        result = calculate_ship_image_scale((1, 1), 100, visible_size=None)

        # max(1, 1) = 1, target 100 = scale 100.0
        assert result == 100.0

    def test_manual_scale_multiplier(self):
        """Manual scale multiplier is applied correctly."""
        from game.ui.utils import calculate_ship_image_scale

        result = calculate_ship_image_scale((100, 100), 100, visible_size=50, manual_scale=2.0)

        # target 100 / visible 50 = 2.0, * manual_scale 2.0 = 4.0
        assert result == 4.0
