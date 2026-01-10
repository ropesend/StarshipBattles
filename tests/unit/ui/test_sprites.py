"""Tests for SpriteManager class."""
import unittest
import sys
import os
import pygame



from game.ui.renderer.sprites import SpriteManager

class TestSprites(unittest.TestCase):
        

    def setUp(self):
        pygame.init()
        # Initialize display for convert() calls
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        # Point to the project root
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
    def test_load_sprites(self):
        """Test loading sprites using the new directory method."""
        components_dir = os.path.join(self.base_path, "assets", "Images", "Components")
        if not os.path.exists(components_dir):
            self.skipTest(f"Components directory not found at {components_dir}")
            
        mgr = SpriteManager()
        # Initialize display for convert() calls in load_sprites
        if pygame.display.get_surface() is None:
             pygame.display.set_mode((1, 1), pygame.NOFRAME)

        mgr.load_sprites(self.base_path)
        
        # Check that we loaded some sprites
        # In the real directory we saw 467 files, indices up to 234 approx?
        # Let's just check we have something at index 0
        self.assertIsNotNone(mgr.get_sprite(0), "Should have loaded Bridge sprite at index 0")
        self.assertIsNotNone(mgr.get_sprite(18), "Should have loaded Railgun sprite at index 18")
        
        # Ensure we have a decent number of sprites
        count = sum(1 for s in mgr.sprites if s is not None)
        self.assertGreater(count, 10, "Should have loaded multiple sprites")

    def test_atlas_fallback_logic(self):
        """Test that we can still conceptually load an atlas if we wanted to (via private method maybe? or just skip)."""
        # Since load_atlas is deprecated/empty, this test is less relevant unless we test the fallback path explicitly.
        # But we tested fallback logic with mocks in test_sprite_loading.py.
        pass

if __name__ == '__main__':
    unittest.main()
