import unittest
from unittest.mock import MagicMock, patch, mock_open
import math
import sys
import os
import json

# Adjust path to find formation_editor if necessary
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    import formation_editor
except ImportError:
    # Attempt to add parent directory if running from tests/
    parent_dir = os.path.dirname(os.getcwd())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    import formation_editor

class TestFormationCore(unittest.TestCase):
    def setUp(self):
        self.core = formation_editor.FormationCore()

    def test_add_arrow(self):
        """Test logical addition of arrows."""
        pos = (150, 200)
        self.core.add_arrow(pos)
        
        self.assertEqual(len(self.core.arrows), 1)
        self.assertEqual(self.core.arrows[0], [150, 200])
        self.assertEqual(len(self.core.arrow_attrs), 1)
        self.assertEqual(self.core.selected_indices, {0})

    def test_move_arrow(self):
        """Test reordering arrows."""
        # Add 3 arrows: A, B, C
        self.core.arrows = [[0,0], [1,1], [2,2]]
        self.core.arrow_attrs = [{'n':0}, {'n':1}, {'n':2}]
        
        # Move index 0 (A) to index 2 (End) -> should be B, C, A
        self.core.move_arrow(0, 2)
        
        self.assertEqual(self.core.arrows, [[1,1], [2,2], [0,0]])
        self.assertEqual(self.core.arrow_attrs, [{'n':1}, {'n':2}, {'n':0}])
        # Selection should follow the moved item (new index 2)
        self.assertEqual(self.core.selected_indices, {2})
        
        # Move index 2 (A) back to 0 -> A, B, C
        self.core.move_arrow(2, 0)
        self.assertEqual(self.core.arrows, [[0,0], [1,1], [2,2]])

    def test_delete_selected(self):
        """Test deletion logic."""
        # Add 3 arrows: 0, 1, 2
        self.core.arrows = [[0,0], [1,1], [2,2]]
        self.core.arrow_attrs = [{'n':0}, {'n':1}, {'n':2}]
        
        # Select index 1
        self.core.selected_indices = {1}
        
        self.core.delete_selected()
        
        self.assertEqual(len(self.core.arrows), 2)
        self.assertEqual(self.core.arrows, [[0,0], [2,2]]) # 1 removed
        self.assertEqual(self.core.arrow_attrs, [{'n':0}, {'n':2}])
        self.assertEqual(self.core.selected_indices, set())

    def test_generate_shape_line(self):
        """Verify ships are placed in a linear sequence."""
        self.core.shape_count = 5
        center = (100, 100)
        self.core.generate_shape('line', center)
        
        self.assertEqual(len(self.core.arrows), 5)
        
        # Check linearity: Y should be constant (equal to center Y), X changes
        for x, y in self.core.arrows:
            self.assertAlmostEqual(y, 100)
            
        xs = [p[0] for p in self.core.arrows]
        self.assertEqual(xs, sorted(xs))
        self.assertTrue(xs[-1] > xs[0])

    def test_generate_shape_circle(self):
        """Verify coordinates form a circle around center."""
        self.core.shape_count = 8
        center = (500, 500)
        self.core.generate_shape('circle', center)
        
        self.assertEqual(len(self.core.arrows), 8)
        
        expected_radius = 200
        for x, y in self.core.arrows:
            dist = math.hypot(x - center[0], y - center[1])
            self.assertAlmostEqual(dist, expected_radius, delta=1.0)

    def test_generate_shape_disc(self):
        """Verify point distribution follows the spiral pattern."""
        self.core.shape_count = 10
        center = (0, 0)
        self.core.generate_shape('disc', center)
        
        self.assertEqual(len(self.core.arrows), 10)
        radius = 200
        
        # Verify all points are within the disc radius
        for x, y in self.core.arrows:
            dist = math.hypot(x, y)
            self.assertLessEqual(dist, radius + 1.0)
            
        # Verify points are distinct
        coords = [tuple(p) for p in self.core.arrows]
        self.assertEqual(len(set(coords)), 10)

    def test_generate_shape_x(self):
        """Verify the cross pattern coordinates."""
        self.core.shape_count = 6
        center = (0, 0)
        self.core.generate_shape('x', center)
        
        self.assertEqual(len(self.core.arrows), 6)
        
        # Center of mass should be roughly the center
        xs = [p[0] for p in self.core.arrows]
        ys = [p[1] for p in self.core.arrows]
        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)
        
        self.assertAlmostEqual(avg_x, 0, delta=5.0)
        self.assertAlmostEqual(avg_y, 0, delta=5.0)

    def test_save_to_file(self):
        """Test saving logic using mock file."""
        self.core.arrows = [[10, 20]]
        self.core.arrow_attrs = [{'rotation_mode': 'fixed'}]
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_dump:
                self.core.save_to_file("test.json")
                
                mock_file.assert_called_with("test.json", 'w')
                mock_dump.assert_called()
                args, _ = mock_dump.call_args
                expected_data = {
                    'arrows': [{'pos': [10, 20], 'rotation_mode': 'fixed'}]
                }
                self.assertEqual(args[0], expected_data)

    def test_load_from_file(self):
        """Test loading logic using mock file."""
        sample_data = {
            'arrows': [
                {'pos': [50, 60], 'rotation_mode': 'relative'},
                {'pos': [70, 80], 'rotation_mode': 'fixed'}
            ]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(sample_data))):
            self.core.load_from_file("test.json")
            
            self.assertEqual(len(self.core.arrows), 2)
            self.assertEqual(self.core.arrows[0], [50, 60])
            self.assertEqual(self.core.arrows[1], [70, 80])
            self.assertEqual(self.core.arrow_attrs[0]['rotation_mode'], 'relative')
            self.assertEqual(self.core.arrow_attrs[1]['rotation_mode'], 'fixed')

    def test_toggle_rotation_mode(self):
        """Test toggling rotation mode logic."""
        self.core.arrows = [[0,0], [1,1]]
        self.core.arrow_attrs = [{'rotation_mode': 'relative'}, {'rotation_mode': 'relative'}]
        self.core.selected_indices = {0}
        
        # Toggle 0 to fixed (since it was relative)
        self.core.toggle_rotation_mode()
        self.assertEqual(self.core.arrow_attrs[0]['rotation_mode'], 'fixed')
        self.assertEqual(self.core.arrow_attrs[1]['rotation_mode'], 'relative') # Unchanged
        
        # Toggle back
        self.core.toggle_rotation_mode()
        self.assertEqual(self.core.arrow_attrs[0]['rotation_mode'], 'relative')

if __name__ == '__main__':
    unittest.main()
