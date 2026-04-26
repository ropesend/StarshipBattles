"""
Shared fixtures for UI integration tests.

Provides a cached pygame_gui.UIManager to avoid the expensive per-test
initialization (theme parsing, font loading). The manager is rebuilt
only when the underlying display surface changes (root conftest handles
pygame init/font.init for every test).
"""

import pytest
import pygame
import pygame_gui

# Module-level cache for UIManager reuse across tests.
# Survives as long as pygame display stays alive.
_cached_manager = None
_cached_display_id = None


def _get_or_create_manager():
    """Return a valid UIManager, creating one if needed.

    Rebuilds if the display surface changed since the last call.
    """
    global _cached_manager, _cached_display_id

    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))

    current_display_id = id(pygame.display.get_surface())
    if _cached_manager is None or _cached_display_id != current_display_id:
        _cached_manager = pygame_gui.UIManager((1920, 1080))
        _cached_display_id = current_display_id

    return _cached_manager


@pytest.fixture(autouse=True)
def _ensure_pygame():
    """Ensure a display surface exists before each UI test."""
    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))


@pytest.fixture
def ui_manager():
    """Provide a clean UIManager for each test.

    Uses a cached manager to avoid expensive re-creation. Clears all
    widgets so each test starts fresh without the initialization cost.
    """
    manager = _get_or_create_manager()
    manager.clear_and_reset()
    return manager
