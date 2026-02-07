import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager, GameRegistries, set_default_registries
from game.core.config import DisplayConfig

@pytest.fixture(autouse=True)
def reset_game_state(monkeypatch, request):
    """
    Primary test isolation fixture using Fast Hydration pattern.

    This fixture runs automatically for every test function and ensures:
    1. PRE-TEST: Clear all singleton state for clean slate
    2. SETUP: Hydrate registries from session cache (fast, no disk I/O)
    3. POST-TEST: Clean up all singleton state to prevent leaks

    Order of cleanup (post-test):
        Core (RegistryManager, Logger, Profiler) ->
        Simulation (ComponentCacheManager) ->
        AI (StrategyManager) ->
        UI (ShipThemeManager, ScreenshotManager, SpriteManager)

    Use @pytest.mark.use_custom_data to skip production data hydration
    for tests that need custom/empty registries.
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

        # 4. Set default GameRegistries for DI consumers (PROJ-58)
        # Code using get_default_registries() needs this to resolve registries
        set_default_registries(GameRegistries(
            components=mgr.components,
            modifiers=mgr.modifiers,
            vehicle_classes=mgr.vehicle_classes,
            resources=mgr.resources,
        ))

        # 5. Patch Loaders/Caches to prevent Disk I/O during test execution

        # A. Component Cache: Inject data so load_components() returns early
        from game.simulation.components.component import ComponentCacheManager
        cache_mgr = ComponentCacheManager.instance()
        cache_mgr.component_cache = cache.get_components()
        cache_mgr.modifier_cache = cache.get_modifiers()

        # B. Ship Vehicle Classes: Patch loader to be a no-op (Data already in Registry)
        monkeypatch.setattr("game.simulation.entities.ship_loader.load_vehicle_classes", lambda *args, **kwargs: None)

        # C. Combat Strategies: Hydrate from cache
        from game.ai.strategy_manager import StrategyManager
        strategy_mgr = StrategyManager.instance()
        strategy_mgr.strategies = cache.get_strategies()

        yield
    finally:
        # POST-TEST CLEANUP (ALWAYS RUNS - even on test failure or use_custom_data)
        # Order: Core singletons -> Simulation caches -> AI -> UI managers

        # 1. Core singletons
        mgr.clear()

        # Clear default registries (PROJ-58)
        import game.core.registry as _reg_mod
        _reg_mod._default_registries = None

        # Reset logger event handler to prevent test pollution
        try:
            from game.core.logger import set_event_handler
            set_event_handler(None)
        except Exception:
            pass

        # Clear profiler records
        try:
            from game.core.profiling import Profiler
            if Profiler._instance is not None:
                Profiler._instance.clear()
        except Exception:
            pass

        # 2. Reset module-level caches to prevent pollution to next test
        reset_component_caches()

        # 3. Reset AI Strategy Manager using singleton pattern
        from game.ai.strategy_manager import StrategyManager
        StrategyManager.instance().clear()

        # 4. Reset UI singletons using thread-safe reset() methods
        from game.ui.assets import ShipThemeManager
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
