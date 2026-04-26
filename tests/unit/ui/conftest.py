"""
UI test configuration and shared fixtures.

This conftest provides:
1. Pre-imports game.ui submodules in deterministic order (race condition prevention)
2. pygame_display_reset fixture for UI-specific display handling
3. Cached UIManager fixture to avoid expensive per-test recreation

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


# Module-level cache for UIManager reuse across tests.
_cached_ui_manager = None
_cached_display_id = None


def _get_or_create_ui_manager():
    """Return a valid pygame_gui.UIManager, creating one only if needed.

    Rebuilds if pygame was reinitialized (display surface changed)
    since the last call. This handles external pygame.quit() calls
    from tests that destroy and recreate the display.
    """
    import pygame
    import pygame_gui

    global _cached_ui_manager, _cached_display_id

    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)

    current_display_id = id(pygame.display.get_surface())
    if _cached_ui_manager is None or _cached_display_id != current_display_id:
        _cached_ui_manager = pygame_gui.UIManager((1440, 900))
        _cached_display_id = current_display_id

    return _cached_ui_manager


@pytest.fixture
def ui_manager():
    """Provide a clean UIManager for each test.

    Uses a cached manager to avoid expensive re-creation (theme parsing,
    font loading ~0.3-0.5s). Clears all widgets so each test starts fresh.
    """
    manager = _get_or_create_ui_manager()
    manager.clear_and_reset()
    return manager


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
        import game.ui.screens.battle_screen
        import game.ui.screens.battle_ui
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
        import game.ui.screens.battle_screen
        import game.ui.panels.battle_panels
    except ImportError as e:
        print(f"ERROR: Worker {node.gateway.id} failed to import game.ui modules: {e}",
              file=sys.stderr)
        raise


@pytest.fixture(autouse=True)
def pygame_display_reset():
    """
    Reset display surface to standard size around each UI test.

    Pygame init/font.init recovery is handled by the root conftest's
    `reset_game_state` autouse fixture. This fixture only normalizes the
    display surface so UI tests see a consistent (1440x900) headless display,
    even if a previous test resized it.
    """
    import pygame

    try:
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass  # Display may not be available in some environments

    yield  # Test runs here

    try:
        if pygame.display.get_init():
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass
