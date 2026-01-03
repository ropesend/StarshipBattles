"""Extended tests for SpatialGrid edge cases."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.engine.spatial import SpatialGrid


class MockObject:
    """Mock object with position for spatial grid testing."""
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)


class TestSpatialGridBasics(unittest.TestCase):
    """Test basic SpatialGrid operations."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_grid_initialization(self):
        """Grid should initialize with specified cell size."""
        grid = SpatialGrid(cell_size=1000)
        
        self.assertEqual(grid.cell_size, 1000)
        self.assertEqual(grid.buckets, {})
    
    def test_insert_creates_bucket(self):
        """Inserting object should create bucket."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(500, 500)
        
        grid.insert(obj)
        
        self.assertGreater(len(grid.buckets), 0)
    
    def test_clear_removes_all(self):
        """clear() should empty all buckets."""
        grid = SpatialGrid(cell_size=1000)
        grid.insert(MockObject(0, 0))
        grid.insert(MockObject(100, 100))
        grid.insert(MockObject(5000, 5000))
        
        self.assertGreater(len(grid.buckets), 0)
        
        grid.clear()
        
        self.assertEqual(grid.buckets, {})


class TestSpatialGridQueries(unittest.TestCase):
    """Test SpatialGrid query operations."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_query_radius_empty_grid(self):
        """Empty grid should return empty list."""
        grid = SpatialGrid(cell_size=1000)
        
        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)
        
        self.assertEqual(result, [])
    
    def test_query_radius_finds_nearby(self):
        """Should find objects within radius."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(100, 100)
        grid.insert(obj)
        
        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)
        
        self.assertIn(obj, result)
    
    def test_query_radius_ignores_distant(self):
        """Should not include objects outside query cells."""
        grid = SpatialGrid(cell_size=1000)
        near_obj = MockObject(100, 100)
        far_obj = MockObject(10000, 10000)  # Very far away
        grid.insert(near_obj)
        grid.insert(far_obj)
        
        result = grid.query_radius(pygame.math.Vector2(0, 0), 500)
        
        self.assertIn(near_obj, result)
        self.assertNotIn(far_obj, result)


class TestSpatialGridCellAssignment(unittest.TestCase):
    """Test correct cell assignment."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_same_cell_multiple_objects(self):
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
        self.assertIn(cell, grid.buckets)
        self.assertEqual(len(grid.buckets[cell]), 3)
    
    def test_different_cells_different_buckets(self):
        """Objects in different cells should be in different buckets."""
        grid = SpatialGrid(cell_size=1000)
        obj1 = MockObject(100, 100)  # Cell (0, 0)
        obj2 = MockObject(1500, 1500)  # Cell (1, 1)
        
        grid.insert(obj1)
        grid.insert(obj2)
        
        self.assertEqual(len(grid.buckets), 2)
    
    def test_negative_coordinates_handled(self):
        """Negative coordinates should work correctly."""
        grid = SpatialGrid(cell_size=1000)
        obj = MockObject(-500, -500)
        
        grid.insert(obj)
        
        # Should be in cell (-1, -1)
        cell = (-1, -1)
        self.assertIn(cell, grid.buckets)
        self.assertIn(obj, grid.buckets[cell])


class TestSpatialGridQueryRadius(unittest.TestCase):
    """Test query_radius across cell boundaries."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_query_spans_multiple_cells(self):
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
        self.assertIn(obj_center, result)
        self.assertIn(obj_right, result)
        self.assertIn(obj_up, result)


if __name__ == '__main__':
    unittest.main()
