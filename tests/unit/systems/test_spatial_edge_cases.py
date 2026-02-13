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


class TestSpatialGridBoundaryEdgeCases:
    """TCG-FND-004: SpatialGrid.query_radius() boundary edge cases.

    Tests cell boundaries, negative coordinates, zero radius, and
    multi-object same-cell scenarios.
    """

    def test_object_exactly_on_cell_boundary_x(self):
        """Object at x=100 (cell boundary) is in cell (1, 0)."""
        grid = SpatialGrid(cell_size=100)

        # Position x=100 is exactly on boundary between cell 0 and 1
        # floor(100/100) = 1, so it's in cell (1, 0)
        obj = MockObject(position=Vector2(100.0, 50.0))
        grid.insert(obj)

        # Query from cell (0, 0) with radius reaching into cell (1, 0)
        results = grid.query_radius(Vector2(50.0, 50.0), radius=100)
        assert obj in results

        # Query from cell (1, 0) where object actually lives
        results = grid.query_radius(Vector2(150.0, 50.0), radius=50)
        assert obj in results

    def test_object_exactly_on_cell_boundary_y(self):
        """Object at y=100 (cell boundary) is in cell (0, 1)."""
        grid = SpatialGrid(cell_size=100)

        obj = MockObject(position=Vector2(50.0, 100.0))
        grid.insert(obj)

        # Query from cell (0, 0) with radius reaching into cell (0, 1)
        results = grid.query_radius(Vector2(50.0, 50.0), radius=100)
        assert obj in results

    def test_object_at_corner_boundary(self):
        """Object at (100, 100) exactly on corner is in cell (1, 1)."""
        grid = SpatialGrid(cell_size=100)

        obj = MockObject(position=Vector2(100.0, 100.0))
        grid.insert(obj)

        # floor(100/100) = 1 for both x and y
        cell = grid._get_cell(obj.position)
        assert cell == (1, 1)

        # Query from corner should find it
        results = grid.query_radius(Vector2(100.0, 100.0), radius=1)
        assert obj in results

    def test_negative_position_cell_assignment(self):
        """Negative positions use floor division correctly."""
        grid = SpatialGrid(cell_size=100)

        # floor(-50/100) = floor(-0.5) = -1
        obj = MockObject(position=Vector2(-50.0, -50.0))
        grid.insert(obj)

        cell = grid._get_cell(obj.position)
        assert cell == (-1, -1)

        # Query should find it
        results = grid.query_radius(Vector2(-50.0, -50.0), radius=10)
        assert obj in results

    def test_negative_boundary_cell_assignment(self):
        """Object at (-100, -100) is in cell (-1, -1)."""
        grid = SpatialGrid(cell_size=100)

        # floor(-100/100) = floor(-1.0) = -1
        obj = MockObject(position=Vector2(-100.0, -100.0))
        grid.insert(obj)

        cell = grid._get_cell(obj.position)
        assert cell == (-1, -1)

    def test_query_spanning_negative_and_positive_cells(self):
        """Query radius spanning from negative to positive cells."""
        grid = SpatialGrid(cell_size=100)

        # Objects in different quadrants
        obj_neg = MockObject(position=Vector2(-50.0, -50.0))  # Cell (-1, -1)
        obj_pos = MockObject(position=Vector2(50.0, 50.0))    # Cell (0, 0)
        grid.insert(obj_neg)
        grid.insert(obj_pos)

        # Query from origin with radius covering both
        results = grid.query_radius(Vector2(0.0, 0.0), radius=100)
        assert obj_neg in results
        assert obj_pos in results

    def test_multiple_objects_same_cell(self):
        """Multiple objects in the same cell are all returned."""
        grid = SpatialGrid(cell_size=100)

        # All objects in cell (0, 0) - positions 0-99
        obj1 = MockObject(position=Vector2(10.0, 10.0))
        obj2 = MockObject(position=Vector2(20.0, 20.0))
        obj3 = MockObject(position=Vector2(90.0, 90.0))
        grid.insert(obj1)
        grid.insert(obj2)
        grid.insert(obj3)

        # Query should return all three
        results = grid.query_radius(Vector2(50.0, 50.0), radius=0)
        assert obj1 in results
        assert obj2 in results
        assert obj3 in results

    def test_radius_zero_returns_only_current_cell(self):
        """Radius=0 returns only objects in the exact same cell."""
        grid = SpatialGrid(cell_size=100)

        obj_same_cell = MockObject(position=Vector2(10.0, 10.0))      # Cell (0, 0)
        obj_adjacent = MockObject(position=Vector2(110.0, 10.0))      # Cell (1, 0)
        grid.insert(obj_same_cell)
        grid.insert(obj_adjacent)

        # Query from cell (0, 0) with radius=0
        # ceil(0/100) = 0, so only cell (0, 0) is checked
        results = grid.query_radius(Vector2(50.0, 50.0), radius=0)
        assert obj_same_cell in results
        assert obj_adjacent not in results

    def test_radius_zero_from_negative_cell(self):
        """Radius=0 query in negative space returns correct cell."""
        grid = SpatialGrid(cell_size=100)

        obj = MockObject(position=Vector2(-50.0, -50.0))  # Cell (-1, -1)
        grid.insert(obj)

        results = grid.query_radius(Vector2(-50.0, -50.0), radius=0)
        assert obj in results

    def test_very_large_radius(self):
        """Very large radius spans many cells and returns all objects."""
        grid = SpatialGrid(cell_size=100)

        # Scatter objects across a wide area
        objects = []
        for x in range(-500, 600, 100):
            for y in range(-500, 600, 100):
                obj = MockObject(position=Vector2(float(x), float(y)))
                objects.append(obj)
                grid.insert(obj)

        # Query with very large radius from center
        results = grid.query_radius(Vector2(0.0, 0.0), radius=2000)

        # All objects should be found
        for obj in objects:
            assert obj in results

    def test_origin_position(self):
        """Object at origin (0, 0) is in cell (0, 0)."""
        grid = SpatialGrid(cell_size=100)

        obj = MockObject(position=Vector2(0.0, 0.0))
        grid.insert(obj)

        cell = grid._get_cell(obj.position)
        assert cell == (0, 0)

        results = grid.query_radius(Vector2(0.0, 0.0), radius=1)
        assert obj in results

    def test_fractional_positions(self):
        """Fractional positions are correctly assigned to cells."""
        grid = SpatialGrid(cell_size=100)

        # Position 99.9 should still be in cell (0, 0)
        obj1 = MockObject(position=Vector2(99.9, 99.9))
        # Position 100.1 should be in cell (1, 1)
        obj2 = MockObject(position=Vector2(100.1, 100.1))
        grid.insert(obj1)
        grid.insert(obj2)

        cell1 = grid._get_cell(obj1.position)
        cell2 = grid._get_cell(obj2.position)
        assert cell1 == (0, 0)
        assert cell2 == (1, 1)

    def test_query_position_near_cell_boundary(self):
        """Query position near boundary checks appropriate cells."""
        grid = SpatialGrid(cell_size=100)

        # Object in cell (1, 0)
        obj = MockObject(position=Vector2(150.0, 50.0))
        grid.insert(obj)

        # Query from position 99 (cell 0) with radius 60 should reach cell 1
        results = grid.query_radius(Vector2(99.0, 50.0), radius=60)
        assert obj in results
