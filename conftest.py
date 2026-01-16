import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager
from game.core.config import DisplayConfig

@pytest.fixture(autouse=True)
def reset_game_state(monkeypatch, request):
    """
    Context manager for strict test isolation using Fast Hydration.
    Ensures global registries are populated from memory (Session Cache) before each test,
    and cleaned up after. Registry is ALWAYS cleared pre/post-test for isolation.
    """
    from tests.infrastructure.session_cache import SessionRegistryCache
    from game.simulation.components.component import reset_component_caches

    # 0. PRE-TEST CLEANUP (ALWAYS - ensures isolation even after test failures)
    mgr = RegistryManager.instance()
    mgr.clear()

    # Reset module-level caches to prevent stale data from previous tests
    reset_component_caches()
    
    try:
        # 1. Skip production hydration if test uses custom data
        if "use_custom_data" in request.keywords:
            yield
            return

        # 2. Ensure Session Cache is loaded (Once per session effectively, via singleton check)
        cache = SessionRegistryCache.instance()
        cache.load_all_data()

        # 3. Fast Hydration: Populate Registry from Cache
        mgr.hydrate(
            cache.get_components(),
            cache.get_modifiers(),
            cache.get_vehicle_classes()
        )

        # 4. Patch Loaders/Caches to prevent Disk I/O during test execution

        # A. Component Cache: Inject data so load_components() returns early
        from game.simulation.components.component import ComponentCacheManager
        cache_mgr = ComponentCacheManager.instance()
        cache_mgr.component_cache = cache.get_components()
        cache_mgr.modifier_cache = cache.get_modifiers()

        # B. Ship Vehicle Classes: Patch loader to be a no-op (Data already in Registry)
        monkeypatch.setattr("game.simulation.entities.ship.load_vehicle_classes", lambda *args, **kwargs: None)

        yield
    finally:
        # POST-TEST CLEANUP (ALWAYS RUNS - even on test failure or use_custom_data)
        mgr.clear()

        # Reset module-level caches to prevent pollution to next test
        reset_component_caches()

        # Reset AI Strategy Manager using singleton pattern
        from game.ai.controller import StrategyManager
        StrategyManager.instance().clear()

        # Reset singletons using thread-safe reset() methods
        from game.simulation.ship_theme import ShipThemeManager
        ShipThemeManager.reset()

        from game.core.screenshot_manager import ScreenshotManager
        ScreenshotManager.reset()

        from game.ui.renderer.sprites import SpriteManager
        SpriteManager.reset()

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
    pygame.display.set_mode(DisplayConfig.test_resolution(), pygame.NOFRAME)
    yield
    pygame.quit()
