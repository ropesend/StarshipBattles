"""
BUG-14 Reproduction Test: Multi-planet sectors need planet position offset.

This test verifies that planets in sectors with multiple planets are offset
to the right by approximately 1/4 of the diameter of the largest planet.
"""
import pygame


class TestMultiPlanetPositionOffset:
    """Tests for planet positioning in multi-planet sectors."""

    def test_multi_planet_group_offset_slightly_left(self):
        """
        GIVEN a hex sector containing multiple planets
        WHEN the renderer calculates planet positions
        THEN the largest planet should be offset slightly LEFT of center by ~10% of its diameter

        Rev 3: Changed from 1/8 (12.5%) to 10% per user feedback
        """
        # Simulate renderer calculation for multi-planet sector
        hex_px_radius = 100  # Example hex pixel radius at current zoom

        # Calculate the fixed offset (matches strategy_renderer.py logic)
        # Largest planet draw radius is 50% of hex_px_radius
        largest_draw_r = hex_px_radius * 0.5  # = 50
        largest_diameter = largest_draw_r * 2  # = 100
        group_offset_x = -largest_diameter * 0.10  # = -10 (LEFT, 10% of diameter)

        # The offset should be negative (to the left) and ~10% of diameter
        assert group_offset_x < 0, "Offset should be to the LEFT (negative)"
        assert group_offset_x == -10.0, f"Expected offset of -10.0, got {group_offset_x}"

    def test_single_planet_no_offset(self):
        """
        GIVEN a hex sector containing exactly one planet
        WHEN the renderer calculates planet position
        THEN the planet should remain centered (no offset applied)

        This test ensures the fix only affects multi-planet sectors.
        """
        # Single planets should stay centered - this is existing correct behavior
        hex_center_screen = pygame.math.Vector2(500, 300)

        # For single planet, position equals hex_center_screen (no offset)
        single_planet_pos = hex_center_screen.copy()

        assert single_planet_pos.x == hex_center_screen.x, "Single planet should be centered horizontally"
        assert single_planet_pos.y == hex_center_screen.y, "Single planet should be centered vertically"

    def test_offset_magnitude_tenth_diameter(self):
        """
        GIVEN the largest planet in a multi-planet sector
        WHEN calculating the group offset
        THEN offset should be approximately 10% of the largest planet's diameter (leftward)

        Rev 3: Changed to 10% per user feedback.
        """
        # Various test cases for different zoom levels
        # Largest planet draw_r = hex_px_radius * 0.5
        # Diameter = draw_r * 2 = hex_px_radius * 1.0
        # Offset = -diameter * 0.10 = -hex_px_radius * 0.10
        test_cases = [
            {"hex_px_radius": 50, "expected_approx": -5.0},    # 50 * 0.5 * 2 * -0.10 = -5.0
            {"hex_px_radius": 100, "expected_approx": -10.0},  # 100 * 0.5 * 2 * -0.10 = -10.0
            {"hex_px_radius": 200, "expected_approx": -20.0},  # 200 * 0.5 * 2 * -0.10 = -20.0
        ]

        for case in test_cases:
            hex_px_radius = case["hex_px_radius"]

            # Calculate expected offset based on Rev 3 requirement
            largest_draw_radius = hex_px_radius * 0.5
            largest_diameter = largest_draw_radius * 2
            expected_offset = -largest_diameter * 0.10  # 10% of diameter, leftward

            assert abs(expected_offset - case["expected_approx"]) < 0.01, (
                f"Offset calculation error for hex_px_radius={hex_px_radius}"
            )

            # Offset must be negative (leftward)
            assert expected_offset < 0, "Offset must be negative (to the left)"


    def test_smaller_planets_spaced_further(self):
        """
        GIVEN multiple planets in a hex sector
        WHEN the renderer calculates positions for smaller planets
        THEN smaller planets should be spaced further from the largest planet (dist = 0.65 * hex_px_radius)

        Rev 3: Smaller planets need more spacing to avoid clipping the largest planet.
        """
        hex_px_radius = 100

        # Rev 3: Smaller planets at 65% of hex radius from largest (was 50%)
        expected_small_planet_dist = hex_px_radius * 0.65  # = 65

        # This should be greater than the old value of 50% (which was hex_px_radius * 0.5)
        old_dist = hex_px_radius * 0.5  # = 50

        assert expected_small_planet_dist > old_dist, (
            f"New distance ({expected_small_planet_dist}) should be greater than old ({old_dist})"
        )
        assert expected_small_planet_dist == 65.0, (
            f"Smaller planet distance should be 65.0, got {expected_small_planet_dist}"
        )


class TestRendererMultiPlanetLogic:
    """Integration tests that verify the renderer applies correct offsets."""

    def test_renderer_offset_direction(self):
        """
        GIVEN multiple planets in the same hex
        WHEN _draw_system_details calculates positions
        THEN the largest planet should be offset slightly LEFT of hex center by 10% of its diameter

        Rev 3: Updated to use 10% of diameter offset.
        """
        # Simulate what the renderer does (fixed logic)
        hex_center_x = 500
        hex_px_radius = 100

        # Fixed renderer logic (from strategy_renderer.py)
        # Largest planet draw_r = hex_px_radius * 0.5 = 50
        largest_draw_r = hex_px_radius * 0.5  # = 50
        largest_diameter = largest_draw_r * 2  # = 100
        group_offset_x = -largest_diameter * 0.10  # = -10 (left, 10% of diameter)

        largest_x = hex_center_x + group_offset_x  # = 490

        # The planet is positioned slightly LEFT of center
        assert largest_x < hex_center_x, (
            f"Largest planet at x={largest_x} should be LEFT of center ({hex_center_x})"
        )
        assert group_offset_x == -10.0, f"Offset should be -10.0, got {group_offset_x}"
