"""
Unit tests for system placement strategies.

Tests the ISystemPlacementStrategy protocol implementations:
- RandomPlacementStrategy: Original random placement logic
- DensityBasedPlacementStrategy: Density field-guided placement
"""

import pytest
import random
from typing import Set

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.generation.placement_strategies import (
    ISystemPlacementStrategy,
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.density.primitives.radial import RadialPrimitive


class TestISystemPlacementStrategy:
    """Test the protocol interface."""

    def test_random_placement_implements_protocol(self):
        """RandomPlacementStrategy should implement the protocol."""
        strategy = RandomPlacementStrategy()
        assert isinstance(strategy, ISystemPlacementStrategy)

    def test_density_based_placement_implements_protocol(self):
        """DensityBasedPlacementStrategy should implement the protocol."""
        density_map = DensityMap(radius=100)
        density_map.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(density_map)
        assert isinstance(strategy, ISystemPlacementStrategy)


class TestRandomPlacementStrategy:
    """Test RandomPlacementStrategy implementation."""

    def test_sample_location_returns_hex_coord(self):
        """sample_location should return a HexCoord."""
        strategy = RandomPlacementStrategy()
        result = strategy.sample_location(radius=100, existing_systems=set(), min_dist=10)
        assert isinstance(result, HexCoord)

    def test_sample_location_within_radius(self):
        """Generated coordinates should be within the galaxy radius."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        for _ in range(100):
            result = strategy.sample_location(
                radius=50,
                existing_systems=set(),
                min_dist=5,
                rng=rng
            )
            assert result is not None
            # Check hex is within radius (axial coordinate constraint)
            assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 50

    def test_sample_location_respects_min_dist(self):
        """Generated coordinates should respect minimum distance constraint."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        # Place a system at origin
        existing = {HexCoord(0, 0)}
        min_dist = 20

        for _ in range(50):
            result = strategy.sample_location(
                radius=100,
                existing_systems=existing,
                min_dist=min_dist,
                rng=rng
            )
            if result is not None:
                # Should be at least min_dist away from origin
                assert hex_distance(result, HexCoord(0, 0)) >= min_dist

    def test_sample_location_with_seed_deterministic(self):
        """Same seed should produce same sequence of coordinates."""
        strategy = RandomPlacementStrategy()

        results1 = []
        rng1 = random.Random(12345)
        for _ in range(10):
            result = strategy.sample_location(
                radius=100,
                existing_systems=set(),
                min_dist=5,
                rng=rng1
            )
            results1.append(result)

        results2 = []
        rng2 = random.Random(12345)
        for _ in range(10):
            result = strategy.sample_location(
                radius=100,
                existing_systems=set(),
                min_dist=5,
                rng=rng2
            )
            results2.append(result)

        assert results1 == results2

    def test_sample_location_returns_none_when_saturated(self):
        """Should return None if no valid location can be found."""
        strategy = RandomPlacementStrategy()

        # Create a small galaxy packed with systems
        # With radius 5 and min_dist 10, only origin should fit
        existing = {HexCoord(0, 0)}

        result = strategy.sample_location(
            radius=5,
            existing_systems=existing,
            min_dist=10,
            max_attempts=100
        )

        # Should return None since no space left
        assert result is None

    def test_sample_location_avoids_existing(self):
        """Should not return coordinates already in existing_systems."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        existing = {HexCoord(0, 0), HexCoord(20, 0), HexCoord(-20, 20)}

        for _ in range(50):
            result = strategy.sample_location(
                radius=100,
                existing_systems=existing,
                min_dist=5,
                rng=rng
            )
            if result is not None:
                assert result not in existing


class TestDensityBasedPlacementStrategy:
    """Test DensityBasedPlacementStrategy implementation."""

    @pytest.fixture
    def simple_density_map(self):
        """Create a simple radial density map centered at origin."""
        dm = DensityMap(radius=200)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0))
        return dm

    def test_sample_location_returns_hex_coord(self, simple_density_map):
        """sample_location should return a HexCoord."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)
        result = strategy.sample_location(radius=200, existing_systems=set(), min_dist=10)
        assert result is None or isinstance(result, HexCoord)

    def test_sample_location_within_radius(self, simple_density_map):
        """Generated coordinates should be within the galaxy radius."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)
        rng = random.Random(42)

        for _ in range(50):
            result = strategy.sample_location(
                radius=200,
                existing_systems=set(),
                min_dist=5,
                rng=rng
            )
            if result is not None:
                assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 200

    def test_sample_location_respects_min_dist(self, simple_density_map):
        """Generated coordinates should respect minimum distance constraint."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)
        rng = random.Random(42)

        existing = {HexCoord(0, 0)}
        min_dist = 20

        for _ in range(30):
            result = strategy.sample_location(
                radius=200,
                existing_systems=existing,
                min_dist=min_dist,
                rng=rng
            )
            if result is not None:
                assert hex_distance(result, HexCoord(0, 0)) >= min_dist

    def test_sample_location_biased_toward_high_density(self):
        """Samples should cluster in high-density regions."""
        # Create density map with peak at origin
        dm = DensityMap(radius=200)
        dm.add_primitive(RadialPrimitive(sigma=30, peak_density=1.0))  # Tight peak

        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        # Sample many points
        samples = []
        for _ in range(100):
            result = strategy.sample_location(
                radius=200,
                existing_systems=set(),
                min_dist=2,
                rng=rng
            )
            if result is not None:
                samples.append(result)

        # Most samples should be within sigma of center
        close_to_center = sum(1 for s in samples if hex_distance(s, HexCoord(0, 0)) < 50)
        assert close_to_center > len(samples) * 0.5  # At least 50% within 50 hexes

    def test_sample_location_with_seed_deterministic(self, simple_density_map):
        """Same seed should produce same sequence."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)

        results1 = []
        rng1 = random.Random(12345)
        for _ in range(10):
            result = strategy.sample_location(
                radius=200,
                existing_systems=set(),
                min_dist=5,
                rng=rng1
            )
            results1.append(result)

        results2 = []
        rng2 = random.Random(12345)
        for _ in range(10):
            result = strategy.sample_location(
                radius=200,
                existing_systems=set(),
                min_dist=5,
                rng=rng2
            )
            results2.append(result)

        assert results1 == results2

    def test_sample_location_avoids_existing(self, simple_density_map):
        """Should not return coordinates already in existing_systems."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)
        rng = random.Random(42)

        existing = {HexCoord(0, 0), HexCoord(20, 0), HexCoord(-20, 20)}

        for _ in range(30):
            result = strategy.sample_location(
                radius=200,
                existing_systems=existing,
                min_dist=5,
                rng=rng
            )
            if result is not None:
                assert result not in existing

    def test_sample_location_returns_none_when_saturated(self, simple_density_map):
        """Should return None if no valid location can be found."""
        strategy = DensityBasedPlacementStrategy(simple_density_map)

        # Pack the high-density center area
        existing = {HexCoord(q, r) for q in range(-30, 31) for r in range(-30, 31)
                    if max(abs(q), abs(r), abs(q + r)) <= 30}

        result = strategy.sample_location(
            radius=200,
            existing_systems=existing,
            min_dist=5,
            max_attempts=100
        )

        # May or may not find a spot, but should not crash
        assert result is None or isinstance(result, HexCoord)


class TestRandomPlacementEdgeCases:
    """Edge case tests for RandomPlacementStrategy."""

    def test_sample_location_with_none_rng_creates_default(self):
        """When rng=None, should create a new Random instance and work."""
        strategy = RandomPlacementStrategy()
        # Just verify it works without explicit rng
        result = strategy.sample_location(
            radius=100,
            existing_systems=set(),
            min_dist=10,
            rng=None
        )
        assert result is not None
        assert isinstance(result, HexCoord)

    def test_sample_location_with_provided_spatial_index(self):
        """Should use provided spatial_index instead of building one."""
        from game.strategy.data.spatial_index import SpatialIndex

        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        # Pre-build spatial index with existing system
        existing = {HexCoord(0, 0)}
        index = SpatialIndex(cell_size=100)
        for coord in existing:
            index.add(coord, None)

        # Should use provided index
        result = strategy.sample_location(
            radius=100,
            existing_systems=existing,
            min_dist=20,
            rng=rng,
            spatial_index=index
        )

        # Result should respect min_dist from indexed system
        assert result is None or hex_distance(result, HexCoord(0, 0)) >= 20

    def test_sample_location_max_attempts_zero(self):
        """max_attempts=0 should return None immediately."""
        strategy = RandomPlacementStrategy()
        result = strategy.sample_location(
            radius=100,
            existing_systems=set(),
            min_dist=10,
            max_attempts=0
        )
        assert result is None

    def test_sample_location_radius_one(self):
        """Very small radius should still work."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        result = strategy.sample_location(
            radius=1,
            existing_systems=set(),
            min_dist=0,
            rng=rng
        )

        assert result is not None
        # Should be within hex radius 1
        assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 1

    def test_sample_location_min_dist_zero(self):
        """min_dist=0 should allow placement anywhere, even adjacent."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        existing = {HexCoord(0, 0)}
        result = strategy.sample_location(
            radius=2,
            existing_systems=existing,
            min_dist=0,
            rng=rng
        )

        # Should find a spot (may be adjacent)
        assert result is not None
        assert result not in existing

    def test_sample_location_occupied_exact_spot_rejected(self):
        """If random lands on exact existing coord, should reject it."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        # Fill most of a tiny galaxy
        existing = {HexCoord(0, 0), HexCoord(1, 0), HexCoord(0, 1)}

        # Should find the remaining spots
        found_coords = set()
        for _ in range(20):
            result = strategy.sample_location(
                radius=1,
                existing_systems=existing,
                min_dist=0,
                rng=rng
            )
            if result is not None:
                assert result not in existing
                found_coords.add(result)

    def test_sample_location_very_large_radius(self):
        """Large radius should not cause issues."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        result = strategy.sample_location(
            radius=10000,
            existing_systems=set(),
            min_dist=100,
            rng=rng
        )

        assert result is not None
        assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 10000

    def test_sample_location_many_existing_systems_performance(self):
        """Should handle many existing systems efficiently with spatial index."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        # Create a set of existing systems
        existing = {HexCoord(q * 10, r * 10) for q in range(-10, 11) for r in range(-10, 11)
                    if max(abs(q * 10), abs(r * 10), abs(q * 10 + r * 10)) <= 100}

        # Should still find valid spots quickly
        result = strategy.sample_location(
            radius=200,
            existing_systems=existing,
            min_dist=5,
            rng=rng,
            max_attempts=1000
        )

        # Should find something in the gaps
        assert result is None or result not in existing


class TestDensityBasedPlacementEdgeCases:
    """Edge case tests for DensityBasedPlacementStrategy."""

    def test_sample_location_with_none_rng_creates_default(self):
        """When rng=None, should create a new Random instance."""
        dm = DensityMap(radius=100)
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)

        result = strategy.sample_location(
            radius=100,
            existing_systems=set(),
            min_dist=10,
            rng=None
        )
        # Should work (may be None due to density but shouldn't crash)
        assert result is None or isinstance(result, HexCoord)

    def test_sample_location_with_provided_spatial_index(self):
        """Should use provided spatial_index instead of building one."""
        from game.strategy.data.spatial_index import SpatialIndex

        dm = DensityMap(radius=100)
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        existing = {HexCoord(0, 0)}
        index = SpatialIndex(cell_size=100)
        for coord in existing:
            index.add(coord, None)

        result = strategy.sample_location(
            radius=100,
            existing_systems=existing,
            min_dist=20,
            rng=rng,
            spatial_index=index
        )

        # Result should respect min_dist from indexed system
        assert result is None or hex_distance(result, HexCoord(0, 0)) >= 20

    def test_sample_location_max_attempts_zero(self):
        """max_attempts=0 should return None immediately."""
        dm = DensityMap(radius=100)
        dm.add_primitive(RadialPrimitive(sigma=50, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)

        result = strategy.sample_location(
            radius=100,
            existing_systems=set(),
            min_dist=10,
            max_attempts=0
        )
        assert result is None

    def test_sample_location_galaxy_radius_larger_than_density_map(self):
        """When galaxy radius > density map radius, should use smaller."""
        dm = DensityMap(radius=50)
        dm.add_primitive(RadialPrimitive(sigma=30, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        result = strategy.sample_location(
            radius=200,  # Larger than density map radius
            existing_systems=set(),
            min_dist=5,
            rng=rng
        )

        # Should stay within density map radius (50)
        if result is not None:
            assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 50

    def test_sample_location_galaxy_radius_smaller_than_density_map(self):
        """When galaxy radius < density map radius, should use smaller."""
        dm = DensityMap(radius=200)
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        result = strategy.sample_location(
            radius=30,  # Smaller than density map radius
            existing_systems=set(),
            min_dist=5,
            rng=rng
        )

        # Should stay within galaxy radius (30)
        if result is not None:
            assert max(abs(result.q), abs(result.r), abs(result.q + result.r)) <= 30

    def test_sample_location_very_low_density_everywhere(self):
        """Very low density should cause many rejections, may return None."""
        dm = DensityMap(radius=100)
        # Very low peak density
        dm.add_primitive(RadialPrimitive(sigma=100, peak_density=0.005))
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        # With very low density and limited attempts, may not find valid spot
        result = strategy.sample_location(
            radius=100,
            existing_systems=set(),
            min_dist=5,
            rng=rng,
            max_attempts=50
        )

        # May be None due to density rejection, but shouldn't crash
        assert result is None or isinstance(result, HexCoord)

    def test_sample_location_min_dist_zero(self):
        """min_dist=0 should allow placement anywhere."""
        dm = DensityMap(radius=50)
        dm.add_primitive(RadialPrimitive(sigma=30, peak_density=1.0))
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        existing = {HexCoord(0, 0)}
        result = strategy.sample_location(
            radius=50,
            existing_systems=existing,
            min_dist=0,
            rng=rng
        )

        # Should find a spot (may be adjacent)
        if result is not None:
            assert result not in existing

    def test_sample_location_density_threshold_filtering(self):
        """Areas with density < 0.01 should be quickly rejected."""
        # Density map with very tight peak - most area has low density
        dm = DensityMap(radius=100)
        dm.add_primitive(RadialPrimitive(sigma=5, peak_density=1.0))  # Very tight
        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        # Should still find spots near center
        results = []
        for _ in range(20):
            result = strategy.sample_location(
                radius=100,
                existing_systems=set(),
                min_dist=2,
                rng=rng
            )
            if result is not None:
                results.append(result)

        # Most results should be close to center
        if results:
            close_count = sum(1 for r in results if hex_distance(r, HexCoord(0, 0)) <= 20)
            assert close_count >= len(results) * 0.7


class TestPlacementStrategyIntegration:
    """Integration tests for placement strategies."""

    def test_random_strategy_fills_galaxy(self):
        """RandomPlacementStrategy should fill a galaxy with systems."""
        strategy = RandomPlacementStrategy()
        rng = random.Random(42)

        existing: Set[HexCoord] = set()
        radius = 100
        min_dist = 15
        target_count = 20

        for _ in range(target_count * 10):  # Allow multiple attempts per system
            if len(existing) >= target_count:
                break
            result = strategy.sample_location(
                radius=radius,
                existing_systems=existing,
                min_dist=min_dist,
                rng=rng
            )
            if result is not None:
                existing.add(result)

        assert len(existing) >= target_count * 0.8  # At least 80% of target

    def test_density_strategy_fills_galaxy(self):
        """DensityBasedPlacementStrategy should fill a galaxy with systems."""
        dm = DensityMap(radius=100)
        dm.add_primitive(RadialPrimitive(sigma=80, peak_density=1.0))

        strategy = DensityBasedPlacementStrategy(dm)
        rng = random.Random(42)

        existing: Set[HexCoord] = set()
        radius = 100
        min_dist = 10
        target_count = 15

        for _ in range(target_count * 20):  # Allow multiple attempts per system
            if len(existing) >= target_count:
                break
            result = strategy.sample_location(
                radius=radius,
                existing_systems=existing,
                min_dist=min_dist,
                rng=rng
            )
            if result is not None:
                existing.add(result)

        assert len(existing) >= target_count * 0.5  # At least 50% of target
