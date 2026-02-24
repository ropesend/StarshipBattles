# PROJ-170: Exception Handling Migration — Full Adoption of PROJ-45 Infrastructure

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-170` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-170 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Infrastructure — Error Codes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Loaders | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simulation Core | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Game Config + UI | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Caller Catch Updates | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Exception Chaining Fixes | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Catch Quality Cleanup | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - Added 3 new error codes (V002, V003, C003)
**Next Action:** Begin Phase 2 - Strategy Loaders Migration
**Blockers:** None
**Baseline:** 11,972 passed, 1 skipped, 0 failures

## Overview

PROJ-45 created an excellent custom exception hierarchy (10 classes, 19 error codes, 563-line usage guide) but adoption is only ~5%. The codebase has 63 generic raises (ValueError, RuntimeError, TypeError) that should use domain exceptions, 36 except blocks catching those generic types, and 80 tests asserting generic exceptions. This project systematically migrates all of them.

## Goals
- Migrate all 63 generic `raise` statements to domain-specific exceptions with error codes and context dicts
- Update all 36 game-code `except` blocks to catch domain exceptions
- Update all 80 tests to assert domain exceptions
- Add 3 missing error codes (V002, V003, C003)
- Fix exception chaining gaps (`from e`)
- Clean up bare/silent exception catches

## Scope
**In:**
- All `raise ValueError/TypeError/RuntimeError` in `game/` that should use custom exceptions (63 raises)
- All `except` blocks in `game/` that catch those generic types from game code (36 blocks)
- All tests asserting generic exceptions on game code (80 tests)
- New error codes needed for migration (3 codes)
- Exception chaining fixes (3 locations)
- Catch quality issues fixable during migration (11 issues)

**Out:**
- Generic exceptions that are correct Python protocol (6 raises — KEEP as-is)
- Stdlib-sourced `except ValueError` for int()/float()/json/enum (34 blocks — NO CHANGE)
- Intentional broad `except Exception` for crash isolation (15 blocks — NO CHANGE)
- Tests asserting stdlib exceptions (46 tests — NO CHANGE)
- Deserialization input validation improvements (separate future project)
- New test creation for currently untested code

## Key Files

### Infrastructure
| Component | File Path |
|-----------|-----------|
| Exception hierarchy | `game/core/exceptions.py` |
| Error codes | `game/core/error_codes.py` |
| Usage guide | `docs/architecture/ERROR_HANDLING_GUIDELINES.md` |

### Reference Implementations (gold standard pattern)
| Component | File Path |
|-----------|-----------|
| Formula exceptions | `game/simulation/formula_system.py` |
| State exceptions | `game/core/registry.py` |
| Component exceptions | `game/simulation/components/modifier_effects.py` |
| Validation exceptions | `game/simulation/entities/projectile.py` |

### Files to Modify (by phase)
| Phase | Files | Raises | Tests |
|-------|-------|--------|-------|
| 1. Infrastructure | 1 | 0 | 0 |
| 2. Strategy Loaders | 4 | 24 | 6 |
| 3. Simulation Core | 15 | 27 | 44 |
| 4. Game Config + UI | 7 | 12 | 10 |
| 5. Caller Catches | 12 | 0 | 0 |
| 6. Exception Chaining | 3 | 0 | 0 |
| 7. Catch Quality | 3 | 0 | 0 |
| **Total** | **~35** | **63** | **~60** |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-23_180421_focused_exception-handling-migration-audit/report.md) — Source review with all 7 agent reports

---

## Phases

### Phase 1: Infrastructure — Add Missing Error Codes [Simple]
**Objective:** Add 3 new error codes needed by the migration. No production behavior changes.
**Status:** Not Started
**Estimated Effort:** 30 min

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

**Summary:**
- Task 1.1: Add V002 SCHEMA_VALIDATION_ERROR, V003 MISSING_ENTITY, C003 MISSING_DEPENDENCY to `game/core/error_codes.py`
- Task 1.2: Add tests for new error codes
- Task 1.3: Update ERROR_HANDLING_GUIDELINES.md with new codes

---

### Phase 2: Strategy Loaders Migration [Simple]
**Objective:** Migrate all 24 ValueErrors in strategy generation loaders. Lowest risk — no external callers.
**Status:** Not Started
**Estimated Effort:** 2 hours

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

**Summary:**
- Task 2.1: `system_blueprints_loader.py` — 15 ValueError → ValidationException (lines 94, 118, 121, 125, 143, 145, 147, 153, 157, 159, 161, 166, 168, 170, 174)
- Task 2.2: `astrophysics_loader.py` — 7 ValueError → ValidationException (lines 119, 126, 133, 138, 143, 148, 150)
- Task 2.3: `galaxy_layouts_loader.py` — 2 ValueError → ValidationException/ResourceException (lines 53, 75)
- Task 2.4: Update 6 tests in `test_density_map.py`, `test_layout_loader.py`, `test_system_blueprints.py`

---

### Phase 3: Simulation Core Migration [Medium]
**Objective:** Migrate 27 raises across simulation module (ValueError, RuntimeError, TypeError DI). Includes 2 self-contained breaking changes.
**Status:** Not Started
**Estimated Effort:** 3 hours

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

**Summary:**
- Task 3.1: `battle_engine.py` — 3 ValueError → ValidationException (lines 269, 320, 467)
- Task 3.2: `battle_state_manager.py` — 1 RuntimeError + 1 ValueError → StateException/ValidationException (lines 50, 79) + update except at line 78
- Task 3.3: `abilities/base.py` — 2 ValueError → ValidationException (lines 98, 105) + update except at line 97
- Task 3.4: `stat_keys.py` — 1 ValueError → ValidationException (line 130)
- Task 3.5: `battle_mode_handler.py` — 1 ValueError → ValidationException (line 288)
- Task 3.6: `ship_serialization.py` — 1 ValueError + 1 TypeError → ValidationException (lines 141, 180)
- Task 3.7: `ship_loader.py` — 1 RuntimeError → MissingResourceException (line 83)
- Task 3.8: `ship.py` — 1 TypeError → ValidationException (line 49)
- Task 3.9: `component.py` — 3 TypeError → ValidationException (lines 94, 695, 721)
- Task 3.10: `battle_state.py` — 1 TypeError → ValidationException (line 248)
- Task 3.11: `ship_validator.py` — 2 TypeError → ValidationException (lines 284, 391)
- Task 3.12: `design_loader.py` — 1 TypeError → ValidationException (line 50)
- Task 3.13: `vehicle_design_service.py` — 1 TypeError → ValidationException (line 66)
- Task 3.14: `modifier_service.py` — 1 TypeError → ValidationException (line 51)
- Task 3.15: `ai_factory.py` — 1 RuntimeError → StateException (line 79)
- Task 3.16: `density_map.py` — 4 ValueError → ValidationException (lines 112, 186, 191, 194) + update except at line 207
- Task 3.17: Update ~44 tests (DI tests, ability tests, engine tests, loader tests)

---

### Phase 4: Game Config + UI Migration [Simple]
**Objective:** Migrate 12 raises in config and UI modules. One self-contained breaking change.
**Status:** Not Started
**Estimated Effort:** 2 hours

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

**Summary:**
- Task 4.1: `game_config.py` — 3 ValueError → ValidationException (lines 159, 161, 163)
- Task 4.2: `build_queue_screen.py` — 4 ValueError → ValidationException (lines 77, 79, 81, 109)
- Task 4.3: `vehicle_class_service.py` — 1 ValueError → ValidationException (line 47)
- Task 4.4: `workshop_viewmodel.py` — 1 ValueError + 1 RuntimeError → ValidationException (lines 67, 344)
- Task 4.5: `new_game_setup_screen.py` — 1 ValueError → ValidationException (line 582)
- Task 4.6: `formation_editor.py` — 1 ValueError → ValidationException (line 217) + update except at line 227
- Task 4.7: `asset_manager.py` — 1 ValueError → ResourceException (line 197)
- Task 4.8: `resource_management_engine.py` — 1 TypeError → ValidationException (line 54)
- Task 4.9: `resupply_engine.py` — 1 TypeError → ValidationException (line 64)
- Task 4.10: `ship_stats_calculator.py` — 1 TypeError → ValidationException (line 70)
- Task 4.11: Update ~10 tests (game_config, new_game_setup, vehicle_class_service, asset_manager)

---

### Phase 5: Caller Catch Updates [Medium]
**Objective:** Update 36 except blocks in game/ that catch generic exceptions from game code. The most complex phase due to broad tuple catches in the persistence tier.
**Status:** Not Started
**Estimated Effort:** 3 hours

See [phase_5_checklist.md](phase_5_checklist.md) for detailed tasks.

**Summary:**
- Task 5.1: Persistence tier — `save_game_service.py` (4 blocks), `design_library.py` (4 blocks), `race_library.py` (2 blocks), `ship_io.py` (2 blocks)
- Task 5.2: Component loading chain — `component.py` (2 blocks), `design_loader.py` (2 blocks), `vehicle_design_service.py` (1 block), `battle_service.py` (1 block), `battle_controller.py` (3 blocks)
- Task 5.3: Other catches — `formation_editor.py` (2 blocks), `new_game_setup_screen.py` (1 block), `abilities/__init__.py` (1 block)
- Task 5.4: Mixed-source review — 13 blocks requiring individual audit

**Strategy:** Add domain exceptions to tuple catches alongside generic types (transitional safety), then remove generic types once all raises are migrated. Example: `except (TypeError, ValueError, ValidationException)` → eventual `except (ValidationException, ComponentException)`.

---

### Phase 6: Exception Chaining Fixes [Simple]
**Objective:** Add `from e` to 3 re-raise patterns that lose the original traceback.
**Status:** Not Started
**Estimated Effort:** 15 min

See [phase_6_checklist.md](phase_6_checklist.md) for detailed tasks.

**Summary:**
- Task 6.1: `battle_state_manager.py:79` — add `from e`
- Task 6.2: `abilities/base.py:98` — add `from e`
- Task 6.3: `density_map.py:208` — add `from e`

---

### Phase 7: Catch Quality Cleanup [Simple]
**Objective:** Fix remaining catch quality issues identified during review.
**Status:** Not Started
**Estimated Effort:** 45 min

See [phase_7_checklist.md](phase_7_checklist.md) for detailed tasks.

**Summary:**
- Task 7.1: Fix bare `except: pass` in `scripts/apply_resource_costs.py`
- Task 7.2: Add logging to silent fallbacks in `battle_panels.py`, `race_environment_panel.py`
- Task 7.3: Final audit — verify no regression, run full test suite

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 12,016 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Verify no new import errors with `python -c "from game.core.exceptions import *; from game.core.error_codes import *"`

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` — same or better than baseline
- [ ] Grep for remaining generic raises: `rg "raise ValueError|raise RuntimeError|raise TypeError\(\"" game/` — only legitimate keeps
- [ ] Grep for custom exception usage: `rg "raise (Validation|State|Resource|Missing|Persistence|Simulation|Component|Formula)Exception" game/` — count should be ~90+
- [ ] Verify error codes used: `rg "ErrorCode\." game/` — count should be ~50+

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All Phase 7 tasks checked off
- [ ] All tests passing (12,016+ passed)
- [ ] Audit passed (no significant issues)
- [ ] User verified
