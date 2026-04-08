# PROJ-258 File Manifest

> Generated during project planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## New Files

| File | Type | Notes |
|------|------|-------|
| `game/context.py` | Production | ApplicationContext DI container class |
| `tests/unit/core/test_application_context.py` | Test | Tests for ApplicationContext |

## Modified Files -- Production

| File | Type | Notes |
|------|------|-------|
| `game/app.py` | Production | Create ApplicationContext, pass to scenes |
| `game/core/registry.py` | Production | Remove SingletonMeta from RegistryManager, update DefaultRegistryProvider |
| `game/core/profiling.py` | Production | Remove SingletonMeta from Profiler, update convenience functions |
| `game/core/strategy_metadata.py` | Production | Remove SingletonMeta from StrategyMetadataService |
| `game/simulation/components/component_loader.py` | Production | Remove SingletonMeta from ComponentCacheManager |
| `game/ai/strategy_manager.py` | Production | Remove SingletonMeta from StrategyManager, add DI for StrategyMetadataService |
| `game/ai/controller.py` | Production | Receive StrategyManager via DI |
| `game/ai/ai_factory.py` | Production | Pass StrategyManager to AIController |
| `game/assets/asset_manager.py` | Production | Remove SingletonMeta from AssetManager |
| `game/ui/renderer/sprites.py` | Production | Remove SingletonMeta from SpriteManager |
| `game/ui/assets/ship_theme_manager.py` | Production | Remove SingletonMeta from ShipThemeManager |
| `game/ui/services/screenshot_manager.py` | Production | Remove SingletonMeta from ScreenshotManager |
| `game/ui/services/game_settings.py` | Production | Remove SingletonMeta from GameSettings |
| `game/ui/renderer/game_renderer.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/panels/race_summary_panel.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/panels/ship_detail_panel.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/panels/ship_stats_renderer.py` | Production | Receive StrategyMetadataService via DI |
| `game/ui/panels/race_theme_gallery.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/screens/build_queue_screen.py` | Production | Receive ScreenshotManager via DI |
| `game/ui/screens/planet_list_window.py` | Production | Receive ScreenshotManager via DI |
| `game/ui/screens/star_list_window.py` | Production | Receive ScreenshotManager via DI |
| `game/ui/screens/strategy_ui_action_router.py` | Production | Receive ScreenshotManager via DI |
| `game/ui/screens/workshop_screen.py` | Production | Receive SpriteManager, ShipThemeManager, ScreenshotManager via DI |
| `game/ui/screens/workshop_data_loader.py` | Production | Receive StrategyManager, StrategyMetadataService via DI |
| `game/ui/screens/workshop_event_router.py` | Production | Receive StrategyMetadataService via DI |
| `game/ui/screens/setup_screen.py` | Production | Receive StrategyMetadataService via DI |
| `game/ui/screens/setup_renderer.py` | Production | Receive StrategyMetadataService via DI |
| `game/ui/screens/fleet_data_source.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/screens/race_browser_dialog.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/screens/race_setup_screen.py` | Production | Receive ShipThemeManager via DI |
| `game/ui/screens/planet_data_source.py` | Production | Receive AssetManager via DI |
| `game/ui/screens/planet_selection_window.py` | Production | Receive AssetManager via DI |
| `game/ui/screens/star_data_source.py` | Production | Receive AssetManager via DI |
| `game/ui/screens/strategy_detail_fmt.py` | Production | Receive RegistryManager via DI |
| `game/ui/screens/settings_window.py` | Production | Receive GameSettings via DI |
| `game/ui/screens/strategy_renderer.py` | Production | Receive GameSettings via DI |
| `game/ui/screens/builder/right_panel.py` | Production | Receive StrategyMetadataService via DI |

## Modified Files -- Test

| File | Type | Notes |
|------|------|-------|
| `tests/conftest.py` | Test | Add test_context fixture, refactor session_registries |
| `tests/infrastructure/session_cache.py` | Test | Refactor to not use singleton .instance() |
| `tests/unit/core/registry/conftest.py` | Test | Simplify reset_registry fixture |
| `tests/unit/core/profiling/conftest.py` | Test | Simplify reset_profiler fixture |
| `tests/integration/ai_strategy/conftest.py` | Test | Simplify setup_game_data fixture |
| `tests/unit/core/resources_registry/conftest.py` | Test | Review for singleton cleanup |
| `tests/unit/core/registry/test_singleton_and_thread.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/registry/test_registry_features.py` | Test | Replace .instance() with DI |
| `tests/unit/core/test_strategy_metadata.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/test_registry_provider.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/test_pure_loaders.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/test_profiling_edge_cases.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/profiling/test_singleton_threading.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/profiling/test_decorators.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/test_singleton.py` | Test | May need updates for removed users |
| `tests/unit/core/test_service_injection.py` | Test | Replace .instance() with DI |
| `tests/unit/core/test_isolation.py` | Test | Update isolation tests |
| `tests/unit/core/test_registry_manager_reload.py` | Test | Replace .instance() with DI |
| `tests/unit/performance/test_profiler_perf.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ai/test_strategy_system.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ai/test_strategy_manager_singleton.py` | Test | Rewrite or remove (singleton-specific tests) |
| `tests/unit/ai/test_ai.py` | Test | Replace .instance() with DI |
| `tests/unit/ai/test_movement_and_ai.py` | Test | Replace .instance() with DI |
| `tests/unit/entities/test_component_cache.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/entities/test_ship_theme_logic.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/assets/test_asset_manager_resolutions.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/core/test_asset_manager.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ui/test_sprites.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ui/test_sprite_loading.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ui/test_theme_discovery.py` | Test | Replace .reset() with fresh instances |
| `tests/unit/ui/services/test_screenshot_manager.py` | Test | Replace .instance() with DI |
| `tests/repro_issues/test_bug_15_screenshot_strategy.py` | Test | Replace .reset() with DI |
| `tests/unit/core/resources_registry/test_integration.py` | Test | Replace .reset() with DI |
| `tests/unit/regressions/test_regressions.py` | Test | Replace .instance() with DI |
| `tests/unit/strategy/data/test_data_layer_boundaries.py` | Test | Replace .instance() with DI |
| `tests/unit/strategy/conftest.py` | Test | Replace .instance() with DI |
| `tests/integration/resource_system/conftest.py` | Test | Replace .instance() with DI |
| `tests/regression/test_deprecated_code_removed.py` | Test | Update singleton removal checks |
| `tests/fixtures/ai.py` | Test | Replace .instance() with DI |
| `tests/unit/builder/test_builder_ui_sync.py` | Test | Replace .instance() with DI |
| `tests/unit/combat/test_battle_setup_logic.py` | Test | Replace .instance() with DI |
| `tests/integration/ai_strategy/test_evaluation.py` | Test | Replace .instance() with DI |
| `tests/integration/ui/test_planet_list_window.py` | Test | Replace .instance() with DI |

## Modified Files -- Documentation

| File | Type | Notes |
|------|------|-------|
| `docs/01_ARCHITECTURE.md` | Docs | Add ApplicationContext to cross-layer communication |
| `docs/02_PATTERNS.md` | Docs | Rewrite Singleton section, add ApplicationContext pattern |
| `docs/03_CONVENTIONS.md` | Docs | Update preferred patterns |
| `docs/guides/testing_infrastructure.md` | Docs | Document test_context fixture |
