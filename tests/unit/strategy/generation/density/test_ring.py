"""
Tests for RingPrimitive density field.
"""

import pytest
from game.strategy.generation.density.primitives.ring import RingPrimitive


class TestRingPrimitive:
    """Tests for RingPrimitive."""

    def test_ring_radius_has_highest_density(self, ring_primitive):
        """Points at ring radius should have maximum density."""
        # Point at ring radius
        at_ring = ring_primitive.evaluate(500, 0)
        assert at_ring == pytest.approx(1.0, abs=0.01)

    def test_center_has_lower_density_than_ring(self, ring_primitive):
        """Center should have lower density than ring."""
        center = ring_primitive.evaluate(0, 0)
        at_ring = ring_primitive.evaluate(500, 0)
        assert at_ring > center

    def test_density_falls_off_from_ring(self, ring_primitive):
        """Density should decrease moving away from ring (inside or outside)."""
        at_ring = ring_primitive.evaluate(500, 0)
        inside = ring_primitive.evaluate(300, 0)
        outside = ring_primitive.evaluate(700, 0)

        assert at_ring > inside
        assert at_ring > outside

    def test_output_always_in_valid_range(self, ring_primitive):
        """Output should always be in [0, 1]."""
        test_coords = [
            (0, 0), (500, 0), (250, 0), (750, 0),
            (1000, 0), (-500, 0), (0, 500)
        ]
        for q, r in test_coords:
            density = ring_primitive.evaluate(q, r)
            assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_ring_is_circular(self):
        """Ring should be approximately circular."""
        prim = RingPrimitive(radius=400, width=50, peak_density=1.0)

        # Points at same distance should have similar density
        d1 = prim.evaluate(400, 0)
        d2 = prim.evaluate(0, 400)  # Approximately same distance in hex coords
        d3 = prim.evaluate(-400, 0)

        # Allow some variance due to hex geometry
        assert abs(d1 - d3) < 0.1

    def test_zero_width_only_ring_has_density(self):
        """With width=0, only exact ring radius should have density."""
        prim = RingPrimitive(radius=100, width=0, peak_density=1.0)

        at_ring = prim.evaluate(100, 0)
        inside = prim.evaluate(50, 0)
        outside = prim.evaluate(150, 0)

        assert at_ring == 1.0
        assert inside == 0.0
        assert outside == 0.0
