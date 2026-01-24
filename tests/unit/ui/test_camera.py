"""Tests for Camera class viewport and coordinate transformations."""
import pytest
import sys
import os
import pygame


from game.ui.renderer.camera import Camera


class MockTarget:
    """Mock object with position for camera following."""
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.is_alive = True


class TestCameraBasics:
    """Test basic camera initialization and properties."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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


class TestCameraFitObjects:
    """Test camera fit_objects functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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
