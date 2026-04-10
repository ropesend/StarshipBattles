"""Tests for CameraNavigator - FEAT-04: center_on_hex for event log navigation."""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord, hex_to_pixel
from game.ui.screens.strategy_camera_nav import CameraNavigator


class MockScene:
    """Mock scene providing camera and hex_size for CameraNavigator."""

    def __init__(self, hex_size=50):
        self.camera = MagicMock()
        self.camera.position = MagicMock()
        self.camera.position.x = 0.0
        self.camera.position.y = 0.0
        self.hex_size = hex_size
        self.systems = []


class TestCenterOnHex:
    """Test CameraNavigator.center_on_hex for direct hex coordinate navigation."""

    def test_center_on_hex_sets_camera_position(self):
        """center_on_hex should set camera position to hex pixel coordinates."""
        scene = MockScene(hex_size=50)
        nav = CameraNavigator(scene)

        target = HexCoord(5, -3)
        nav.center_on_hex(target)

        expected_x, expected_y = hex_to_pixel(target, 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y

    def test_center_on_hex_origin(self):
        """center_on_hex at origin should set camera to (0, 0) pixel position."""
        scene = MockScene(hex_size=50)
        nav = CameraNavigator(scene)

        target = HexCoord(0, 0)
        nav.center_on_hex(target)

        assert scene.camera.position.x == 0.0
        assert scene.camera.position.y == 0.0
