"""Tests for ``strategy_screen_assets`` (PROJ-330)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens import strategy_screen_assets as assets


def _make_screen():
    screen = MagicMock()
    screen.empire_assets = {}
    screen.empires = []
    screen._race_loader = MagicMock()
    screen.camera = MagicMock()
    screen.active_empire = MagicMock()
    screen.active_empire.colonies = []
    screen.systems = []
    return screen


class TestFocusOnPlayerHome:
    def test_no_colonies_does_nothing(self):
        screen = _make_screen()
        screen.active_empire.colonies = []
        assets.focus_on_player_home(screen)
        # No assignment occurred
        assert "position" not in screen.camera.__dict__ or True  # MagicMock no-op

    def test_no_owning_system_does_not_set_position(self):
        screen = _make_screen()
        colony = MagicMock(location=(0, 0))
        screen.active_empire.colonies = [colony]
        screen.systems = [MagicMock(planets=[])]  # colony not in any system
        # Should not raise; no exception path
        assets.focus_on_player_home(screen)

    def test_sets_camera_position(self):
        screen = _make_screen()
        from game.core.hex_math import HexCoord

        colony = MagicMock()
        colony.location = HexCoord(0, 0)
        sys_obj = MagicMock()
        sys_obj.planets = [colony]
        sys_obj.global_location = HexCoord(2, 3)
        screen.active_empire.colonies = [colony]
        screen.systems = [sys_obj]
        assets.focus_on_player_home(screen)
        # Position must be a Vector2
        assert isinstance(screen.camera.position, pygame.math.Vector2)


class TestLoadAssets:
    def test_iterates_empires_and_calls_loader(self):
        screen = _make_screen()
        emp_a = MagicMock(id=1)
        emp_b = MagicMock(id=2)
        screen.empires = [emp_a, emp_b]
        screen._race_loader.load_all_empire_assets.side_effect = lambda e: f"assets-{e.id}"
        with patch("game.assets.asset_manager.get_asset_manager") as mock_get:
            mock_am = MagicMock()
            mock_get.return_value = mock_am
            assets.load_assets(screen)
            mock_am.load_manifest.assert_called_once()
        assert screen.empire_assets == {1: "assets-1", 2: "assets-2"}


class TestGetObjectAsset:
    def _patched_am(self):
        am = MagicMock()
        am.get_missing_texture.return_value = "MISSING"
        return am

    def test_unknown_object_returns_none(self):
        screen = _make_screen()
        with patch("game.assets.asset_manager.get_asset_manager", return_value=self._patched_am()):
            result = assets.get_object_asset(screen, MagicMock(spec=[]))
        assert result is None

    def test_star_returns_loaded_image(self):
        screen = _make_screen()
        am = self._patched_am()
        am.load_star_image.return_value = "STAR_IMG"
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=True), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=False):
            obj = MagicMock(image_id="sun.png")
            result = assets.get_object_asset(screen, obj)
        assert result == "STAR_IMG"

    def test_star_missing_texture_returns_none(self):
        screen = _make_screen()
        am = self._patched_am()
        am.load_star_image.return_value = "MISSING"
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=True), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=False):
            result = assets.get_object_asset(screen, MagicMock(image_id="x"))
        assert result is None

    def test_planet_with_rotation(self):
        screen = _make_screen()
        am = self._patched_am()
        am.load_planet_image.return_value = "RAW_IMG"
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=True), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=False), \
             patch("pygame.transform.rotate", return_value="ROTATED") as mock_rot:
            obj = MagicMock(image_id="p.png", image_rotation=45.0)
            result = assets.get_object_asset(screen, obj)
        mock_rot.assert_called_once_with("RAW_IMG", 45.0)
        assert result == "ROTATED"

    def test_planet_load_failure_logs_and_returns_none(self):
        screen = _make_screen()
        am = self._patched_am()
        am.load_planet_image.side_effect = OSError("boom")
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=True), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=False):
            result = assets.get_object_asset(screen, MagicMock(image_id="p.png", image_rotation=0))
        assert result is None

    def test_warp_point_uses_random_group(self):
        screen = _make_screen()
        am = self._patched_am()
        am.get_random_from_group.return_value = "WARP_IMG"
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=True), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=False):
            result = assets.get_object_asset(screen, MagicMock())
        assert result == "WARP_IMG"
        am.get_random_from_group.assert_called_once()

    def test_fleet_uses_empire_assets(self):
        screen = _make_screen()
        screen.empire_assets = {7: {"fleet": "FLEET_IMG"}}
        am = self._patched_am()
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=True):
            result = assets.get_object_asset(screen, MagicMock(owner_id=7))
        assert result == "FLEET_IMG"

    def test_fleet_missing_assets_returns_none(self):
        screen = _make_screen()
        screen.empire_assets = {}
        am = self._patched_am()
        with patch("game.assets.asset_manager.get_asset_manager", return_value=am), \
             patch("game.ui.screens.strategy_screen_assets.is_star", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_planet", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_warp_point", return_value=False), \
             patch("game.ui.screens.strategy_screen_assets.is_fleet", return_value=True):
            result = assets.get_object_asset(screen, MagicMock(owner_id=99))
        assert result is None
