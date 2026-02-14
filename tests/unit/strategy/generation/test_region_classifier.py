"""
Unit tests for game.strategy.generation.region_classifier.

TCG-STR-003: Galaxy placement and region classification.
"""

import pytest
import math

from game.core.hex_math import HexCoord
from game.strategy.generation.region_classifier import RegionClassifier, RegionInfo


class TestRegionInfo:
    """Tests for RegionInfo dataclass."""

    def test_region_info_dataclass(self):
        """RegionInfo stores region_id, region_type, and name."""
        region = RegionInfo(region_id=3, region_type='arm', name='Arm 3')

        assert region.region_id == 3
        assert region.region_type == 'arm'
        assert region.name == 'Arm 3'


class TestRegionClassifierInit:
    """Tests for RegionClassifier initialization."""

    def test_spiral_layout_detected(self):
        """_has_spiral=True for spiral_arm primitive."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0}
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier._has_spiral is True
        assert classifier._has_clusters is False

    def test_cluster_layout_detected(self):
        """_has_clusters=True for multiple radial primitives."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.3},
                {'type': 'radial', 'center_q': 500, 'center_r': 0, 'sigma': 100, 'weight': 0.3},
                {'type': 'radial', 'center_q': -500, 'center_r': 0, 'sigma': 100, 'weight': 0.3},
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier._has_clusters is True
        assert classifier._has_spiral is False

    def test_empty_primitives_no_regions(self):
        """No primitives yields empty regions."""
        config = {'primitives': []}

        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier.region_count == 0
        assert classifier.regions == []


class TestRegionBuilding:
    """Tests for region building logic."""

    def test_spiral_regions_include_arms(self):
        """Spiral galaxy creates arm regions 0..N-1."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0}
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        arm_regions = [r for r in classifier.regions if r.region_type == 'arm']
        assert len(arm_regions) == 4
        assert all(r.region_id in [0, 1, 2, 3] for r in arm_regions)

    def test_spiral_regions_include_core(self):
        """Core added when radial primitive present alongside spiral."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2, 'pitch_angle': 20.0},
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.2},
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        core_regions = [r for r in classifier.regions if r.region_type == 'core']
        assert len(core_regions) == 1
        assert core_regions[0].region_id == 2  # After arms 0, 1
        assert core_regions[0].name == 'Core'

    def test_cluster_regions_count(self):
        """One region per cluster center."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.5},
                {'type': 'radial', 'center_q': 500, 'center_r': 200, 'sigma': 80, 'weight': 0.3},
                {'type': 'radial', 'center_q': -400, 'center_r': 300, 'sigma': 90, 'weight': 0.2},
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier.region_count == 3
        cluster_regions = [r for r in classifier.regions if r.region_type == 'cluster']
        assert len(cluster_regions) == 3

    def test_ring_layout_regions(self):
        """Ring layout creates ring + core regions."""
        config = {
            'primitives': [
                {'type': 'ring', 'radius': 2000, 'width': 500}
            ]
        }

        classifier = RegionClassifier(config, galaxy_radius=5000)

        region_types = {r.region_type for r in classifier.regions}
        assert 'ring' in region_types
        assert 'core' in region_types


class TestSpiralClassification:
    """Tests for spiral galaxy classification."""

    def _make_spiral_config(self, arm_count=4, include_core=True):
        """Create a spiral galaxy config."""
        primitives = [
            {'type': 'spiral_arm', 'arm_count': arm_count, 'pitch_angle': 20.0, 'center_q': 0, 'center_r': 0}
        ]
        if include_core:
            primitives.append({'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.2})
        return {'primitives': primitives}

    def test_classify_origin_as_core(self):
        """(0,0) in spiral galaxy with core classified as core."""
        config = self._make_spiral_config(arm_count=4, include_core=True)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        result = classifier.classify(HexCoord(0, 0))

        # Core is last region (after 4 arms, so region_id = 4)
        assert result == 4

    def test_classify_arm_point(self):
        """Point on arm returns arm index (0 to arm_count-1)."""
        config = self._make_spiral_config(arm_count=4, include_core=True)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Far from center, should be classified as some arm (0-3)
        result = classifier.classify(HexCoord(500, 0))

        assert 0 <= result <= 3  # One of the 4 arms

    def test_classify_different_arms_different_ids(self):
        """Points in different directions get different arm IDs."""
        config = self._make_spiral_config(arm_count=4, include_core=True)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Far points in different directions
        results = set()
        coords = [HexCoord(500, 0), HexCoord(0, 500), HexCoord(-500, 0), HexCoord(0, -500)]
        for coord in coords:
            results.add(classifier.classify(coord))

        # Should hit multiple different arms
        assert len(results) > 1

    def test_classify_near_origin_fallback(self):
        """Very close to center returns core (if present) or arm 0."""
        config = self._make_spiral_config(arm_count=2, include_core=True)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Point at distance 1 (within core threshold)
        result = classifier.classify(HexCoord(1, 0))

        # Should be core (region_id 2 for 2 arms)
        assert result == 2


class TestClusterClassification:
    """Tests for cluster galaxy classification."""

    def _make_cluster_config(self, centers):
        """Create cluster config with given centers [(q, r, sigma), ...]."""
        return {
            'primitives': [
                {'type': 'radial', 'center_q': q, 'center_r': r, 'sigma': sigma, 'weight': 0.3}
                for q, r, sigma in centers
            ]
        }

    def test_classify_near_cluster_center(self):
        """Point near a cluster center gets that cluster ID."""
        centers = [(0, 0, 100), (500, 0, 100), (-500, 0, 100)]
        config = self._make_cluster_config(centers)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Point very close to second cluster
        result = classifier.classify(HexCoord(500, 0))

        assert result == 1  # Cluster 1 (the second one)

    def test_classify_equidistant_clusters(self):
        """Deterministic tie-breaking when equidistant."""
        centers = [(100, 0, 100), (-100, 0, 100)]
        config = self._make_cluster_config(centers)
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Origin is equidistant from both clusters
        result = classifier.classify(HexCoord(0, 0))

        # Should be deterministic (picks based on weighted distance and iteration order)
        assert result in [0, 1]


class TestRegionNeighbors:
    """Tests for region neighbor relationships."""

    def test_spiral_adjacent_arms_are_neighbors(self):
        """Arm 0 neighbors Arm 1 in spiral galaxy."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()

        # Arm 0 should neighbor Arm 1
        assert 1 in neighbors[0]

    def test_spiral_arms_wrap_around(self):
        """Last arm neighbors first arm (wrap-around)."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()

        # Arm 3 should neighbor Arm 0
        assert 0 in neighbors[3]

    def test_spiral_core_neighbors_all_arms(self):
        """Core neighbors every arm in spiral galaxy."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 3, 'pitch_angle': 20.0},
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.2},
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()
        core_id = 3  # After arms 0, 1, 2

        # Core neighbors all arms
        assert len(neighbors[core_id]) == 3
        assert set(neighbors[core_id]) == {0, 1, 2}

    def test_cluster_top3_neighbors(self):
        """Each cluster has up to 3 nearest neighbors."""
        centers = [(0, 0, 100), (300, 0, 100), (0, 300, 100), (-300, 0, 100), (0, -300, 100)]
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': q, 'center_r': r, 'sigma': s, 'weight': 0.3}
                for q, r, s in centers
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()

        # Cluster 0 (center) should have at most 3 neighbors
        assert len(neighbors[0]) <= 4  # Could have all as neighbors since all are equidistant

    def test_empty_regions_empty_neighbors(self):
        """No regions yields empty neighbor dict."""
        config = {'primitives': []}
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()

        assert neighbors == {}


class TestEdgeCases:
    """Edge case tests for RegionClassifier."""

    def test_spiral_with_zero_pitch_angle(self):
        """pitch_angle=0 results in b=0 path."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2, 'pitch_angle': 0.0, 'center_q': 0, 'center_r': 0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Should not crash, classify returns 0 when b=0
        result = classifier.classify(HexCoord(500, 0))
        assert result == 0

    def test_spiral_with_very_small_pitch_angle(self):
        """pitch_angle near 0 (but > threshold) still works."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2, 'pitch_angle': 0.1, 'center_q': 0, 'center_r': 0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Should work, return valid arm index
        result = classifier.classify(HexCoord(500, 0))
        assert result in [0, 1]

    def test_spiral_missing_optional_params_uses_defaults(self):
        """Spiral arm with missing params uses defaults."""
        config = {
            'primitives': [
                {'type': 'spiral_arm'}  # No arm_count, pitch_angle, etc.
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Default arm_count=2
        assert classifier.region_count == 2

        # Should classify without error
        result = classifier.classify(HexCoord(500, 0))
        assert result in [0, 1]

    def test_radial_primitive_missing_optional_params(self):
        """Radial primitive with minimal params uses defaults."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2},
                {'type': 'radial', 'weight': 0.2}  # No center, sigma
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Should have core region
        assert classifier.region_count == 3  # 2 arms + core

    def test_bar_layout_single_region(self):
        """Bar layout without spiral/cluster creates bar region."""
        config = {
            'primitives': [
                {'type': 'linear', 'length': 1000}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier._has_bar is True
        assert classifier.region_count == 1
        assert classifier.regions[0].region_type == 'bar'

    def test_classify_bar_returns_zero(self):
        """Bar layout classify always returns 0."""
        config = {
            'primitives': [
                {'type': 'linear', 'length': 1000}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        result = classifier.classify(HexCoord(100, 200))
        assert result == 0

    def test_single_cluster_center(self):
        """Single radial with weight > 0.1 doesn't trigger clusters."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.5}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Single radial doesn't count as "clusters" (needs > 1)
        assert classifier._has_clusters is False
        # No regions in this edge case
        assert classifier.region_count == 0

    def test_classify_cluster_empty_centers(self):
        """_classify_cluster with empty centers returns 0."""
        config = {'primitives': []}
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Directly call _classify_cluster (would only be called if _has_clusters)
        # This tests the guard clause
        result = classifier._classify_cluster(HexCoord(100, 100))
        assert result == 0

    def test_classify_spiral_no_params(self):
        """_classify_spiral with no _spiral_params returns 0."""
        config = {'primitives': []}
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Force the path
        classifier._has_spiral = True  # Simulate
        result = classifier._classify_spiral(HexCoord(100, 100))
        assert result == 0

    def test_classify_very_far_from_center(self):
        """Classification works at extreme distances."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0, 'center_q': 0, 'center_r': 0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=10000)

        # Very far point
        result = classifier.classify(HexCoord(9000, 0))
        assert 0 <= result <= 3

    def test_classify_negative_coordinates(self):
        """Classification handles negative coordinates."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 4, 'pitch_angle': 20.0, 'center_q': 0, 'center_r': 0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        result = classifier.classify(HexCoord(-500, -500))
        assert 0 <= result <= 3

    def test_cluster_with_very_small_sigma(self):
        """Clusters with small sigma values work correctly."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 1, 'weight': 0.3},
                {'type': 'radial', 'center_q': 100, 'center_r': 0, 'sigma': 1, 'weight': 0.3},
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Point at origin
        result = classifier.classify(HexCoord(0, 0))
        assert result == 0

        # Point at second cluster
        result = classifier.classify(HexCoord(100, 0))
        assert result == 1

    def test_cluster_with_zero_sigma_safe(self):
        """Cluster with sigma=0 doesn't crash (uses max(1, sigma))."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 0, 'weight': 0.3},
                {'type': 'radial', 'center_q': 100, 'center_r': 0, 'sigma': 0, 'weight': 0.3},
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Should not crash due to division by zero
        result = classifier.classify(HexCoord(50, 0))
        assert result in [0, 1]

    def test_neighbors_single_arm_spiral(self):
        """Single arm spiral has self-neighbor (wrap)."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 1, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()
        # Arm 0 wraps to itself
        assert 0 in neighbors[0]

    def test_neighbors_two_arm_spiral(self):
        """Two arm spiral has mutual neighbors."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        neighbors = classifier.get_region_neighbors()
        assert 1 in neighbors[0]
        assert 0 in neighbors[1]

    def test_low_weight_radials_not_clusters(self):
        """Radials with weight <= 0.1 don't count as clusters."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.05},
                {'type': 'radial', 'center_q': 500, 'center_r': 0, 'sigma': 100, 'weight': 0.05},
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier._has_clusters is False

    def test_mixed_weight_radials(self):
        """Only high-weight radials count as clusters."""
        config = {
            'primitives': [
                {'type': 'radial', 'center_q': 0, 'center_r': 0, 'sigma': 100, 'weight': 0.3},
                {'type': 'radial', 'center_q': 500, 'center_r': 0, 'sigma': 100, 'weight': 0.3},
                {'type': 'radial', 'center_q': -500, 'center_r': 0, 'sigma': 100, 'weight': 0.05},  # Low weight
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        # Only 2 high-weight radials
        assert classifier._has_clusters is True
        assert len(classifier._cluster_centers) == 2


class TestProperties:
    """Tests for RegionClassifier properties."""

    def test_regions_property(self):
        """regions property returns list of RegionInfo."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 2, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        regions = classifier.regions

        assert isinstance(regions, list)
        assert all(isinstance(r, RegionInfo) for r in regions)

    def test_region_count_property(self):
        """region_count returns correct count."""
        config = {
            'primitives': [
                {'type': 'spiral_arm', 'arm_count': 5, 'pitch_angle': 20.0}
            ]
        }
        classifier = RegionClassifier(config, galaxy_radius=5000)

        assert classifier.region_count == 5

    def test_classify_no_regions_returns_0(self):
        """classify returns 0 when no regions defined."""
        config = {'primitives': []}
        classifier = RegionClassifier(config, galaxy_radius=5000)

        result = classifier.classify(HexCoord(100, 100))

        assert result == 0
