import pytest
from unittest.mock import MagicMock, patch
import os
import pygame
from game.ui.renderer.sprites import SpriteManager, get_default_sprite_manager, set_default_sprite_manager


class TestSpriteLoading:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Reset default
        set_default_sprite_manager(SpriteManager())
        self.mgr = get_default_sprite_manager()

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pygame.image.load')
    def test_load_sprites_from_directory(self, mock_load, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True

        # Mock directory contents (PROJ-393: legacy Comp_NNN.bmp pattern was
        # deleted; only canonical {resolution}Portrait_Comp_NNN.ext loads now).
        mock_listdir.return_value = [
            "64Portrait_Comp_001.png",
            "64Portrait_Comp_005.png",
            "64Portrait_Comp_010.png",
            "OtherFile.txt"
        ]

        # Mock image loading
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.convert_alpha.return_value = mock_surface
        mock_load.return_value = mock_surface

        # Execute
        base_path = "c:\\fake\\path"
        self.mgr.load_sprites(base_path)

        # Verify
        assert self.mgr.get_sprite(1) is not None
        assert self.mgr.get_sprite(5) is not None
        assert self.mgr.get_sprite(10) is not None

        # Index 2 should be None (not in files)
        assert self.mgr.get_sprite(2) is None

        # Verify image load calls
        expected_path_1 = os.path.join(base_path, "assets", "images", "components", "64", "64Portrait_Comp_001.png")
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
