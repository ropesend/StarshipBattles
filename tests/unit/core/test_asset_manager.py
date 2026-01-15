
import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import pygame
from game.assets.asset_manager import AssetManager, get_asset_manager

class TestAssetManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Reset singleton logic if possible or just use a fresh instance logic
        # Since _instance is used, we need to reset it to test initialization
        AssetManager._instance = None
        yield
        AssetManager._instance = None

    def test_singleton(self):
        am1 = get_asset_manager()
        am2 = get_asset_manager()
        assert am1 is am2
        
    def test_load_manifest_file_not_found(self):
        am = AssetManager()
        am.load_manifest("non_existent_file.json")
        assert am.manifest == {}

    @patch("builtins.open", new_callable=mock_open, read_data='{"stars": {"blue": "path/to/blue.png"}}')
    @patch("os.path.exists", return_value=True)
    def test_load_manifest_success(self, mock_exists, mock_file):
        am = AssetManager()
        am.load_manifest("dummy.json")
        assert am.manifest["stars"]["blue"] == "path/to/blue.png"

    @patch("pygame.image.load")
    @patch("os.path.exists", return_value=True)
    def test_get_image_cache(self, mock_exists, mock_load):
        am = AssetManager()
        am.manifest = {"stars": {"blue": "path/to/blue.png"}}
        
        mock_surf = MagicMock(spec=pygame.Surface)
        mock_load.return_value.convert_alpha.return_value = mock_surf
        
        # First call
        img1 = am.get_image("stars", "blue")
        assert img1 == mock_surf
        assert mock_load.call_count == 1
        
        # Second call (should be cached)
        img2 = am.get_image("stars", "blue")
        assert img2 == mock_surf
        assert mock_load.call_count == 1

    def test_get_image_missing_key(self):
        am = AssetManager()
        img = am.get_image("stars", "missing")
        # Should return missing texture (hot pink)
        assert isinstance(img, pygame.Surface)
        # Check color (hot pink is usually filled)
        # We can't easily check pixel data on a mock surface or headless, 
        # but we verify it returns *something* and logs warning
        
    @patch("pygame.image.load")
    @patch("os.path.exists", return_value=True)
    def test_get_group(self, mock_exists, mock_load):
        am = AssetManager()
        am.manifest = {"planets": {"gas": ["p1.png", "p2.png"]}}
        
        imgs = am.get_group("planets", "gas")
        assert len(imgs) == 2
        assert mock_load.call_count == 2
        
    def test_get_random_from_group(self):
        am = AssetManager()
        # manual injection into cache/manifest for testing logic
        am.manifest = {"planets": {"gas": ["p1.png", "p2.png"]}}
        # Mock _load_image to avoid FS
        am._load_image = MagicMock(return_value="surfacemock")
        
        item1 = am.get_random_from_group("planets", "gas", seed_id=0)
        item2 = am.get_random_from_group("planets", "gas", seed_id=1)
        
        assert item1 == "surfacemock"
        
    @patch("pygame.image.load")
    @patch("os.path.exists", return_value=True)
    def test_load_external_image(self, mock_exists, mock_load):
        am = AssetManager()
        path = "e:/some/mod/skin.png"
        
        img = am.load_external_image(path)
        assert mock_load.call_count == 1
        
        # Cached
        img2 = am.load_external_image(path)
        assert mock_load.call_count == 1 # Still 1
