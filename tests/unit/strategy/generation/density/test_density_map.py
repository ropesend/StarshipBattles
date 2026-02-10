"""
Tests for DensityMap composite class.
"""

import pytest
import random

from game.core.hex_math import HexCoord
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.density.primitives.radial import RadialPrimitive
from game.strategy.generation.density.primitives.ring import RingPrimitive


class TestDensityMapBasics:
    """Basic tests for DensityMap."""

    def test_empty_map_evaluates_to_zero(self, empty_density_map):
        """Empty map should return zero density."""
        assert empty_density_map.evaluate(0, 0) == 0.0
        assert empty_density_map.evaluate(100, 100) == 0.0

    def test_empty_map_raises_on_sample(self, empty_density_map):
        """Empty map should raise when sampling."""
        with pytest.raises(ValueError, match="empty DensityMap"):
            empty_density_map.sample()

    def test_single_primitive_works(self, simple_density_map):
        """Map with single primitive should work."""
        density = simple_density_map.evaluate(0, 0)
        assert density > 0.9

    def test_len_returns_primitive_count(self, empty_density_map, simple_density_map):
        """len() should return number of primitives."""
        assert len(empty_density_map) == 0
        assert len(simple_density_map) == 1


class TestDensityMapComposition:
    """Tests for combining primitives."""

    def test_multiple_primitives_combine(self):
        """Multiple primitives should combine."""
        dm = DensityMap(radius=1000)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0), weight=0.5)
        dm.add_primitive(RadialPrimitive(sigma=200, peak_density=1.0), weight=0.5)

        assert len(dm) == 2
        density = dm.evaluate(0, 0)
        assert density > 0.9

    def test_weights_affect_contribution(self):
        """Weights should affect primitive contribution."""
        # One map with high weight on center
        dm1 = DensityMap(radius=1000)
        dm1.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0), weight=0.9)
        dm1.add_primitive(RingPrimitive(radius=300, width=50, peak_density=1.0), weight=0.1)

        # One map with high weight on ring
        dm2 = DensityMap(radius=1000)
        dm2.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0), weight=0.1)
        dm2.add_primitive(RingPrimitive(radius=300, width=50, peak_density=1.0), weight=0.9)

        # At center, dm1 should be higher
        center1 = dm1.evaluate(0, 0)
        center2 = dm2.evaluate(0, 0)
        assert center1 > center2

        # At ring radius, dm2 should be higher
        ring1 = dm1.evaluate(300, 0)
        ring2 = dm2.evaluate(300, 0)
        assert ring2 > ring1

    def test_zero_weight_primitive_ignored(self):
        """Primitive with zero weight should be ignored."""
        dm = DensityMap(radius=1000)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0), weight=1.0)
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0), weight=0.0)

        # Should only have one primitive
        assert len(dm) == 1

    def test_output_clamped_to_valid_range(self):
        """Output should be clamped to [0, 1] even with high weights."""
        dm = DensityMap(radius=1000, normalize=False)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0), weight=5.0)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0), weight=5.0)

        density = dm.evaluate(0, 0)
        assert 0.0 <= density <= 1.0


class TestDensityMapSampling:
    """Tests for DensityMap sampling."""

    def test_sample_returns_hexcoord(self, simple_density_map, seeded_rng):
        """Sample should return HexCoord."""
        coord = simple_density_map.sample(rng=seeded_rng)
        assert isinstance(coord, HexCoord)

    def test_sample_within_radius(self, simple_density_map, seeded_rng):
        """Sampled coordinates should be within radius."""
        for _ in range(50):
            coord = simple_density_map.sample(rng=seeded_rng)
            if coord is not None:
                # Check hex radius constraint
                assert max(abs(coord.q), abs(coord.r), abs(coord.q + coord.r)) <= simple_density_map.radius

    def test_samples_prefer_high_density(self, seeded_rng):
        """Samples should cluster in high-density regions."""
        dm = DensityMap(radius=500)
        # Strong center concentration
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0), weight=1.0)

        # Sample many points
        samples = []
        for _ in range(100):
            coord = dm.sample(rng=seeded_rng)
            if coord is not None:
                samples.append(coord)

        # Most samples should be near center
        near_center = sum(1 for c in samples if abs(c.q) < 100 and abs(c.r) < 100)
        assert near_center > len(samples) * 0.5, "Most samples should be near center"

    def test_sample_reproducible_with_same_seed(self):
        """Same seed should produce same samples."""
        dm = DensityMap(radius=500)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0), weight=1.0)

        rng1 = random.Random(54321)
        rng2 = random.Random(54321)

        samples1 = [dm.sample(rng=rng1) for _ in range(10)]
        samples2 = [dm.sample(rng=rng2) for _ in range(10)]

        assert samples1 == samples2


class TestDensityMapFromConfig:
    """Tests for creating DensityMap from config."""

    def test_from_config_creates_map(self):
        """from_config should create working DensityMap."""
        config = {
            'primitives': [
                {'type': 'radial', 'sigma': 100, 'peak_density': 1.0, 'weight': 1.0}
            ]
        }
        dm = DensityMap.from_config(config, radius=1000)

        assert len(dm) == 1
        assert dm.evaluate(0, 0) > 0.9

    def test_from_config_multiple_primitives(self):
        """from_config should handle multiple primitives."""
        config = {
            'primitives': [
                {'type': 'radial', 'sigma': 50, 'peak_density': 1.0, 'weight': 0.5},
                {'type': 'ring', 'radius': 300, 'width': 50, 'peak_density': 1.0, 'weight': 0.5}
            ]
        }
        dm = DensityMap.from_config(config, radius=1000)

        assert len(dm) == 2

    def test_from_config_unknown_type_raises(self):
        """from_config should raise for unknown primitive type."""
        config = {
            'primitives': [
                {'type': 'unknown_type', 'weight': 1.0}
            ]
        }
        with pytest.raises(ValueError, match="Unknown primitive type"):
            DensityMap.from_config(config, radius=1000)

    def test_from_config_empty_primitives_raises(self):
        """from_config should raise for empty primitives list."""
        config = {'primitives': []}
        with pytest.raises(ValueError, match="must contain"):
            DensityMap.from_config(config, radius=1000)

    def test_from_config_missing_type_raises(self):
        """from_config should raise for primitive without type."""
        config = {
            'primitives': [
                {'sigma': 100, 'weight': 1.0}  # Missing 'type'
            ]
        }
        with pytest.raises(ValueError, match="must have a 'type'"):
            DensityMap.from_config(config, radius=1000)


class TestDensityMapCoverage:
    """Tests for coverage estimation."""

    def test_coverage_estimate_reasonable(self, simple_density_map, seeded_rng):
        """Coverage estimate should return reasonable value."""
        coverage = simple_density_map.get_coverage_estimate(sample_count=500, rng=seeded_rng)
        assert 0.0 <= coverage <= 1.0

    def test_sparse_map_low_coverage(self, seeded_rng):
        """Very sparse map should have low coverage."""
        dm = DensityMap(radius=1000)
        # Small sigma relative to radius = sparse
        dm.add_primitive(RadialPrimitive(sigma=10, peak_density=1.0), weight=1.0)

        coverage = dm.get_coverage_estimate(sample_count=500, rng=seeded_rng)
        assert coverage < 0.2

    def test_dense_map_high_coverage(self, seeded_rng):
        """Dense map should have high coverage."""
        dm = DensityMap(radius=500)
        # Large sigma = dense
        dm.add_primitive(RadialPrimitive(sigma=500, peak_density=1.0), weight=1.0)

        coverage = dm.get_coverage_estimate(sample_count=500, rng=seeded_rng)
        assert coverage > 0.5
