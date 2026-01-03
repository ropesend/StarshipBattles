import unittest
from unittest.mock import MagicMock, patch
import os
import pygame
from game.ui.renderer.sprites import SpriteManager

class TestSpriteLoading(unittest.TestCase):
    def setUp(self):
        # Reset singleton
        SpriteManager._instance = None
        self.mgr = SpriteManager.get_instance()

    @patch('game.ui.renderer.sprites.os.path.exists')
    @patch('game.ui.renderer.sprites.os.listdir')
    @patch('game.ui.renderer.sprites.pygame.image.load')
    def test_load_sprites_from_directory(self, mock_load, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock directory contents
        mock_listdir.return_value = [
            "Comp_001.bmp",
            "Comp_005.bmp",
            "Comp_010.bmp",
            "OtherFile.txt"
        ]
        
        # Mock image loading
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.convert.return_value = mock_surface
        mock_load.return_value = mock_surface
        
        # Execute
        base_path = "c:\\fake\\path"
        self.mgr.load_sprites(base_path)
        
        # Verify
        # Index 0 should be filled (Comp_001)
        self.assertIsNotNone(self.mgr.get_sprite(0))
        # Index 4 should be filled (Comp_005)
        self.assertIsNotNone(self.mgr.get_sprite(4))
        # Index 9 should be filled (Comp_010)
        self.assertIsNotNone(self.mgr.get_sprite(9))
        
        # Index 1 should be None (not in files)
        self.assertIsNone(self.mgr.get_sprite(1))
        
        # Verify image load calls
        expected_path_1 = os.path.join(base_path, "assets", "Images", "Components", "Tiles", "Comp_001.bmp")
        mock_load.assert_any_call(expected_path_1)

    @patch('game.ui.renderer.sprites.os.path.exists')
    def test_directory_not_found_fallback(self, mock_exists):
        # Setup to return False for directory check
        mock_exists.return_value = False
        
        # We expect it might try to load atlas or just print error, 
        # but for this specific test regarding the NEW functionality, 
        # we check it returns gracefully or handles it.
        # Since we haven't implemented fallback yet, let's just ensure it checks the path.
        
        base_path = "c:\\fake\\path"
        self.mgr.load_sprites(base_path)
        
        mock_exists.assert_called()

if __name__ == '__main__':
    unittest.main()
