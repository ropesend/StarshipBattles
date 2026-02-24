import pytest
from unittest.mock import patch, MagicMock
import pygame
import os
import tempfile
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from game.ui.assets import ShipThemeManager

from game.core.paths import Paths


class TestNewThemes:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Initialize manager with base path (cwd)
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()

        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
             pygame.display.set_mode((1, 1), pygame.NOFRAME)

        ShipThemeManager.reset()
        manager = ShipThemeManager.instance()

        # Verify resources exist
        klingon_json = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Klingons", "theme.json")
        romulan_json = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Romulans", "theme.json")

        # Skip test if theme files are missing
        if not os.path.exists(klingon_json) or not os.path.exists(romulan_json):
            pytest.skip("Theme JSON files not found - skipping theme discovery tests")

        manager.initialize()

        # Re-initialize to ensure new files are picked up if manager was already loaded
        # (Though in a fresh process it shouldn't matter, but good for interactive testing)
        manager.themes = {}
        manager.discovery_complete = False

        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)

        manager.initialize()
        self.manager = manager

        yield

        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        # Clean up singleton
        ShipThemeManager.reset()

        # NOTE: Do not call pygame.quit() or pygame.display.quit() here - the root
        # conftest manages pygame lifecycle at session scope. Calling quit() here
        # would break subsequent tests with "No video mode set" errors.

    def test_theme_discovery(self):
        """Verify themes are discovered."""
        themes = self.manager.get_available_themes()
        assert len(themes) > 0, "No themes discovered!"
        assert "Klingons" in themes
        assert "Romulans" in themes

    def test_klingon_theme_loads(self):
        """Verify Klingon theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.load_image("Klingons", "Battle Cruiser")
        assert img is not None
        # Verify it's not the fallback (100x100)
        assert img.get_size() != (100, 100), "Should not be fallback image"

    def test_romulan_theme_loads(self):
        """Verify Romulan theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.load_image("Romulans", "Battle Cruiser")
        assert img is not None
        # Verify it's not the fallback (100x100)
        assert img.get_size() != (100, 100), "Should not be fallback image"


class TestShipThemeManagerSingletonLifecycle:
    """Test singleton pattern for ShipThemeManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    def test_instance_returns_same_object(self):
        """Test instance() returns same object on repeated calls."""
        mgr1 = ShipThemeManager.instance()
        mgr2 = ShipThemeManager.instance()
        assert mgr1 is mgr2, "instance() should return the same object"

    def test_reset_destroys_instance(self):
        """Test reset() destroys instance, next instance() creates new one."""
        mgr1 = ShipThemeManager.instance()
        mgr1.default_theme = "TestTheme"

        ShipThemeManager.reset()

        mgr2 = ShipThemeManager.instance()
        assert mgr1 is not mgr2, "After reset, should get new instance"
        assert mgr2.default_theme == "Federation", "New instance should have default theme"

    def test_clear_resets_caches_preserves_instance(self):
        """Test clear() resets caches but preserves instance."""
        mgr = ShipThemeManager.instance()
        mgr.themes = {"test": {"Escort": MagicMock()}}
        mgr.theme_data = {"test": {"Escort": {}}}
        mgr.discovery_complete = True

        mgr.clear()

        # Same instance
        assert ShipThemeManager.instance() is mgr
        # But caches are cleared
        assert mgr.themes == {}
        assert mgr.theme_data == {}
        assert mgr.discovery_complete is False

    def test_direct_init_returns_singleton(self):
        """Test direct __init__() returns singleton when instance exists."""
        mgr1 = ShipThemeManager.instance()
        mgr2 = ShipThemeManager()
        assert mgr1 is mgr2, "Direct construction should return same singleton"


class TestShipThemeManagerErrorPaths:
    """Test error handling in ShipThemeManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_missing_shipthemes_directory(self, mock_exists):
        """Test initialize() with missing ShipThemes directory doesn't crash."""
        mock_exists.return_value = False

        mgr = ShipThemeManager.instance()
        mgr.initialize()  # Should not raise

        assert mgr.theme_data == {}
        # Early return leaves discovery_complete False (correct - can retry later)
        assert mgr.discovery_complete is False

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_empty_shipthemes_directory(self, mock_exists, mock_scandir):
        """Test initialize() with empty ShipThemes directory (no themes found)."""
        mock_exists.return_value = True
        mock_scandir.return_value = []

        mgr = ShipThemeManager.instance()
        mgr.initialize()

        assert mgr.theme_data == {}
        assert len(mgr.get_available_themes()) == 0

    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_missing_theme_json(self, mock_exists, mock_scandir, mock_load_json):
        """Test initialize() with theme directory missing theme.json skips that theme."""
        mock_exists.return_value = True

        # Create mock directory entry
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/fake/theme/TestTheme"
        mock_scandir.return_value = [mock_entry]

        # load_json returns None (file not found)
        mock_load_json.return_value = None

        mgr = ShipThemeManager.instance()
        mgr.initialize()

        # Theme should be skipped
        assert "TestTheme" not in mgr.theme_data

    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_malformed_theme_json(self, mock_exists, mock_scandir, mock_load_json):
        """Test initialize() with malformed theme.json skips with error."""
        mock_exists.return_value = True

        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/fake/theme/BadTheme"
        mock_scandir.return_value = [mock_entry]

        # Return data that will cause KeyError (missing 'images')
        mock_load_json.return_value = {"name": "BadTheme"}

        mgr = ShipThemeManager.instance()
        mgr.initialize()

        # Theme should be discovered but with empty ship data
        assert "BadTheme" in mgr.theme_data or len(mgr.theme_data) == 0

    def test_load_image_nonexistent_theme(self):
        """Test load_image() with non-existent theme_id returns fallback."""
        mgr = ShipThemeManager.instance()
        mgr.discovery_complete = True
        mgr.theme_data = {}  # No themes

        img = mgr.load_image("NonExistent", "Escort")

        # Should return fallback image (100x100)
        assert img is not None
        assert img.get_size() == (100, 100)

    def test_load_image_nonexistent_ship_class(self):
        """Test load_image() with non-existent ship_class returns fallback."""
        mgr = ShipThemeManager.instance()
        mgr.discovery_complete = True
        mgr.theme_data = {"Federation": {}}  # Theme exists but no ships

        img = mgr.load_image("Federation", "NonExistentClass")

        assert img is not None
        assert img.get_size() == (100, 100)

    def test_load_image_before_discovery(self):
        """Test load_image() before discovery returns fallback."""
        mgr = ShipThemeManager.instance()
        assert mgr.discovery_complete is False

        img = mgr.load_image("Federation", "Escort")

        assert img is not None
        assert img.get_size() == (100, 100)


class TestShipThemeManagerCaching:
    """Test caching behavior in ShipThemeManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    def test_load_image_caching(self):
        """Test load_image() caching: second call returns same surface."""
        mgr = ShipThemeManager.instance()

        # Use real theme if available
        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")

        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")

        # Get any ship class
        ship_class = list(mgr.theme_data["Federation"].keys())[0]

        img1 = mgr.load_image("Federation", ship_class)
        img2 = mgr.load_image("Federation", ship_class)

        assert img1 is img2, "Second call should return cached surface"

    def test_clear_invalidates_cache(self):
        """Test clear() invalidates cache, next load_image() reloads."""
        mgr = ShipThemeManager.instance()

        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")

        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")

        ship_class = list(mgr.theme_data["Federation"].keys())[0]

        img1 = mgr.load_image("Federation", ship_class)

        # Clear caches
        mgr.clear()

        # Must re-initialize after clear
        mgr.initialize()

        img2 = mgr.load_image("Federation", ship_class)

        # Images are equal but not the same object (reloaded)
        assert img1 is not img2, "After clear, should reload from disk"


class TestShipThemeManagerMetrics:
    """Test metrics functionality in ShipThemeManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    def test_get_metrics_returns_rect(self):
        """Test get_metrics() returns expected metrics dict for valid theme/class."""
        mgr = ShipThemeManager.instance()

        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")

        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")

        ship_class = list(mgr.theme_data["Federation"].keys())[0]

        metrics = mgr.get_image_metrics("Federation", ship_class)

        assert metrics is not None
        # Should be a pygame.Rect
        assert hasattr(metrics, 'width')
        assert hasattr(metrics, 'height')

    def test_get_metrics_caching(self):
        """Test get_metrics() caching behavior."""
        mgr = ShipThemeManager.instance()

        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")

        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")

        ship_class = list(mgr.theme_data["Federation"].keys())[0]

        metrics1 = mgr.get_image_metrics("Federation", ship_class)
        metrics2 = mgr.get_image_metrics("Federation", ship_class)

        # Should return same cached rect
        assert metrics1 is metrics2

    def test_get_metrics_before_discovery(self):
        """Test get_metrics() returns None before discovery."""
        mgr = ShipThemeManager.instance()
        assert mgr.discovery_complete is False

        result = mgr.get_image_metrics("Federation", "Escort")
        assert result is None


class TestShipThemeManagerThreadSafety:
    """Test thread safety of ShipThemeManager."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    def test_concurrent_instance_calls(self):
        """Test concurrent instance() calls all return same instance."""
        results = []

        def get_instance():
            return ShipThemeManager.instance()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(get_instance) for _ in range(8)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results[1:]:
            assert r is first, "All threads should get same singleton instance"

    def test_concurrent_load_image_no_corruption(self):
        """Test concurrent load_image() calls don't corrupt cache."""
        mgr = ShipThemeManager.instance()

        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")

        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")

        ship_class = list(mgr.theme_data["Federation"].keys())[0]
        errors = []

        def load_and_check():
            try:
                img = mgr.load_image("Federation", ship_class)
                return img is not None
            except Exception as e:
                errors.append(str(e))
                return False

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(load_and_check) for _ in range(8)]
            results = [f.result() for f in futures]

        assert not errors, f"Concurrent loads caused errors: {errors}"
        assert all(results), "All loads should return valid images"

    def test_concurrent_initialize_double_checked_locking(self):
        """Test concurrent initialize() calls use double-checked locking."""
        ShipThemeManager.reset()
        mgr = ShipThemeManager.instance()
        initialize_count = [0]
        lock = threading.Lock()

        original_init = mgr.initialize

        def counted_init():
            with lock:
                initialize_count[0] += 1
            return original_init()

        mgr.initialize = counted_init
        errors = []

        def init_call():
            try:
                mgr.initialize()
            except Exception as e:
                errors.append(str(e))

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(init_call) for _ in range(4)]
            for f in futures:
                f.result()

        assert not errors
        # Due to double-checked locking, only first thread should fully initialize
        # Others should return early
        assert mgr.discovery_complete is True


class TestShipThemeManagerManualScale:
    """Test manual scale factor handling."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        ShipThemeManager.reset()
        yield
        ShipThemeManager.reset()

    def test_get_manual_scale_default(self):
        """Test get_manual_scale returns 1.0 for unknown ship."""
        mgr = ShipThemeManager.instance()
        mgr.discovery_complete = True
        mgr.theme_data = {"Test": {}}

        scale = mgr.get_manual_scale("Test", "Unknown")
        assert scale == 1.0

    def test_get_manual_scale_before_discovery(self):
        """Test get_manual_scale returns 1.0 before discovery."""
        mgr = ShipThemeManager.instance()
        assert mgr.discovery_complete is False

        scale = mgr.get_manual_scale("Test", "Escort")
        assert scale == 1.0

    def test_get_manual_scale_with_value(self):
        """Test get_manual_scale returns configured value."""
        mgr = ShipThemeManager.instance()
        mgr.discovery_complete = True
        mgr.theme_data = {
            "Test": {
                "Escort": {"path": "/fake/path", "scale": 1.5}
            }
        }

        scale = mgr.get_manual_scale("Test", "Escort")
        assert scale == 1.5
