# PROJ-258: Dependency Injection - ApplicationContext and Singleton Migration

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-258` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-258 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create ApplicationContext (wrapper) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Core singletons | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate AI + Strategy singletons | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate UI singletons | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simplify conftest.py and session cache | Deferred | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Documentation + Verification | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Remove Core shims (RegistryManager, Profiler, SMS, CCM) | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Remove AI shims (StrategyManager) | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Remove UI shims (5 managers) | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Final verification — zero shims | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |

## Current State
**Last Updated:** 2026-04-08
**Active Phase:** Phase 7 ready (Remove Shims)
**Last Action:** All 10 singletons migrated + docs updated. Phase 7 added to remove all .instance()/.reset() compatibility shims (48 production + ~347 test call sites across 11 tasks).
**Next Action:** Begin Phase 7 Task 7.1 — Remove RegistryManager shims
**Blockers:** None
**Note on Phase 5:** The skeptical review confirmed conftest cleanup is "not fragile" with "logical order, documented, defensive try/except". The compatibility shims (.instance()/.reset()) make the existing conftest work without modification. Simplification can be done incrementally as a future improvement.

## Overview

This project migrates 11 singletons using `SingletonMeta` to dependency injection via a new `ApplicationContext` container. The migration follows a wrapper-first approach: Phase 1 creates `ApplicationContext` as a thin wrapper around existing singletons (all tests stay green), then Phases 2-4 migrate singletons one-at-a-time into the container, removing `SingletonMeta` usage from each. Phase 5 simplifies the test infrastructure (conftest.py, SessionRegistryCache) to use `ApplicationContext.create_test()`. Phase 6 updates documentation.

## Goals
- Replace all 11 `SingletonMeta` singletons with DI via `ApplicationContext`
- Provide `ApplicationContext.create_production()` and `ApplicationContext.create_test()` factory methods
- Simplify test isolation (no more per-singleton `reset()` calls in conftest files)
- Maintain 14783+ test baseline throughout migration (zero regressions)
- One singleton per commit for easy `git bisect`

## Scope
**In:**
- Creating `ApplicationContext` class in `game/core/application_context.py`
- Migrating all 11 singletons: RegistryManager, ComponentCacheManager, Profiler, StrategyMetadataService, AssetManager, SpriteManager, ShipThemeManager, ScreenshotManager, StrategyManager, GameSettings, SessionRegistryCache (test infra)
- Updating all 62 production `.instance()` call sites across 34 files
- Updating all 284 test `.instance()` call sites across 43 files
- Simplifying conftest.py singleton reset logic
- Updating `docs/02_PATTERNS.md` and `docs/01_ARCHITECTURE.md`

**Out:**
- Changing any singleton's internal behavior or API (only how instances are obtained)
- Modifying the `IRegistryProvider` protocol or `DefaultRegistryProvider`/`TestRegistryProvider`
- Deleting `SingletonMeta` itself (may still be useful, just no longer used)
- Changing save file format or game data loading logic

## Key Files Reference

### Singleton Source Files (11 singletons)
| Singleton | File Path | Layer | Production .instance() calls | Test .instance() calls |
|-----------|-----------|-------|------------------------------|------------------------|
| RegistryManager | `game/core/registry.py` | Core | 9 (in registry.py wrappers + app.py + strategy_detail_fmt.py) | ~50 |
| ComponentCacheManager | `game/simulation/components/component_loader.py` | Simulation | 2 | ~9 |
| Profiler | `game/core/profiling.py` | Core | 6 (app.py + profiling.py internals) | ~22 |
| StrategyMetadataService | `game/core/strategy_metadata.py` | Core | 11 (strategy_manager.py, UI panels, setup screens) | ~13 |
| AssetManager | `game/assets/asset_manager.py` | Assets | 3 (planet/star data sources) | ~1 |
| SpriteManager | `game/ui/renderer/sprites.py` | UI | 2 (app.py, workshop_screen.py) | ~18 |
| ShipThemeManager | `game/ui/assets/ship_theme_manager.py` | UI | 8 (game_renderer, panels, screens) | ~26 |
| ScreenshotManager | `game/ui/services/screenshot_manager.py` | UI | 6 (build_queue, planet_list, star_list, strategy_ui, workshop) | ~11 |
| StrategyManager | `game/ai/strategy_manager.py` | AI | 2 (controller.py, workshop_data_loader.py) | ~20 |
| GameSettings | `game/ui/services/game_settings.py` | UI | 2 (settings_window.py, strategy_renderer.py via `GameSettings()`) | 0 |
| SessionRegistryCache | `tests/infrastructure/session_cache.py` | Test | 0 | ~3 |

### New Files
| File | Purpose |
|------|---------|
| `game/core/application_context.py` | ApplicationContext container class |
| `tests/unit/core/test_application_context.py` | Tests for ApplicationContext |

### Key Conftest/Test Infrastructure Files
| File | What Changes |
|------|-------------|
| `tests/conftest.py` | Root conftest - session_registries, fresh_registries |
| `tests/infrastructure/session_cache.py` | SessionRegistryCache - simplify or remove |
| `tests/unit/core/registry/conftest.py` | reset_registry autouse fixture |
| `tests/unit/core/profiling/conftest.py` | reset_profiler autouse fixture |
| `tests/integration/ai_strategy/conftest.py` | setup_game_data autouse fixture |
| `tests/unit/ui/conftest.py` | UI test fixtures |

### Documentation Files
| File | What Changes |
|------|-------------|
| `docs/01_ARCHITECTURE.md` | Add ApplicationContext to Cross-Layer Communication |
| `docs/02_PATTERNS.md` | Update Singleton section, add ApplicationContext pattern |
| `docs/03_CONVENTIONS.md` | Update preferred patterns (DI over singletons) |

## Decisions Log
See [decisions.md](decisions.md) for the full decisions history.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection

## Verification
- [ ] All phase checklists complete
- [ ] All 14783+ tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] Zero `SingletonMeta` usage remains in production code (grep verification)
- [ ] `ApplicationContext.create_production()` used in `game/app.py`
- [ ] `ApplicationContext.create_test()` used in `tests/conftest.py`
- [ ] All `.instance()` calls eliminated from production code
- [ ] conftest.py no longer calls individual singleton `.reset()` methods
- [ ] `docs/01_ARCHITECTURE.md` updated with ApplicationContext
- [ ] `docs/02_PATTERNS.md` updated (Singleton section rewritten, DI section updated)
- [ ] Audit passed
- [ ] User verified
