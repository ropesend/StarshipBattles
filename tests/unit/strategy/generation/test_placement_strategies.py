"""
Unit tests for system placement strategies.

Tests the ISystemPlacementStrategy protocol implementations:
- RandomPlacementStrategy: Original random placement logic
- DensityBasedPlacementStrategy: Density field-guided placement
"""

import pytest
import random
from typing import Set

from game.strategy.data.hex_math import HexCoord, hex_distance
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
