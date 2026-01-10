import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
import os
import sys

# Dummy video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.ui.screens.builder_screen import BuilderSceneGUI
from game.core.registry import RegistryManager

class TestBuilderWarningLogic(unittest.TestCase):
    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()
    def setUp(self):
        pygame.init()
        
        # Patch _create_ui to avoid complex UI initialization
        self.patcher = patch('game.ui.screens.builder_screen.BuilderSceneGUI._create_ui')
        self.mock_create_ui = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        
        # Mock internal managers
        self.p1 = patch('game.ui.screens.builder_screen.SpriteManager')
        self.p2 = patch('game.ui.screens.builder_screen.PresetManager')
        self.p3 = patch('game.ui.screens.builder_screen.ShipThemeManager')
        self.p4 = patch('game.ui.screens.builder_screen.UIConfirmationDialog')
        self.p5 = patch('game.ui.screens.builder_event_router.UIConfirmationDialog')  # Also patch in event router
        self.p1.start(); self.p2.start(); self.p3.start(); self.p4.start(); self.p5.start()
        self.addCleanup(self.p1.stop); self.addCleanup(self.p2.stop); 
        self.addCleanup(self.p3.stop); self.addCleanup(self.p4.stop); self.addCleanup(self.p5.stop)
        
        self.builder = BuilderSceneGUI(800, 600, MagicMock())
             
        # Manually setup the mocks that _create_ui would have created
        self.builder.ui_manager = MagicMock()
        self.builder.left_panel = MagicMock()
        self.builder.right_panel = MagicMock()
        self.builder.right_panel.class_dropdown = MagicMock()
        self.builder.right_panel.vehicle_type_dropdown = MagicMock()
        self.builder.layer_panel = MagicMock()
        self.builder.modifier_panel = MagicMock()
        self.builder.weapons_report_panel = MagicMock()
        self.builder.detail_panel = MagicMock()
        
        self.builder.left_panel.get_add_count.return_value = 1
        self.builder.left_panel.handle_event.return_value = None
        self.builder.layer_panel.handle_event.return_value = None
        self.builder.modifier_panel.handle_event.return_value = None
        self.builder.weapons_report_panel.handle_event.return_value = None
        
        # Reset pending action
        self.builder.pending_action = None
        self.builder.confirm_dialog = None

    def test_change_class_empty_ship(self):
        """Test changing class with no components triggers immediate action (no warning)."""
        # Ensure ship is empty
        self.builder.ship.layers = {'CORE': {'components': []}} 
        
        # Setup event
        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = self.builder.right_panel.class_dropdown
        event.text = "Cruiser"
        
        # Mock _execute_pending_action to verify it's called
        with patch.object(self.builder, '_execute_pending_action') as mock_execute:
            print(f"DEBUG: Left Panel Handle Event returns: {self.builder.left_panel.handle_event(event)}")
            print(f"DEBUG: Layer Panel Handle Event returns: {self.builder.layer_panel.handle_event(event)}")
            self.builder.handle_event(event)
            
            # Check success
            self.assertEqual(self.builder.pending_action, ('change_class', "Cruiser"))
            mock_execute.assert_called_once()
            self.assertIsNone(self.builder.confirm_dialog)

    def test_change_class_non_empty_ship(self):
        """Test changing class WITH components triggers warning dialog."""
        # Add a dummy component
        self.builder.ship.layers = {'CORE': {'components': ['mock_comp']}}
        
        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = self.builder.right_panel.class_dropdown
        event.text = "Cruiser"
        
        with patch.object(self.builder, '_execute_pending_action') as mock_execute:
            self.builder.handle_event(event)
            
            # Check warning
            self.assertEqual(self.builder.pending_action, ('change_class', "Cruiser"))
            mock_execute.assert_not_called()
            self.assertIsNotNone(self.builder.confirm_dialog)
            # Verify dialog created via mock
            # pygame_gui.windows.UIConfirmationDialog should have been called
            # We can't easily access the mock object here without importing it or saving it in setUp
            # But existence of confirm_dialog (which is the return node of the mock) is enough proof for now
            # since we mocked the class.

    def test_change_type_empty_ship(self):
        """Test changing type with no components triggers immediate action."""
        self.builder.ship.layers = {'CORE': {'components': []}}
        
        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = self.builder.right_panel.vehicle_type_dropdown
        event.text = "Station"
        
        # Mock getattr for checking current type
        from game.core.registry import RegistryManager
        with patch.object(RegistryManager.instance(), 'vehicle_classes', {'Station': {'type': 'Station', 'max_mass': 5000}}):
            with patch.object(self.builder, '_execute_pending_action') as mock_execute:
                self.builder.handle_event(event)
                
                # Should find a pending action and execute it
                # Note: The actual class it resolves to depends on logic, but we just check flow
                self.assertIsNotNone(self.builder.pending_action)
                self.assertEqual(self.builder.pending_action[0], 'change_type')
                mock_execute.assert_called_once()
                self.assertIsNone(self.builder.confirm_dialog)

    def test_change_type_non_empty_ship(self):
        """Test changing type WITH components triggers warning."""
        self.builder.ship.layers = {'CORE': {'components': ['mock_comp']}}
        
        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = self.builder.right_panel.vehicle_type_dropdown
        event.text = "Station"
        
        from game.core.registry import RegistryManager
        with patch.object(RegistryManager.instance(), 'vehicle_classes', {'Station': {'type': 'Station', 'max_mass': 5000}}):
            with patch.object(self.builder, '_execute_pending_action') as mock_execute:
                self.builder.handle_event(event)
                
                self.assertIsNotNone(self.builder.pending_action)
                mock_execute.assert_not_called()
                self.assertIsNotNone(self.builder.confirm_dialog)

if __name__ == '__main__':
    unittest.main()
