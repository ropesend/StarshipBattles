"""Tests for the Camera class."""
import pytest
import pygame
from game.ui.renderer.camera import Camera

class MockEvent:
    def __init__(self, type, y=0):
        self.type = type
        self.y = y

def test_screen_to_world_conversion():
    """Verify screen coordinates map correctly to world coordinates."""
    # Camera 800x600, centered at (0,0) world
    camera = Camera(800, 600)
    camera.position = pygame.math.Vector2(0, 0)
    camera.zoom = 1.0
    
    # Center of screen (400, 300) should be (0, 0) world
    screen_center = pygame.math.Vector2(400, 300)
    world_pos = camera.screen_to_world(screen_center)
    assert world_pos.x == 0
    assert world_pos.y == 0
    
    # Top Left (0, 0) screen
    # Offset from center is (-400, -300)
    # World should be (-400, -300)
    screen_tl = pygame.math.Vector2(0, 0)
    world_tl = camera.screen_to_world(screen_tl)
    assert world_tl.x == -400
    assert world_tl.y == -300

def test_world_to_screen_conversion():
    """Verify world coordinates map correctly to screen coordinates."""
    camera = Camera(800, 600)
    camera.position = pygame.math.Vector2(100, 50) # Camera centered at 100, 50
    camera.zoom = 2.0
    
    # World Point at (100, 50) should be at screen center (400, 300)
    world_pt = pygame.math.Vector2(100, 50)
    screen_pt = camera.world_to_screen(world_pt)
    assert screen_pt.x == 400
    assert screen_pt.y == 300
    
    # World Point at (110, 50) -> +10 units X
    # Zoom 2.0 -> +20 pixels X -> Screen (420, 300)
    world_right = pygame.math.Vector2(110, 50)
    screen_right = camera.world_to_screen(world_right)
    assert screen_right.x == 420
    assert screen_right.y == 300

def test_zoom_centers_on_mouse_simulation():
    """Mouse-centered zoom invariant: after zoom + adjust, the world point
    under the mouse stays the same.

    PROJ-494 T4.8: was 29-line inline derivation with intermediate "explain
    the math" comments. Reduced to (1) pre-computed expected constants from
    the engineering notes archived in PROJ-XX, plus (2) the invariant the
    code under test must preserve.

    Pre-computed engineering values for the (800×600 viewport, mouse at
    (600, 300), zoom 1.0 → 2.0) case:
    - Pre-zoom world point under mouse: (200, 0)
    - Camera target position to preserve invariant: (100, 0)
    """
    camera = Camera(800, 600)
    camera.position = pygame.math.Vector2(0, 0)
    camera.zoom = 1.0
    mouse_screen = (600, 300)

    EXPECTED_WORLD_BEFORE = pygame.math.Vector2(200, 0)
    EXPECTED_CAMERA_POS_AFTER = pygame.math.Vector2(100, 0)

    # Capture world point under mouse before zoom.
    world_before = camera.screen_to_world(mouse_screen)
    assert world_before == EXPECTED_WORLD_BEFORE

    # Apply zoom and shift camera to preserve the invariant.
    camera.zoom = 2.0
    diff = world_before - camera.screen_to_world(mouse_screen)
    camera.position += diff

    # The world point under the mouse must be unchanged by zoom + adjust.
    final_world = camera.screen_to_world(mouse_screen)
    assert final_world == EXPECTED_WORLD_BEFORE
    assert camera.position.x == EXPECTED_CAMERA_POS_AFTER.x
