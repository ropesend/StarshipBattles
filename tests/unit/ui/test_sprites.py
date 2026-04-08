"""Tests for SpriteManager class."""
import pytest
import sys
import os
import pygame
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock

from game.ui.renderer.sprites import SpriteManager
from tests.fixtures.paths import get_project_root, get_assets_dir


class TestSprites:

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        # Initialize display for convert() calls
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        # Point to the project root
        self.base_path = str(get_project_root())

        yield

        # Always reset singleton after test
        SpriteManager.reset()

    def test_load_sprites(self):
        """Test loading sprites using the new directory method."""
        components_dir = str(get_assets_dir() / "Images" / "Components")
        if not os.path.exists(components_dir):
            pytest.skip(f"Components directory not found at {components_dir}")

        mgr = SpriteManager()
        # Initialize display for convert() calls in load_sprites
        if pygame.display.get_surface() is None:
             pygame.display.set_mode((1, 1), pygame.NOFRAME)

        mgr.load_sprites(self.base_path)

        # Check that we loaded some sprites
        # In the real directory we saw 467 files, indices up to 234 approx?
        # Let's just check we have something at index 0
        assert mgr.get_sprite(0) is not None, "Should have loaded Bridge sprite at index 0"
        assert mgr.get_sprite(18) is not None, "Should have loaded Railgun sprite at index 18"

        # Ensure we have a decent number of sprites
        count = sum(1 for s in mgr.sprites if s is not None)
        assert count > 10, "Should have loaded multiple sprites"

    def test_atlas_fallback_logic(self):
        """Test that we can still conceptually load an atlas if we wanted to (via private method maybe? or just skip)."""
        # Since load_atlas is deprecated/empty, this test is less relevant unless we test the fallback path explicitly.
        # But we tested fallback logic with mocks in test_sprite_loading.py.
        pass


class TestSpriteManagerSingletonLifecycle:
    """Test singleton pattern for SpriteManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        SpriteManager.reset()
        yield
        SpriteManager.reset()

    def test_instance_returns_same_object(self):
        """Test instance() returns same object on repeated calls."""
        mgr1 = SpriteManager.instance()
        mgr2 = SpriteManager.instance()
        assert mgr1 is mgr2, "instance() should return the same object"

    def test_reset_destroys_instance(self):
        """Test reset() destroys instance, next instance() creates new one."""
        mgr1 = SpriteManager.instance()
        mgr1.tile_size = 999  # Modify it

        SpriteManager.reset()

        mgr2 = SpriteManager.instance()
        assert mgr1 is not mgr2, "After reset, should get new instance"
        assert mgr2.tile_size == 36, "New instance should have default tile_size"

    def test_direct_init_returns_singleton(self):
        """Test direct __init__() returns singleton when instance exists."""
        mgr1 = SpriteManager.instance()
        mgr2 = SpriteManager()  # Direct construction
        assert mgr1 is mgr2, "Direct construction should return same singleton"


class TestSpriteManagerErrorPaths:
    """Test error handling in SpriteManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        SpriteManager.reset()
        yield
        SpriteManager.reset()

    def test_load_sprites_nonexistent_directory(self):
        """Test load_sprites() with non-existent directory path falls back gracefully."""
        mgr = SpriteManager.instance()
        # Use temp dir that doesn't have assets
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr.load_sprites(tmpdir)
            # Should not crash, sprites list should be empty or minimal
            assert mgr.sprites == [] or len(mgr.sprites) == 0

    def test_load_from_directory_empty_directory(self):
        """Test _load_from_directory() with empty directory (no image files)."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr._load_from_directory(tmpdir)
            # Should handle gracefully with empty sprites list
            assert mgr.sprites == []

    @patch('game.ui.renderer.sprites.pygame.image.load')
    def test_load_from_directory_corrupt_image(self, mock_load):
        """Test _load_from_directory() with corrupt/invalid image file."""
        mock_load.side_effect = pygame.error("Corrupt image")

        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with valid naming pattern
            corrupt_file = os.path.join(tmpdir, "Comp_001.png")
            with open(corrupt_file, 'w') as f:
                f.write("not an image")

            # Should not crash, just log error and skip
            mgr._load_from_directory(tmpdir)
            # Sprites list should be empty (file failed to load)
            assert mgr.sprites == [] or mgr.get_sprite(0) is None

    def test_get_sprite_out_of_bounds_index(self):
        """Test get_sprite() with out-of-bounds index returns None."""
        mgr = SpriteManager.instance()
        mgr.sprites = [MagicMock()]  # One sprite at index 0

        result = mgr.get_sprite(999)
        assert result is None, "Out of bounds index should return None"

    def test_get_sprite_negative_index(self):
        """Test get_sprite() with negative index returns None."""
        mgr = SpriteManager.instance()
        mgr.sprites = [MagicMock()]

        result = mgr.get_sprite(-1)
        assert result is None, "Negative index should return None"

    def test_get_sprite_empty_list(self):
        """Test get_sprite() with empty sprites list returns None."""
        mgr = SpriteManager.instance()
        mgr.sprites = []

        result = mgr.get_sprite(0)
        assert result is None


class TestSpriteManagerNamingConventions:
    """Test parsing of different sprite naming conventions."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        SpriteManager.reset()
        yield
        SpriteManager.reset()

    def _create_test_image(self, path):
        """Create a minimal valid image file."""
        surf = pygame.Surface((10, 10))
        pygame.image.save(surf, path)

    def test_comp_pattern_parsing(self):
        """Test loading files matching Comp_* pattern."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Comp_001.png -> index 1
            self._create_test_image(os.path.join(tmpdir, "Comp_001.png"))
            # Create Comp_005.png -> index 5
            self._create_test_image(os.path.join(tmpdir, "Comp_005.png"))

            mgr._load_from_directory(tmpdir)

            assert mgr.get_sprite(1) is not None, "Comp_001 should be at index 1"
            assert mgr.get_sprite(5) is not None, "Comp_005 should be at index 5"
            assert mgr.get_sprite(2) is None, "Index 2 should be None (gap)"

    def test_portrait_pattern_parsing(self):
        """Test loading files matching {resolution}Portrait_Comp_* pattern."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 64Portrait_Comp_001.png -> index 1
            self._create_test_image(os.path.join(tmpdir, "64Portrait_Comp_001.png"))

            mgr._load_from_directory(tmpdir)

            assert mgr.get_sprite(1) is not None, "64Portrait_Comp_001 should be at index 1"

    def test_portrait_pattern_various_resolutions(self):
        """Test parsing works for different resolution prefixes."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_test_image(os.path.join(tmpdir, "2048Portrait_Comp_001.png"))
            self._create_test_image(os.path.join(tmpdir, "128Portrait_Comp_003.png"))

            mgr._load_from_directory(tmpdir)

            assert mgr.get_sprite(1) is not None, "Comp_001 should be at index 1"
            assert mgr.get_sprite(3) is not None, "Comp_003 should be at index 3"

    def test_unexpected_prefix_skipped(self):
        """Test loading files with unexpected prefixes are skipped."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with unknown prefix
            self._create_test_image(os.path.join(tmpdir, "Unknown_001.png"))
            # Create valid file
            self._create_test_image(os.path.join(tmpdir, "Comp_001.png"))

            mgr._load_from_directory(tmpdir)

            # Should only have one sprite (the valid one)
            assert mgr.get_sprite(1) is not None
            count = sum(1 for s in mgr.sprites if s is not None)
            assert count == 1

    def test_sparse_sprite_list(self):
        """Test sparse sprite list (indices with gaps)."""
        mgr = SpriteManager.instance()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sprites at indices 1, 3, 6 (with gaps)
            self._create_test_image(os.path.join(tmpdir, "Comp_001.bmp"))  # index 1
            self._create_test_image(os.path.join(tmpdir, "Comp_003.bmp"))  # index 3
            self._create_test_image(os.path.join(tmpdir, "Comp_006.bmp"))  # index 6

            mgr._load_from_directory(tmpdir)

            assert mgr.get_sprite(0) is None, "Index 0 should be None (no Comp_000)"
            assert mgr.get_sprite(1) is not None, "Index 1 should have sprite"
            assert mgr.get_sprite(2) is None, "Index 2 should be None (gap)"
            assert mgr.get_sprite(3) is not None, "Index 3 should have sprite"
            assert mgr.get_sprite(4) is None, "Index 4 should be None (gap)"
            assert mgr.get_sprite(5) is None, "Index 5 should be None (gap)"
            assert mgr.get_sprite(6) is not None, "Index 6 should have sprite"


class TestSpriteManagerThreadSafety:
    """Test thread safety of SpriteManager singleton."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        SpriteManager.reset()
        yield
        SpriteManager.reset()

    def test_concurrent_instance_calls(self):
        """Test concurrent instance() calls all return same instance."""
        results = []

        def get_instance():
            return SpriteManager.instance()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(get_instance) for _ in range(8)]
            results = [f.result() for f in futures]

        # All results should be the same instance
        first = results[0]
        for r in results[1:]:
            assert r is first, "All threads should get same singleton instance"

    def test_concurrent_load_sprites_no_corruption(self):
        """Test concurrent load_sprites() calls don't corrupt state."""
        base_path = str(get_project_root())
        components_dir = str(get_assets_dir() / "Images" / "Components")
        if not os.path.exists(components_dir):
            pytest.skip(f"Components directory not found")

        mgr = SpriteManager.instance()
        errors = []

        def load_and_check():
            try:
                mgr.load_sprites(base_path)
                # Basic sanity check - should have sprites
                return len(mgr.sprites) > 0
            except Exception as e:
                errors.append(str(e))
                return False

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(load_and_check) for _ in range(4)]
            results = [f.result() for f in futures]

        assert not errors, f"Concurrent loads caused errors: {errors}"
        # At least some should succeed
        assert any(results), "At least one load should succeed"
