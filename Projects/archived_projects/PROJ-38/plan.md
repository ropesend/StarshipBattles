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
| 2. Service Layer | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Entity Layer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Layer | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remaining Consumers | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup & Test Migration | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Audit Fixes (Cycle 2) | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Audit Fixes (Cycle 3) | Complete | [phase_8_checklist.md](phase_8_checklist.md) |
| **AUDIT** | **PASSED** | Cycle 4 complete |

## Current State
**Last Updated:** 2026-01-28 Audit Cycle 4 PASSED
**Active Phase:** COMPLETE - Awaiting User Verification
**Last Action:** Audit Cycle 4 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None
**Test Count:** 5159 passed, 0 failed with both `-n 0` and `-n auto`

### Session 6 Summary (2026-01-28)
**Tasks Completed:**
- Task 6.1: Created new DI test fixtures (`session_registries`, `fresh_registries`, `minimal_registries`) - 15 new tests
- Task 6.2: Migrated critical test files to use `fresh_registries` fixture (3 files migrated)
- Task 6.4: Added deprecation warnings to all 5 accessor functions - 6 new tests

**Task 6.3 DEFERRED:** Removing transitional code (`get_default_registries()`, `set_default_registries()`) would break 25+ files that rely on the fallback pattern. This should be done when ALL consumers are migrated to explicit DI. Deprecation warnings now signal the migration path.

**Files Modified:**
- `tests/conftest.py` - Added 3 new DI fixtures (session_registries, fresh_registries, minimal_registries)
- `tests/unit/core/test_registry_fixtures.py` - New test file (15 tests for fixtures)
- `tests/unit/core/test_registry_deprecation.py` - New test file (6 tests for deprecation)
- `tests/unit/builder/test_builder_ui_sync.py` - Migrated to use fresh_registries
- `tests/unit/builder/test_designs.py` - Migrated to use fresh_registries
- `tests/unit/entities/test_ship.py` - Migrated to use fresh_registries
- `game/core/registry.py` - Added deprecation warnings to 5 accessor functions

**New Fixtures Pattern:**
```python
@pytest.fixture(scope="session")
def session_registries() -> GameRegistries:
    """Session-scoped, loaded once."""
    cache = SessionRegistryCache.instance()
    cache.load_all_data()
    return GameRegistries(components=cache.components_data, ...)

@pytest.fixture
def fresh_registries(session_registries) -> GameRegistries:
    """Function-scoped, deep copies for isolation."""
    return GameRegistries(components=copy.deepcopy(...), ...)
```

**Remaining Tasks:**
- Task 6.5: Evaluate if SessionRegistryCache still needed, remove redundant workarounds
- Task 6.6: Final grep verification for remaining singleton usage

**Verification Needed:**
- [ ] Manual: Launch game and verify main menu displays correctly
- [ ] Manual: Open Design Workshop and verify ship creation/modification works
- [ ] Manual: Run quickstart battle and verify turn processing

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
- [x] All phase checklists complete (Phases 1-8 complete)
- [x] Phase 8 complete (DI test cleanup)
- [x] All tests passing with `-n auto` (5159 passed, 0 failed)
- [x] All tests passing with `-n 0` (5159 passed, 0 failed)
- [x] Audit passed (Cycle 4)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-28 | 10-17 flaky tests in parallel mode | INCORRECTLY PASSED - failed to verify with -n 0 |
| 2 | 2026-01-28 | CRITICAL: test_registry.py causes test pollution | Added Phase 7 for fixes |
| 3 | 2026-01-28 | Phase 7 MISDIAGNOSED: "15 pre-existing bugs" are actually PROJ-38 REGRESSIONS | FAILED - Added Phase 8 |
| 3 | 2026-01-28 | Root cause: DI test files call set_default_registries() without cleanup | Phase 8 complete - PENDING Cycle 4 |
| 4 | 2026-01-28 | No significant issues found | **PASSED** |
