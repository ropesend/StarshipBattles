"""Extended tests for SpatialGrid edge cases."""
import pytest
import pygame

from game.engine.spatial import SpatialGrid


class MockObject:
    """Mock object with position for spatial grid testing."""
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()
    from game.core.registry import RegistryManager
    RegistryManager.instance().clear()


class TestSpatialGridBasics:
    """Test basic SpatialGrid operations."""

    def test_grid_initialization(self, pygame_init):
        """Grid should initialize with specified cell size."""
        grid = SpatialGrid(cell_size=1000)

        assert grid.cell_size == 1000
        assert grid.buckets == {}

    def test_insert_creates_bucket(self, pygame_init):
        """Inserting object should create bucket."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(500, 500)

        grid.insert(obj)

        assert len(grid.buckets) > 0

    def test_clear_removes_all(self, pygame_init):
        """clear() should empty all buckets."""
        grid = SpatialGrid(cell_size=1000)
        grid.insert(MockObject(0, 0))
        grid.insert(MockObject(100, 100))
        grid.insert(MockObject(5000, 5000))

        assert len(grid.buckets) > 0

        grid.clear()

        assert grid.buckets == {}


class TestSpatialGridQueries:
    """Test SpatialGrid query operations."""

    def test_query_radius_empty_grid(self, pygame_init):
        """Empty grid should return empty list."""
        grid = SpatialGrid(cell_size=1000)

        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)

        assert result == []

    def test_query_radius_finds_nearby(self, pygame_init):
        """Should find objects within radius."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(100, 100)
        grid.insert(obj)

        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)

        assert obj in result

    def test_query_radius_ignores_distant(self, pygame_init):
        """Should not include objects outside query cells."""
        grid = SpatialGrid(cell_size=1000)
        near_obj = MockObject(100, 100)
        far_obj = MockObject(10000, 10000)  # Very far away
        grid.insert(near_obj)
        grid.insert(far_obj)

        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)

        assert near_obj in result
        assert far_obj not in result


class TestSpatialGridCellAssignment:
    """Test correct cell assignment."""

    def test_same_cell_multiple_objects(self, pygame_init):
        """Multiple objects in same cell should all be in same bucket."""
        grid = SpatialGrid(cell_size=1000)
        obj1 = MockObject(100, 100)
        obj2 = MockObject(200, 200)
        obj3 = MockObject(300, 300)

        grid.insert(obj1)
        grid.insert(obj2)
        grid.insert(obj3)

        # All should be in cell (0, 0)
        cell = (0, 0)
        assert cell in grid.buckets
        assert len(grid.buckets[cell]) == 3

    def test_different_cells_different_buckets(self, pygame_init):
        """Objects in different cells should be in different buckets."""
        grid = SpatialGrid(cell_size=1000)
        obj1 = MockObject(100, 100)  # Cell (0, 0)
        obj2 = MockObject(1500, 1500)  # Cell (1, 1)

        grid.insert(obj1)
        grid.insert(obj2)

        assert len(grid.buckets) == 2

    def test_negative_coordinates_handled(self, pygame_init):
        """Negative coordinates should work correctly."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(-500, -500)

        grid.insert(obj)

        # Should be in cell (-1, -1)
        cell = (-1, -1)
        assert cell in grid.buckets
        assert obj in grid.buckets[cell]


class TestSpatialGridQueryRadius:
    """Test query_radius across cell boundaries."""

    def test_query_spans_multiple_cells(self, pygame_init):
        """Large radius should query multiple cells."""
        grid = SpatialGrid(cell_size=1000)

        # Place objects in different cells
        obj_center = MockObject(0, 0)       # Cell (0, 0)
        obj_right = MockObject(1500, 0)     # Cell (1, 0)
        obj_up = MockObject(0, 1500)        # Cell (0, 1)

        grid.insert(obj_center)
        grid.insert(obj_right)
        grid.insert(obj_up)

        # Query with large radius from center
        result = grid.query_radius(pygame.math.Vector2(500, 500), 2000)

        # Should find all three
        assert obj_center in result
        assert obj_right in result
        assert obj_up in result
