"""
Tests for LinearPrimitive density field.
"""

import pytest
import math
from game.strategy.generation.density.primitives.linear import LinearPrimitive


class TestLinearPrimitive:
    """Tests for LinearPrimitive."""

    def test_bar_center_has_highest_density(self, linear_primitive):
        """Center of bar should have maximum density."""
        center = linear_primitive.evaluate(0, 0)
        assert center == pytest.approx(1.0, abs=0.01)

    def test_density_along_bar_is_high(self, linear_primitive):
        """Points along the bar should have high density."""
        # Bar is along x-axis (rotation=0)
        along_bar = linear_primitive.evaluate(100, 0)
        assert along_bar > 0.8

    def test_density_perpendicular_falls_off(self, linear_primitive):
        """Density should fall off perpendicular to bar."""
        on_bar = linear_primitive.evaluate(0, 0)
        off_bar = linear_primitive.evaluate(0, 100)  # Perpendicular

        assert on_bar > off_bar

    def test_bar_ends_have_lower_density(self):
        """Points past bar ends should have lower density."""
        prim = LinearPrimitive(length=200, width=30, peak_density=1.0)

        center = prim.evaluate(0, 0)
        at_end = prim.evaluate(100, 0)  # At bar end
        past_end = prim.evaluate(200, 0)  # Past bar end

        assert center >= at_end
        assert at_end > past_end

    def test_output_always_in_valid_range(self, linear_primitive):
        """Output should always be in [0, 1]."""
        test_coords = [
            (0, 0), (200, 0), (-200, 0), (0, 200), (0, -200),
            (300, 300), (-300, -300)
        ]
        for q, r in test_coords:
            density = linear_primitive.evaluate(q, r)
            assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_rotation_affects_bar_orientation(self):
        """Rotation should change bar orientation."""
        prim_horiz = LinearPrimitive(length=200, width=30, rotation=0, peak_density=1.0)
        prim_vert = LinearPrimitive(length=200, width=30, rotation=math.pi/2, peak_density=1.0)

        # Point along x-axis: high for horizontal, low for vertical
        d_horiz = prim_horiz.evaluate(80, 0)
        d_vert = prim_vert.evaluate(80, 0)

        assert d_horiz > d_vert

    def test_zero_width_only_line_has_density(self):
        """With width=0, only points on the line have density."""
        prim = LinearPrimitive(length=200, width=0, peak_density=1.0)

        on_line = prim.evaluate(50, 0)
        off_line = prim.evaluate(0, 50)

        assert on_line == 1.0
        assert off_line == 0.0
