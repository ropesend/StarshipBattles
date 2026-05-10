"""
Tests for RadialPrimitive density field.
"""

import pytest
from game.strategy.generation.density.primitives.radial import RadialPrimitive


class TestRadialPrimitive:
    """Tests for RadialPrimitive."""

    def test_center_has_highest_density(self, radial_primitive):
        """Center point should have maximum density."""
        center_density = radial_primitive.evaluate(0, 0)
        assert center_density == pytest.approx(1.0, abs=0.01)

    def test_density_decreases_with_distance(self, radial_primitive):
        """Density should decrease as we move away from center."""
        center = radial_primitive.evaluate(0, 0)
        near = radial_primitive.evaluate(50, 0)
        far = radial_primitive.evaluate(200, 0)

        assert center > near > far

    def test_output_always_in_valid_range(self, radial_primitive):
        """Output should always be in [0, 1]."""
        test_coords = [
            (0, 0), (100, 0), (-100, 0), (0, 100), (0, -100),
            (500, 500), (-500, -500), (1000, 1000)
        ]
        for q, r in test_coords:
            density = radial_primitive.evaluate(q, r)
            assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_handles_negative_coordinates(self, radial_primitive):
        """Should handle negative coordinates correctly."""
        # Symmetric around center
        pos = radial_primitive.evaluate(50, 50)
        neg = radial_primitive.evaluate(-50, -50)
        assert pos == pytest.approx(neg, abs=0.01)

    def test_symmetric_around_center(self):
        """Density should be symmetric around the center point."""
        prim = RadialPrimitive(center_q=100, center_r=100, sigma=50, peak_density=1.0)

        # Points equidistant from center should have same density
        d1 = prim.evaluate(150, 100)  # +50 in q
        d2 = prim.evaluate(50, 100)   # -50 in q
        d3 = prim.evaluate(100, 150)  # +50 in r

        assert d1 == pytest.approx(d2, abs=0.01)
        # Note: hex geometry means d3 might differ slightly

    def test_offset_center(self):
        """Primitive with offset center should peak at that center."""
        prim = RadialPrimitive(center_q=200, center_r=-100, sigma=50, peak_density=1.0)

        center_density = prim.evaluate(200, -100)
        origin_density = prim.evaluate(0, 0)

        assert center_density > origin_density

    def test_zero_sigma_only_center_has_density(self):
        """With sigma=0, only exact center should have density."""
        prim = RadialPrimitive(center_q=0, center_r=0, sigma=0, peak_density=1.0)

        assert prim.evaluate(0, 0) == 1.0
        assert prim.evaluate(1, 0) == 0.0

    def test_large_sigma_flat_distribution(self):
        """Large sigma should produce relatively flat distribution."""
        prim = RadialPrimitive(center_q=0, center_r=0, sigma=10000, peak_density=1.0)

        center = prim.evaluate(0, 0)
        far = prim.evaluate(500, 500)

        # With very large sigma, far point should still have significant density
        assert far > 0.8
