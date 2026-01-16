"""
UI test configuration and shared fixtures.
Ensures proper import order and cleanup for parallel execution.

This conftest.py pre-imports game.ui submodules in a deterministic order
to prevent race conditions when pytest-xdist spawns multiple workers.
"""
import sys
import pytest
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_project_root, get_unit_test_data_dir, get_assets_dir


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


@pytest.fixture
def data_dir() -> Path:
    """Return the production data directory path."""
    return get_data_dir()


@pytest.fixture
def project_root() -> Path:
    """Return the project root path."""
    return get_project_root()


@pytest.fixture
def unit_test_data_dir() -> Path:
    """Return the unit test data directory path."""
    return get_unit_test_data_dir()


@pytest.fixture
def assets_dir() -> Path:
    """Return the assets directory path."""
    return get_assets_dir()


@pytest.fixture(autouse=True)
def pygame_display_reset():
    """
    Reset pygame display to session state after each test.

    The root conftest's enforce_headless fixture manages pygame lifecycle
    at session scope. This fixture ensures any display modifications made
    by tests are reset without destroying the session-level pygame state.

    IMPORTANT: Do NOT call pygame.quit() here - that destroys the session
    fixture's pygame initialization and breaks subsequent tests.
    """
    import pygame

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
