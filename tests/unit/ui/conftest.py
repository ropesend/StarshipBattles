"""
UI test configuration and shared fixtures.

This conftest provides:
1. Pre-imports game.ui submodules in deterministic order (race condition prevention)
2. pygame_display_reset fixture for UI-specific display handling

Note: Basic pygame initialization is handled by enforce_headless in root conftest.py.
Test isolation (cleanup) is handled by reset_game_state in root conftest.py.
The pygame_display_reset fixture here handles UI-specific display mode reset.
"""
import sys
import pytest

from tests.fixtures.paths import (
    data_dir,
    project_root,
    unit_test_data_dir,
    assets_dir,
)  # noqa: F401


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
        import game.ui.screens.workshop_screen
        import game.ui.panels.battle_panels
        import game.ui.panels.builder_widgets
    except ImportError as e:
        # Log but don't fail - tests may mock these modules
        print(f"Warning: Could not pre-import game.ui modules: {e}", file=sys.stderr)


def pytest_configure_node(node):
    """
    Called when a pytest-xdist worker node is initialized.
    Verifies all critical imports succeeded before tests start.

    Note: The time.sleep(0.3) workaround was removed - it added 4.8s total
    overhead with 16 workers and didn't guarantee synchronization. The
    pytest_configure() hook already imports modules; this just verifies.
    """
    # Verify critical imports succeeded (they should be loaded by pytest_configure)
    try:
        import game.ui.renderer.sprites
        import game.ui.screens.battle_scene
        import game.ui.panels.battle_panels
    except ImportError as e:
        print(f"ERROR: Worker {node.gateway.id} failed to import game.ui modules: {e}",
              file=sys.stderr)
        raise


@pytest.fixture(autouse=True)
def pygame_display_reset():
    """
    Ensure pygame is initialized and display is reset for each UI test.

    This fixture:
    1. Initializes pygame if not already initialized (handles cases where
       earlier tests called pygame.quit())
    2. Sets up a headless display for tests that need surfaces
    3. Resets display state after each test

    IMPORTANT: Do NOT call pygame.quit() here - that would break subsequent tests.
    """
    import os
    import pygame

    # Ensure headless mode for CI/testing
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    # Initialize pygame if not already initialized
    # This is critical for sequential test runs where earlier tests may have quit pygame
    if not pygame.get_init():
        pygame.init()

    # Ensure display is initialized with a valid size
    if not pygame.display.get_init():
        pygame.display.init()

    # Set up a display surface (required for pygame_gui and Surface creation)
    try:
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass  # Display may not be available in some environments

    # Ensure pygame font subsystem is initialized for this test
    # This fixes "font not initialized" errors in parallel execution
    if not pygame.font.get_init():
        pygame.font.init()

    yield  # Test runs here

    # Reset display to session state (1440x900 dummy display)
    # This handles tests that create their own display surfaces
    try:
        if pygame.display.get_init():
            # Restore the standard session display size
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass  # Display may not be available
