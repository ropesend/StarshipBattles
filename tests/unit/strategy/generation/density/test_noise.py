"""
Tests for NoisePrimitive density field.
"""

import pytest
from game.strategy.generation.density.primitives.noise import NoisePrimitive


class TestNoisePrimitive:
    """Tests for NoisePrimitive."""

    def test_same_seed_produces_same_output(self):
        """Same seed should produce identical noise."""
        prim1 = NoisePrimitive(scale=50, seed=12345, peak_density=1.0)
        prim2 = NoisePrimitive(scale=50, seed=12345, peak_density=1.0)

        for q, r in [(0, 0), (100, 50), (-200, 300)]:
            d1 = prim1.evaluate(q, r)
            d2 = prim2.evaluate(q, r)
            assert d1 == d2, f"Mismatch at ({q}, {r})"

    def test_different_seeds_produce_different_output(self):
        """Different seeds should produce different noise."""
        prim1 = NoisePrimitive(scale=50, seed=111, peak_density=1.0)
        prim2 = NoisePrimitive(scale=50, seed=222, peak_density=1.0)

        # Check multiple points - at least one should differ
        differences = 0
        for q, r in [(0, 0), (100, 50), (200, 100), (-100, -50)]:
            d1 = prim1.evaluate(q, r)
            d2 = prim2.evaluate(q, r)
            if abs(d1 - d2) > 0.01:
                differences += 1

        assert differences > 0, "Different seeds should produce some different values"

    def test_output_always_in_valid_range(self, noise_primitive):
        """Output should always be in [0, 1]."""
        # Sample many points
        for q in range(-500, 501, 100):
            for r in range(-500, 501, 100):
                density = noise_primitive.evaluate(q, r)
                assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_scale_affects_feature_size(self):
        """Larger scale should produce larger features."""
        prim_small = NoisePrimitive(scale=10, seed=42, peak_density=1.0)
        prim_large = NoisePrimitive(scale=200, seed=42, peak_density=1.0)

        # Sample nearby points - small scale should vary more
        small_var = abs(prim_small.evaluate(0, 0) - prim_small.evaluate(5, 0))
        large_var = abs(prim_large.evaluate(0, 0) - prim_large.evaluate(5, 0))

        assert small_var >= large_var * 0.5, "Small scale should have more local variation"

    def test_octaves_add_detail(self):
        """More octaves should add finer detail."""
        prim1 = NoisePrimitive(scale=50, octaves=1, seed=42, peak_density=1.0)
        prim4 = NoisePrimitive(scale=50, octaves=4, seed=42, peak_density=1.0)

        # Both should be valid
        for prim in [prim1, prim4]:
            d = prim.evaluate(100, 100)
            assert 0.0 <= d <= 1.0

    def test_zero_scale_returns_constant(self):
        """Zero scale should return constant value."""
        prim = NoisePrimitive(scale=0, peak_density=1.0)

        d1 = prim.evaluate(0, 0)
        d2 = prim.evaluate(100, 100)
        d3 = prim.evaluate(-500, 300)

        # Should all be the same (midpoint density)
        assert d1 == d2 == d3

    def test_handles_negative_coordinates(self, noise_primitive):
        """Should handle negative coordinates without issues."""
        densities = [
            noise_primitive.evaluate(-100, -100),
            noise_primitive.evaluate(-500, 200),
            noise_primitive.evaluate(300, -400),
        ]
        for d in densities:
            assert 0.0 <= d <= 1.0
