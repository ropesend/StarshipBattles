"""
Unit tests for AssetManager planet image resolution selection (PROJ-54 Phase 9).

Tests:
- _get_planet_folder_for_size() with valid and invalid sizes
- load_planet_image() with resolution fallback chain
- load_planet_image() with missing files
"""
import os
import pytest
import pygame
from unittest.mock import patch, MagicMock

from game.assets.asset_manager import AssetManager, get_default_asset_manager, set_default_asset_manager
from game.core.paths import Paths
from game.core.exceptions import ResourceException


@pytest.fixture
def asset_manager():
    """Create a fresh AssetManager instance for each test."""
    # Reset default before test
    set_default_asset_manager(AssetManager())
    manager = get_default_asset_manager()
    yield manager
    # Reset default after test for isolation
    set_default_asset_manager(AssetManager())


class TestGetPlanetFolderForSize:
    """Test _get_planet_folder_for_size() helper method."""

    def test_get_folder_128px(self, asset_manager):
        """Test that 128px maps to PLANETS_V3_128_DIR."""
        result = asset_manager._get_planet_folder_for_size(128)
        assert result == Paths.PLANETS_V3_128_DIR

    def test_get_folder_256px(self, asset_manager):
        """Test that 256px maps to PLANETS_V3_256_DIR."""
        result = asset_manager._get_planet_folder_for_size(256)
        assert result == Paths.PLANETS_V3_256_DIR

    def test_get_folder_512px(self, asset_manager):
        """Test that 512px maps to PLANETS_V3_512_DIR."""
        result = asset_manager._get_planet_folder_for_size(512)
        assert result == Paths.PLANETS_V3_512_DIR

    def test_get_folder_1024px(self, asset_manager):
        """Test that 1024px maps to PLANETS_V3_1024_DIR."""
        result = asset_manager._get_planet_folder_for_size(1024)
        assert result == Paths.PLANETS_V3_1024_DIR

    def test_get_folder_2048px(self, asset_manager):
        """Test that 2048px maps to PLANETS_V3_2048_DIR."""
        result = asset_manager._get_planet_folder_for_size(2048)
        assert result == Paths.PLANETS_V3_2048_DIR

    def test_invalid_size_raises_error(self, asset_manager):
        """Test that invalid size raises ResourceException."""
        with pytest.raises(ResourceException, match="Invalid planet image size"):
            asset_manager._get_planet_folder_for_size(999)


class TestStarAssets:
    """Test star image resolution and core metadata helpers."""

    def test_init_loads_existing_star_metadata(self):
        """Existing star metadata JSON is loaded during construction."""
        metadata = {
            "blue.png": {
                "centerX": 0.45,
                "centerY": 0.55,
                "radiusCore": 0.2,
                "radiusCorona": 0.4,
            }
        }

        with patch("game.assets.asset_manager.os.path.exists", return_value=True), \
                patch("game.assets.asset_manager.load_json", return_value=metadata):
            manager = AssetManager()

        assert manager.star_metadata == metadata

    def test_init_keeps_empty_star_metadata_when_file_missing(self):
        """Missing star metadata leaves the metadata cache empty."""
        with patch("game.assets.asset_manager.os.path.exists", return_value=False), \
                patch("game.assets.asset_manager.load_json") as mock_load:
            manager = AssetManager()

        mock_load.assert_not_called()
        assert manager.star_metadata == {}

    def test_get_star_core_info_returns_metadata_or_default(self, asset_manager):
        """Core metadata lookup falls back to normalized defaults."""
        custom = {
            "centerX": 0.4,
            "centerY": 0.6,
            "radiusCore": 0.22,
            "radiusCorona": 0.38,
        }
        asset_manager.star_metadata = {"custom.png": custom}

        assert asset_manager.get_star_core_info("custom.png") == custom
        assert asset_manager.get_star_core_info("missing.png") == {
            "centerX": 0.5,
            "centerY": 0.5,
            "radiusCore": 0.25,
            "radiusCorona": 0.35,
        }

    def test_get_star_asset_key_for_type_uses_manifest_and_yellow_fallback(self, asset_manager):
        """Star type mapping reads manifest data and defaults to yellow."""
        asset_manager.manifest = {
            "star_type_assets": {
                "RED_GIANT": "red",
            }
        }

        assert asset_manager.get_star_asset_key_for_type("RED_GIANT") == "red"
        assert asset_manager.get_star_asset_key_for_type("UNKNOWN_TYPE") == "yellow"

    def test_get_star_folder_for_size_returns_known_directories(self, asset_manager):
        """Star image sizes map to the configured Stars folders."""
        assert asset_manager._get_star_folder_for_size(128) == Paths.STARS_128_DIR
        assert asset_manager._get_star_folder_for_size(256) == Paths.STARS_256_DIR
        assert asset_manager._get_star_folder_for_size(512) == Paths.STARS_512_DIR
        assert asset_manager._get_star_folder_for_size(1024) == Paths.STARS_1024_DIR

    def test_get_star_folder_for_size_rejects_invalid_size(self, asset_manager):
        """Unsupported star image sizes raise a ResourceException."""
        with pytest.raises(ResourceException, match="Invalid star image size"):
            asset_manager._get_star_folder_for_size(2048)

    def test_load_star_image_falls_back_to_next_higher_resolution(self, asset_manager):
        """Missing lower-resolution star image falls back to the next size."""
        valid_surface = pygame.Surface((4, 4))

        with patch.object(asset_manager, "_get_star_folder_for_size", return_value="/stars") as mock_folder, \
                patch.object(asset_manager, "load_external_image") as mock_load:
            mock_load.side_effect = [
                asset_manager.get_missing_texture(),
                valid_surface,
            ]

            result = asset_manager.load_star_image("star.png", requested_size=129)

        assert result is valid_surface
        assert [call.args[0] for call in mock_folder.call_args_list] == [256, 512]

    def test_load_star_image_returns_missing_texture_after_loader_errors(self, asset_manager):
        """Loader errors are swallowed per-resolution before returning the placeholder."""
        with patch.object(asset_manager, "_get_star_folder_for_size", return_value="/stars"), \
                patch.object(asset_manager, "load_external_image", side_effect=RuntimeError("boom")):
            result = asset_manager.load_star_image("star.png", requested_size=512)

        assert result is asset_manager.get_missing_texture()


class TestLoadPlanetImage:
    """Test load_planet_image() method with fallback chain."""

    def test_load_at_requested_resolution(self, asset_manager):
        """Test loading image at requested resolution when it exists."""
        # Use a real planet image from the 512px folder
        test_filename = "planet_5_994_1769750020702.png"
        expected_path = os.path.join(Paths.PLANETS_V3_512_DIR, test_filename)

        # Only run if file actually exists
        if os.path.exists(expected_path):
            surface = asset_manager.load_planet_image(test_filename, requested_size=512)

            # Should return a valid surface, not missing texture
            assert surface is not None
            assert surface != asset_manager.get_missing_texture()
            assert isinstance(surface, pygame.Surface)

    def test_fallback_to_higher_resolution(self, asset_manager):
        """Test fallback chain when requested resolution is missing."""
        # Create a fake filename that doesn't exist at 128px but exists at higher res
        fake_filename = "nonexistent_at_128.png"

        with patch.object(asset_manager, 'load_external_image') as mock_load:
            # First call (128px) returns missing texture
            # Second call (256px) returns valid surface
            mock_surface = MagicMock(spec=pygame.Surface)
            mock_load.side_effect = [
                asset_manager.get_missing_texture(),  # 128px missing
                mock_surface,  # 256px exists
            ]

            result = asset_manager.load_planet_image(fake_filename, requested_size=128)

            # Should have tried 128px first, then 256px
            assert mock_load.call_count >= 2
            # Should return the valid surface from 256px
            assert result == mock_surface

    def test_all_resolutions_missing_returns_missing_texture(self, asset_manager):
        """Test that missing texture is returned when no resolution exists."""
        # Use a filename that definitely doesn't exist
        fake_filename = "definitely_does_not_exist_12345.png"

        surface = asset_manager.load_planet_image(fake_filename, requested_size=512)

        # Should return missing texture when all resolutions fail
        assert surface == asset_manager.get_missing_texture()

    def test_requested_size_selects_correct_starting_point(self, asset_manager):
        """Test that requested size determines correct starting point in fallback chain."""
        test_filename = "test.png"

        with patch.object(asset_manager, '_get_planet_folder_for_size') as mock_get_folder:
            with patch.object(asset_manager, 'load_external_image') as mock_load:
                # Make all loads fail to see which resolutions are tried
                mock_load.return_value = asset_manager.get_missing_texture()
                mock_get_folder.return_value = "/fake/path"

                # Request 256px - should try: 256, 512, 1024, 2048
                asset_manager.load_planet_image(test_filename, requested_size=256)

                # Check that _get_planet_folder_for_size was called with correct sizes
                called_sizes = [call[0][0] for call in mock_get_folder.call_args_list]
                assert 256 in called_sizes
                assert 512 in called_sizes
                assert 1024 in called_sizes
                assert 2048 in called_sizes
                # Should NOT try 128px (smaller than requested)
                assert 128 not in called_sizes

    def test_caching_works_for_planet_images(self, asset_manager):
        """Test that planet images are cached after first load."""
        # Use a real planet image
        test_filename = "planet_5_994_1769750020702.png"
        expected_path = os.path.join(Paths.PLANETS_V3_512_DIR, test_filename)

        # Only run if file actually exists
        if os.path.exists(expected_path):
            # First load
            surface1 = asset_manager.load_planet_image(test_filename, requested_size=512)

            # Second load (should be from cache)
            surface2 = asset_manager.load_planet_image(test_filename, requested_size=512)

            # Should return the same cached surface
            assert surface1 is surface2

    def test_default_requested_size_is_512(self, asset_manager):
        """Test that default requested_size parameter is 512."""
        test_filename = "planet_5_994_1769750020702.png"
        expected_path = os.path.join(Paths.PLANETS_V3_512_DIR, test_filename)

        # Only run if file actually exists
        if os.path.exists(expected_path):
            # Call without specifying requested_size
            surface = asset_manager.load_planet_image(test_filename)

            # Should load successfully (default is 512)
            assert surface is not None
            assert surface != asset_manager.get_missing_texture()
