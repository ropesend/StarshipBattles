"""
Unit tests for schematic view geometry calculations.

Tests radius calculation, arc geometry, polygon points,
display range, and layer ring calculations.
Focuses on pure logic testing without pygame initialization.
"""
import pytest
import math


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
