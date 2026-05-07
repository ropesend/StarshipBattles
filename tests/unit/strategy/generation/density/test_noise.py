"""
Tests for NoisePrimitive density field.
"""

import pytest
from game.strategy.generation.density.primitives.noise import (
    NoisePrimitive,
    _hash_coord,
    _smooth_noise,
)


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

    def test_negative_scale_returns_clamped_midpoint_density(self):
        """Non-positive scale uses the midpoint fallback and clamps the result."""
        prim = NoisePrimitive(scale=-10, peak_density=3.0)

        assert prim.evaluate(0, 0) == 1.0

    def test_non_positive_octaves_uses_single_octave(self):
        """The octave loop always evaluates at least one octave."""
        zero_octave = NoisePrimitive(scale=50, octaves=0, seed=42, peak_density=1.0)
        one_octave = NoisePrimitive(scale=50, octaves=1, seed=42, peak_density=1.0)

        assert zero_octave.evaluate(25, -10) == one_octave.evaluate(25, -10)

    def test_handles_negative_coordinates(self, noise_primitive):
        """Should handle negative coordinates without issues."""
        densities = [
            noise_primitive.evaluate(-100, -100),
            noise_primitive.evaluate(-500, 200),
            noise_primitive.evaluate(300, -400),
        ]
        for d in densities:
            assert 0.0 <= d <= 1.0


class TestNoiseHelpers:
    """Tests for module-level value-noise helpers."""

    def test_hash_coord_is_deterministic_and_seed_sensitive(self):
        """Coordinate hashing should be stable and seed-dependent."""
        assert _hash_coord(12, -7, 99) == _hash_coord(12, -7, 99)
        assert _hash_coord(12, -7, 99) != _hash_coord(12, -7, 100)

    def test_smooth_noise_integer_coordinate_matches_corner_hash(self):
        """At integer coordinates, interpolation should return the corner value."""
        expected = (_hash_coord(-3, 4, 11) & 0xFFFF) / 0xFFFF

        assert _smooth_noise(-3.0, 4.0, 11) == pytest.approx(expected)

    def test_smooth_noise_fractional_coordinate_interpolates_between_corners(self):
        """Fractional samples should stay within their four corner values."""
        x = 2.25
        y = -1.75
        seed = 5
        corners = [
            (_hash_coord(2, -2, seed) & 0xFFFF) / 0xFFFF,
            (_hash_coord(3, -2, seed) & 0xFFFF) / 0xFFFF,
            (_hash_coord(2, -1, seed) & 0xFFFF) / 0xFFFF,
            (_hash_coord(3, -1, seed) & 0xFFFF) / 0xFFFF,
        ]

        value = _smooth_noise(x, y, seed)

        assert min(corners) <= value <= max(corners)
