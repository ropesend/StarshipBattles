"""Unit tests for ShipThemeManager logic (PROJ-314 schema).

The legacy portrait filename convention and the
`_ship_class_to_portrait_name()` parser were both deleted in PROJ-314
Phase 3; portrait paths now come from the theme.json `assets:` block.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.assets import (
    ShipThemeManager,
    get_default_ship_theme_manager,
    set_default_ship_theme_manager,
)


def _theme_json(name: str = "TestTheme") -> dict:
    """Build a minimal new-schema theme.json payload for mocked tests."""
    return {
        "schema_version": 1,
        "name": name,
        "description": "Test theme",
        "image_sizes": {"skin": [2048, 2048], "portrait": [2048, 2048]},
        "assets": {
            "Battleship": {
                "skin": "skins/battleship.png",
                "portrait": "portraits/battleship.png",
                "scale": 1.0,
            },
            "Escort": {
                "skin": "skins/escort.png",
                "portrait": "portraits/escort.png",
                "scale": 1.5,
            },
        },
    }


class TestShipThemeLogic:
    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.set_mode((1, 1))
        set_default_ship_theme_manager(ShipThemeManager())
        self.manager = get_default_ship_theme_manager()
        yield
        patch.stopall()
        set_default_ship_theme_manager(ShipThemeManager())

    def test_instance_management(self):
        """get_default_ship_theme_manager returns same instance, direct construction creates new."""
        instance1 = get_default_ship_theme_manager()
        instance2 = get_default_ship_theme_manager()
        assert instance1 is instance2
        instance3 = ShipThemeManager()
        assert instance1 is not instance3

    def test_fallback_generation(self):
        """Fallback image is a 100x100 Surface."""
        fallback = self.manager._create_fallback_image("UnknownClass")
        assert isinstance(fallback, pygame.Surface)
        assert fallback.get_size() == (100, 100)

    def test_load_image_fallback_behavior(self):
        """load_image returns fallback when not loaded or theme missing."""
        img = self.manager.load_image("AnyTheme", "AnyClass")
        assert img.get_size() == (100, 100)

        self.manager.discovery_complete = True
        img = self.manager.load_image("NonExistentTheme", "AnyClass")
        assert img.get_size() == (100, 100)

    @patch('game.ui.assets.ship_theme_manager.logger')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_manual_scaling_and_loading(
        self, mock_load, mock_load_json, mock_exists, mock_scandir, mock_logger,
    ):
        """A theme with `scale: 1.5` registers and exposes that scale via get_manual_scale."""
        json_content = _theme_json("ScaledTheme")
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/ScaledTheme"
        mock_entry.name = "ScaledTheme"
        mock_scandir.return_value = [mock_entry]
        mock_exists.return_value = True
        mock_load_json.return_value = json_content
        mock_load.return_value = pygame.Surface((50, 50))

        self.manager.initialize()

        mock_logger.error.assert_not_called()
        assert self.manager.get_manual_scale("ScaledTheme", "Escort") == 1.5
        assert self.manager.get_manual_scale("ScaledTheme", "Battleship") == 1.0
        # Unknown ship class falls back to 1.0.
        assert self.manager.get_manual_scale("ScaledTheme", "UnknownClass") == 1.0

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_get_image_metrics(
        self, mock_load, mock_load_json, mock_exists, mock_scandir,
    ):
        """Bounding rect is calculated from the loaded skin Surface."""
        json_content = _theme_json("MetricsTheme")
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/MetricsTheme"
        mock_entry.name = "MetricsTheme"
        mock_scandir.return_value = [mock_entry]
        mock_exists.return_value = True
        mock_load_json.return_value = json_content

        surf = MagicMock(spec=pygame.Surface)
        surf.get_bounding_rect.side_effect = lambda *a, **k: pygame.Rect(5, 5, 10, 10)
        surf.convert_alpha.return_value = surf
        surf.get_size.return_value = (20, 20)
        mock_load.return_value = surf

        self.manager.initialize()
        rect = self.manager.get_image_metrics("MetricsTheme", "Battleship")
        assert rect is not None
        assert rect.x == 5
        assert rect.width == 10

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    def test_malformed_theme_json(self, mock_load_json, mock_exists, mock_scandir):
        """Malformed (None) theme.json is silently skipped."""
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/BadTheme"
        mock_scandir.return_value = [mock_entry]
        mock_exists.return_value = True
        mock_load_json.return_value = None

        self.manager.initialize()
        assert len(self.manager.theme_data) == 0

    @patch('game.ui.assets.ship_theme_manager.logger')
    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    def test_legacy_images_schema_rejected(
        self, mock_load_json, mock_exists, mock_scandir, mock_logger,
    ):
        """PROJ-314: a theme.json with the old `images:` block does NOT register."""
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/LegacyTheme"
        mock_entry.name = "LegacyTheme"
        mock_scandir.return_value = [mock_entry]
        mock_exists.return_value = True
        mock_load_json.return_value = {
            "name": "LegacyTheme",
            "images": {"Battleship": "skins/battleship.png"},
        }

        self.manager.initialize()

        assert "LegacyTheme" not in self.manager.theme_data
        # Loader emits an error pointing to PROJ-314.
        assert any(
            "PROJ-314" in str(call.args[0]) or "assets" in str(call.args[0]).lower()
            for call in mock_logger.error.call_args_list
        )


class TestGetPortraitImage:
    """PROJ-314: get_portrait_image always returns a Surface (no None)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.set_mode((1, 1))
        set_default_ship_theme_manager(ShipThemeManager())
        self.manager = get_default_ship_theme_manager()
        yield
        patch.stopall()
        set_default_ship_theme_manager(ShipThemeManager())

    def test_returns_fallback_when_not_initialized(self):
        """Before discovery completes, get_portrait_image returns the synthetic fallback."""
        result = self.manager.get_portrait_image("AnyTheme", "AnyClass")
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (100, 100)

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_returns_fallback_for_missing_portrait_file(
        self, mock_load, mock_load_json, mock_exists, mock_scandir,
    ):
        """When `portrait` is declared but the file is absent, fallback Surface is returned."""
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/TestTheme"
        mock_entry.name = "TestTheme"
        mock_scandir.return_value = [mock_entry]
        mock_load_json.return_value = _theme_json("TestTheme")

        # Skin exists; portrait does not.
        def exists_side_effect(path: str) -> bool:
            if "Portrait" in path or "portrait" in path:
                return False
            return True
        mock_exists.side_effect = exists_side_effect
        mock_load.return_value = pygame.Surface((50, 50))

        self.manager.initialize()
        result = self.manager.get_portrait_image("TestTheme", "Battleship")
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (100, 100)

    @patch('game.ui.assets.ship_theme_manager.os.scandir')
    @patch('game.ui.assets.ship_theme_manager.os.path.exists')
    @patch('game.ui.assets.ship_theme_manager.load_json')
    @patch('game.ui.assets.ship_theme_manager.pygame.image.load')
    def test_loads_and_caches_portrait(
        self, mock_load, mock_load_json, mock_exists, mock_scandir,
    ):
        """get_portrait_image loads the declared portrait file and caches it."""
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = "/themes/TestTheme"
        mock_entry.name = "TestTheme"
        mock_scandir.return_value = [mock_entry]
        mock_load_json.return_value = _theme_json("TestTheme")
        mock_exists.return_value = True

        ship_surface = pygame.Surface((50, 50))
        portrait_surface = pygame.Surface((200, 300))

        def load_side_effect(path):
            if "Portrait" in path or "portrait" in path:
                return portrait_surface
            return ship_surface
        mock_load.side_effect = load_side_effect

        self.manager.initialize()
        first = self.manager.get_portrait_image("TestTheme", "Escort")
        assert first.get_size() == (200, 300)

        load_count = mock_load.call_count
        again = self.manager.get_portrait_image("TestTheme", "Escort")
        assert again is first
        assert mock_load.call_count == load_count

    def test_falls_back_to_default_theme_then_synthetic(self):
        """Unknown theme falls back to default; if default has no data, synthetic Surface returned."""
        self.manager.discovery_complete = True
        self.manager.theme_data = {}
        result = self.manager.get_portrait_image("UnknownTheme", "Escort")
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (100, 100)
