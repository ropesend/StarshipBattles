import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def reset_game_state(monkeypatch, request):
    """
    Context manager for strict test isolation using Fast Hydration.
    Ensures global registries are populated from memory (Session Cache) before each test,
    and cleaned up after.
    """
    from tests.infrastructure.session_cache import SessionRegistryCache
    
    # 0. Skip production hydration if test uses custom data
    if "use_custom_data" in request.keywords:
        yield
        return

    # 1. Ensure Session Cache is loaded (Once per session effectively, via singleton check)
    cache = SessionRegistryCache.instance()
    cache.load_all_data()

    # 2. Fast Hydration: Populate Registry from Cache
    RegistryManager.instance().hydrate(
        cache.get_components(),
        cache.get_modifiers(),
        cache.get_vehicle_classes()
    )

    # 3. Patch Loaders/Caches to prevent Disk I/O during test execution
    
    # A. Component Cache: Inject data so load_components() returns early
    monkeypatch.setattr("game.simulation.components.component._COMPONENT_CACHE", cache.get_components())
    monkeypatch.setattr("game.simulation.components.component._MODIFIER_CACHE", cache.get_modifiers())

    # B. Ship Vehicle Classes: Patch loader to be a no-op (Data already in Registry)
    monkeypatch.setattr("game.simulation.entities.ship.load_vehicle_classes", lambda *args, **kwargs: None)

    yield
    
    # Post-test cleanup
    RegistryManager.instance().clear()
    
    # Reset AI Strategy Manager
    from game.ai.controller import STRATEGY_MANAGER
    if STRATEGY_MANAGER:
        STRATEGY_MANAGER.clear()
        
    # Reset Ship Theme Manager
    from ship_theme import ShipThemeManager
    ShipThemeManager.get_instance().clear()

@pytest.fixture(scope="session", autouse=True)
def enforce_headless():
    """
    Enforce headless mode for Pygame to prevent window creation and interference.
    Initializes core modules once per worker session.
    """
    import pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    # Create a persistent dummy display to satisfy tests that require one
    # Use standard resolution to prevent UI recursion issues in 1x1 windows
    pygame.display.set_mode((1440, 900), pygame.NOFRAME)
    yield
    pygame.quit()
