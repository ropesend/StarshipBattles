import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch

from game.simulation.entities.ship import Ship
from game.core.registry import RegistryManager


class TestBuilderUISync(unittest.TestCase):


    def setUp(self):
        # All data (components, modifiers, strategies) loaded by root conftest.py
        pygame.display.set_mode((800, 600))  # Dummy mode
        self.manager = pygame_gui.UIManager((800, 600))
        
        # Mock Builder
        self.mock_builder = MagicMock()
        self.test_ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Escort")
        self.mock_builder.ship = self.test_ship
        
        # MVVM: viewmodel.ship must return the same ship for Panel refactoring
        self.mock_builder.viewmodel.ship = self.test_ship
        
        # Mock Theme Manager
        self.mock_builder.theme_manager.get_available_themes.return_value = ["Federation", "Klingon"]
        
        # Mock image loading to avoid file IO errors during refresh_controls -> update_portrait_image
        with patch('pygame.image.load'):
             with patch('ui.builder.right_panel.BuilderRightPanel.update_portrait_image'):
                from ui.builder.right_panel import BuilderRightPanel
                self.panel = BuilderRightPanel(self.mock_builder, self.manager, pygame.Rect(0, 0, 300, 600))

    def tearDown(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        # NOTE: Do NOT call pygame.quit() here - it destroys the session-scoped
        # pygame initialization from root conftest's enforce_headless fixture.
        # The root conftest handles pygame lifecycle and registry cleanup.

    def _get_option_value(self, option):
        """Helper to handle pygame_gui returning (id, text) tuples or raw values."""
        if isinstance(option, tuple):
            return option[0]
        return option

    def test_refresh_controls_syncs_ui(self):
        """Verify that refresh_controls updates UI elements to match ship state."""
        # 1. Modify Ship State from defaults (Escort, Federation)
        self.mock_builder.ship.name = "New Name"
        
        # Ensure we pick a class that definitely exists and isn't Escort
        target_class = "Cruiser" 
        classes = RegistryManager.instance().vehicle_classes
        if target_class not in classes:
             target_class = list(classes.keys())[-1]
             
        self.mock_builder.ship.ship_class = target_class
        self.mock_builder.ship.theme_id = "Klingon"
        
        # Set AI to something non-default
        # Default is usually optimal_firing_range
        self.mock_builder.ship.ai_strategy = "kamikaze"
        
        # 2. Call Refresh (mocking portrait update to avoid side effects)
        # 2. Call Refresh (mocking portrait update to avoid side effects)
        with patch.object(self.panel, 'update_portrait_image') as mock_update_img:
            self.panel.refresh_controls()
            mock_update_img.assert_called_once()
        
        # 3. Assert UI values match Ship State
        
        # Name
        self.assertEqual(self.panel.name_entry.get_text(), "New Name")
        
        # Theme
        val = self._get_option_value(self.panel.theme_dropdown.selected_option)
        self.assertEqual(val, "Klingon")
        
        # Class
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        self.assertEqual(val, target_class)
        
        # AI Strategy Name lookup
        from game.ai.controller import StrategyManager
        strat_name = StrategyManager.instance().strategies["kamikaze"]["name"]
        val = self._get_option_value(self.panel.ai_dropdown.selected_option)
        self.assertEqual(val, strat_name)

    def test_type_change_filtering(self):
        """Verify that changing vehicle type filters the class list."""
        # Dynamically find a type that is NOT 'Ship' and has classes
        target_type = None
        target_class = None
        
        # Group classes by type
        type_map = {}
        for name, data in RegistryManager.instance().vehicle_classes.items():
            ctype = data.get('type', 'Ship')
            if ctype not in type_map: type_map[ctype] = []
            type_map[ctype].append(name)
            
        # Prefer 'Station' or 'Fighter' if available
        candidates = ['Station', 'Fighter', 'Defense Satellite', 'Unknown']
        for c in candidates:
            if c in type_map and len(type_map[c]) > 0:
                target_type = c
                target_class = type_map[c][0]
                break
        
        if not target_type:
            # Fallback to any type that isn't 'Ship' (if possible) or just skip
            for t, classes in type_map.items():
                if classes:
                    target_type = t
                    target_class = classes[0]
                    break
        
        if not target_type:
             self.skipTest("No vehicle classes found to test type filtering.")

        self.mock_builder.ship.vehicle_type = target_type
        self.mock_builder.ship.ship_class = target_class
        
        with patch.object(self.panel, 'update_portrait_image'):
            self.panel.refresh_controls()
        
        # Verify Type Dropdown
        val = self._get_option_value(self.panel.vehicle_type_dropdown.selected_option)
        self.assertEqual(val, target_type)
        
        # Verify Class Dropdown selected option
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        self.assertEqual(val, target_class)
        
        # Verify Class Dropdown ONLY contains classes of this type
        for option in self.panel.class_dropdown.options_list:
             # Check if option is a valid class of this type
             # option might be tuple
             opt_val = self._get_option_value(option)
             c_def = RegistryManager.instance().vehicle_classes.get(opt_val)
             if c_def:
                 self.assertEqual(c_def.get('type', 'Ship'), target_type, f"Class {opt_val} should be type {target_type}")

    def test_revert_protection(self):
        """Regression test: Changes to ship MUST reflect in UI after refresh."""
        # Start state: Escort
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        self.assertEqual(val, "Escort")
        
        # Change state
        self.mock_builder.ship.ship_class = "Battleship"
        
        # Trigger sync
        with patch.object(self.panel, 'update_portrait_image'):
            self.panel.refresh_controls()
            
        # Assert sync happened
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        self.assertEqual(val, "Battleship", 
                         "UI did not update to reflect ship class change. Fix may have reverted.")

if __name__ == '__main__':
    unittest.main()
