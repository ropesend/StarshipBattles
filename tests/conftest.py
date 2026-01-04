import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def reset_game_state():
    """
    Context manager for strict test isolation.
    Ensures all global registries are cleared before and after each test.
    """
    # Pre-test cleanup
    RegistryManager.instance().clear()
    
    yield
    
    # Post-test cleanup (catch any pollution)
    RegistryManager.instance().clear()

@pytest.fixture(scope="session", autouse=True)
def enforce_headless():
    """
    Enforce headless mode for Pygame to prevent window creation and interference.
    """
    import pygame
    pygame.init()
    yield
    pygame.quit()
