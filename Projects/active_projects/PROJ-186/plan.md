# PROJ-186: Exception Handling Polish - ErrorCode Consistency and Final Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-186` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-186 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Replace String Codes with ErrorCode Enums | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix Stale Docstrings | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Exception Chaining and Re-raise | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fix Error Code Semantics | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - Added `from e` to ship_loader.py, fixed `raise e` to `raise` in app.py
**Next Action:** Phase 4 - Fix Error Code Semantics
**Blockers:** None
**Baseline:** 12,366 passed, 1 skipped, 0 failures

## Overview
PROJ-170/PROJ-177 successfully migrated exception handling to domain-specific exceptions. However, an independent 8-agent swarm review identified 19 remaining consistency issues: 12 sites using hard-coded string error codes instead of ErrorCode enums, 2 stale docstrings, 1 missing exception chain, 1 improper re-raise, and 3 sites using semantically incorrect error codes.

## Goals
- Replace all 12 hard-coded string error codes with `ErrorCode.<ENUM>.value` references
- Fix 2 remaining stale docstrings referencing old exception types
- Add missing `from e` exception chaining in ship_loader.py
- Fix `raise e` to bare `raise` in app.py crash handler
- Correct 3 semantically mismatched error codes

## Scope
**In:**
- 12 string-code-to-enum conversions across 4 files
- 2 stale docstring fixes across 2 files
- 1 missing exception chain fix (ship_loader.py)
- 1 improper re-raise fix (app.py)
- 3 error code semantic corrections across 3 files

**Out:**
- 20 protective tuple catches (confirmed legitimate by all 8 agents)
- 3 generic raises (`NotImplementedError` x2, `TypeError` in `__init_subclass__`) - legitimate Python protocols
- All broad `except Exception` catches (confirmed properly logged with justification comments)
- Module-level docstring in resources.py (informational, not a Raises: section - debatable)

## Key Files
| Component | File Path | Issues |
|-----------|-----------|--------|
| Battle Controller | `game/simulation/battle_controller.py` | 2 string codes ("S001") |
| Projectile | `game/simulation/entities/projectile.py` | 3 string codes ("V003") |
| Modifier Effects | `game/simulation/components/modifier_effects.py` | 4 string codes ("F001"-"F004") |
| Game Session | `game/strategy/engine/game_session.py` | 3 string codes ("P001"-"P003") + stale docstring |
| Resources | `game/core/resources.py` | Stale module docstring |
| Ship Loader | `game/simulation/entities/ship_loader.py` | Missing `from e` |
| App | `game/app.py` | `raise e` → bare `raise` |
| Battle Engine | `game/simulation/systems/battle_engine.py` | 3 wrong error codes |
| Battle State Manager | `game/simulation/managers/battle_state_manager.py` | 1 wrong error code |
| Build Queue Screen | `game/ui/screens/build_queue_screen.py` | 1 wrong error code |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | All 5 categories of issues in scope | User confirmed: string codes, stale docstrings, missing chaining, bad re-raise, wrong semantics |
| 2026-02-24 | resources.py module docstring OUT of scope | It's informational ("Exceptions:"), not a function Raises: section. Describes what the module handles, not what it raises. |
| 2026-02-24 | 20 protective tuple catches confirmed OUT of scope | All 8 agents independently confirmed these guard legitimate stdlib/JSON/deserialization boundaries |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- PROJ-170 plan - Original exception handling migration
- PROJ-177 plan - First cleanup pass

---

## Phases

### Phase 1: Replace String Codes with ErrorCode Enums [Simple]
**Objective:** Convert all 12 hard-coded string error codes to `ErrorCode.<ENUM>.value` references.
**Status:** Complete

#### Task 1.1: Fix battle_controller.py string codes [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ -n 4`
- [ ] Line 260: Change `code="S001"` to `code=ErrorCode.STATE_FROZEN.value`
- [ ] Line 446: Change `code="S001"` to `code=ErrorCode.STATE_FROZEN.value`
- [ ] Verify `ErrorCode` is already imported, or add: `from game.core.error_codes import ErrorCode`
**Notes:**

#### Task 1.2: Fix projectile.py string codes [Simple]
**File:** `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/entities/ -k projectile`
- [ ] Line 32: Change `code="V003"` to `code=ErrorCode.MISSING_ENTITY.value`
- [ ] Line 38: Change `code="V003"` to `code=ErrorCode.MISSING_ENTITY.value`
- [ ] Line 45: Change `code="V003"` to `code=ErrorCode.MISSING_ENTITY.value`
- [ ] Verify `ErrorCode` is already imported, or add: `from game.core.error_codes import ErrorCode`
- [ ] NOTE: V003 = MISSING_ENTITY. However, the context is "invalid projectile damage/range/endurance" which is really OUT_OF_RANGE (V004). **Decision needed:** Use V003 (MISSING_ENTITY) to match existing string, or V004 (OUT_OF_RANGE) for semantic correctness? Recommend V004.
**Notes:**

#### Task 1.3: Fix modifier_effects.py string codes [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/ -k modifier`
- [ ] Line 163: Change `code="F001"` to `code=ErrorCode.FORMULA_SYNTAX_ERROR.value`
- [ ] Line 169: Change `code="F002"` to `code=ErrorCode.FORMULA_UNDEFINED_VAR.value`
- [ ] Line 175: Change `code="F003"` to `code=ErrorCode.EVAL_ERROR.value`
- [ ] Line 181: Change `code="F004"` to `code=ErrorCode.FORMULA_GENERAL_ERROR.value`
- [ ] Verify `ErrorCode` is already imported, or add: `from game.core.error_codes import ErrorCode`
**Notes:**

#### Task 1.4: Fix game_session.py string codes [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/test_game_session.py`
- [ ] Line 301: Change `code="P001"` to `code=ErrorCode.SAVE_FAILED.value`
- [ ] Line 322: Change `code="P002"` to `code=ErrorCode.LOAD_FAILED.value`
- [ ] Line 336: Change `code="P003"` to `code=ErrorCode.CORRUPT_DATA.value`
- [ ] Add import at line 288 (inside from_dict): `from game.core.error_codes import ErrorCode`
**Notes:** The import can go alongside the existing `from game.core.exceptions import PersistenceException`

#### Task 1.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12,366 tests pass
- [ ] No new warnings
- [ ] Grep confirms: `grep -rn 'code="[A-Z][0-9]' game/` returns 0 results
**Notes:**

---

### Phase 2: Fix Stale Docstrings [Simple]
**Objective:** Update 2 docstrings that reference old generic exception types.
**Status:** Not Started

#### Task 2.1: Fix game_session.py from_dict() docstring [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** No test changes needed
- [ ] Lines 284-286: Change:
  ```
  Raises:
      KeyError: If required fields (config, galaxy, empires) are missing.
      TypeError: If data structures are invalid.
  ```
  To:
  ```
  Raises:
      PersistenceException: If required fields are missing or data structures are invalid.
  ```
**Notes:**

#### Task 2.2: Fix resources.py module docstring [Simple]
**File:** `game/core/resources.py`
**Tests:** No test changes needed
- [ ] Lines 6-10: Change:
  ```
  Exceptions:
      FileNotFoundError: File not found (handled with fallback to defaults)
      json.JSONDecodeError: Invalid JSON (handled with fallback to defaults)
      PermissionError: Cannot read file (handled with fallback to defaults)
      TypeError: Malformed data structure (handled with fallback to defaults)
  ```
  To:
  ```
  Error Handling:
      All loading errors (FileNotFoundError, JSONDecodeError, PermissionError,
      TypeError) are caught and logged, with graceful fallback to default resources.
  ```
**Notes:** This is an informational module docstring. Reword to clarify these are handled, not raised.

---

### Phase 3: Fix Exception Chaining and Re-raise [Simple]
**Objective:** Fix 1 missing exception chain and 1 improper re-raise.
**Status:** Complete

#### Task 3.1: Add missing `from e` in ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/ -k ship_loader`
- [ ] Lines 95-100: Change:
  ```python
  except FileNotFoundError:
      raise MissingResourceException(
  ```
  To:
  ```python
  except FileNotFoundError as e:
      raise MissingResourceException(
          ...
      ) from e
  ```
**Notes:**

#### Task 3.2: Fix `raise e` in app.py [Simple]
**File:** `game/app.py`
**Tests:** Manual verification (crash handler)
- [ ] Line 718: Change `raise e` to `raise`
**Notes:** Bare `raise` preserves the original traceback. `raise e` creates a new traceback.

#### Task 3.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All tests pass
**Notes:**

---

### Phase 4: Fix Error Code Semantics [Simple]
**Objective:** Correct 5 sites where the wrong ErrorCode is used for the situation.
**Status:** Not Started

#### Task 4.1: Fix battle_engine.py - NOT_INITIALIZED → MISSING_DEPENDENCY [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/ -k battle_engine`
- [ ] Line 273: Change `ErrorCode.NOT_INITIALIZED.value` to `ErrorCode.MISSING_DEPENDENCY.value`
- [ ] Line 325: Change `ErrorCode.NOT_INITIALIZED.value` to `ErrorCode.MISSING_DEPENDENCY.value`
- [ ] Line 473: Change `ErrorCode.NOT_INITIALIZED.value` to `ErrorCode.MISSING_DEPENDENCY.value`
- [ ] Verify ErrorCode import is present
**Notes:** These raise when AI configuration (ai_controllers, ai_factory) is not injected. That's a missing dependency, not an uninitialized state.

#### Task 4.2: Fix battle_state_manager.py - INVALID_STATE with ValidationException [Simple]
**File:** `game/simulation/managers/battle_state_manager.py`
**Tests:** `pytest tests/unit/simulation/managers/ -k battle_state_manager`
- [ ] Line 87: Change `ErrorCode.INVALID_STATE.value` to `ErrorCode.VALIDATION_FAILED.value`
**Notes:** This catches a ValueError from enum conversion and re-raises as ValidationException. The error code should match the exception class (validation).

#### Task 4.3: Fix build_queue_screen.py - INVALID_STATE for validation [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue`
- [ ] Line 180: Change `ErrorCode.INVALID_STATE.value` to `ErrorCode.SCHEMA_VALIDATION_ERROR.value`
**Notes:** This validates that `build_context` has required attributes. That's schema/structural validation, not a state error.

#### Task 4.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12,366 tests pass
- [ ] No new warnings
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 12,366 passed, 1 skipped (baseline established 2026-02-24)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new warnings related to exception handling

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep confirms no string codes: `grep -rn 'code="[A-Z][0-9]' game/` returns 0 results
- [ ] Grep confirms all ErrorCode usage: `rg "ErrorCode\." game/` count matches or exceeds baseline
- [ ] No stale docstrings referencing generic exceptions in Raises: sections

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 | 2026-02-24 | Independent 8-agent swarm review identified 19 issues across 5 categories | This project created |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
