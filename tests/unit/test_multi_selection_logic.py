
import unittest
from unittest.mock import MagicMock
import pygame
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from game.ui.screens.builder_screen import BuilderSceneGUI
from game.simulation.components.component import Component

class TestMultiSelectionLogic(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Initialize display for pygame_gui
        pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        
        # Mocking Builder with minimal dependencies
        self.builder = BuilderSceneGUI(800, 600, None)
        self.builder.ship = MagicMock()
        self.builder.ship.layers = {}
        
        # Mocks for panels to avoid errors during event handling/updates
        self.builder.left_panel = MagicMock()
        self.builder.right_panel = MagicMock()
        self.builder.layer_panel = MagicMock()
        self.builder.modifier_panel = MagicMock()
        self.builder.weapons_panel = MagicMock()
        if hasattr(self.builder, 'weapons_report_panel'):
            self.builder.weapons_report_panel = MagicMock()
        
        # Create test components
        self.comp_data_a = {
            "id": "type_a", 
            "name": "Type A", 
            "type": "Weapon", 
            "mass": 10, 
            "hp":100,
            "modifiers": []
        }
        
        self.comp_a1 = Component(self.comp_data_a)
        self.comp_a2 = Component(self.comp_data_a)
        self.comp_a3 = Component(self.comp_data_a)
        self.comp_a4 = Component(self.comp_data_a)
        
        self.builder.selected_components = []

    def tearDown(self):
        pass # pygame.quit() removed for session isolation

    def test_toggle_behavior(self):
        """Test that Ctrl+Click toggles items in selection."""
        # 1. Select A1
        self.builder.on_selection_changed(self.comp_a1, append=False)
        self.assertEqual(len(self.builder.selected_components), 1)
        self.assertEqual(self.builder.selected_components[0][2], self.comp_a1)
        
        # 2. Ctrl+Click A2 (Append)
        self.builder.on_selection_changed(self.comp_a2, append=True, toggle=True)
        self.assertEqual(len(self.builder.selected_components), 2)
        
        # 3. Ctrl+Click A1 (Toggle OFF)
        self.builder.on_selection_changed(self.comp_a1, append=True, toggle=True)
        self.assertEqual(len(self.builder.selected_components), 1)
        self.assertEqual(self.builder.selected_components[0][2], self.comp_a2)
        
        # 4. Ctrl+Click A2 (Toggle OFF) -> Empty
        self.builder.on_selection_changed(self.comp_a2, append=True, toggle=True)
        self.assertEqual(len(self.builder.selected_components), 0)

    def test_range_selection_integration(self):
        """Test usage of get_range_selection via on_selection_changed."""
        # Note: We are testing the integration in on_selection_changed handling of lists
        # The actual get_range_selection logic is mocked here because it depends on UI list state
        
        # Setup: A1 is selected
        self.builder.on_selection_changed(self.comp_a1, append=False)
        
        # Simulating Shift Click A4 -> Returns [A1, A2, A3, A4]
        range_selection = [self.comp_a1, self.comp_a2, self.comp_a3, self.comp_a4]
        
        # Case 1: Shift Click (append=False implies Replace, but usually Shift Range replaces existing selection with Range)
        # But if we treat it as "Add Range", we use append=True?
        # In my logic: is_shift -> self.on_selection_changed(range_comps, append=is_ctrl, toggle=False)
        # If just Shift (no Ctrl), append=False.
        
        # Execute (Shift only)
        self.builder.on_selection_changed(range_selection, append=False, toggle=False)
        
        self.assertEqual(len(self.builder.selected_components), 4)
        
        # Validate order preservation (implementation dependent but sets usually order by insertion)
        self.assertEqual(self.builder.selected_components[0][2], self.comp_a1)
        self.assertEqual(self.builder.selected_components[3][2], self.comp_a4)

    def test_range_append_integration(self):
        """Test Ctrl+Shift Append Range."""
        # Setup A1 Selected
        self.builder.on_selection_changed(self.comp_a1, append=False)
        
        # Range is A3-A4 (User anchor shifted? Or just adding distinct range?)
        # Let's say we have A1, and we add range [A3, A4]
        range_selection = [self.comp_a3, self.comp_a4]
        
        # Execute (Ctrl+Shift)
        self.builder.on_selection_changed(range_selection, append=True, toggle=False)
        
        self.assertEqual(len(self.builder.selected_components), 3) # A1 + A3 + A4
        selected_objs = {c[2] for c in self.builder.selected_components}
        self.assertIn(self.comp_a1, selected_objs)
        self.assertIn(self.comp_a3, selected_objs)
        self.assertIn(self.comp_a4, selected_objs)

if __name__ == '__main__':
    unittest.main()
