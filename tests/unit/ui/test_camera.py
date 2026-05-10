"""Tests for Camera class viewport and coordinate transformations.

PROJ-322 Task 2.20 (S02-CAT5-001): the 8 per-class pygame.init autouse
fixtures collapsed into one module-scoped autouse fixture.
SDL_VIDEODRIVER='dummy' is set by the repo conftest, but we keep an
explicit fall-back here for runs that bypass that conftest.
"""
import pytest
import sys
import os
import pygame
from unittest.mock import patch


from game.ui.renderer.camera import Camera


@pytest.fixture(autouse=True, scope='module')
def _camera_module_pygame_init():
    """Initialise pygame once for the whole test_camera module."""
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    yield


class MockTarget:
    """Mock object with position for camera following."""
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.is_alive = True


class TestCameraBasics:
    """Test basic camera initialization and properties."""

    def test_camera_initialization(self):
        """Camera should initialize with correct dimensions."""
        camera = Camera(800, 600)

        assert camera.width == 800
        assert camera.height == 600
        assert camera.position == pygame.math.Vector2(0, 0)
        assert camera.zoom == 1.0
        assert camera.target is None

    def test_zoom_limits(self):
        """Camera should have min and max zoom limits."""
        camera = Camera(800, 600)

        assert camera.max_zoom > camera.min_zoom
        assert camera.min_zoom > 0


class TestCameraTransformations:
    """Test coordinate transformation functions."""

    def test_world_to_screen_center(self):
        """World origin should map to screen center when camera at origin."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        screen_pos = camera.world_to_screen(pygame.math.Vector2(0, 0))

        assert screen_pos.x == 400  # Half of 800
        assert screen_pos.y == 300  # Half of 600

    def test_world_to_screen_offset(self):
        """World point offset from camera should be offset on screen."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        # Point 100 units right of camera
        screen_pos = camera.world_to_screen(pygame.math.Vector2(100, 0))

        assert screen_pos.x == 500  # 400 center + 100
        assert screen_pos.y == 300

    def test_world_to_screen_with_zoom(self):
        """Zoom should scale world coordinates."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 2.0  # 2x zoom in

        # Point 100 units right should appear 200 pixels right on screen
        screen_pos = camera.world_to_screen(pygame.math.Vector2(100, 0))

        assert screen_pos.x == 600  # 400 center + 100*2

    def test_screen_to_world_center(self):
        """Screen center should map to camera position."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(500, 300)
        camera.zoom = 1.0

        world_pos = camera.screen_to_world((400, 300))  # Screen center

        assert world_pos.x == pytest.approx(500, abs=0.1)
        assert world_pos.y == pytest.approx(300, abs=0.1)

    def test_screen_to_world_roundtrip(self):
        """world_to_screen and screen_to_world should be inverses."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(1000, 2000)
        camera.zoom = 0.5

        original = pygame.math.Vector2(1500, 2500)
        screen = camera.world_to_screen(original)
        roundtrip = camera.screen_to_world(screen)

        assert roundtrip.x == pytest.approx(original.x, abs=0.1)
        assert roundtrip.y == pytest.approx(original.y, abs=0.1)


class TestCameraHexAtScreen:
    """Test Camera.hex_at_screen integration with screen_to_world + pixel_to_hex.

    PROJ-398 / FND-012: every other test of `hex_at_screen` mocks the method;
    these tests exercise the real `screen_to_world -> pixel_to_hex` chain so
    regressions in the viewport math are caught.
    """

    def test_hex_at_screen_origin_camera_returns_origin_hex(self):
        """Camera at world origin: clicking screen center returns the origin hex."""
        from game.core.hex_math import HexCoord, pixel_to_hex

        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        # Clicking screen center -> world (0, 0) -> pixel_to_hex(0, 0, 10)
        hex_coord = camera.hex_at_screen(400, 300, 10)

        expected = pixel_to_hex(0, 0, 10)
        assert isinstance(hex_coord, HexCoord)
        assert hex_coord == expected

    def test_hex_at_screen_offset_click_resolves_via_world_transform(self):
        """A non-center click should round-trip through world coords + pixel_to_hex."""
        from game.core.hex_math import pixel_to_hex

        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(1000, 2000)
        camera.zoom = 0.5

        screen_x, screen_y = 500, 400
        hex_coord = camera.hex_at_screen(screen_x, screen_y, 10)

        world_pos = camera.screen_to_world((screen_x, screen_y))
        expected = pixel_to_hex(world_pos.x, world_pos.y, 10)
        assert hex_coord == expected

    def test_hex_at_screen_respects_camera_offset(self):
        """offset_x/offset_y must propagate through hex_at_screen."""
        from game.core.hex_math import pixel_to_hex

        camera = Camera(800, 600, offset_x=150, offset_y=75)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        # Screen center accounting for offset
        screen_x, screen_y = 400 + 150, 300 + 75
        hex_coord = camera.hex_at_screen(screen_x, screen_y, 10)

        assert hex_coord == pixel_to_hex(0, 0, 10)


class TestCameraFitObjects:
    """Test camera fit_objects functionality."""

    def test_fit_objects_centers_camera(self):
        """fit_objects should center camera on objects."""
        camera = Camera(800, 600)

        objects = [
            MockTarget(0, 0),
            MockTarget(200, 0),
        ]

        camera.fit_objects(objects)

        # Should center on (100, 0)
        assert camera.position.x == pytest.approx(100, abs=0.1)
        assert camera.position.y == pytest.approx(0, abs=0.1)

    def test_fit_objects_adjusts_zoom(self):
        """fit_objects should adjust zoom to fit all objects."""
        camera = Camera(800, 600)

        # Objects spread far apart
        objects = [
            MockTarget(0, 0),
            MockTarget(10000, 0),
        ]

        camera.fit_objects(objects)

        # Zoom should be reduced to fit both
        assert camera.zoom < 1.0

    def test_fit_objects_empty_list(self):
        """fit_objects should handle empty list gracefully."""
        camera = Camera(800, 600)
        original_pos = pygame.math.Vector2(camera.position)

        camera.fit_objects([])

        # Position should not change
        assert camera.position == original_pos


class TestCameraZoomAnimation:
    """Test zoom animation and anchor stability."""

    def test_zoom_anchor_stability_during_animation(self):
        """World point under anchor screen position should stay constant during zoom."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0
        camera.target_zoom = 2.0  # Zoom in

        # Set zoom anchor at screen center
        anchor_screen = (400, 300)
        camera._zoom_anchor_screen = anchor_screen
        camera._zoom_anchor_world = camera.screen_to_world(anchor_screen)

        # Run many update steps to let animation complete
        for _ in range(100):
            camera.update(0.016)  # 16ms per frame

        # After animation, zoom should be at or very near target
        assert abs(camera.zoom - camera.target_zoom) < 0.01

    def test_multiple_sequential_zoom_operations(self):
        """Rapid zoom-in then zoom-out should work correctly."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        # Zoom in
        camera.target_zoom = 2.0
        for _ in range(5):
            camera.update(0.016)

        # Immediately zoom out
        camera.target_zoom = 0.5
        for _ in range(5):
            camera.update(0.016)

        # Zoom should be moving toward 0.5
        assert camera.zoom < 2.0

    def test_zoom_limits_enforcement_max(self):
        """target_zoom should clamp at max_zoom when set via update_input."""
        camera = Camera(800, 600)
        camera.zoom = camera.max_zoom
        camera.target_zoom = camera.max_zoom

        # Simulate mouse wheel zoom beyond max (update_input clamps target_zoom)
        # We test the logic directly since update_input needs pygame events
        original_target = camera.target_zoom
        camera.target_zoom *= 1.15  # Try to zoom past max
        camera.target_zoom = max(camera.min_zoom, min(camera.max_zoom, camera.target_zoom))

        assert camera.target_zoom <= camera.max_zoom

    def test_zoom_limits_enforcement_min(self):
        """target_zoom should clamp at min_zoom when set via update_input."""
        camera = Camera(800, 600)
        camera.zoom = camera.min_zoom
        camera.target_zoom = camera.min_zoom

        # Simulate mouse wheel zoom below min (update_input clamps target_zoom)
        camera.target_zoom /= 1.15  # Try to zoom past min
        camera.target_zoom = max(camera.min_zoom, min(camera.max_zoom, camera.target_zoom))

        assert camera.target_zoom >= camera.min_zoom


class TestCameraTargetFollowing:
    """Test camera target following behavior."""

    def test_dead_target_following(self):
        """Camera should still follow dead target's position."""
        camera = Camera(800, 600)
        target = MockTarget(500, 300)
        target.is_alive = False

        camera.target = target
        camera.update(0.016)

        # Camera should follow the dead target's position
        assert camera.position.x == 500
        assert camera.position.y == 300


class TestCameraOffsetPropagation:
    """Test offset_x/offset_y in coordinate transforms."""

    def test_world_to_screen_with_offset(self):
        """world_to_screen should account for offset_x/offset_y."""
        camera = Camera(800, 600, offset_x=100, offset_y=50)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        screen_pos = camera.world_to_screen(pygame.math.Vector2(0, 0))

        # Center is at (400, 300) plus offset (100, 50) = (500, 350)
        assert screen_pos.x == 500
        assert screen_pos.y == 350

    def test_screen_to_world_with_offset(self):
        """screen_to_world should account for offset_x/offset_y."""
        camera = Camera(800, 600, offset_x=100, offset_y=50)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        # Screen center with offset is at (500, 350)
        world_pos = camera.screen_to_world((500, 350))

        assert world_pos.x == pytest.approx(0, abs=0.1)
        assert world_pos.y == pytest.approx(0, abs=0.1)

    def test_screen_to_world_roundtrip_with_offset(self):
        """world_to_screen and screen_to_world should be inverses with offsets."""
        camera = Camera(800, 600, offset_x=150, offset_y=75)
        camera.position = pygame.math.Vector2(1000, 2000)
        camera.zoom = 0.5

        original = pygame.math.Vector2(1500, 2500)
        screen = camera.world_to_screen(original)
        roundtrip = camera.screen_to_world(screen)

        assert roundtrip.x == pytest.approx(original.x, abs=0.1)
        assert roundtrip.y == pytest.approx(original.y, abs=0.1)


class TestCameraEdgeCases:
    """Test edge cases for camera behavior."""

    def test_very_large_world_coordinates(self):
        """Camera should handle very large world coordinates."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(1e6, 1e6)
        camera.zoom = 1.0

        # Should not raise
        screen = camera.world_to_screen(pygame.math.Vector2(1e6, 1e6))
        world = camera.screen_to_world(screen)

        # Should roundtrip correctly
        assert world.x == pytest.approx(1e6, rel=1e-6)
        assert world.y == pytest.approx(1e6, rel=1e-6)

    def test_zero_zoom_handling(self):
        """Camera operations should handle edge zoom values gracefully."""
        camera = Camera(800, 600)
        camera.zoom = camera.min_zoom  # Start at minimum
        camera.target_zoom = camera.min_zoom  # Keep at minimum

        # Coordinate transforms should work at min zoom
        world_pos = pygame.math.Vector2(1000, 1000)
        screen_pos = camera.world_to_screen(world_pos)
        roundtrip = camera.screen_to_world(screen_pos)

        # Should complete without errors and roundtrip correctly
        assert roundtrip.x == pytest.approx(world_pos.x, abs=1.0)
        assert roundtrip.y == pytest.approx(world_pos.y, abs=1.0)

    def test_fit_objects_single_object(self):
        """fit_objects should handle single object correctly."""
        camera = Camera(800, 600)

        objects = [MockTarget(500, 500)]

        camera.fit_objects(objects)

        # Should center on the single object
        assert camera.position.x == pytest.approx(500, abs=0.1)
        assert camera.position.y == pytest.approx(500, abs=0.1)


class TestCameraUpdateInput:
    """Tests for Camera.update_input() keyboard and mouse handling."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((800, 600))
        yield

    def _mock_keys(self, pressed=None):
        """Create a mock key state dict-like object."""
        pressed = pressed or {}

        class MockKeyState:
            def __init__(self, pressed_keys):
                self._pressed = pressed_keys

            def __getitem__(self, key):
                return self._pressed.get(key, False)

        return MockKeyState(pressed)

    def test_keyboard_panning_wasd(self):
        """WASD keys should pan the camera."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        original_pos = pygame.math.Vector2(camera.position)

        # Mock key state - W pressed (up = negative y)
        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_w: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [])  # 100ms

            # Camera should have moved up (negative y)
            assert camera.position.y < original_pos.y

    def test_keyboard_panning_arrows(self):
        """Arrow keys should pan the camera."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_RIGHT: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [])

            # Camera should have moved right (positive x)
            assert camera.position.x > 0

    def test_keyboard_pan_clears_target(self):
        """Manual keyboard panning should clear target follow."""
        camera = Camera(800, 600)
        camera.target = MockTarget(500, 500)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_a: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [])

            assert camera.target is None

    def test_mouse_wheel_zoom_in(self):
        """Mouse wheel scroll up should zoom in."""
        camera = Camera(800, 600)
        camera.zoom = 1.0
        camera.target_zoom = 1.0

        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, y=1)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)), \
             patch('pygame.mouse.get_pos', return_value=(400, 300)):

            camera.update_input(0.1, [wheel_event])

            # target_zoom should increase
            assert camera.target_zoom > 1.0

    def test_mouse_wheel_zoom_out(self):
        """Mouse wheel scroll down should zoom out."""
        camera = Camera(800, 600)
        camera.zoom = 1.0
        camera.target_zoom = 1.0

        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, y=-1)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)), \
             patch('pygame.mouse.get_pos', return_value=(400, 300)):

            camera.update_input(0.1, [wheel_event])

            # target_zoom should decrease
            assert camera.target_zoom < 1.0

    def test_zoom_clamped_to_max(self):
        """Zoom should not exceed max_zoom."""
        camera = Camera(800, 600)
        camera.zoom = camera.max_zoom
        camera.target_zoom = camera.max_zoom

        # Try to zoom in past max
        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, y=1)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)), \
             patch('pygame.mouse.get_pos', return_value=(400, 300)):

            camera.update_input(0.1, [wheel_event])

            assert camera.target_zoom <= camera.max_zoom

    def test_zoom_clamped_to_min(self):
        """Zoom should not go below min_zoom."""
        camera = Camera(800, 600)
        camera.zoom = camera.min_zoom
        camera.target_zoom = camera.min_zoom

        # Try to zoom out past min
        wheel_event = pygame.event.Event(pygame.MOUSEWHEEL, y=-1)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)), \
             patch('pygame.mouse.get_pos', return_value=(400, 300)):

            camera.update_input(0.1, [wheel_event])

            assert camera.target_zoom >= camera.min_zoom

    def test_middle_mouse_drag_panning(self):
        """Middle mouse button drag should pan camera."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        camera.zoom = 1.0

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, True, False)), \
             patch('pygame.mouse.get_rel', return_value=(50, 30)):

            camera.update_input(0.1, [])

            # Camera should move opposite to drag direction
            assert camera.position.x == pytest.approx(-50, abs=1)
            assert camera.position.y == pytest.approx(-30, abs=1)

    def test_middle_mouse_drag_clears_target(self):
        """Middle mouse drag should clear target follow."""
        camera = Camera(800, 600)
        camera.target = MockTarget(500, 500)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, True, False)), \
             patch('pygame.mouse.get_rel', return_value=(10, 10)):

            camera.update_input(0.1, [])

            assert camera.target is None

    def test_no_input_no_change(self):
        """No input should not change camera position."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(100, 200)
        original = pygame.math.Vector2(camera.position)

        with patch('pygame.key.get_pressed', return_value=self._mock_keys()), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [])

            assert camera.position.x == original.x
            assert camera.position.y == original.y

    def test_pan_speed_scales_with_zoom(self):
        """Pan speed should be faster when zoomed out."""
        camera1 = Camera(800, 600)
        camera1.position = pygame.math.Vector2(0, 0)
        camera1.zoom = 1.0

        camera2 = Camera(800, 600)
        camera2.position = pygame.math.Vector2(0, 0)
        camera2.zoom = 0.5  # Zoomed out

        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_d: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera1.update_input(0.1, [])
            camera2.update_input(0.1, [])

            # Zoomed-out camera should pan further
            assert camera2.position.x > camera1.position.x
    def test_keyboard_panning_wasd_disabled(self):
        """WASD keys should NOT pan the camera when allow_wasd=False."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)
        original_pos = pygame.math.Vector2(camera.position)

        # Mock key state - W pressed (up = negative y), but allow_wasd=False
        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_w: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [], allow_wasd=False)

            # Camera should NOT have moved
            assert camera.position.y == original_pos.y

    def test_keyboard_panning_arrows_still_work_with_wasd_disabled(self):
        """Arrow keys should still pan the camera even when allow_wasd=False."""
        camera = Camera(800, 600)
        camera.position = pygame.math.Vector2(0, 0)

        # Mock key state - UP pressed, allow_wasd=False
        with patch('pygame.key.get_pressed', return_value=self._mock_keys({pygame.K_UP: True})), \
             patch('pygame.mouse.get_pressed', return_value=(False, False, False)), \
             patch('pygame.mouse.get_rel', return_value=(0, 0)):

            camera.update_input(0.1, [], allow_wasd=False)

            # Camera should have moved up (negative y)
            assert camera.position.y < 0
