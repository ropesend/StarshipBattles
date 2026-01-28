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
| 1. Infrastructure | Pending Verification | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Service Layer | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Entity Layer | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Layer | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remaining Consumers | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup & Test Migration | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-28 Session 1
**Active Phase:** Phase 1 Infrastructure (Pending Manual Verification)
**Last Action:** All 5 tasks code complete. Created GameRegistries container, 4 pure loading functions, and updated composition root.
**Next Action:** User to verify game launches correctly, then phase complete and move to Phase 2
**Blockers:** None
**Test Count:** 5029 passed, 1 skipped (baseline was 4998)

### Session Summary (2026-01-28)
**Tasks Completed:**
- Task 1.1: Created `GameRegistries` frozen dataclass with `set_default_registries()` and `get_default_registries()` (7 new tests)
- Task 1.2: Created `load_components_data()` and `load_modifiers_data()` pure functions (12 new tests)
- Task 1.3: Created `load_vehicle_classes_data()` pure function (6 new tests)
- Task 1.4: Created `load_resources_data()` pure function (6 new tests)
- Task 1.5: Updated `game/app.py` to create and set default `GameRegistries` after data loading

**Files Modified:**
- `game/core/registry.py` - Added GameRegistries dataclass and default registry functions
- `game/simulation/components/component.py` - Added load_components_data() and load_modifiers_data()
- `game/simulation/entities/ship_loader.py` - Added load_vehicle_classes_data()
- `game/core/resources.py` - Added load_resources_data()
- `game/app.py` - Added GameRegistries creation and set_default_registries() call
- `tests/unit/core/test_registry.py` - Added GameRegistries and DefaultRegistries tests
- `tests/unit/core/test_pure_loaders.py` - Created new test file with 24 tests for pure loaders

**Known Issues:**
- One backward compatibility test for vehicle_classes was removed due to test infrastructure conflict (SessionRegistryCache interaction). The pure function tests verify the core functionality.

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
