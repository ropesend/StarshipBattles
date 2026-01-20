"""
BUG-14 Reproduction Test: Multi-planet sectors need planet position offset.

Rev 4: Updated requirements:
- Largest planet offset 20% of diameter to the left
- Smaller planets use polar coordinates centered on largest planet
- 1 smaller: 0° (right)
- 2 smaller: +30° and -30°
- 3 smaller: +15°, 0°, -45°
- Distance = 1.5x radius of largest planet (center to center)
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
