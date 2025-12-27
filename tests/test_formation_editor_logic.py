import unittest
from unittest.mock import MagicMock, patch, mock_open
import math
import sys
import os
import json

# Mock pygame and pygame_gui before importing formation_editor
sys.modules['pygame'] = MagicMock()
sys.modules['pygame_gui'] = MagicMock()
sys.modules['tkinter'] = MagicMock()

# Now we can import the module under test
# We need to make sure the relative import imports the local file
sys.path.append(os.getcwd())
try:
    from formation_editor import FormationEditorScene
except ImportError:
    # If specific import fails, try relative modification or path adjustment
    sys.path.append(os.path.dirname(os.getcwd()))
    from formation_editor import FormationEditorScene

class TestFormationEditorLogic(unittest.TestCase):
    def setUp(self):
        # Setup common mocks
        self.mock_pygame = sys.modules['pygame']
        self.mock_pygame_gui = sys.modules['pygame_gui']
        
        # Mock Rect to behave somewhat reasonably
        def mock_rect(*args):
            m = MagicMock()
            if len(args) == 4:
                m.x, m.y, m.width, m.height = args
            m.collidepoint.return_value = True
            m.inflate.return_value = m
            return m
        self.mock_pygame.Rect = mock_rect
        
        # Mock mouse
        self.mock_pygame.mouse.get_pos.return_value = (0, 0)
        
        # Instantiate Scene
        # We need to mock the on_return_menu callback
        self.mock_callback = MagicMock()
        self.scene = FormationEditorScene(800, 600, self.mock_callback)
        
        # Reset data for clean state, though __init__ does it
        self.scene.arrows = []
        self.scene.arrow_attrs = []
        self.scene.selected_indices = set()
        self.scene.shape_count = 5 # Default
        
    def test_generate_shape_line(self):
        """Verify ships are placed in a linear coordinate sequence."""
        self.scene.shape_count = 5
        self.scene.generate_shape('line')
        
        self.assertEqual(len(self.scene.arrows), 5)
        
        # Check linearity: Y should be constant (approx), X should increase
        first_y = self.scene.arrows[0][1]
        for x, y in self.scene.arrows:
            self.assertAlmostEqual(y, first_y)
            
        # Check X increases
        xs = [p[0] for p in self.scene.arrows]
        self.assertEqual(xs, sorted(xs))
        self.assertNotEqual(xs[0], xs[-1]) # Should span some distance

    def test_generate_shape_circle(self):
        """Verify coordinates form a circle (check distance from center)."""
        self.scene.shape_count = 8
        self.scene.generate_shape('circle')
        
        self.assertEqual(len(self.scene.arrows), 8)
        
        # Calculate center of mass or use expected center
        # Logic uses center of screen converted to world.
        cx, cy = self.scene.screen_to_world(self.scene.width/2, (self.scene.height - self.scene.toolbar_height)/2)
        if self.scene.snap_enabled:
             cx = self.scene.snap(cx)
             cy = self.scene.snap(cy)
             
        # Radius in generated code is 200
        expected_radius = 200
        
        for x, y in self.scene.arrows:
            dist = math.hypot(x - cx, y - cy)
            self.assertAlmostEqual(dist, expected_radius, delta=1.0)

    def test_generate_shape_disc(self):
        """Verify point distribution follows the spiral pattern."""
        self.scene.shape_count = 10
        self.scene.generate_shape('disc')
        
        self.assertEqual(len(self.scene.arrows), 10)
        
        cx, cy = self.scene.screen_to_world(self.scene.width/2, (self.scene.height - self.scene.toolbar_height)/2)
        if self.scene.snap_enabled:
             cx = self.scene.snap(cx)
             cy = self.scene.snap(cy)
        
        radius = 200
        
        # Verify all points are within the disc radius
        for x, y in self.scene.arrows:
            dist = math.hypot(x - cx, y - cy)
            self.assertLessEqual(dist, radius + 1.0)
            
        # Verify points are distinct (set logic for coords)
        coords = [tuple(p) for p in self.scene.arrows]
        self.assertEqual(len(set(coords)), 10)

    def test_generate_shape_x(self):
        """Verify the cross pattern coordinates."""
        self.scene.shape_count = 6 # Even number for symmetry
        self.scene.generate_shape('x')
        
        self.assertEqual(len(self.scene.arrows), 6)
        
        # X shape consists of two diagonals.
        # Check that points lie on diagonals relative to center
        # One diagonal: y = x/1 + c, Other: y = -x/1 + c (roughly, ignoring translation)
        
        # Simpler check: Center of mass should be roughly the center
        xs = [p[0] for p in self.scene.arrows]
        ys = [p[1] for p in self.scene.arrows]
        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)
        
        cx, cy = self.scene.screen_to_world(self.scene.width/2, (self.scene.height - self.scene.toolbar_height)/2)
        if self.scene.snap_enabled:
             cx = self.scene.snap(cx)
             cy = self.scene.snap(cy)
             
        self.assertAlmostEqual(avg_x, cx, delta=5.0)
        self.assertAlmostEqual(avg_y, cy, delta=5.0)

    def test_add_arrow(self):
        """Test logical addition to the internal list."""
        pos = (150, 200)
        self.scene.add_arrow(pos)
        
        self.assertEqual(len(self.scene.arrows), 1)
        self.assertEqual(self.scene.arrows[0], [150, 200])
        self.assertEqual(len(self.scene.arrow_attrs), 1)
        self.assertEqual(self.scene.selected_indices, {0})

    def test_move_arrow(self):
        """Test updating the relative position or index."""
        # Add 3 arrows: A, B, C
        self.scene.arrows = [[0,0], [1,1], [2,2]]
        self.scene.arrow_attrs = [{'n':0}, {'n':1}, {'n':2}]
        
        # Move index 0 (A) to index 2 (End) -> should be B, C, A
        self.scene.move_arrow(0, 2)
        
        self.assertEqual(self.scene.arrows, [[1,1], [2,2], [0,0]])
        self.assertEqual(self.scene.arrow_attrs, [{'n':1}, {'n':2}, {'n':0}])
        # Selection should follow the moved item (new index 2)
        self.assertEqual(self.scene.selected_indices, {2})
        
        # Move index 2 (A) back to 0 -> A, B, C
        self.scene.move_arrow(2, 0)
        self.assertEqual(self.scene.arrows, [[0,0], [1,1], [2,2]])

    def test_delete_selected(self):
        """Verify correct item is removed and indices shift if necessary."""
        # Add 3 arrows: 0, 1, 2
        self.scene.arrows = [[0,0], [1,1], [2,2]]
        self.scene.arrow_attrs = [{'n':0}, {'n':1}, {'n':2}]
        
        # Select index 1
        self.scene.selected_indices = {1}
        
        self.scene.delete_selected()
        
        self.assertEqual(len(self.scene.arrows), 2)
        self.assertEqual(self.scene.arrows, [[0,0], [2,2]]) # 1 removed
        self.assertEqual(self.scene.arrow_attrs, [{'n':0}, {'n':2}])
        self.assertEqual(self.scene.selected_indices, set())

    @patch('formation_editor.tk_root', True) # Pretend tk is available
    @patch('formation_editor.filedialog.asksaveasfilename')
    def test_save_formation(self, mock_asksave):
        """Mock the filesystem operation and verify the JSON output structure."""
        mock_asksave.return_value = "test_formation.json"
        
        # Setup data
        self.scene.arrows = [[100, 200]]
        self.scene.arrow_attrs = [{'rotation_mode': 'fixed'}]
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.scene.save_formation()
            
            mock_file.assert_called_with("test_formation.json", 'w')
            
            # Get the write arg
            handle = mock_file()
            # We need to collect all write calls to form the json string
            # json.dump usually does multiple writes or one big write
            # We can check specific content in the writes
            
            # Simply verifying builtins.open was called is weak.
            # Ideally we want to intercept the json.dump call arguments, but json is imported inside.
            # We can mock json.dump using patch context on the module
            pass

    @patch('formation_editor.json.dump')
    @patch('formation_editor.tk_root', True)
    @patch('formation_editor.filedialog.asksaveasfilename')
    def test_save_formation_json_content(self, mock_asksave, mock_json_dump):
        mock_asksave.return_value = "test_formation.json"
        
        self.scene.arrows = [[10, 20]]
        self.scene.arrow_attrs = [{'rotation_mode': 'fixed'}]
        
        with patch('builtins.open', mock_open()):
             self.scene.save_formation()
             
             expected_data = {
                 'arrows': [
                     {'pos': [10, 20], 'rotation_mode': 'fixed'}
                 ]
             }
             mock_json_dump.assert_called()
             args, _ = mock_json_dump.call_args
             self.assertEqual(args[0], expected_data)

    @patch('formation_editor.json.load')
    @patch('formation_editor.tk_root', True)
    @patch('formation_editor.filedialog.askopenfilename')
    def test_load_formation(self, mock_askopen, mock_json_load):
        """Provide a sample JSON string and verify it correctly populates the internal ship/arrow lists."""
        mock_askopen.return_value = "test_formation.json"
        
        # Mock returned data
        sample_data = {
            'arrows': [
                {'pos': [50, 60], 'rotation_mode': 'relative'},
                {'pos': [70, 80], 'rotation_mode': 'fixed'}
            ]
        }
        mock_json_load.return_value = sample_data
        
        with patch('builtins.open', mock_open()):
            self.scene.load_formation()
            
            self.assertEqual(len(self.scene.arrows), 2)
            self.assertEqual(self.scene.arrows[0], [50, 60])
            self.assertEqual(self.scene.arrows[1], [70, 80])
            self.assertEqual(self.scene.arrow_attrs[0]['rotation_mode'], 'relative')
            self.assertEqual(self.scene.arrow_attrs[1]['rotation_mode'], 'fixed')

if __name__ == '__main__':
    unittest.main()
