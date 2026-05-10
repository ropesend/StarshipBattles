"""
Tests for GeometricPrimitive density field.
"""

import pytest
import math
from game.strategy.generation.density.primitives.geometric import GeometricPrimitive


class TestGeometricPrimitive:
    """Tests for GeometricPrimitive."""

    def test_center_has_high_density(self, geometric_primitive):
        """Center should be inside shape with high density."""
        center = geometric_primitive.evaluate(0, 0)
        assert center > 0.9

    def test_inside_shape_has_density(self):
        """Points inside the shape should have density."""
        prim = GeometricPrimitive(sides=4, radius=300, edge_falloff=20, peak_density=1.0)

        # Point clearly inside
        inside = prim.evaluate(100, 0)
        assert inside > 0.5

    def test_outside_shape_has_low_density(self):
        """Points outside the shape should have low/no density."""
        prim = GeometricPrimitive(sides=4, radius=200, edge_falloff=20, peak_density=1.0)

        # Point clearly outside
        outside = prim.evaluate(500, 0)
        assert outside < 0.2

    def test_output_always_in_valid_range(self, geometric_primitive):
        """Output should always be in [0, 1]."""
        test_coords = [
            (0, 0), (200, 0), (-200, 0), (0, 200), (0, -200),
            (500, 500), (-500, -500), (300, 300)
        ]
        for q, r in test_coords:
            density = geometric_primitive.evaluate(q, r)
            assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_diamond_shape_four_sides(self):
        """4-sided shape should create diamond pattern."""
        prim = GeometricPrimitive(
            sides=4, radius=400, rotation=math.pi/4,  # 45 degree rotation
            edge_falloff=30, peak_density=1.0
        )

        # After 45 degree rotation, the diamond has vertices along diagonals
        # Edge distance at axis = radius * cos(45°) ≈ 283
        # So a point at (200, 0) should be clearly inside
        inside = prim.evaluate(200, 0)
        assert inside > 0.5  # Should be inside

        # Point at (350, 0) is outside (past the edge at ~283)
        outside = prim.evaluate(350, 0)
        assert outside < inside  # Should have lower density than inside

    def test_triangle_shape(self):
        """3-sided shape should create triangle pattern."""
        prim = GeometricPrimitive(sides=3, radius=300, edge_falloff=20, peak_density=1.0)

        center = prim.evaluate(0, 0)
        assert center > 0.9

    def test_hexagon_shape(self):
        """6-sided shape should create hexagon pattern."""
        prim = GeometricPrimitive(sides=6, radius=300, edge_falloff=20, peak_density=1.0)

        center = prim.evaluate(0, 0)
        assert center > 0.9

    def test_rotation_affects_shape(self):
        """Rotation should change shape orientation."""
        prim1 = GeometricPrimitive(sides=4, radius=300, rotation=0, edge_falloff=30)
        prim2 = GeometricPrimitive(sides=4, radius=300, rotation=math.pi/4, edge_falloff=30)

        # Sample at a point that should differ between rotations
        d1 = prim1.evaluate(250, 0)
        d2 = prim2.evaluate(250, 0)

        # The densities should differ due to rotation
        # (one point is inside, the other near edge or outside)
        assert d1 != d2

    def test_zero_edge_falloff_hard_edge(self):
        """Zero edge falloff should create hard boundary."""
        prim = GeometricPrimitive(sides=4, radius=200, edge_falloff=0, peak_density=1.0)

        inside = prim.evaluate(100, 0)
        outside = prim.evaluate(400, 0)

        assert inside == 1.0
        assert outside == 0.0
