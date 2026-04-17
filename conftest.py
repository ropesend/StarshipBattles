import logging
import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager, set_default_registry_manager
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
        AI (PolicyManager) ->
        UI (ShipThemeManager, SpriteManager)

    Use @pytest.mark.use_custom_data to skip production data hydration
    for tests that need custom/empty registries.
    """
    from tests.infrastructure.session_cache import SessionRegistryCache
    from game.simulation.components.component import reset_component_caches

    # 0. PRE-TEST CLEANUP (ALWAYS - ensures isolation even after test failures)
    # PROJ-258: RegistryManager is no longer a singleton — create fresh and set as default
    mgr = RegistryManager()
    set_default_registry_manager(mgr)

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

        # PROJ-181: Deprecated set_default_registries() removed.
        # All DI consumers now use get_default_registry_provider() which reads
        # from RegistryManager (hydrated above).

        # 4. Patch Loaders/Caches to prevent Disk I/O during test execution

        # A. Component Cache: Inject data so load_components() returns early
        from game.simulation.components.component_loader import get_default_cache_manager
        cache_mgr = get_default_cache_manager()
        cache_mgr.component_cache = cache.get_components()
        cache_mgr.modifier_cache = cache.get_modifiers()

        # B. Ship Vehicle Classes: Patch loader to be a no-op (Data already in Registry)
        monkeypatch.setattr("game.simulation.entities.ship_loader.load_vehicle_classes", lambda *args, **kwargs: None)

        # C. Policies: Hydrate from cache
        from game.ai.policy_manager import get_default_policy_manager
        policy_mgr = get_default_policy_manager()
        policy_mgr.targeting_policies = cache.get_targeting_policies()
        policy_mgr.movement_policies = cache.get_movement_policies()

        yield
    finally:
        # POST-TEST CLEANUP (ALWAYS RUNS - even on test failure or use_custom_data)
        # Order: Core singletons -> Simulation caches -> AI -> UI managers

        # 1. Core singletons
        mgr.clear()

        # PROJ-181: _default_registries removed - no cleanup needed

        # Reset event handler to prevent test pollution
        try:
            from game.core.event_logging import set_event_handler
            set_event_handler(None)
        except Exception:
            pass

        # PROJ-258: Profiler is DI-managed — no module-level cleanup needed

        # 2. Reset module-level caches to prevent pollution to next test
        reset_component_caches()

        # 3. Reset AI Policy Manager
        from game.ai.policy_manager import get_default_policy_manager
        get_default_policy_manager().clear()

        # 4. Reset UI module-level defaults
        from game.ui.assets import ShipThemeManager, set_default_ship_theme_manager
        set_default_ship_theme_manager(ShipThemeManager())

        from game.ui.renderer.sprites import SpriteManager, set_default_sprite_manager
        set_default_sprite_manager(SpriteManager())

@pytest.fixture(scope="session", autouse=True)
def configure_test_logging():
    """Set up logging for tests — NullHandler to suppress file I/O."""
    logging.getLogger("game").addHandler(logging.NullHandler())


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
