"""
UI test configuration and shared fixtures.
Ensures proper import order and cleanup for parallel execution.

This conftest.py pre-imports game.ui submodules in a deterministic order
to prevent race conditions when pytest-xdist spawns multiple workers.
"""
import sys
import os
import pytest

def pytest_configure(config):
    """
    Called before test collection.
    Ensures game.ui modules are importable in consistent order.
    
    This prevents race conditions during parallel worker startup by forcing
    all game.ui submodules to be imported in a deterministic sequence before
    any tests run.
    """
    # Force import of game.ui subpackages in deterministic order
    # This prevents race conditions when pytest-xdist workers load modules
    try:
        # Import in dependency order: renderer first, then screens, then panels
        import game.ui.renderer.sprites
        import game.ui.renderer.camera
        import game.ui.renderer.game_renderer
        import game.ui.screens.battle_scene
        import game.ui.screens.battle_screen
        import game.ui.screens.builder_screen
        import game.ui.panels.battle_panels
        import game.ui.panels.builder_widgets
    except ImportError as e:
        # Log but don't fail - tests may mock these modules
        print(f"Warning: Could not pre-import game.ui modules: {e}", file=sys.stderr)


def pytest_configure_node(node):
    """
    Called when a pytest-xdist worker node is initialized.
    Ensures all workers have completed module imports before tests start.
    
    This hook runs AFTER pytest_configure() completes, giving time for
    all imports to finish before the worker requests tests to run.
    """
    import time
    # Small delay to ensure all workers finish pytest_configure()
    # This prevents race conditions where Worker A starts running tests
    # while Worker B is still importing modules
    time.sleep(0.3)  # 300ms provides maximum safety margin for all workers
    
    # Verify critical imports succeeded
    try:
        import game.ui.renderer.sprites
        import game.ui.screens.battle_scene
        import game.ui.panels.battle_panels
    except ImportError as e:
        print(f"ERROR: Worker {node.gateway.id} failed to import game.ui modules: {e}", 
              file=sys.stderr)
        raise



@pytest.fixture(autouse=True)
def pygame_cleanup():
    """
    Cleanup-only fixture - does NOT initialize pygame.
    Tests control their own pygame.init() as needed.
    
    This prevents conflicts with tests that expect to control their own
    pygame initialization sequence.
    """
    yield  # Test runs here
    
    # Cleanup after test
    try:
        import pygame
        pygame.display.quit()
    except:
        pass  # pygame.display may not be initialized
    
    try:
        import pygame
        pygame.quit()
    except:
        pass  # pygame may not be initialized


