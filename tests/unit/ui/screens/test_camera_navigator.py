"""Tests for CameraNavigator - FEAT-04: center_on_hex for event log navigation."""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord, hex_to_pixel
from game.ui.screens.strategy_camera_nav import CameraNavigator, ZOOM_KEYBOARD_STEP


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


class _ZoomScene:
    """Mock scene with a real-attribute camera for keyboard zoom step tests.

    MagicMock's auto-attributes don't behave well with arithmetic mutation,
    so we use a plain object exposing target_zoom / min_zoom / max_zoom.
    """

    def __init__(self, target_zoom: float = 1.0, min_zoom: float = 0.01, max_zoom: float = 5.0):
        camera = type("_Cam", (), {})()
        camera.target_zoom = target_zoom
        camera.min_zoom = min_zoom
        camera.max_zoom = max_zoom
        self.camera = camera
        self.hex_size = 50
        self.systems = []


class TestZoomInStep:
    """FEAT-21: keyboard zoom-in step on CameraNavigator."""

    def test_zoom_in_multiplies_target_zoom_by_step(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_in_step()

        assert scene.camera.target_zoom == pytest.approx(1.0 * ZOOM_KEYBOARD_STEP)

    def test_zoom_in_clamps_at_max_zoom(self):
        scene = _ZoomScene(target_zoom=4.9, max_zoom=5.0)
        nav = CameraNavigator(scene)

        # 4.9 * 1.5 = 7.35, must clamp to 5.0
        nav.zoom_in_step()
        assert scene.camera.target_zoom == 5.0

        # Repeated presses stay at max
        nav.zoom_in_step()
        assert scene.camera.target_zoom == 5.0


class TestZoomOutStep:
    """FEAT-21: keyboard zoom-out step on CameraNavigator."""

    def test_zoom_out_divides_target_zoom_by_step(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_out_step()

        assert scene.camera.target_zoom == pytest.approx(1.0 / ZOOM_KEYBOARD_STEP)

    def test_zoom_out_clamps_at_min_zoom(self):
        scene = _ZoomScene(target_zoom=0.012, min_zoom=0.01)
        nav = CameraNavigator(scene)

        # 0.012 / 1.5 = 0.008, must clamp to 0.01
        nav.zoom_out_step()
        assert scene.camera.target_zoom == 0.01

        # Repeated presses stay at min
        nav.zoom_out_step()
        assert scene.camera.target_zoom == 0.01


class TestZoomStepReversibility:
    """One zoom-in followed by one zoom-out returns to ~original target_zoom."""

    def test_in_then_out_returns_to_origin(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_in_step()
        nav.zoom_out_step()

        assert scene.camera.target_zoom == pytest.approx(1.0)
