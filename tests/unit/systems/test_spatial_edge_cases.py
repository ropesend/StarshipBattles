"""
Unit tests for SpatialGrid query edge cases.

Tests cell boundary queries, negative coordinates,
empty grid queries, radius=0 queries, and many objects.
"""
import pytest
from dataclasses import dataclass

from game.core.math import Vector2
from game.engine.spatial import SpatialGrid


@dataclass
class MockObject:
    """Mock object with position for spatial grid testing."""
    position: Vector2


class TestSpatialGridQueryEdgeCases:
    """Tests for SpatialGrid query edge cases."""

    def test_query_radius_at_cell_boundary(self):
        """Object exactly on cell boundary is found."""
        grid = SpatialGrid(cell_size=100)

        # Place object exactly at cell boundary (100, 100)
        obj = MockObject(position=Vector2(100.0, 100.0))
        grid.insert(obj)

        # Query from slightly different position should find it
        results = grid.query_radius(Vector2(99.0, 99.0), radius=10)
        assert obj in results

    def test_query_negative_coordinates(self):
        """Objects at negative positions are found."""
        grid = SpatialGrid(cell_size=100)

        # Place objects at negative coordinates
        obj1 = MockObject(position=Vector2(-150.0, -200.0))
        obj2 = MockObject(position=Vector2(-50.0, -50.0))
        grid.insert(obj1)
        grid.insert(obj2)

        # Query in negative space
        results = grid.query_radius(Vector2(-100.0, -100.0), radius=200)

        assert obj1 in results
        assert obj2 in results

    def test_query_empty_grid(self):
        """Empty grid returns empty list."""
        grid = SpatialGrid(cell_size=100)

        results = grid.query_radius(Vector2(500.0, 500.0), radius=1000)

        assert results == []

    def test_query_radius_zero(self):
        """radius=0 returns objects in same cell only."""
        grid = SpatialGrid(cell_size=100)

        # Object in cell (0, 0) - positions 0-99
        obj_same_cell = MockObject(position=Vector2(50.0, 50.0))
        # Object in cell (1, 1) - positions 100-199
        obj_other_cell = MockObject(position=Vector2(150.0, 150.0))

        grid.insert(obj_same_cell)
        grid.insert(obj_other_cell)

        # Query with radius=0 from center of cell (0, 0)
        results = grid.query_radius(Vector2(50.0, 50.0), radius=0)

        # With radius=0, steps = ceil(0/100) = 0, so only current cell checked
        assert obj_same_cell in results
        assert obj_other_cell not in results

    def test_insert_and_query_many_objects(self):
        """100+ objects handled correctly."""
        grid = SpatialGrid(cell_size=100)

        objects = []
        # Insert 150 objects spread across the grid
        for i in range(150):
            x = (i % 10) * 50  # 0 to 450
            y = (i // 10) * 50  # 0 to 700
            obj = MockObject(position=Vector2(float(x), float(y)))
            objects.append(obj)
            grid.insert(obj)

        # Query with large radius should find all
        results = grid.query_radius(Vector2(225.0, 350.0), radius=1000)

        # All objects should be in results
        for obj in objects:
            assert obj in results

    def test_query_across_multiple_cells(self):
        """Query spanning multiple cells finds all relevant objects."""
        grid = SpatialGrid(cell_size=100)

        # Objects in different cells
        obj1 = MockObject(position=Vector2(50.0, 50.0))    # Cell (0, 0)
        obj2 = MockObject(position=Vector2(150.0, 50.0))   # Cell (1, 0)
        obj3 = MockObject(position=Vector2(50.0, 150.0))   # Cell (0, 1)
        obj4 = MockObject(position=Vector2(150.0, 150.0))  # Cell (1, 1)

        grid.insert(obj1)
        grid.insert(obj2)
        grid.insert(obj3)
        grid.insert(obj4)

        # Query from center with radius covering all 4 cells
        results = grid.query_radius(Vector2(100.0, 100.0), radius=150)

        assert obj1 in results
        assert obj2 in results
        assert obj3 in results
        assert obj4 in results

    def test_clear_removes_all_objects(self):
        """Clear method removes all objects from grid."""
        grid = SpatialGrid(cell_size=100)

        obj = MockObject(position=Vector2(50.0, 50.0))
        grid.insert(obj)

        # Verify object is in grid
        results_before = grid.query_radius(Vector2(50.0, 50.0), radius=50)
        assert obj in results_before

        # Clear and verify empty
        grid.clear()

        results_after = grid.query_radius(Vector2(50.0, 50.0), radius=50)
        assert results_after == []
