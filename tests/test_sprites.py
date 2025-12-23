"""Tests for SpriteManager class."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sprites import SpriteManager

class TestSprites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Initialize display for convert() calls
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        # We need a valid path to components.png or similar
        # Assuming data/components.png exists based on codebase usage
        self.sprite_path = "data/components.png"
        
    def test_load_atlas(self):
        """Test loading the sprite atlas."""
        if not os.path.exists(self.sprite_path):
            self.skipTest(f"Sprite atlas not found at {self.sprite_path}")
            
        mgr = SpriteManager()
        try:
            mgr.load_atlas(self.sprite_path)
            self.assertIsNotNone(mgr.atlas)
        except pygame.error as e:
             self.fail(f"Failed to load atlas: {e}")

    def test_sprite_slicing(self):
        """Test that sprites are sliced correctly."""
        if not os.path.exists(self.sprite_path):
            self.skipTest("No atlas to slice")
            
        mgr = SpriteManager()
        mgr.load_atlas(self.sprite_path)
        
        # Should have sprites
        self.assertGreater(len(mgr.sprites), 0)
        
        # Check first sprite is a surface
        self.assertIsInstance(mgr.get_sprite(0), pygame.Surface)

if __name__ == '__main__':
    unittest.main()
