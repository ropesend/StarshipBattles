"""
Unit tests for schematic view rendering logic.

Tests weapon arc colors, cache key generation, rect center calculation,
image scaling, and component hit testing.
Focuses on pure logic testing without pygame initialization.
"""
import pytest
import math
from types import SimpleNamespace


# =============================================================================
# Tests for weapon arc color selection
# =============================================================================

class TestWeaponArcColorSelection:
    """Tests for weapon arc color selection."""

    def get_weapon_arc_color(self, is_beam_weapon):
        """
        Get color for a weapon arc based on weapon type.

        Args:
            is_beam_weapon: True if weapon has BeamWeaponAbility

        Returns:
            RGBA color tuple
        """
        if is_beam_weapon:
            return (100, 255, 255, 100)  # Cyan for beams
        else:
            return (255, 200, 100, 100)  # Orange for projectiles

    def test_beam_weapon_color(self):
        """Test color for beam weapons (cyan)."""
        color = self.get_weapon_arc_color(is_beam_weapon=True)
        assert color == (100, 255, 255, 100)
        # Verify it's predominantly blue/cyan
        assert color[1] == 255  # Green channel high
        assert color[2] == 255  # Blue channel high
        assert color[0] < color[1]  # Red less than green

    def test_projectile_weapon_color(self):
        """Test color for projectile weapons (orange)."""
        color = self.get_weapon_arc_color(is_beam_weapon=False)
        assert color == (255, 200, 100, 100)
        # Verify it's predominantly orange
        assert color[0] == 255  # Red channel high
        assert color[2] < color[0]  # Blue less than red

    def test_colors_are_distinct(self):
        """Test that beam and projectile colors are distinct."""
        beam_color = self.get_weapon_arc_color(is_beam_weapon=True)
        proj_color = self.get_weapon_arc_color(is_beam_weapon=False)
        assert beam_color != proj_color


# =============================================================================
# Tests for cache key generation
# =============================================================================

class TestCacheKeyGeneration:
    """Tests for arc cache key generation."""

    def generate_cache_key(self, weapon_id, weapon_range, arc_degrees, facing, screen_size):
        """
        Generate cache key for a weapon arc.

        Args:
            weapon_id: Unique weapon identifier
            weapon_range: Weapon range
            arc_degrees: Firing arc in degrees
            facing: Facing angle
            screen_size: Tuple of (width, height)

        Returns:
            Cache key tuple
        """
        return (weapon_id, weapon_range, arc_degrees, facing, screen_size)

    def test_cache_key_includes_all_params(self):
        """Test that cache key includes all parameters."""
        key = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        assert len(key) == 5
        assert key[0] == "laser_1"
        assert key[1] == 1000
        assert key[2] == 20
        assert key[3] == 0
        assert key[4] == (800, 600)

    def test_different_weapons_different_keys(self):
        """Test that different weapons produce different keys."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_2", 1000, 20, 0, (800, 600))
        assert key1 != key2

    def test_different_ranges_different_keys(self):
        """Test that different ranges produce different keys."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_1", 2000, 20, 0, (800, 600))
        assert key1 != key2

    def test_different_arcs_different_keys(self):
        """Test that different arcs produce different keys."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_1", 1000, 40, 0, (800, 600))
        assert key1 != key2

    def test_different_facing_different_keys(self):
        """Test that different facing angles produce different keys."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_1", 1000, 20, 90, (800, 600))
        assert key1 != key2

    def test_different_screen_size_different_keys(self):
        """Test that different screen sizes produce different keys."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_1", 1000, 20, 0, (1920, 1080))
        assert key1 != key2

    def test_same_params_same_key(self):
        """Test that same parameters produce same key."""
        key1 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        key2 = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        assert key1 == key2

    def test_key_is_hashable(self):
        """Test that cache key is hashable (usable as dict key)."""
        key = self.generate_cache_key("laser_1", 1000, 20, 0, (800, 600))
        cache = {}
        cache[key] = "test_value"
        assert cache[key] == "test_value"


# =============================================================================
# Tests for rect center calculation
# =============================================================================

class TestRectCenterCalculation:
    """Tests for view rect center calculation."""

    def calculate_center(self, rect):
        """
        Calculate center point of a rect.

        Args:
            rect: Object with x, y, width, height attributes

        Returns:
            Tuple of (cx, cy)
        """
        return (rect.x + rect.width // 2, rect.y + rect.height // 2)

    def test_origin_rect(self):
        """Test center of rect at origin."""
        rect = SimpleNamespace(x=0, y=0, width=100, height=100)
        cx, cy = self.calculate_center(rect)
        assert cx == 50
        assert cy == 50

    def test_offset_rect(self):
        """Test center of offset rect."""
        rect = SimpleNamespace(x=100, y=200, width=100, height=100)
        cx, cy = self.calculate_center(rect)
        assert cx == 150
        assert cy == 250

    def test_non_square_rect(self):
        """Test center of non-square rect."""
        rect = SimpleNamespace(x=0, y=0, width=200, height=100)
        cx, cy = self.calculate_center(rect)
        assert cx == 100
        assert cy == 50

    def test_large_rect(self):
        """Test center of large rect."""
        rect = SimpleNamespace(x=0, y=0, width=1920, height=1080)
        cx, cy = self.calculate_center(rect)
        assert cx == 960
        assert cy == 540


# =============================================================================
# Tests for image scaling calculation
# =============================================================================

class TestImageScalingCalculation:
    """Tests for ship image scaling calculations."""

    def calculate_scale_factor(self, target_diameter, visible_size, manual_scale=1.0):
        """
        Calculate scale factor for ship image.

        Args:
            target_diameter: Target diameter (2 * max_r)
            visible_size: Current visible size of the image
            manual_scale: Manual scale override

        Returns:
            Scale factor to apply to image
        """
        if visible_size < 1:
            visible_size = 1
        if manual_scale <= 0:
            manual_scale = 1.0
        return (target_diameter / visible_size) * manual_scale

    def test_image_fits_exactly(self):
        """Test when image size matches target."""
        scale = self.calculate_scale_factor(200, 200)
        assert math.isclose(scale, 1.0, abs_tol=0.01)

    def test_image_needs_enlargement(self):
        """Test when image needs to be enlarged."""
        scale = self.calculate_scale_factor(200, 100)
        assert math.isclose(scale, 2.0, abs_tol=0.01)

    def test_image_needs_shrinking(self):
        """Test when image needs to be shrunk."""
        scale = self.calculate_scale_factor(200, 400)
        assert math.isclose(scale, 0.5, abs_tol=0.01)

    def test_manual_scale_multiplier(self):
        """Test manual scale multiplier."""
        scale = self.calculate_scale_factor(200, 200, manual_scale=1.5)
        assert math.isclose(scale, 1.5, abs_tol=0.01)

    def test_zero_visible_size_protection(self):
        """Test protection against zero visible size."""
        scale = self.calculate_scale_factor(200, 0)
        # Should treat 0 as 1
        assert math.isclose(scale, 200.0, abs_tol=0.01)

    def test_negative_manual_scale_protection(self):
        """Test protection against negative manual scale."""
        scale = self.calculate_scale_factor(200, 200, manual_scale=-1.0)
        # Should treat negative as 1.0
        assert math.isclose(scale, 1.0, abs_tol=0.01)

    def test_zero_manual_scale_protection(self):
        """Test protection against zero manual scale."""
        scale = self.calculate_scale_factor(200, 200, manual_scale=0.0)
        # Should treat zero as 1.0
        assert math.isclose(scale, 1.0, abs_tol=0.01)


# =============================================================================
# Tests for scaled image dimensions
# =============================================================================

class TestScaledImageDimensions:
    """Tests for calculating scaled image dimensions."""

    def calculate_scaled_dimensions(self, orig_width, orig_height, scale_factor):
        """
        Calculate scaled image dimensions.

        Args:
            orig_width, orig_height: Original image dimensions
            scale_factor: Scale factor to apply

        Returns:
            Tuple of (new_width, new_height)
        """
        new_w = int(orig_width * scale_factor)
        new_h = int(orig_height * scale_factor)
        return (new_w, new_h)

    def test_no_scaling(self):
        """Test dimensions with no scaling."""
        w, h = self.calculate_scaled_dimensions(100, 100, 1.0)
        assert w == 100
        assert h == 100

    def test_double_scaling(self):
        """Test dimensions with 2x scaling."""
        w, h = self.calculate_scaled_dimensions(100, 100, 2.0)
        assert w == 200
        assert h == 200

    def test_half_scaling(self):
        """Test dimensions with 0.5x scaling."""
        w, h = self.calculate_scaled_dimensions(100, 100, 0.5)
        assert w == 50
        assert h == 50

    def test_non_square_image(self):
        """Test scaling non-square image."""
        w, h = self.calculate_scaled_dimensions(200, 100, 1.5)
        assert w == 300
        assert h == 150

    def test_fractional_result(self):
        """Test that fractional results are truncated."""
        w, h = self.calculate_scaled_dimensions(100, 100, 0.33)
        assert w == 33
        assert h == 33


# =============================================================================
# Tests for get_component_at behavior
# =============================================================================

class TestGetComponentAt:
    """Tests for get_component_at (disabled) behavior."""

    def get_component_at(self, pos, ship):
        """
        Get component at position (DISABLED).
        Always returns None per user request.
        """
        return None

    def test_always_returns_none(self):
        """Test that get_component_at always returns None."""
        result = self.get_component_at((100, 100), "any_ship")
        assert result is None

    def test_returns_none_regardless_of_position(self):
        """Test that any position returns None."""
        positions = [(0, 0), (100, 100), (-50, -50), (1000, 1000)]
        for pos in positions:
            assert self.get_component_at(pos, "ship") is None
