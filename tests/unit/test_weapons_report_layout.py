import unittest
import sys
import os
import pygame
import pygame_gui
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.builder.weapons_panel import WeaponsReportPanel

class TestWeaponsReportLayout(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Headless mode if possible, but UIManager needs a surface usually
        # We can set SDL_VIDEODRIVER to dummy
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        self.surface = pygame.display.set_mode((800, 600))
        self.manager = pygame_gui.UIManager((800, 600))
        
        # Mock dependencies
        self.builder = MagicMock()
        self.builder.ship = MagicMock()
        # Mock layers for _get_all_weapons
        self.builder.ship.layers = {} 
        
        self.sprite_mgr = MagicMock()
        
        self.rect = pygame.Rect(10, 400, 800, 200)
        
    def tearDown(self):
        pass # pygame.quit() removed for session isolation
        
    def test_button_creation_widths(self):
        """Verify buttons are created with updated widths and positions."""
        panel = WeaponsReportPanel(self.builder, self.manager, self.rect, self.sprite_mgr)
        
        # Expected dimensions from my planning
        # Start X = 220
        # Spacing = 5
        
        # Proj: 110
        self.assertEqual(panel.btn_proj.relative_rect.width, 110)
        self.assertEqual(panel.btn_proj.relative_rect.x, 220)
        
        # Beam: 110. X = 220 + 110 + 5 = 335
        self.assertEqual(panel.btn_beam.relative_rect.width, 110)
        self.assertEqual(panel.btn_beam.relative_rect.x, 335)
        
        # Seek: 110. X = 335 + 110 + 5 = 450
        self.assertEqual(panel.btn_seek.relative_rect.width, 110)
        self.assertEqual(panel.btn_seek.relative_rect.x, 450)
        
        # All: 60. X = 450 + 110 + 5 = 565
        self.assertEqual(panel.btn_all.relative_rect.width, 60)
        self.assertEqual(panel.btn_all.relative_rect.x, 565)
        
        # Ensure total width ends at 565 + 60 = 625
        self.assertEqual(panel.btn_all.relative_rect.right, 625)

if __name__ == '__main__':
    unittest.main()
