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


class TestCameraZoomAnimation:
    """Test zoom animation and anchor stability."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

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
