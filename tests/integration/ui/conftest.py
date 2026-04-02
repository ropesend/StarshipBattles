"""
Shared fixtures for UI integration tests.

Provides a session-scoped pygame_gui.UIManager to avoid the expensive
per-test initialization of pygame and UIManager (theme parsing, font loading).
"""

import pytest
import pygame
import pygame_gui


@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    """Ensure pygame and a display surface exist for all UI integration tests.

    Autouse ensures pygame is available for all tests under tests/integration/ui/.
    Does NOT call pygame.quit() on teardown — other tests in the same process
    may still need pygame (sharded runner shares a process across directories).
    """
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))
    yield pygame.display.get_surface()


@pytest.fixture(scope="session")
def _ui_manager_session(_pygame_session):
    """Create a single UIManager for the entire test session.

    UIManager initialization is expensive (theme parsing, font loading).
    Reusing it across tests saves ~0.7s per test.
    """
    manager = pygame_gui.UIManager((1920, 1080))
    return manager


@pytest.fixture
def ui_manager(_ui_manager_session):
    """Provide a clean UIManager for each test.

    Clears all widgets from the session-scoped manager so each test
    starts with a fresh slate, without paying the initialization cost.
    """
    _ui_manager_session.clear_and_reset()
    return _ui_manager_session
