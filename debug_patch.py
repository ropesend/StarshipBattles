
import unittest
from unittest.mock import patch
import sys
import os

# Setup path
sys.path.append(os.getcwd())

from ui.builder import right_panel

class TestPatch(unittest.TestCase):
    @patch('ui.builder.right_panel.UILabel')
    def test_patch_working(self, mock_label):
        print(f"DEBUG: right_panel.UILabel is {right_panel.UILabel}")
        print(f"DEBUG: mock_label is {mock_label}")
        self.assertIs(right_panel.UILabel, mock_label)

    def test_patch_manual(self):
        with patch('ui.builder.right_panel.UILabel') as mock:
            print(f"DEBUG: Manual patch right_panel.UILabel is {right_panel.UILabel}")
            self.assertIs(right_panel.UILabel, mock)

if __name__ == '__main__':
    unittest.main()
