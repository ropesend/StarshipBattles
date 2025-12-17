import unittest
import sys
import os
import pygame

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sprites import SpriteManager

class TestSprites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pygame requires initialization to load images/convert
        pygame.init()
        # We might need a display mode for .convert() to work
        pygame.display.set_mode((1, 1))

    def test_singleton(self):
        s1 = SpriteManager.get_instance()
        s2 = SpriteManager.get_instance()
        self.assertIs(s1, s2)

    def test_load_atlas(self):
        mgr = SpriteManager.get_instance()
        # Assume resources/images/Components.bmp exists relative to project root
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        atlas_path = os.path.join(base_path, "resources", "images", "Components.bmp")
        
        # Verify file exists first (unit test sanity)
        self.assertTrue(os.path.exists(atlas_path), f"Atlas not found at {atlas_path}")
        
        mgr.load_atlas(atlas_path)
        
        # Verify dimensions (864 x 432)
        self.assertIsNotNone(mgr.atlas)
        self.assertEqual(mgr.atlas.get_width(), 864)
        self.assertEqual(mgr.atlas.get_height(), 432)

    def test_sprite_slicing(self):
        mgr = SpriteManager.get_instance()
        # Width 864 / 36 = 24 cols
        # Height 432 / 36 = 12 rows
        # Total = 24 * 12 = 288 sprites
        self.assertEqual(len(mgr.sprites), 288)
        
        # Check first sprite
        s0 = mgr.get_sprite(0)
        self.assertIsNotNone(s0)
        self.assertEqual(s0.get_width(), 36)
        self.assertEqual(s0.get_height(), 36)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
