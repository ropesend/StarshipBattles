"""
Unit tests for SpatialIndex class.

Tests grid-based spatial indexing for efficient neighbor queries.
"""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.spatial_index import SpatialIndex


class TestSpatialIndexBasics:
    """Basic functionality tests for SpatialIndex."""

    def test_create_empty_index(self):
        """Can create an empty spatial index."""
        index = SpatialIndex(cell_size=100)
        assert index is not None
        assert index.cell_size == 100

    def test_add_single_point(self):
        """Can add a single point to the index."""
        index = SpatialIndex(cell_size=100)
        coord = HexCoord(50, 50)

        index.add(coord, "system_a")

        # Should be able to find it
        neighbors = index.get_neighbors(coord, radius=10)
        assert len(neighbors) == 1
        assert neighbors[0][1] == "system_a"

    def test_add_multiple_points(self):
        """Can add multiple points to the index."""
        index = SpatialIndex(cell_size=100)

        index.add(HexCoord(0, 0), "a")
        index.add(HexCoord(50, 50), "b")
        index.add(HexCoord(100, 100), "c")

        # All should be findable with large enough radius
        neighbors = index.get_neighbors(HexCoord(0, 0), radius=200)
        assert len(neighbors) == 3

    def test_get_neighbors_returns_empty_for_empty_index(self):
        """get_neighbors returns empty list for empty index."""
        index = SpatialIndex(cell_size=100)

        neighbors = index.get_neighbors(HexCoord(0, 0), radius=100)

        assert neighbors == []


class TestSpatialIndexNeighborQuery:
    """Tests for neighbor query functionality."""

    def test_get_neighbors_within_radius(self):
        """get_neighbors returns only points within radius."""
        index = SpatialIndex(cell_size=100)

        # Add points at various distances from origin
        index.add(HexCoord(0, 0), "origin")
        index.add(HexCoord(10, 0), "close")      # ~10 hex distance
        index.add(HexCoord(500, 0), "far")       # ~500 hex distance

        # Query with small radius should only find close ones
        neighbors = index.get_neighbors(HexCoord(0, 0), radius=50)

        data_values = [data for coord, data in neighbors]
        assert "origin" in data_values
        assert "close" in data_values
        assert "far" not in data_values

    def test_get_neighbors_returns_with_distance(self):
        """get_neighbors returns (coord, data) tuples."""
        index = SpatialIndex(cell_size=100)
        coord = HexCoord(25, 25)
        index.add(coord, "test_data")

        neighbors = index.get_neighbors(HexCoord(0, 0), radius=100)

        assert len(neighbors) == 1
        result_coord, result_data = neighbors[0]
        assert result_coord == coord
        assert result_data == "test_data"

    def test_get_neighbors_excludes_self(self):
        """get_neighbors can optionally exclude the query point."""
        index = SpatialIndex(cell_size=100)
        query_coord = HexCoord(0, 0)

        index.add(query_coord, "self")
        index.add(HexCoord(10, 10), "other")

        # Exclude self
        neighbors = index.get_neighbors(query_coord, radius=50, exclude_coord=query_coord)

        data_values = [data for coord, data in neighbors]
        assert "self" not in data_values
        assert "other" in data_values

    def test_get_k_nearest(self):
        """get_k_nearest returns the k closest points."""
        index = SpatialIndex(cell_size=100)

        # Add points at increasing distances
        index.add(HexCoord(0, 0), "origin")
        index.add(HexCoord(10, 0), "d10")
        index.add(HexCoord(20, 0), "d20")
        index.add(HexCoord(30, 0), "d30")
        index.add(HexCoord(100, 0), "d100")

        # Get 3 nearest to origin
        nearest = index.get_k_nearest(HexCoord(0, 0), k=3)

        assert len(nearest) == 3
        data_values = [data for coord, data in nearest]
        # Should be the 3 closest
        assert "origin" in data_values
        assert "d10" in data_values
        assert "d20" in data_values
        assert "d100" not in data_values

    def test_get_k_nearest_excludes_self(self):
        """get_k_nearest can exclude the query point."""
        index = SpatialIndex(cell_size=100)
        query = HexCoord(0, 0)

        index.add(query, "self")
        index.add(HexCoord(10, 0), "neighbor1")
        index.add(HexCoord(20, 0), "neighbor2")

        nearest = index.get_k_nearest(query, k=2, exclude_coord=query)

        data_values = [data for coord, data in nearest]
        assert "self" not in data_values
        assert len(nearest) == 2

    def test_get_k_nearest_finds_far_only_neighbor_in_sparse_index(self):
        """In sparse layouts, k-nearest must still find a far-away only neighbor.

        Regression: SpatialIndex.get_k_nearest() previously stopped expanding
        the search radius once the candidate count stopped changing. With two
        points many cell-widths apart and no points in between, a starting
        empty-cell scan could lock the candidate count at 0 and return [].
        Reproduces the seed-2 N=2 galaxy isolation: two systems at
        HexCoord(2844, -2615) and HexCoord(2029, 1486) — distance 4101 with
        cell_size=500 — must still see each other.
        """
        index = SpatialIndex(cell_size=500)
        a = HexCoord(2844, -2615)
        b = HexCoord(2029, 1486)
        index.add(a, "a")
        index.add(b, "b")

        nearest = index.get_k_nearest(a, k=1, exclude_coord=a)

        assert len(nearest) == 1
        assert nearest[0][1] == "b"


class TestSpatialIndexPerformance:
    """Tests for spatial index performance characteristics."""

    def test_handles_many_points_same_cell(self):
        """Index handles multiple points in the same cell."""
        index = SpatialIndex(cell_size=1000)

        # Add many points within one cell
        for i in range(50):
            index.add(HexCoord(i, i), f"point_{i}")

        neighbors = index.get_neighbors(HexCoord(25, 25), radius=100)

        # Should find points within radius
        assert len(neighbors) > 0
        assert len(neighbors) <= 50

    def test_handles_negative_coordinates(self):
        """Index handles negative coordinates correctly."""
        index = SpatialIndex(cell_size=100)

        index.add(HexCoord(-50, -50), "negative")
        index.add(HexCoord(50, 50), "positive")
        index.add(HexCoord(-50, 50), "mixed1")
        index.add(HexCoord(50, -50), "mixed2")

        # Query from origin should find all with large radius
        neighbors = index.get_neighbors(HexCoord(0, 0), radius=200)

        assert len(neighbors) == 4

    def test_clear_removes_all_points(self):
        """clear() removes all points from the index."""
        index = SpatialIndex(cell_size=100)

        index.add(HexCoord(0, 0), "a")
        index.add(HexCoord(100, 100), "b")

        index.clear()

        neighbors = index.get_neighbors(HexCoord(0, 0), radius=500)
        assert neighbors == []

    def test_bulk_add(self):
        """bulk_add efficiently adds multiple points."""
        index = SpatialIndex(cell_size=100)

        points = [(HexCoord(i * 10, i * 5), f"sys_{i}") for i in range(100)]

        index.bulk_add(points)

        # Should all be findable
        neighbors = index.get_neighbors(HexCoord(500, 250), radius=1000)
        assert len(neighbors) == 100


class TestSpatialIndexMinDistance:
    """Tests for minimum distance checking."""

    def test_has_neighbor_within_distance_true(self):
        """has_neighbor_within_distance returns True when neighbor exists."""
        index = SpatialIndex(cell_size=100)

        index.add(HexCoord(0, 0), "existing")

        # Point within distance
        result = index.has_neighbor_within_distance(HexCoord(5, 5), min_dist=50)

        assert result is True

    def test_has_neighbor_within_distance_false(self):
        """has_neighbor_within_distance returns False when no neighbor exists."""
        index = SpatialIndex(cell_size=100)

        index.add(HexCoord(0, 0), "existing")

        # Point outside distance
        result = index.has_neighbor_within_distance(HexCoord(100, 100), min_dist=50)

        assert result is False

    def test_has_neighbor_within_distance_empty_index(self):
        """has_neighbor_within_distance returns False for empty index."""
        index = SpatialIndex(cell_size=100)

        result = index.has_neighbor_within_distance(HexCoord(0, 0), min_dist=50)

        assert result is False
