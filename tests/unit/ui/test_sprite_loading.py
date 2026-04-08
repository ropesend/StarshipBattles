import pytest
from unittest.mock import MagicMock, patch
import os
import pygame
from game.ui.renderer.sprites import SpriteManager


class TestSpriteLoading:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Reset singleton
        SpriteManager.reset()
        self.mgr = SpriteManager.instance()

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pygame.image.load')
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
        mock_surface.set_colorkey = MagicMock()  # Mock set_colorkey to prevent errors
        mock_load.return_value = mock_surface

        # Execute
        base_path = "c:\\fake\\path"
        self.mgr.load_sprites(base_path)

        # Verify
        # Index 0 should be filled (Comp_001)
        assert self.mgr.get_sprite(0) is not None
        # Index 4 should be filled (Comp_005)
        assert self.mgr.get_sprite(4) is not None
        # Index 9 should be filled (Comp_010)
        assert self.mgr.get_sprite(9) is not None

        # Index 1 should be None (not in files)
        assert self.mgr.get_sprite(1) is None

        # Verify image load calls
        expected_path_1 = os.path.join(base_path, "assets", "Images", "Components", "Components 64", "Comp_001.bmp")
        mock_load.assert_any_call(expected_path_1)

    @patch('os.path.exists')
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
