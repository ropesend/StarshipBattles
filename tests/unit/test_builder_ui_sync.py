
import unittest
import pygame
import pygame_gui
import os
from unittest.mock import MagicMock, patch

# Environment setup for headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, initialize_ship_data, VEHICLE_CLASSES
from game.simulation.components.component import load_components
from game.ai.controller import COMBAT_STRATEGIES

class TestBuilderUISync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Initialize data needed for dropdowns
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "game.simulation.components.component.json"))
        
        pygame.display.set_mode((800, 600)) # Dummy mode

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.manager = pygame_gui.UIManager((800, 600))
        
        # Mock Builder
        self.mock_builder = MagicMock()
        self.mock_builder.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Escort")
        
        # Mock Theme Manager
        self.mock_builder.theme_manager.get_available_themes.return_value = ["Federation", "Klingon"]
        
        # Mock image loading to avoid file IO errors during refresh_controls -> update_portrait_image
        with patch('pygame.image.load'):
             with patch('ui.builder.right_panel.BuilderRightPanel.update_portrait_image'):
                from ui.builder.right_panel import BuilderRightPanel
                self.panel = BuilderRightPanel(self.mock_builder, self.manager, pygame.Rect(0, 0, 300, 600))

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
        if target_class not in VEHICLE_CLASSES:
             # Fallback if data is different
             target_class = list(VEHICLE_CLASSES.keys())[-1]
             
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
        
        # AI
        # AI Strategy Name lookup
        strat_name = COMBAT_STRATEGIES["kamikaze"]["name"]
        val = self._get_option_value(self.panel.ai_dropdown.selected_option)
        self.assertEqual(val, strat_name)

    def test_type_change_filtering(self):
        """Verify that changing vehicle type filters the class list."""
        # Dynamically find a type that is NOT 'Ship' and has classes
        target_type = None
        target_class = None
        
        # Group classes by type
        type_map = {}
        for name, data in VEHICLE_CLASSES.items():
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
             c_def = VEHICLE_CLASSES.get(opt_val)
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
