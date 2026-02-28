# PROJ-109: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The codebase contains 48 legacy findings across 5 layers (Foundation, Simulation, Strategy, UI-Framework, UI-Screens). These range from dead code (zero risk to delete) to deeply embedded backward compatibility layers with dozens of callers.

The project policy is clear: **"When a new system replaces an old one, ERADICATE the old system completely."** Save files are disposable. No migration code needed.

### Inventory Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 8 | Dual code paths, bootstrap fallbacks, save migration, flag-based transitions |
| MAJOR | 19 | Dead methods, deprecated params, hasattr checks, wrapper functions |
| MINOR | 17 | Comments, naming, documentation, sync methods |
| INFO | 4 | TypeGuard import, classification fallback, comment framing |

### Exclusion: LEG-UI2-001 (Singleton-to-DI Migration)

**SpriteManager and ShipThemeManager singleton migration** (LEG-UI2-001) is explicitly **OUT OF SCOPE** for PROJ-109. This is a Complex-rated item requiring 18+ call site migrations across the UI layer, touching game/app.py initialization, every file that uses theme images, and the test isolation infrastructure. It warrants its own dedicated project with proper DI container support. See DEC-002 in decisions.md.

## Architecture Analysis

### Layer Dependencies (relevant to this project)

```
Core (validation.py, logger.py, profiling.py, protocols.py)
  |
Simulation (component.py, battle_engine.py, ship_loader.py, formula_system.py)
  |
Strategy (save_game_service.py, game_session.py, fleet.py, pathfinding.py, adapters)
  |
UI (battle_screen.py, strategy_screen.py, build_queue_screen.py, input_handler.py)
```

### Key Patterns Used in Removals

1. **Direct replacement**: Old factory -> standard constructor (ValidationResult)
2. **Require parameter**: Optional param with fallback -> required param with TypeError (registries)
3. **Delete dead code**: No callers -> delete (BattleController methods, ComponentRef tuple methods)
4. **Inline wrapper**: Wrapper function -> replace callers with direct call
5. **Single path**: Dual dispatch (mapper vs legacy) -> require mapper only

### Risk Assessment by Phase

| Phase | Risk | Approach | Rollback |
|-------|------|----------|----------|
| 1 (Dead Code) | Minimal | Delete-only, no behavior change | Git revert |
| 2 (Simple Shims) | Low | Few callers, straightforward migration | Git revert |
| 3 (Medium Removals) | Medium | Multiple callers, need grep-verified migration | Git revert per task |
| 4 (Complex Legacy) | High | Deep serialization, save format, dual paths | Per-task commits |
| 5 (Foundation Cleanup) | Medium-High | Many callers for logger proxy, profiler proxy | Per-task commits |

## Key Patterns to Reuse

- **PROJ-50 pattern**: `if registries is None: raise TypeError(...)` - used for strict DI enforcement
- **PROJ-71 pattern**: InputMapper required, no legacy fallback - used in StrategyInputHandler
- **PROJ-43 pattern**: `ai_factory` parameter for BattleEngine - replaces direct AIController import

### Dependencies & Risks

1. **Logger proxy removal (LEG-FND-002)**: 109 files import `log_debug/log_info/log_warning/log_error`. These are module-level functions, not the `Logger` class directly. The proxy functions are thin wrappers around a module-level `_logger = Logger()` global. Removing the proxy means either (a) keeping the convenience functions but removing the global, or (b) migrating 109 files. Decision: Keep convenience functions as direct Logger.instance() delegates (see DEC-003).

2. **Profiler proxy removal (LEG-FND-003)**: `PROFILER` global used in `profile_action` and `profile_block` decorators plus `game/app.py`. Only 3-4 real callers. Replace with `Profiler.instance()` calls.

3. **Save game migration (LEG-STR-001)**: MIGRATABLE_VERSIONS and related methods. Simple deletion per project policy. Old saves are disposable.

4. **FleetOrder serialization (LEG-STR-007)**: 8+ format branches in `from_dict()`. Analysis shows most formats are CURRENT output formats (HexCoord, fleet_ref, transfer, planet_ref, ship_id_list, warp_params, raw). Only `coord` type (tuple-style `[x,y]`) is truly legacy. The current `to_dict()` never produces `coord` type. Decision: Remove only `coord` format branch (see DEC-004).

5. **ValidationResult `.message` property**: Used by 8+ UI/strategy files. The property is a convenience accessor (`errors[0]`), not a backward compat shim. Decision: Keep `.message` property (see DEC-005).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
