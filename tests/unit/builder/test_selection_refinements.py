
import unittest
from unittest.mock import MagicMock
import pygame
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.simulation.components.component import Component

class TestSelectionRefinements(unittest.TestCase):
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
        
        # Create test components
        self.comp_data_a = {
            "id": "type_a", 
            "name": "Type A", 
            "type": "Weapon", 
            "mass": 10, 
            "hp":100,
            "modifiers": []
        }
        self.comp_data_b = {
            "id": "type_b", 
            "name": "Type B", 
            "type": "Engine", 
            "mass": 20, 
            "hp":100,
            "modifiers": []
        }
        
        self.comp_a1 = Component(self.comp_data_a)
        self.comp_a2 = Component(self.comp_data_a)
        self.comp_b1 = Component(self.comp_data_b)
        
        # Setup selected_components list manually if needed, or rely on methods
        self.builder.selected_components = []

    def tearDown(self):
        pass # pygame.quit() removed for session isolation

    def test_homogeneity_enforcement(self):
        """Test that selection is restricted to identical component types."""
        # 1. Select A1
        self.builder.on_selection_changed(self.comp_a1, append=False)
        self.assertEqual(len(self.builder.selected_components), 1)
        self.assertEqual(self.builder.selected_components[0][2], self.comp_a1)
        
        # 2. Append A2 (Same type) - Should Succeed
        self.builder.on_selection_changed(self.comp_a2, append=True)
        self.assertEqual(len(self.builder.selected_components), 2)
        
        # 3. Append B1 (Different type) - Should Replace
        self.builder.on_selection_changed(self.comp_b1, append=True)
        self.assertEqual(len(self.builder.selected_components), 1)
        self.assertEqual(self.builder.selected_components[0][2], self.comp_b1)
        
    def test_reselection_behavior(self):
        """Test re-selecting behavior."""
        self.builder.on_selection_changed(self.comp_a1, append=False)
        
        # Append same item - should not duplicate
        self.builder.on_selection_changed(self.comp_a1, append=True)
        self.assertEqual(len(self.builder.selected_components), 1)

if __name__ == '__main__':
    unittest.main()
