
import pytest
from unittest.mock import patch, MagicMock
import pygame
import os
from game.ui.assets import ShipThemeManager


class TestShipThemeLogic:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Set dummy driver for headless execution
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))

        # Ensure singleton is reset before each test
        ShipThemeManager.reset()
        self.manager = ShipThemeManager.instance()

        yield

        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.

        # Clean up singleton
        ShipThemeManager.reset()

    def test_singleton_handling(self):
        """Test that the singleton pattern works and returns unique instance."""
        instance1 = ShipThemeManager.instance()
        instance2 = ShipThemeManager.instance()
        assert instance1 is instance2

        # With SingletonMeta, direct construction returns the singleton
        instance3 = ShipThemeManager()
        assert instance1 is instance3

    def test_fallback_generation(self):
        """Test that fallback image is generated with expected properties."""
        fallback = self.manager._create_fallback_image("UnknownClass")

        assert isinstance(fallback, pygame.Surface)
        assert fallback.get_size() == (100, 100)

    def test_load_image_fallback_behavior(self):
        """Test load_image returns fallback when not loaded or theme missing."""
        # Not loaded yet
        img = self.manager.load_image("AnyTheme", "AnyClass")
        assert img.get_size() == (100, 100)

        # Pretend loaded but theme missing
        self.manager.loaded = True
        img = self.manager.load_image("NonExistentTheme", "AnyClass")
        assert img.get_size() == (100, 100)

    @patch('game.ui.assets.ship_theme_manager.logger')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_manual_scaling_and_loading(self, mock_load, mock_load_json, mock_exists, mock_scandir, mock_logger):
        """Test loading a theme with manual scaling configured."""

        # Setup mock file system structure
        theme_name = "ScaledTheme"
        ship_class = "BigShip"
        json_content = {
            "name": theme_name,
            "images": {
                ship_class: {
                    "file": "big_ship.png",
                    "scale": 1.5
                }
            }
        }

        # Mock directory entry
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_entry.name = theme_name
        mock_scandir.return_value = [mock_entry]

        # Mock file existence
        def side_effect(path):
            if path.endswith("ShipThemes"): return True
            if "theme.json" in path: return True
            if "big_ship.png" in path: return True
            return False
        mock_exists.side_effect = side_effect

        # Mock load_json
        mock_load_json.return_value = json_content

        # Mock image loading
        dummy_surface = pygame.Surface((50, 50))
        mock_load.return_value = dummy_surface

        # Run initialize
        self.manager.initialize()

        # Verify no errors logged (e.g. convert_alpha failure)
        mock_logger.error.assert_not_called()

        # Verify scaling
        scale = self.manager.get_manual_scale(theme_name, ship_class)
        assert scale == 1.5

        # Verify default scaling for unknown class
        scale_default = self.manager.get_manual_scale(theme_name, "OtherShip")
        assert scale_default == 1.0

    @patch('game.ui.assets.ship_theme_manager.logger')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_get_image_metrics(self, mock_load, mock_load_json, mock_exists, mock_scandir, mock_logger):
        """Test that bounding rect is correctly calculated and cached."""

        theme_name = "MetricsTheme"
        ship_class = "TestShip"
        json_content = {
            "name": theme_name,
            "images": {
                ship_class: "game.simulation.entities.ship.png"
            }
        }

        # Mocks setup
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_entry.name = theme_name
        mock_scandir.return_value = [mock_entry]

        mock_exists.return_value = True # Simplify exists checks
        mock_load_json.return_value = json_content

        # Use a Mock Surface since real ones are immutable and can't have convert_alpha patched
        surf = MagicMock(spec=pygame.Surface)
        # Use side_effect to catch any get_bounding_rect call regardless of arg types
        surf.get_bounding_rect.side_effect = lambda *args, **kwargs: pygame.Rect(5, 5, 10, 10)
        surf.convert_alpha.return_value = surf
        surf.get_size.return_value = (20, 20)

        mock_load.return_value = surf

        # Initialize
        self.manager.initialize()

        # Verify no errors logged
        mock_logger.error.assert_not_called()

        # Verify metrics
        rect = self.manager.get_image_metrics(theme_name, ship_class)
        assert rect is not None
        assert rect.x == 5
        assert rect.y == 5
        assert rect.width == 10
        assert rect.height == 10

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    def test_malformed_theme_json(self, mock_load_json, mock_exists, mock_scandir):
        """Test handling of malformed JSON in theme file."""

        theme_name = "BadTheme"
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_scandir.return_value = [mock_entry]

        mock_exists.return_value = True

        # Mock load_json returning None (simulating malformed JSON)
        mock_load_json.return_value = None

        # Initialize shouldn't crash
        self.manager.initialize()

        # With load_json returning None, the code returns early without error
        # Verify no theme was discovered
        assert len(self.manager.theme_data) == 0


class TestShipClassToPortraitName:
    """Tests for _ship_class_to_portrait_name() parsing logic."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))
        ShipThemeManager.reset()
        self.manager = ShipThemeManager.instance()
        yield
        patch.stopall()
        ShipThemeManager.reset()

    def test_simple_class_name(self):
        """Simple class names pass through unchanged."""
        assert self.manager._ship_class_to_portrait_name("Battleship") == "Battleship"
        assert self.manager._ship_class_to_portrait_name("Escort") == "Escort"
        assert self.manager._ship_class_to_portrait_name("Frigate") == "Frigate"

    def test_parenthetical_format(self):
        """Parenthetical format (e.g., 'Fighter (Medium)') converts to prefix format."""
        assert self.manager._ship_class_to_portrait_name("Fighter (Medium)") == "MediumFighter"
        assert self.manager._ship_class_to_portrait_name("Fighter (Heavy)") == "HeavyFighter"
        assert self.manager._ship_class_to_portrait_name("Fighter (Light)") == "LightFighter"
        assert self.manager._ship_class_to_portrait_name("Satellite (Heavy)") == "HeavySatellite"

    def test_space_separated_names(self):
        """Space-separated names have spaces removed."""
        assert self.manager._ship_class_to_portrait_name("Light Cruiser") == "LightCruiser"
        assert self.manager._ship_class_to_portrait_name("Heavy Cruiser") == "HeavyCruiser"
        assert self.manager._ship_class_to_portrait_name("Battle Cruiser") == "BattleCruiser"

    def test_edge_cases(self):
        """Edge cases for portrait name conversion."""
        # Empty string
        assert self.manager._ship_class_to_portrait_name("") == ""
        # Single word
        assert self.manager._ship_class_to_portrait_name("Destroyer") == "Destroyer"
        # Multiple spaces
        assert self.manager._ship_class_to_portrait_name("Super Heavy Cruiser") == "SuperHeavyCruiser"


class TestGetPortraitImage:
    """Tests for get_portrait_image() loading and caching."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))
        ShipThemeManager.reset()
        self.manager = ShipThemeManager.instance()
        yield
        patch.stopall()
        ShipThemeManager.reset()

    def test_returns_none_when_not_initialized(self):
        """get_portrait_image returns None when discovery not complete."""
        result = self.manager.get_portrait_image("AnyTheme", "AnyClass")
        assert result is None

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_returns_none_for_missing_portrait(
        self, mock_load, mock_load_json, mock_exists, mock_scandir
    ):
        """get_portrait_image returns None when portrait file doesn't exist."""
        theme_name = "TestTheme"
        ship_class = "Battleship"

        # Setup minimal theme discovery
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/TestTheme"
        mock_entry.name = theme_name
        mock_scandir.return_value = [mock_entry]

        mock_load_json.return_value = {
            "name": theme_name,
            "images": {"Battleship": "Skins/Battleship.png"}
        }

        def exists_side_effect(path):
            # Theme dir and ship image exist, but NOT portrait
            if "ShipThemes" in path or "theme.json" in path:
                return True
            if "Battleship.png" in path and "Portrait" not in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect

        # Mock ship image loading
        surf = pygame.Surface((50, 50))
        mock_load.return_value = surf

        self.manager.initialize()

        # Portrait doesn't exist, should return None
        result = self.manager.get_portrait_image(theme_name, ship_class)
        assert result is None

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_loads_and_caches_portrait(
        self, mock_load, mock_load_json, mock_exists, mock_scandir
    ):
        """get_portrait_image loads portrait from disk and caches it."""
        theme_name = "TestTheme"
        ship_class = "Escort"

        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/TestTheme"
        mock_entry.name = theme_name
        mock_scandir.return_value = [mock_entry]

        mock_load_json.return_value = {
            "name": theme_name,
            "images": {"Escort": "Skins/Escort.png"}
        }

        # All paths exist
        mock_exists.return_value = True

        # Create distinct surfaces to verify caching
        ship_surface = pygame.Surface((50, 50))
        portrait_surface = pygame.Surface((200, 300))

        def load_side_effect(path):
            if "Portrait" in path:
                return portrait_surface
            return ship_surface
        mock_load.side_effect = load_side_effect

        self.manager.initialize()

        # First call loads from disk
        result1 = self.manager.get_portrait_image(theme_name, ship_class)
        # Verify it loaded a portrait (size matches)
        assert result1.get_size() == (200, 300)

        # Second call returns cached version (no additional load calls)
        initial_call_count = mock_load.call_count
        result2 = self.manager.get_portrait_image(theme_name, ship_class)
        assert result2 is result1
        assert mock_load.call_count == initial_call_count  # No additional loads

    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    def test_falls_back_to_default_theme(self, mock_exists):
        """get_portrait_image falls back to default theme for unknown theme."""
        # Portrait doesn't exist for the default theme fallback
        mock_exists.return_value = False

        # Manually mark discovery complete with empty theme data
        self.manager.discovery_complete = True
        self.manager.theme_data = {}

        # Should not crash, returns None (no theme data to fall back to)
        result = self.manager.get_portrait_image("UnknownTheme", "Escort")
        assert result is None
