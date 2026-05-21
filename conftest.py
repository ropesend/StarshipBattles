import logging
import os
# Force headless mode BEFORE any imports happen during collection
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from game.core.registry import RegistryManager, set_default_registry_manager
from game.core.config import DisplayConfig

# PROJ-411: register the perf smoke-scenario fixture as a session-wide plugin
# so any test (under tests/performance/, tests/fixtures/, etc.) can request
# `smoke_turn1_scenario` without a directory-local conftest wrapper.
pytest_plugins = ("tests.fixtures.perf_smoke_scenario",)

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
    from game.simulation.entities.stat_contributors.registry import (
        reset_stat_contributor_registry,
        reset_crew_priority_registry,
    )

    # 0. PRE-TEST CLEANUP (ALWAYS - ensures isolation even after test failures)
    # PROJ-258: RegistryManager is no longer a singleton — create fresh and set as default
    # PROJ-420: set_default_registry_manager() now also invalidates the
    # shared lazy GameRegistries cache; explicit reset below is belt-and-
    # braces in case the helper is referenced before this line in future.
    mgr = RegistryManager()
    set_default_registry_manager(mgr)

    # Reset module-level caches to prevent stale data from previous tests
    from game.core.registry_cache import reset_cached_registries
    reset_cached_registries()
    reset_component_caches()
    # PROJ-360 audit A1: registry mutable state must reset per-test, not just
    # via in-test cleanup fixtures. A test that crashes before its
    # `clean_extension_registry` finally-block leaks STAT_CONTRIBUTOR_REGISTRY
    # into the next test, where it can silently double-fire (or after the
    # EXT-02 fix, suppress built-ins) for an unrelated test's ship.
    reset_stat_contributor_registry()
    # PROJ-471 Task 3.4: sibling crew-priority registry has the same
    # append-only/leak-across-tests hazard; restore its canonical defaults too.
    reset_crew_priority_registry()

    # Pygame state recovery: ~45 legacy test files still call pygame.quit() in
    # teardown, which leaves the next test in the shard with an uninitialized
    # pygame and font subsystem. Any later test that constructs a UI screen
    # (e.g. BattleScreen) crashes with "font not initialized". The session-scoped
    # enforce_headless fixture only runs once, so it can't recover. Re-init here
    # so every test starts with a healthy pygame regardless of what ran before.
    # Mirrors the pattern in tests/unit/ui/conftest.py::pygame_display_reset,
    # promoted to root scope so non-UI tests (e.g. tests/fixtures/) benefit too.
    import pygame
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    
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
        # PROJ-420: mgr.clear() does NOT invalidate the helper cache
        # (only the module-level clear_registry() function does); reset
        # explicitly here to keep test isolation tight.
        mgr.clear()
        reset_cached_registries()

        # PROJ-181: _default_registries removed - no cleanup needed

        # PROJ-390: module-level event handler global was retired; each
        # GameSession owns its own EventBus, so there's nothing to reset
        # at process scope between tests.

        # PROJ-258: Profiler is DI-managed — no module-level cleanup needed

        # 2. Reset module-level caches to prevent pollution to next test
        reset_component_caches()
        # PROJ-360 audit A1: paired with the pre-test reset above.
        reset_stat_contributor_registry()
        # PROJ-471 Task 3.4: paired with the pre-test crew-priority reset.
        reset_crew_priority_registry()

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
