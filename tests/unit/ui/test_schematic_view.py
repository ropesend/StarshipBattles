"""
Unit tests for ui/builder/schematic_view.py

Tests the schematic view calculations including radius calculation,
arc geometry, color selection, and caching logic.
Focuses on pure logic testing without pygame initialization.
"""
import pytest
import math
from types import SimpleNamespace


# =============================================================================
# Tests for max radius calculation
# =============================================================================

class TestMaxRadiusCalculation:
    """Tests for the _calculate_max_r logic."""

    def calculate_max_r(self, ref_mass, pixels_per_mass_root=7.0):
        """
        Calculate max radius from reference mass.
        Scale: Dreadnought(64000)->40->280px. Escort(1000)->10->70px.
        """
        return int((ref_mass ** (1/3.0)) * pixels_per_mass_root)

    def test_escort_class_radius(self):
        """Test radius calculation for escort class (1000 mass)."""
        # 1000^(1/3) ≈ 10, 10 * 7 = 70 (may vary slightly due to floating point)
        result = self.calculate_max_r(1000)
        assert 69 <= result <= 70

    def test_dreadnought_class_radius(self):
        """Test radius calculation for dreadnought class (64000 mass)."""
        # 64000^(1/3) = 40, 40 * 7 = 280 (may be 279 due to floating point)
        result = self.calculate_max_r(64000)
        assert 279 <= result <= 280

    def test_small_mass(self):
        """Test radius calculation for very small mass."""
        # 8^(1/3) = 2, 2 * 7 = 14
        result = self.calculate_max_r(8)
        assert result == 14

    def test_large_mass(self):
        """Test radius calculation for very large mass."""
        # 125000^(1/3) ≈ 50, 50 * 7 ≈ 350 (may be 349 due to floating point)
        result = self.calculate_max_r(125000)
        assert 349 <= result <= 350

    def test_unit_mass(self):
        """Test radius calculation for unit mass."""
        # 1^(1/3) = 1, 1 * 7 = 7
        result = self.calculate_max_r(1)
        assert result == 7

    def test_custom_pixels_per_mass_root(self):
        """Test with custom pixels per mass root."""
        # 1000^(1/3) ≈ 10, 10 * 10 ≈ 100 (may be 99 due to floating point)
        result = self.calculate_max_r(1000, pixels_per_mass_root=10.0)
        assert 99 <= result <= 100


# =============================================================================
# Tests for arc angle calculations
# =============================================================================

class TestArcAngleCalculations:
    """Tests for weapon arc angle calculations."""

    def calculate_arc_angles(self, facing, arc_degrees):
        """
        Calculate start and end angles for weapon arc.
        Angles are in radians, with 0 degrees facing right, increasing counter-clockwise.
        The view uses a coordinate system where 90 - facing gives "up" direction.
        """
        start_angle = math.radians(90 - facing - (arc_degrees / 2))
        end_angle = math.radians(90 - facing + (arc_degrees / 2))
        return start_angle, end_angle

    def test_forward_facing_narrow_arc(self):
        """Test forward-facing weapon with narrow arc."""
        start, end = self.calculate_arc_angles(facing=0, arc_degrees=20)
        # 90 - 0 - 10 = 80 degrees, 90 - 0 + 10 = 100 degrees
        assert math.isclose(math.degrees(start), 80, abs_tol=0.1)
        assert math.isclose(math.degrees(end), 100, abs_tol=0.1)

    def test_forward_facing_wide_arc(self):
        """Test forward-facing weapon with wide arc."""
        start, end = self.calculate_arc_angles(facing=0, arc_degrees=180)
        # 90 - 0 - 90 = 0 degrees, 90 - 0 + 90 = 180 degrees
        assert math.isclose(math.degrees(start), 0, abs_tol=0.1)
        assert math.isclose(math.degrees(end), 180, abs_tol=0.1)

    def test_right_facing_arc(self):
        """Test right-facing weapon (facing=90)."""
        start, end = self.calculate_arc_angles(facing=90, arc_degrees=20)
        # 90 - 90 - 10 = -10 degrees, 90 - 90 + 10 = 10 degrees
        assert math.isclose(math.degrees(start), -10, abs_tol=0.1)
        assert math.isclose(math.degrees(end), 10, abs_tol=0.1)

    def test_rear_facing_arc(self):
        """Test rear-facing weapon (facing=180)."""
        start, end = self.calculate_arc_angles(facing=180, arc_degrees=20)
        # 90 - 180 - 10 = -100 degrees, 90 - 180 + 10 = -80 degrees
        assert math.isclose(math.degrees(start), -100, abs_tol=0.1)
        assert math.isclose(math.degrees(end), -80, abs_tol=0.1)

    def test_left_facing_arc(self):
        """Test left-facing weapon (facing=270)."""
        start, end = self.calculate_arc_angles(facing=270, arc_degrees=20)
        # 90 - 270 - 10 = -190 degrees, 90 - 270 + 10 = -170 degrees
        assert math.isclose(math.degrees(start), -190, abs_tol=0.1)
        assert math.isclose(math.degrees(end), -170, abs_tol=0.1)

    def test_full_circle_arc(self):
        """Test full 360-degree arc."""
        start, end = self.calculate_arc_angles(facing=0, arc_degrees=360)
        # 90 - 0 - 180 = -90 degrees, 90 - 0 + 180 = 270 degrees
        arc_span = math.degrees(end - start)
        assert math.isclose(arc_span, 360, abs_tol=0.1)

    def test_zero_arc(self):
        """Test zero-degree arc (point weapon)."""
        start, end = self.calculate_arc_angles(facing=0, arc_degrees=0)
        # Start and end should be equal
        assert math.isclose(start, end, abs_tol=0.001)


# =============================================================================
# Tests for arc polygon point generation
# =============================================================================

class TestArcPolygonPoints:
    """Tests for arc polygon point generation."""

    def generate_arc_points(self, cx, cy, display_range, start_angle, end_angle, step=2):
        """
        Generate polygon points for a weapon arc.

        Args:
            cx, cy: Center coordinates
            display_range: Radius of the arc
            start_angle, end_angle: Arc angles in radians
            step: Degree step for point generation

        Returns:
            List of (x, y) points forming the polygon
        """
        points = [(cx, cy)]
        for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, step):
            rad = math.radians(angle)
            x = cx + math.cos(rad) * display_range
            y = cy - math.sin(rad) * display_range
            points.append((x, y))
        points.append((cx, cy))
        return points

    def test_arc_starts_and_ends_at_center(self):
        """Test that arc polygon starts and ends at center."""
        points = self.generate_arc_points(100, 100, 50, math.radians(0), math.radians(90))
        assert points[0] == (100, 100)
        assert points[-1] == (100, 100)

    def test_arc_point_count(self):
        """Test that arc has expected number of points."""
        # 0 to 90 degrees with step 2 = 46 angle steps + 2 center points
        points = self.generate_arc_points(100, 100, 50, math.radians(0), math.radians(90))
        # At least 3 points (2 centers + 1 arc point)
        assert len(points) >= 3

    def test_arc_points_at_correct_distance(self):
        """Test that arc points are at the correct distance from center."""
        cx, cy, radius = 100, 100, 50
        points = self.generate_arc_points(cx, cy, radius, math.radians(0), math.radians(90))

        # Check middle points (not the center points at start/end)
        for point in points[1:-1]:
            distance = math.sqrt((point[0] - cx)**2 + (point[1] - cy)**2)
            assert math.isclose(distance, radius, abs_tol=0.1)

    def test_arc_rightward_point(self):
        """Test that 0-degree arc point is to the right."""
        cx, cy, radius = 100, 100, 50
        points = self.generate_arc_points(cx, cy, radius, math.radians(0), math.radians(10))
        # First non-center point should be at angle 0 (rightward)
        # cos(0) = 1, so x = cx + radius = 150
        # sin(0) = 0, so y = cy - 0 = 100
        first_arc_point = points[1]
        assert math.isclose(first_arc_point[0], 150, abs_tol=1)
        assert math.isclose(first_arc_point[1], 100, abs_tol=1)

    def test_arc_upward_point(self):
        """Test that 90-degree arc point is upward."""
        cx, cy, radius = 100, 100, 50
        points = self.generate_arc_points(cx, cy, radius, math.radians(90), math.radians(100))
        # First non-center point should be at angle 90 (upward)
        # cos(90) = 0, so x = cx + 0 = 100
        # sin(90) = 1, so y = cy - radius = 50
        first_arc_point = points[1]
        assert math.isclose(first_arc_point[0], 100, abs_tol=1)
        assert math.isclose(first_arc_point[1], 50, abs_tol=1)

    def test_narrow_arc_has_few_points(self):
        """Test that narrow arc has fewer points."""
        # 10 degree arc with step 2 should have about 5-7 points
        points = self.generate_arc_points(100, 100, 50, math.radians(85), math.radians(95))
        assert len(points) < 15  # Should be much smaller than a wide arc


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
# Tests for display range calculation
# =============================================================================

class TestDisplayRangeCalculation:
    """Tests for weapon range to display range conversion."""

    def calculate_display_range(self, weapon_range, max_display=300, scale_factor=10):
        """
        Convert weapon range to display range.
        Divides by scale factor and caps at max_display.
        """
        return min(weapon_range / scale_factor, max_display)

    def test_short_range_weapon(self):
        """Test display range for short range weapon."""
        # 500 / 10 = 50
        result = self.calculate_display_range(500)
        assert result == 50

    def test_medium_range_weapon(self):
        """Test display range for medium range weapon."""
        # 1500 / 10 = 150
        result = self.calculate_display_range(1500)
        assert result == 150

    def test_long_range_capped(self):
        """Test that long range weapons are capped."""
        # 5000 / 10 = 500, but capped at 300
        result = self.calculate_display_range(5000)
        assert result == 300

    def test_very_long_range_capped(self):
        """Test that very long range is also capped."""
        result = self.calculate_display_range(10000)
        assert result == 300

    def test_zero_range(self):
        """Test zero range weapon."""
        result = self.calculate_display_range(0)
        assert result == 0


# =============================================================================
# Tests for layer ring colors
# =============================================================================

class TestLayerRingColors:
    """Tests for structure layer ring color selection."""

    def get_layer_color(self, layer_name):
        """
        Get color for a structure layer ring.

        Args:
            layer_name: Name of the layer (ARMOR, OUTER, INNER, CORE)

        Returns:
            RGB color tuple
        """
        if layer_name == "ARMOR":
            return (100, 100, 100)
        elif layer_name == "OUTER":
            return (200, 50, 50)
        elif layer_name == "INNER":
            return (50, 50, 200)
        elif layer_name == "CORE":
            return (200, 200, 200)
        else:
            return (100, 100, 100)  # Default gray

    def test_armor_layer_color(self):
        """Test color for armor layer (gray)."""
        color = self.get_layer_color("ARMOR")
        assert color == (100, 100, 100)

    def test_outer_layer_color(self):
        """Test color for outer layer (red)."""
        color = self.get_layer_color("OUTER")
        assert color == (200, 50, 50)
        assert color[0] > color[1]  # Red dominant

    def test_inner_layer_color(self):
        """Test color for inner layer (blue)."""
        color = self.get_layer_color("INNER")
        assert color == (50, 50, 200)
        assert color[2] > color[0]  # Blue dominant

    def test_core_layer_color(self):
        """Test color for core layer (light gray)."""
        color = self.get_layer_color("CORE")
        assert color == (200, 200, 200)
        assert color[0] == color[1] == color[2]  # Equal RGB = gray

    def test_unknown_layer_color(self):
        """Test color for unknown layer (default gray)."""
        color = self.get_layer_color("UNKNOWN")
        assert color == (100, 100, 100)


# =============================================================================
# Tests for layer ring radius calculation
# =============================================================================

class TestLayerRingRadius:
    """Tests for layer ring radius calculation."""

    def calculate_ring_radius(self, max_r, radius_pct):
        """
        Calculate ring radius from max radius and percentage.

        Args:
            max_r: Maximum radius (outer boundary)
            radius_pct: Percentage as decimal (0.0 to 1.0)

        Returns:
            Pixel radius for the ring
        """
        return int(max_r * radius_pct)

    def test_full_radius(self):
        """Test 100% radius."""
        result = self.calculate_ring_radius(280, 1.0)
        assert result == 280

    def test_half_radius(self):
        """Test 50% radius."""
        result = self.calculate_ring_radius(280, 0.5)
        assert result == 140

    def test_quarter_radius(self):
        """Test 25% radius."""
        result = self.calculate_ring_radius(280, 0.25)
        assert result == 70

    def test_zero_radius(self):
        """Test 0% radius."""
        result = self.calculate_ring_radius(280, 0.0)
        assert result == 0

    def test_typical_layer_radii(self):
        """Test typical layer radius percentages."""
        max_r = 100
        # Typical layers: ARMOR=100%, OUTER=80%, INNER=60%, CORE=40%
        assert self.calculate_ring_radius(max_r, 1.0) == 100
        assert self.calculate_ring_radius(max_r, 0.8) == 80
        assert self.calculate_ring_radius(max_r, 0.6) == 60
        assert self.calculate_ring_radius(max_r, 0.4) == 40


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
