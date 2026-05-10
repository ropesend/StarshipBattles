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
    """simulate the logic we WANT to implement: mouse-centered zoom."""
    camera = Camera(800, 600)
    camera.position = pygame.math.Vector2(0, 0)
    camera.zoom = 1.0
    
    # Mouse at (600, 300) -> Screen Right Center
    # At zoom 1.0, World pos is (200, 0)  [(600-400)/1 + 0]
    mouse_screen = (600, 300)
    
    # Goal: Zoom to 2.0, keeping World(200, 0) at Screen(600, 300)
    
    # 1. Get World Pos BEFORE Zoom
    world_before = camera.screen_to_world(mouse_screen)
    assert world_before.x == 200
    assert world_before.y == 0
    
    # 2. Apply New Zoom
    camera.zoom = 2.0
    
    # 3. Calculate where camera MUST be
    # New World(200, 0) -> Screen(600, 300)
    # screen_to_world(600, 300) = camera.pos + (offset / zoom)
    # 200 = camera.x + ((600 - 400) / 2.0)
    # 200 = camera.x + (200 / 2.0)
    # 200 = camera.x + 100
    # camera.x = 100
    
    # Implementation Logic check:
    # new_pos = old_pos + (mouse_world_offset * (1 - 1/zoom_factor))? 
    # Let's trust the invariant method:
    # Set camera such that screen_to_world(mouse) == world_before
    
    new_world_at_mouse = camera.screen_to_world(mouse_screen) 
    # Currently, without adjusting pos, center is still (0,0)
    # So new world at mouse is: 0 + (200) / 2 = 100.
    # We WANT it to be 200.
    # So we need to shift camera by (200 - 100) = +100.
    
    diff = world_before - new_world_at_mouse
    camera.position += diff
    
    # Verify
    final_world = camera.screen_to_world(mouse_screen)
    assert final_world.x == 200
    assert final_world.y == 0
    assert camera.position.x == 100
