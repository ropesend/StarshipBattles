"""
Builder test configuration and shared fixtures.

Provides a cached pygame display reset fixture (autouse) that ensures
pygame is initialized without calling pygame.init()/pygame.quit() per test,
mirroring the pattern from tests/unit/ui/conftest.py.

Note: Basic pygame initialization is handled by enforce_headless in root conftest.py.
"""
import os
import pytest


@pytest.fixture(autouse=True)
def pygame_display_reset():
    """
    Ensure pygame is initialized and display is available for builder tests.

    Mirrors tests/unit/ui/conftest.py pygame_display_reset. Does NOT call
    pygame.init()/pygame.quit() per test -- the session-scoped enforce_headless
    fixture handles that.
    """
    import pygame

    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    if not pygame.get_init():
        pygame.init()

    if not pygame.display.get_init():
        pygame.display.init()

    try:
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass

    if not pygame.font.get_init():
        pygame.font.init()

    yield

    try:
        if pygame.display.get_init():
            pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    except Exception:
        pass
