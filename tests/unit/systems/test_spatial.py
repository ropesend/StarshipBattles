"""Tests for SpatialGrid class behavior."""
import pytest
import pygame

from game.engine.spatial import SpatialGrid


class MockObject:
    """Simple mock object with a position for spatial grid testing."""
    def __init__(self, x, y, name="obj"):
        self.position = pygame.math.Vector2(x, y)
        self.name = name

    def __repr__(self):
        return f"MockObject({self.name} at {self.position})"


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()
    from game.core.registry import RegistryManager
    RegistryManager.instance().clear()


class TestSpatialGridBasics:
    """Test basic SpatialGrid initialization and operations."""

    def test_grid_initialization(self, pygame_init):
        """SpatialGrid should initialize with correct cell size."""
        grid = SpatialGrid(cell_size=1000)
        assert grid.cell_size == 1000
        assert grid.buckets == {}

    def test_default_cell_size(self, pygame_init):
        """SpatialGrid should use default cell size of 2000."""
        grid = SpatialGrid()
        assert grid.cell_size == 2000

    def test_insert_single_object(self, pygame_init):
        """Inserting an object should add it to the correct bucket."""
        grid = SpatialGrid(cell_size=100)
        obj = MockObject(50, 50, "A")

        grid.insert(obj)

        # Object at (50, 50) with cell_size=100 should be in cell (0, 0)
        assert (0, 0) in grid.buckets
        assert obj in grid.buckets[(0, 0)]

    def test_insert_multiple_objects_same_cell(self, pygame_init):
        """Multiple objects in same cell should share a bucket."""
        grid = SpatialGrid(cell_size=100)
        obj1 = MockObject(10, 10, "A")
        obj2 = MockObject(20, 20, "B")

        grid.insert(obj1)
        grid.insert(obj2)

        assert len(grid.buckets[(0, 0)]) == 2

    def test_insert_objects_different_cells(self, pygame_init):
        """Objects in different cells should be in separate buckets."""
        grid = SpatialGrid(cell_size=100)
        obj1 = MockObject(50, 50, "A")    # Cell (0, 0)
        obj2 = MockObject(150, 50, "B")   # Cell (1, 0)

        grid.insert(obj1)
        grid.insert(obj2)

        assert (0, 0) in grid.buckets
        assert (1, 0) in grid.buckets
        assert obj1 in grid.buckets[(0, 0)]
        assert obj2 in grid.buckets[(1, 0)]

    def test_clear_empties_grid(self, pygame_init):
        """Clear should remove all objects from the grid."""
        grid = SpatialGrid(cell_size=100)
        grid.insert(MockObject(50, 50))
        grid.insert(MockObject(150, 150))

        assert len(grid.buckets) > 0

        grid.clear()

        assert grid.buckets == {}


class TestSpatialGridQueries:
    """Test SpatialGrid query_radius functionality."""

    def test_query_finds_object_in_range(self, pygame_init):
        """Query should return objects within specified radius."""
        grid = SpatialGrid(cell_size=100)
        obj = MockObject(50, 50, "A")
        grid.insert(obj)

        # Query from origin with radius 100 should find the object
        results = grid.query_radius(pygame.math.Vector2(0, 0), 100)

        assert obj in results

    def test_query_returns_empty_for_far_objects(self, pygame_init):
        """Query should not return objects outside the cell range."""
        grid = SpatialGrid(cell_size=100)
        obj = MockObject(5000, 5000, "Far")
        grid.insert(obj)

        # Query from origin with small radius
        results = grid.query_radius(pygame.math.Vector2(0, 0), 50)

        assert obj not in results

    def test_query_crosses_cell_boundaries(self, pygame_init):
        """Query should check neighboring cells when radius spans boundaries."""
        grid = SpatialGrid(cell_size=100)
        # Object just past the cell boundary
        obj = MockObject(110, 0, "EdgeObj")
        grid.insert(obj)

        # Query from near origin with radius that reaches the next cell
        results = grid.query_radius(pygame.math.Vector2(0, 0), 150)

        assert obj in results

    def test_query_returns_candidates_not_exact_distance(self, pygame_init):
        """Query returns all objects in overlapping cells, not just those in exact radius."""
        grid = SpatialGrid(cell_size=100)
        # Object at corner of cell (0, 0), close to boundary
        obj1 = MockObject(99, 99, "Close")
        obj2 = MockObject(5, 5, "Near")
        grid.insert(obj1)
        grid.insert(obj2)

        # Query from origin with small radius - both in same cell, both returned
        results = grid.query_radius(pygame.math.Vector2(0, 0), 10)

        # Both objects are in cell (0,0) which is within range steps
        assert obj2 in results
        # Note: obj1 is also in cell (0,0), so it's returned even if geometrically further
        assert obj1 in results

    def test_query_with_negative_coordinates(self, pygame_init):
        """Query should work correctly with negative coordinates."""
        grid = SpatialGrid(cell_size=100)
        obj = MockObject(-50, -50, "Negative")
        grid.insert(obj)

        results = grid.query_radius(pygame.math.Vector2(-100, -100), 100)

        assert obj in results
