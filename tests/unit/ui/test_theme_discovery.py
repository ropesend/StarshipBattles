"""Theme discovery and contract tests for ShipThemeManager (PROJ-314)."""
from __future__ import annotations

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.core.paths import Paths
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from game.ui.assets import (
    ShipThemeManager,
    get_default_ship_theme_manager,
    set_default_ship_theme_manager,
)


# PROJ-479 Task 2.1: class-scoped pygame display init shared across all
# tests in a class. The per-test setup_teardown fixtures below still
# reset the ShipThemeManager singleton per-test (necessary because tests
# mutate manager state); only the heavy pygame.display.set_mode call is
# class-scoped now.
@pytest.fixture(scope="class", autouse=True)
def _shared_pygame_display():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    if not pygame.display.get_surface():
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield


class TestNewThemes:
    """Smoke tests against the real assets/ShipThemes/ directory."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)

        set_default_ship_theme_manager(ShipThemeManager())
        manager = get_default_ship_theme_manager()

        klingon_json = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Klingons", "theme.json")
        romulan_json = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Romulans", "theme.json")
        if not os.path.exists(klingon_json) or not os.path.exists(romulan_json):
            pytest.skip("Theme JSON files not found - skipping theme discovery tests")

        manager.initialize()
        manager.themes = {}
        manager.discovery_complete = False
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        manager.initialize()
        self.manager = manager

        yield
        patch.stopall()
        set_default_ship_theme_manager(ShipThemeManager())

    def test_theme_discovery(self):
        """Themes are discovered (post-PROJ-314: all 9 use the new schema)."""
        themes = self.manager.get_available_themes()
        assert len(themes) > 0
        assert "Klingons" in themes
        assert "Romulans" in themes

    def test_klingon_theme_loads(self):
        """Klingon Battle Cruiser skin renders, not a fallback."""
        img = self.manager.load_image("Klingons", "Battle Cruiser")
        assert img is not None
        assert img.get_size() != (100, 100), "Should not be the synthetic fallback"

    def test_romulan_theme_loads(self):
        """Romulan Battle Cruiser skin renders, not a fallback."""
        img = self.manager.load_image("Romulans", "Battle Cruiser")
        assert img is not None
        assert img.get_size() != (100, 100), "Should not be the synthetic fallback"


class TestThemeContractAgainstRealAssets:
    """PROJ-314 contract tests against real theme.json files on disk."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        themes_dir = Paths.SHIP_THEMES_DIR
        if not os.path.isdir(themes_dir):
            pytest.skip("ShipThemes directory not found")
        self.themes_dir = themes_dir
        self.theme_dirs = [
            os.path.join(themes_dir, name)
            for name in os.listdir(themes_dir)
            if os.path.isdir(os.path.join(themes_dir, name))
        ]
        yield

    def test_every_theme_json_parses(self):
        """Every theme.json must be valid JSON."""
        for theme_dir in self.theme_dirs:
            json_path = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            assert isinstance(data, dict), f"Theme {theme_dir} json is not a dict"
            assert "name" in data, f"Theme {theme_dir} missing 'name'"

    def test_every_theme_uses_new_assets_schema(self):
        """Every theme.json declares the PROJ-314 `assets:` block."""
        for theme_dir in self.theme_dirs:
            json_path = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            theme_name = data.get("name", os.path.basename(theme_dir))
            assert "assets" in data, (
                f"Theme {theme_name}: legacy 'images:' schema is no longer "
                f"supported (PROJ-314)"
            )
            assert isinstance(data["assets"], dict)

    def test_every_declared_skin_path_exists(self):
        """Every declared `skin` path in every theme.json must exist on disk."""
        for theme_dir in self.theme_dirs:
            json_path = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            theme_name = data.get("name", os.path.basename(theme_dir))
            for ship_class, entry in (data.get("assets") or {}).items():
                if not isinstance(entry, dict):
                    continue
                skin_rel = entry.get("skin")
                if not skin_rel:
                    continue
                skin_path = os.path.join(theme_dir, skin_rel)
                assert os.path.exists(skin_path), (
                    f"Theme {theme_name} / {ship_class}: declared "
                    f"skin {skin_rel!r} not found on disk"
                )

    def test_every_declared_portrait_path_exists(self):
        """Every declared `portrait` path (when present) must exist on disk."""
        for theme_dir in self.theme_dirs:
            json_path = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            theme_name = data.get("name", os.path.basename(theme_dir))
            for ship_class, entry in (data.get("assets") or {}).items():
                if not isinstance(entry, dict):
                    continue
                portrait_rel = entry.get("portrait")
                if not portrait_rel:
                    continue  # Portrait is optional; the loader synthesises a fallback.
                portrait_path = os.path.join(theme_dir, portrait_rel)
                assert os.path.exists(portrait_path), (
                    f"Theme {theme_name} / {ship_class}: declared "
                    f"portrait {portrait_rel!r} not found on disk"
                )

    def test_every_declared_key_is_canonical(self):
        """Every key in `assets:` matches SHIP_CLASSES_WITH_VISUAL_THEMES exactly."""
        for theme_dir in self.theme_dirs:
            json_path = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            theme_name = data.get("name", os.path.basename(theme_dir))
            for ship_class in (data.get("assets") or {}):
                assert ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES, (
                    f"Theme {theme_name}: ship class {ship_class!r} is not in "
                    f"SHIP_CLASSES_WITH_VISUAL_THEMES"
                )


class TestImageSizeValidationWarning:
    """PROJ-314: image_sizes mismatch logs a warning, does not reject."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        patch.stopall()
        set_default_ship_theme_manager(ShipThemeManager())

    @patch('game.ui.assets.ship_theme_manager.logger')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    def test_size_mismatch_warns_does_not_reject(
        self, mock_load_json, mock_exists, mock_scandir, mock_logger,
    ):
        """When PIL reports a size != declared image_sizes, the loader warns but registers the asset."""
        json_content = {
            "schema_version": 1,
            "name": "WrongSizeTheme",
            "image_sizes": {"skin": [2048, 2048], "portrait": [2048, 2048]},
            "assets": {
                "Battleship": {
                    "skin": "Skins/battleship.png",
                    "portrait": "Portraits/battleship.png",
                    "scale": 1.0,
                }
            },
        }
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/WrongSizeTheme"
        mock_entry.name = "WrongSizeTheme"
        mock_scandir.return_value = [mock_entry]
        mock_exists.return_value = True
        mock_load_json.return_value = json_content

        # Stub PIL to report a wrong size.
        fake_img = MagicMock()
        fake_img.width = 1024
        fake_img.height = 1024
        fake_img.__enter__ = lambda self: self
        fake_img.__exit__ = lambda self, *a: None
        with patch("PIL.Image.open", return_value=fake_img):
            mgr = get_default_ship_theme_manager()
            mgr.initialize()

        assert "WrongSizeTheme" in mgr.theme_data
        assert "Battleship" in mgr.theme_data["WrongSizeTheme"]
        warned = any(
            "image_sizes" in str(call.args[0])
            for call in mock_logger.warning.call_args_list
        )
        assert warned, "Expected an image_sizes-mismatch warning"


class TestShipThemeManagerSingletonLifecycle:
    """Singleton-pattern lifecycle tests."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    def test_instance_returns_same_object(self):
        mgr1 = get_default_ship_theme_manager()
        mgr2 = get_default_ship_theme_manager()
        assert mgr1 is mgr2

    def test_reset_destroys_instance(self):
        mgr1 = get_default_ship_theme_manager()
        mgr1.default_theme = "TestTheme"
        set_default_ship_theme_manager(ShipThemeManager())
        mgr2 = get_default_ship_theme_manager()
        assert mgr1 is not mgr2
        assert mgr2.default_theme == "Federation"

    def test_clear_resets_caches_preserves_instance(self):
        mgr = get_default_ship_theme_manager()
        mgr.themes = {"test": {"Escort": MagicMock()}}
        mgr.theme_data = {"test": {"Escort": {}}}
        mgr.discovery_complete = True
        mgr.clear()
        assert get_default_ship_theme_manager() is mgr
        assert mgr.themes == {}
        assert mgr.theme_data == {}
        assert mgr.discovery_complete is False

    def test_direct_init_creates_new_instance(self):
        mgr1 = get_default_ship_theme_manager()
        mgr2 = ShipThemeManager()
        assert mgr1 is not mgr2


class TestShipThemeManagerErrorPaths:
    """Error-handling tests."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_missing_shipthemes_directory(self, mock_exists):
        mock_exists.return_value = False
        mgr = get_default_ship_theme_manager()
        mgr.initialize()
        assert mgr.theme_data == {}
        assert mgr.discovery_complete is False

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_empty_shipthemes_directory(self, mock_exists, mock_scandir):
        mock_exists.return_value = True
        mock_scandir.return_value = []
        mgr = get_default_ship_theme_manager()
        mgr.initialize()
        assert mgr.theme_data == {}
        assert len(mgr.get_available_themes()) == 0

    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_missing_theme_json(self, mock_exists, mock_scandir, mock_load_json):
        mock_exists.return_value = True
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/fake/theme/TestTheme"
        mock_scandir.return_value = [mock_entry]
        mock_load_json.return_value = None
        mgr = get_default_ship_theme_manager()
        mgr.initialize()
        assert "TestTheme" not in mgr.theme_data

    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_initialize_missing_assets_block(self, mock_exists, mock_scandir, mock_load_json):
        """A theme.json without `assets:` is rejected (no longer falls back to images)."""
        mock_exists.return_value = True
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/fake/theme/BadTheme"
        mock_scandir.return_value = [mock_entry]
        mock_load_json.return_value = {"name": "BadTheme"}
        mgr = get_default_ship_theme_manager()
        mgr.initialize()
        assert "BadTheme" not in mgr.theme_data

    def test_load_image_nonexistent_theme(self):
        mgr = get_default_ship_theme_manager()
        mgr.discovery_complete = True
        mgr.theme_data = {}
        img = mgr.load_image("NonExistent", "Escort")
        assert img is not None
        assert img.get_size() == (100, 100)

    def test_load_image_nonexistent_ship_class(self):
        mgr = get_default_ship_theme_manager()
        mgr.discovery_complete = True
        mgr.theme_data = {"Federation": {}}
        img = mgr.load_image("Federation", "NonExistentClass")
        assert img is not None
        assert img.get_size() == (100, 100)

    def test_load_image_before_discovery(self):
        mgr = get_default_ship_theme_manager()
        assert mgr.discovery_complete is False
        img = mgr.load_image("Federation", "Escort")
        assert img is not None
        assert img.get_size() == (100, 100)


class TestShipThemeManagerCaching:
    """Caching behaviour tests against real Federation theme."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    def test_load_image_caching(self):
        mgr = get_default_ship_theme_manager()
        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")
        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")
        ship_class = list(mgr.theme_data["Federation"].keys())[0]
        img1 = mgr.load_image("Federation", ship_class)
        img2 = mgr.load_image("Federation", ship_class)
        assert img1 is img2

    def test_clear_invalidates_cache(self):
        mgr = get_default_ship_theme_manager()
        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")
        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")
        ship_class = list(mgr.theme_data["Federation"].keys())[0]
        img1 = mgr.load_image("Federation", ship_class)
        mgr.clear()
        mgr.initialize()
        img2 = mgr.load_image("Federation", ship_class)
        assert img1 is not img2


class TestShipThemeManagerMetrics:
    """Metrics tests against real Federation theme."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    def test_get_metrics_returns_rect(self):
        mgr = get_default_ship_theme_manager()
        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")
        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")
        ship_class = list(mgr.theme_data["Federation"].keys())[0]
        metrics = mgr.get_image_metrics("Federation", ship_class)
        assert metrics is not None
        assert hasattr(metrics, 'width')
        assert hasattr(metrics, 'height')

    def test_get_metrics_caching(self):
        mgr = get_default_ship_theme_manager()
        themes_dir = os.path.join(Paths.ASSET_DIR, "ShipThemes", "Federation")
        if not os.path.exists(themes_dir):
            pytest.skip("Federation theme not found")
        mgr.initialize()
        if "Federation" not in mgr.theme_data or not mgr.theme_data["Federation"]:
            pytest.skip("Federation theme has no ships")
        ship_class = list(mgr.theme_data["Federation"].keys())[0]
        m1 = mgr.get_image_metrics("Federation", ship_class)
        m2 = mgr.get_image_metrics("Federation", ship_class)
        assert m1 is m2

    def test_get_metrics_before_discovery(self):
        mgr = get_default_ship_theme_manager()
        assert mgr.discovery_complete is False
        result = mgr.get_image_metrics("Federation", "Escort")
        assert result is None


class TestShipThemeManagerThreadSafety:
    """Thread-safety tests."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    def test_concurrent_instance_calls(self):
        results = []

        def get_instance():
            return get_default_ship_theme_manager()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(get_instance) for _ in range(8)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results[1:]:
            assert r is first

    def test_concurrent_load_image_no_corruption(self):
        mgr = get_default_ship_theme_manager()
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

        assert not errors
        assert all(results)

    def test_concurrent_initialize_double_checked_locking(self):
        set_default_ship_theme_manager(ShipThemeManager())
        mgr = get_default_ship_theme_manager()
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
        assert mgr.discovery_complete is True


class TestShipThemeManagerManualScale:
    """Manual scale factor handling."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        set_default_ship_theme_manager(ShipThemeManager())
        yield
        set_default_ship_theme_manager(ShipThemeManager())

    def test_get_manual_scale_default(self):
        mgr = get_default_ship_theme_manager()
        mgr.discovery_complete = True
        mgr.theme_data = {"Test": {}}
        assert mgr.get_manual_scale("Test", "Unknown") == 1.0

    def test_get_manual_scale_before_discovery(self):
        mgr = get_default_ship_theme_manager()
        assert mgr.discovery_complete is False
        assert mgr.get_manual_scale("Test", "Escort") == 1.0

    def test_get_manual_scale_with_value(self):
        mgr = get_default_ship_theme_manager()
        mgr.discovery_complete = True
        mgr.theme_data = {
            "Test": {
                "Escort": {"skin_path": "/fake/path", "portrait_path": None, "scale": 1.5}
            }
        }
        assert mgr.get_manual_scale("Test", "Escort") == 1.5
