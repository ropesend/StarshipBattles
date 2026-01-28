# PROJ-38: Registry DI Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-38` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-38 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Service Layer | Pending Verification | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Entity Layer | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Layer | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remaining Consumers | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup & Test Migration | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-28 Session 2 (end)
**Active Phase:** Phase 2 Service Layer Migration - COMPLETE (Pending Manual Verification)
**Last Action:** Completed all 3 tasks in Phase 2. All service classes now support constructor-based DI with GameRegistries.
**Next Action:** User to verify game launches correctly, then Phase 2 complete and move to Phase 3
**Blockers:** None
**Test Count:** 5056 passed, 1 skipped (baseline was 4998)

### Session 2 Summary (2026-01-28)
**Tasks Completed:**
- Task 2.1: Converted `ModifierService` to constructor injection (12 new tests)
- Task 2.2: Converted `ShipStatsService` to constructor injection (8 new tests)
- Task 2.3: Converted `VehicleDesignService` to constructor injection (7 new tests)

**Files Modified:**
- `game/simulation/services/modifier_service.py` - Added constructor with DI, hybrid instance/static method pattern
- `game/strategy/services/ship_stats_service.py` - Added constructor with DI, hybrid instance/static method pattern
- `game/simulation/services/vehicle_design_service.py` - Extended constructor to support GameRegistries alongside IRegistryProvider
- `tests/unit/services/test_modifier_service_di.py` - New test file (12 tests)
- `tests/unit/services/test_ship_stats_service_di.py` - New test file (8 tests)
- `tests/unit/services/test_vehicle_design_service_di.py` - New test file (7 tests)

**Key Pattern Used:**
All services use a hybrid instance/static method pattern for full backward compatibility:
1. Constructor accepts `registries: GameRegistries` or falls back to `get_default_registries()`
2. Methods detect whether called on instance (uses `self._registries`) or as static (uses legacy `get_*()` functions)
3. Keyword argument support preserved for methods that use them

**Verification Needed:**
- [ ] Manual: Launch game and verify main menu displays correctly
- [ ] Manual: Open Design Workshop and verify it works

## Overview
Refactor the `RegistryManager` singleton in `game/core/registry.py` to use explicit Dependency Injection. This eliminates hidden global state dependencies, making the codebase more testable and architecturally pure. All 19 consumer files will be updated to receive registries via constructor injection.

## Goals
- Eliminate implicit global state access via `RegistryManager.instance()`
- Convert all `get_*_registry()` utility function calls to constructor-injected dependencies
- Remove module-level registry references (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`)
- Keep singleton pattern ONLY at the composition root (`app.py`)
- Improve test isolation and enable parallel test execution

## Scope
**In Scope:**
- Create `GameRegistries` dataclass container
- Convert loading functions to pure functions returning data
- Inject registries into all 19 consumer files
- Update test fixtures to use DI-friendly patterns

**Out of Scope:**
- `SpriteManager` singleton (separate concern)
- `StrategyManager` singleton (separate project)
- Performance optimizations beyond maintaining current speed

## Key Files
| Component | File Path | Current Pattern |
|-----------|-----------|-----------------|
| Registry singleton | `game/core/registry.py` | `RegistryManager.instance()` |
| Composition root | `game/app.py:68-131` | `Game.__init__()` |
| Component class | `game/simulation/components/component.py` | Module-level `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY` |
| Ship class | `game/simulation/entities/ship.py` | Module-level `VEHICLE_CLASSES` |
| Ship stats (GOOD PATTERN) | `game/simulation/entities/ship_stats.py:64` | `__init__(self, vehicle_classes)` |
| Stats service | `game/strategy/services/ship_stats_service.py` | Static methods with `get_*()` calls |
| Design service | `game/simulation/services/vehicle_design_service.py` | Instance methods with `get_*()` calls |
| Modifier service | `game/simulation/services/modifier_service.py` | Functions with `get_modifier_registry()` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log Summary
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Use `GameRegistries` frozen dataclass | Reduces parameter count, immutable/shareable, matches mental model |
| 2026-01-27 | Transitional fallback pattern | Allows incremental migration without breaking all code at once |
| 2026-01-27 | Follow `ShipStatsCalculator` pattern | Already demonstrates proper DI at line 64 |
| 2026-01-27 | Full replacement (not incremental) | User preference for architectural purity |

## Verification
### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - all tests pass (baseline: 4998 passed, 1 skipped)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: Launch game, verify main menu loads
- [ ] Manual test: Open Design Workshop, create a ship

### Final Verification
- [ ] `pytest tests/` - full suite passes (not --testmon)
- [ ] Launch game and complete a full quickstart battle
- [ ] Verify no `get_*_registry()` calls remain (except in registry.py)
- [ ] Verify no module-level registry aliases remain
- [ ] Grep for `RegistryManager.instance()` - should only appear in registry.py

### Completion Checklist
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
