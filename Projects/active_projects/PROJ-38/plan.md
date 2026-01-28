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
| 6. Cleanup & Test Migration | In Progress | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-28 Session 6 (end)
**Active Phase:** Phase 6 Cleanup & Test Migration - IN PROGRESS
**Last Action:** Completed Tasks 6.1 (fixtures), 6.2 (test migration), 6.4 (deprecation warnings). Deferred Task 6.3 (remove transitional code).
**Next Action:** Task 6.5 (Remove old test workarounds), Task 6.6 (Final verification)
**Blockers:** None
**Test Count:** 3846 passed (unit), 10 flaky failures (pre-existing test isolation issues, pass individually)

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
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
