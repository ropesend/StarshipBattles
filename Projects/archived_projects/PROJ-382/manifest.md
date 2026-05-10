# PROJ-382 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/build_queue_screen.py` | Production | Phase 1 — remove session attribute + 3 fallback dispatch sites; reroute registries access |
| `game/ui/screens/empire_build_queue_window.py` | Production | Phase 1 — remove session attribute + 1 fallback dispatch site |
| `game/ui/screens/strategy_screen.py` | Production | Phase 1 — privatize `self.session` → `self._session`; audit downstream public properties |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Phase 1 — drop `session=` kwarg when constructing `BuildQueueScreen` |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Production | Phase 1 — drop `session=` kwarg when constructing `EmpireBuildQueueWindow` |
| `tests/static_guards/test_facade_bypass_guard.py` | Test (new) | Phase 1 — AST static-guard against `session.handle_command` in UI |
| `game/strategy/data/galaxy_spatial_index.py` | Production | Phase 2 — replace isinstance(Planet) with is_planet TypeGuard |
| `game/strategy/data/empire.py` | Production | Phase 2 — collapse dual-path event logging (Pattern #10) |
| `game/strategy/data/fleet.py` | Production | Phase 2 — collapse two dual-path event-logging blocks |
| `game/simulation/entities/projectile.py` | Production | Phase 2 — inject EventBus, drop module-level log_event shim usage |
| `game/ui/screens/design_selector_window.py` | Production | Phase 2 — switch base class to `StrategyModalWindow` |
| `game/ui/screens/builder/stat_getters.py` | Production | Phase 2 — replace hardcoded `_SUPERWEAPON_ABILITIES` with `SUPERWEAPONS` registry |
| `game/ui/screens/builder/event_bus.py` | Production | Phase 2 — rename class `EventBus` → `WorkshopEventBus` |
| `game/ui/screens/workshop_screen.py` | Production | Phase 2 — update import for renamed `WorkshopEventBus` |
| `game/ui/screens/builder/weapons_viewmodel.py` | Production | Phase 2 — update import |
| `game/ui/screens/builder/weapons_panel.py` | Production | Phase 2 — update import |
| `game/ui/screens/test_lab/screen.py` | Production | Phase 2 — update import |
| `game/ui/screens/empire_build_queue_viewmodel.py` | Production | Phase 2 — update import |
| `game/ui/screens/empire_build_queue_sidebar.py` | Production | Phase 2 — update import |
| `game/ui/screens/build_queue_viewmodel.py` | Production | Phase 2 — update import |
| `game/simulation/components/__init__.py` | Production | Phase 2 — add canonical re-exports or document namespace marker |
| `game/strategy/engine/game_session.py` | Production | Phase 3 — drop tautology guard in `handle_command` |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Phase 3 — re-route `BaseCommandHandler` import to canonical `handlers/base.py` |
| `game/strategy/systems/race_library.py` | Production | Phase 3 — replace bare json with json_utils |
| `game/ui/screens/builder/detail_panel.py` | Production | Phase 3 — replace bare json with json_utils (or document why kept) |
| `game/strategy/data/galaxy_warp_generator.py` | Production | Phase 3 — replace inline `json.load` with `load_json` |
| `game/ui/screens/setup_data_io.py` | Production | Phase 3 — drop unused `import json` |
| `game/strategy/engine/production_spawner.py` | Production | Phase 3 — make `registries` required; eager `planet_mutator` injection |
| `docs/02_PATTERNS.md` | Doc | Phase 3 + 4 — Pattern #23 phase list, Pattern #7 canonical path, new Re-Export Shim entry, Pattern #12 Strategy Config Singleton subsection |
| `game/simulation/components/abilities/planetary.py` | Production | Phase 5 — split into `planetary/` sub-package (913 → ≤500 per file) |
| `game/simulation/systems/battle_engine.py` | Production | Phase 5 — extract `BattleLogger`, boundary enforcement |
| `game/strategy/services/fleet_navigation_service.py` | Production | Phase 5 — extract cohesive helper modules |
| `game/strategy/engine/superweapon_order_processor.py` | Production | Phase 5 — extract per-superweapon effect closures |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Phase 5 — extract one cohesive helper to land under 500 LOC |
