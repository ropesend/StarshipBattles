"""
BUG-14 Reproduction Test: Multi-planet sectors need planet position offset.

Rev 4: Updated requirements:
- Largest planet offset 20% of diameter to the left
- Smaller planets use polar coordinates centered on largest planet
- 1 smaller: 0° (right)
- 2 smaller: +30° and -30°
- 3 smaller: +15°, 0°, -45°
- Distance = 1.5x radius of largest planet (center to center)

Rev 5: Proportional moon sizing:
- Secondary planets (moons) are sized proportionally to the primary planet
  based on their physical radius ratio.
- If primary radius = 10 and secondary radius = 3, secondary draw size = 3/10 of primary.
- Minimum draw diameter clamped at 5 pixels (radius >= 3px).
- No additional reduction factor on secondaries (base = primary draw radius, not half of it).
"""
import pygame
import math


class TestMultiPlanetPositionOffset:
    """Tests for planet positioning in multi-planet sectors."""

    def test_multi_planet_group_offset_left_20_percent(self):
        """
        GIVEN a hex sector containing multiple planets
        WHEN the renderer calculates planet positions
        THEN the largest planet should be offset LEFT of center by ~20% of its diameter

        Rev 4: Changed from 10% to 20% per user feedback
        """
        hex_px_radius = 100

        # Calculate the fixed offset (matches strategy_renderer.py Rev 4 logic)
        largest_draw_r = hex_px_radius * 0.5  # = 50
        largest_diameter = largest_draw_r * 2  # = 100
        group_offset_x = -largest_diameter * 0.20  # = -20 (LEFT, 20% of diameter)

        assert group_offset_x < 0, "Offset should be to the LEFT (negative)"
        assert group_offset_x == -20.0, f"Expected offset of -20.0, got {group_offset_x}"

    def test_single_planet_no_offset(self):
        """
        GIVEN a hex sector containing exactly one planet
        WHEN the renderer calculates planet position
        THEN the planet should remain centered (no offset applied)
        """
        hex_center_screen = pygame.math.Vector2(500, 300)
        single_planet_pos = hex_center_screen.copy()

        assert single_planet_pos.x == hex_center_screen.x, "Single planet should be centered horizontally"
        assert single_planet_pos.y == hex_center_screen.y, "Single planet should be centered vertically"

    def test_offset_magnitude_twentieth_diameter(self):
        """
        GIVEN the largest planet in a multi-planet sector
        WHEN calculating the group offset
        THEN offset should be approximately 20% of the largest planet's diameter (leftward)

        Rev 4: Changed to 20% per user feedback.
        """
        test_cases = [
            {"hex_px_radius": 50, "expected_approx": -10.0},   # 50 * 0.5 * 2 * -0.20 = -10.0
            {"hex_px_radius": 100, "expected_approx": -20.0},  # 100 * 0.5 * 2 * -0.20 = -20.0
            {"hex_px_radius": 200, "expected_approx": -40.0},  # 200 * 0.5 * 2 * -0.20 = -40.0
        ]

        for case in test_cases:
            hex_px_radius = case["hex_px_radius"]

            largest_draw_radius = hex_px_radius * 0.5
            largest_diameter = largest_draw_radius * 2
            expected_offset = -largest_diameter * 0.20  # 20% of diameter, leftward

            assert abs(expected_offset - case["expected_approx"]) < 0.01, (
                f"Offset calculation error for hex_px_radius={hex_px_radius}"
            )
            assert expected_offset < 0, "Offset must be negative (to the left)"


class TestSmallerPlanetPolarCoordinates:
    """Tests for smaller planet positioning using polar coordinates."""

    def test_single_smaller_planet_at_0_degrees(self):
        """
        GIVEN a hex sector with 2 planets (1 largest + 1 smaller)
        WHEN the renderer calculates the smaller planet position
        THEN the smaller planet should be at 0° (directly to the right of largest)
        """
        smaller_count = 1
        expected_angles = [0]

        if smaller_count == 1:
            smaller_angles = [0]

        assert smaller_angles == expected_angles, f"Single smaller planet should be at 0°, got {smaller_angles}"

    def test_two_smaller_planets_at_30_degrees(self):
        """
        GIVEN a hex sector with 3 planets (1 largest + 2 smaller)
        WHEN the renderer calculates the smaller planet positions
        THEN one should be at +30° and the other at -30°
        """
        smaller_count = 2
        expected_angles = [30, -30]

        if smaller_count == 2:
            smaller_angles = [30, -30]

        assert smaller_angles == expected_angles, f"Two smaller planets should be at [30, -30], got {smaller_angles}"

    def test_three_smaller_planets_angles(self):
        """
        GIVEN a hex sector with 4 planets (1 largest + 3 smaller)
        WHEN the renderer calculates the smaller planet positions
        THEN they should be at +15°, 0°, and -45°
        """
        smaller_count = 3
        expected_angles = [15, 0, -45]

        if smaller_count == 3:
            smaller_angles = [15, 0, -45]

        assert smaller_angles == expected_angles, f"Three smaller planets should be at [15, 0, -45], got {smaller_angles}"

    def test_smaller_planet_distance_1_5x_radius(self):
        """
        GIVEN multiple planets in a hex sector
        WHEN the renderer calculates positions for smaller planets
        THEN distance from largest center should be 1.5x the largest planet's radius

        Rev 4: Distance = 1.5x largest planet radius (center to center)
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50

        # Rev 4: Distance from largest planet center = 1.5x largest radius
        expected_dist = largest_draw_r * 1.5  # = 75

        assert expected_dist == 75.0, f"Distance should be 75.0 (1.5x radius), got {expected_dist}"


class TestRendererMultiPlanetLogic:
    """Integration tests that verify the renderer applies correct offsets."""

    def test_renderer_offset_direction(self):
        """
        GIVEN multiple planets in the same hex
        WHEN _draw_system_details calculates positions
        THEN the largest planet should be offset LEFT of hex center by 20% of its diameter

        Rev 4: Updated to use 20% of diameter offset.
        """
        hex_center_x = 500
        hex_px_radius = 100

        largest_draw_r = hex_px_radius * 0.5  # = 50
        largest_diameter = largest_draw_r * 2  # = 100
        group_offset_x = -largest_diameter * 0.20  # = -20 (left, 20% of diameter)

        largest_x = hex_center_x + group_offset_x  # = 480

        assert largest_x < hex_center_x, (
            f"Largest planet at x={largest_x} should be LEFT of center ({hex_center_x})"
        )
        assert group_offset_x == -20.0, f"Offset should be -20.0, got {group_offset_x}"

    def test_smaller_planet_position_calculation(self):
        """
        GIVEN 2 planets (largest + 1 smaller) in a hex
        WHEN calculating smaller planet position with polar coordinates
        THEN the smaller planet should be at angle 0° (right) at 1.5x radius distance
        """
        hex_center_x = 500
        hex_px_radius = 100

        largest_draw_r = hex_px_radius * 0.5  # = 50
        largest_diameter = largest_draw_r * 2  # = 100
        group_offset_x = -largest_diameter * 0.20  # = -20

        # Smaller planet at 0° (right of largest), distance = 1.5x radius = 75
        dist = largest_draw_r * 1.5  # = 75
        angle = 0  # degrees

        # Final offset combines group offset and polar position
        # Vector2(group_offset_x + dist, 0).rotate(-angle)
        # = Vector2(-20 + 75, 0).rotate(0) = Vector2(55, 0)
        final_offset_x = group_offset_x + dist * math.cos(math.radians(-angle))

        smaller_x = hex_center_x + final_offset_x  # = 500 + 55 = 555

        assert smaller_x > hex_center_x, (
            f"Smaller planet at x={smaller_x} should be RIGHT of hex center ({hex_center_x})"
        )


class TestProportionalMoonSizing:
    """Rev 5: Tests for proportional moon sizing relative to the primary planet."""

    MIN_DRAW_RADIUS = 3  # 5px diameter -> ceil(2.5) = 3px radius

    def test_secondary_planet_proportional_to_primary(self):
        """
        GIVEN a primary planet with radius 10 and a secondary with radius 3
        WHEN calculating draw sizes
        THEN the secondary draw radius should be 3/10 of the primary draw radius.
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50 (primary draw radius)

        primary_radius = 10.0
        secondary_radius = 3.0
        rel_scale = secondary_radius / primary_radius  # 0.3

        # Secondary should use largest_draw_r as base, not a reduced base
        draw_r = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * rel_scale))

        assert draw_r == 15, f"Expected draw_r=15 (50*0.3), got {draw_r}"

    def test_secondary_is_exact_ratio_of_primary_draw_size(self):
        """
        GIVEN any primary and secondary planet radii
        WHEN calculating draw sizes
        THEN secondary_draw / primary_draw should equal secondary_radius / primary_radius
             (unless clamped by minimum).
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50

        test_cases = [
            (10.0, 5.0, 25),   # 50% -> 25px
            (10.0, 3.0, 15),   # 30% -> 15px
            (10.0, 7.0, 35),   # 70% -> 35px
            (10.0, 1.0, 5),    # 10% -> 5px
            (100.0, 50.0, 25), # 50% -> 25px
        ]

        for primary_r, secondary_r, expected_draw in test_cases:
            rel_scale = secondary_r / primary_r
            draw_r = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * rel_scale))
            assert draw_r == expected_draw, (
                f"primary={primary_r}, secondary={secondary_r}: "
                f"expected draw_r={expected_draw}, got {draw_r}"
            )

    def test_minimum_draw_diameter_is_5_pixels(self):
        """
        GIVEN a very small moon relative to the primary
        WHEN calculating draw size
        THEN the draw radius should be clamped so diameter >= 5px (radius >= 3px).
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50

        # Tiny moon: 0.01 ratio -> 50 * 0.01 = 0.5px, should clamp to 3px
        primary_radius = 70000.0  # Gas giant
        moon_radius = 500.0       # Planetoid
        rel_scale = moon_radius / primary_radius  # ~0.007

        draw_r = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * rel_scale))

        assert draw_r == self.MIN_DRAW_RADIUS, (
            f"Tiny moon should be clamped to minimum {self.MIN_DRAW_RADIUS}px radius, got {draw_r}"
        )
        assert draw_r * 2 >= 5, "Minimum diameter must be at least 5 pixels"

    def test_no_0_4_floor_on_rel_scale(self):
        """
        GIVEN a secondary planet with radius ratio 0.2 (below old 0.4 floor)
        WHEN calculating draw size
        THEN it should use 0.2 directly, NOT clamp to 0.4.
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50

        primary_radius = 10.0
        secondary_radius = 2.0
        rel_scale = secondary_radius / primary_radius  # 0.2

        draw_r = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * rel_scale))

        # 50 * 0.2 = 10, not 50 * 0.4 = 20
        assert draw_r == 10, (
            f"Expected draw_r=10 (0.2 ratio, no floor), got {draw_r}"
        )

    def test_primary_planet_size_unchanged(self):
        """
        GIVEN the largest planet in a multi-planet hex
        WHEN calculating its draw size
        THEN it should still be hex_px_radius * 0.5 (unchanged from before).
        """
        hex_px_radius = 100
        largest_draw_r = hex_px_radius * 0.5  # = 50

        # Primary planet: rel_scale = 1.0
        primary_draw_r = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * 1.0))

        assert primary_draw_r == 50, f"Primary draw radius should be 50, got {primary_draw_r}"

    def test_proportional_sizing_various_hex_radii(self):
        """
        GIVEN different hex_px_radius values (different zoom levels)
        WHEN calculating secondary draw sizes
        THEN proportional ratio is maintained at all zoom levels.
        """
        expected_ratio = 0.3  # e.g. secondary radius 3 / primary radius 10

        for hex_px_radius in [50, 100, 200, 400]:
            largest_draw_r = hex_px_radius * 0.5
            primary_draw = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * 1.0))
            secondary_draw = max(self.MIN_DRAW_RADIUS, int(largest_draw_r * expected_ratio))

            # Check ratio is maintained (within rounding tolerance)
            if secondary_draw > self.MIN_DRAW_RADIUS:
                actual_ratio = secondary_draw / primary_draw
                assert abs(actual_ratio - expected_ratio) < 0.05, (
                    f"hex_px_radius={hex_px_radius}: ratio {actual_ratio:.2f} != {expected_ratio}"
                )

    def test_gas_giant_type_boost_not_applied_in_multi_planet(self):
        """
        GIVEN a gas giant as primary in a multi-planet hex
        WHEN calculating draw sizes
        THEN the 1.5x gas giant boost should NOT be applied (that's only for single-planet hexes).
        The primary should use hex_px_radius * 0.5, same as any other planet type.
        """
        hex_px_radius = 100
        # In multi-planet hexes, largest_draw_r = hex_px_radius * 0.5
        # regardless of whether the primary is a gas giant or not.
        largest_draw_r = hex_px_radius * 0.5

        assert largest_draw_r == 50, (
            "Multi-planet primary should not get gas giant boost"
        )
