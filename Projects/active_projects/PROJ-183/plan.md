# PROJ-183: PROJ-175 Post-Refactor Cleanup - Logging Pattern Completion

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-183` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-183 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Inline Logger in strategy_renderer.py | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Replace traceback.format_exc() with logger.exception() | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Log Level Misuses | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Planning
**Last Action:** Independent audit swarm completed with 7 agents, findings analyzed
**Next Action:** User approval of plan, then begin Phase 1
**Blockers:** None
**Context for Next Agent:** This project addresses findings from an independent 7-agent audit of PROJ-175. The original audit report was mostly accurate but missed several issues. Test baseline: 12338 passed, 1 skipped.

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Overview
Independent audit of PROJ-175 (Logger & JSON Loading Pattern Standardization) revealed several remaining issues that the original audit missed. While the core migration was thorough (old logger.py deleted, 134/135 game files compliant, zero json.load/dump violations), the following gaps remain:

1. **Inline logger instantiation** in strategy_renderer.py (the one file the original audit flagged)
2. **traceback.format_exc() antipattern** in 7 files (should use logger.exception())
3. **Log level misuses** where errors/failures are logged at INFO level

## Goals
- 100% compliance with module-level `logger = logging.getLogger(__name__)` pattern
- Replace all `traceback.format_exc()` with `logger.exception()` in game/ files
- Fix log level misuses (errors logged at INFO -> WARNING/ERROR)

## Scope
**In Scope:**
- `game/ui/screens/strategy_renderer.py` - inline logger fix
- 7 files using `import traceback` + `traceback.format_exc()` antipattern
- Log level misuses in `game/ui/screens/test_lab/validation_manager.py` and similar files

**Out of Scope:**
- `game/app.py` traceback usage (top-level crash handler - appropriate use)
- Test files (`tests/`) json.load/dump patterns (test fixtures are exempt per PROJ-175 scope)
- Archived documentation referencing old logger (historical artifacts, not active code)
- `warnings.warn()` usage in registry.py (correct use for DeprecationWarning)
- Threading logging enhancements (low priority, no current issues)

## Key Files Reference
| Component | File Path | Issue |
|-----------|-----------|-------|
| Strategy Renderer | `game/ui/screens/strategy_renderer.py` | Inline logger (line 655-656) |
| Ship Serialization | `game/simulation/entities/ship_serialization.py` | traceback.format_exc() (line 109-110) |
| Save Game Service | `game/strategy/systems/save_game_service.py` | traceback.format_exc() (lines 109, 112, 224) |
| Design Library | `game/strategy/systems/design_library.py` | traceback.format_exc() (lines 105-106, 187-188, 192-193) |
| Build Queue Controller | `game/ui/panels/build_queue_controller.py` | traceback.format_exc() (line 575-576) |
| Workshop Data Reloader | `game/ui/screens/workshop_data_reloader.py` | traceback.format_exc() (line 155-156) |
| Workshop Ship IO | `game/ui/screens/workshop_ship_io.py` | traceback.format_exc() (line 157-158) |
| Validation Manager | `game/ui/screens/test_lab/validation_manager.py` | INFO for errors (line 103) |
| Galaxy System Mode | `game/ui/screens/galaxy_test/system_mode.py` | INFO for failures (lines 198, 238) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Exclude game/app.py traceback usage | Top-level crash handler needs format_exc() for display, not just logging |
| 2026-02-24 | Exclude test file json.load/dump | PROJ-175 scope explicitly excludes tests/ for JSON patterns |
| 2026-02-24 | Exclude archived docs with old logger refs | Historical artifacts, not active templates |
| 2026-02-24 | Exclude warnings.warn() in registry.py | DeprecationWarning is correct Python pattern for deprecations |

## Swarm Findings Summary

### Independent Audit Results (7 agents)

**Agent 1 - Ghost Code Hunter:** PASS. Old logger.py fully deleted. Zero imports remain. One orphaned .pyc file in `__pycache__` (benign artifact).

**Agent 2 - Logging Compliance Checker:** 134/135 files compliant. ONE violation: `strategy_renderer.py:655-656` has inline `import logging` + inline `logging.getLogger(__name__).warning(...)` inside a method instead of using module-level logger.

**Agent 3 - JSON Serialization Auditor:** game/ directory is 100% clean. All json.load/dump calls are inside json_utils.py. Tests have extensive direct json.load/dump usage (27+ files) but this was explicitly out of scope for PROJ-175.

**Agent 4 - Event System Reviewer:** PASS. event_logging.py is 58 lines, excellent architecture, comprehensive test coverage (31 tests), zero file I/O side effects, proper test isolation via conftest cleanup.

**Agent 5 - Documentation Auditor:** ERROR_HANDLING_GUIDELINES.md correctly updated with anti-patterns. Archived docs contain old logger references but these are historical artifacts, not active code.

**Agent 6 - Test Isolation Auditor:** NullHandler setup works correctly for the "game" namespace. BattleLogger and CombatLab have separate log namespaces but don't cause test issues in practice.

**Agent 7 - Broader Quality Auditor:** Found 7 files using `traceback.format_exc()` antipattern (should use `logger.exception()`). Found log level misuses where errors are logged at INFO. Found 1 bare except without logging.

### Risks Identified
1. **LOW** - traceback replacements are mechanical but need to preserve error context

---

## Phases

### Phase 1: Fix Inline Logger in strategy_renderer.py [Simple]
**Objective:** Add module-level logger and fix inline instantiation
**Status:** Not Started

#### Task 1.1: Add Module-Level Logger to strategy_renderer.py [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/ -k strategy --tb=short`
- [ ] Add `import logging` after existing imports (after line 19)
- [ ] Add `logger = logging.getLogger(__name__)` after imports
- [ ] Replace lines 655-656 (inline `import logging` + `logging.getLogger(__name__).warning(...)`) with `logger.warning(...)`
- [ ] Remove the inline `import logging` on line 655
- [ ] Run tests to verify no regressions
**Notes:**

---

### Phase 2: Replace traceback.format_exc() with logger.exception() [Simple]
**Objective:** Standardize exception logging across 7 files
**Status:** Not Started

#### Task 2.1: Fix ship_serialization.py [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/ --tb=short`
- [ ] At line 109-110, replace:
  ```python
  import traceback
  logger.error(traceback.format_exc())
  ```
  with:
  ```python
  logger.exception("Ship serialization error")
  ```
- [ ] Remove `import traceback` (inline import)
**Notes:**

#### Task 2.2: Fix save_game_service.py [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/ --tb=short`
- [ ] At line 16, remove top-level `import traceback`
- [ ] At line 109, replace `logger.error(f"SaveGameService: Serialization error - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Serialization error - {e}")`
- [ ] At line 112, replace `logger.error(f"SaveGameService: Unexpected save error - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Unexpected save error - {e}")`
- [ ] At line 224, replace `logger.error(f"SaveGameService: Unexpected load error from {save_path} - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Unexpected load error from {save_path} - {e}")`
**Notes:**

#### Task 2.3: Fix design_library.py [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/design_library/ --tb=short`
- [ ] At lines 105-106, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design scan error")`
- [ ] At lines 187-188, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design save error")`
- [ ] At lines 192-193, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design save error")`
**Notes:**

#### Task 2.4: Fix build_queue_controller.py [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue --tb=short`
- [ ] At lines 575-576, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Build queue error")`
**Notes:**

#### Task 2.5: Fix workshop_data_reloader.py [Simple]
**File:** `game/ui/screens/workshop_data_reloader.py`
**Tests:** `pytest tests/unit/ui/ -k workshop --tb=short`
- [ ] At lines 155-156, replace inline `import traceback` + `logger.error(f"Failed to reload data: {e}\n{traceback.format_exc()}")` with `logger.exception(f"Failed to reload data: {e}")`
**Notes:**

#### Task 2.6: Fix workshop_ship_io.py [Simple]
**File:** `game/ui/screens/workshop_ship_io.py`
**Tests:** `pytest tests/unit/ui/ -k workshop --tb=short`
- [ ] At lines 157-158, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Workshop ship I/O error")`
**Notes:**

---

### Phase 3: Fix Log Level Misuses [Simple]
**Objective:** Ensure error/failure conditions are logged at appropriate levels
**Status:** Not Started

#### Task 3.1: Fix validation_manager.py [Simple]
**File:** `game/ui/screens/test_lab/validation_manager.py`
**Tests:** `pytest tests/unit/ui/ -k validation --tb=short`
- [ ] At line 103, change `logger.info(f"  {test_id}: Validation error - {e}")` to `logger.warning(f"  {test_id}: Validation error - {e}")`
**Notes:**

#### Task 3.2: Fix galaxy_test/system_mode.py [Simple]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Tests:** `pytest tests/unit/ui/ -k galaxy --tb=short`
- [ ] At line 198, change `logger.info(f"Failed to load blueprints: {e}")` to `logger.warning(f"Failed to load blueprints: {e}")`
- [ ] At line 238, change `logger.info(f"Failed to load blueprint '{self.selected_blueprint}': {e}")` to `logger.warning(f"Failed to load blueprint '{self.selected_blueprint}': {e}")`
**Notes:**

#### Task 3.3: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify zero regressions
- [ ] Confirm baseline: 12338 passed, 1 skipped
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 12338 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify no inline `import logging` remains in strategy_renderer.py
- [ ] Verify zero `traceback.format_exc()` in game/ (except app.py crash handler)

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep confirms: zero `import traceback` in game/ except app.py
- [ ] Grep confirms: zero `traceback.format_exc()` in game/ except app.py
- [ ] Grep confirms: zero inline `logging.getLogger` calls (all module-level)
