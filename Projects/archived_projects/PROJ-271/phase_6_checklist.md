# Phase 6: Fix Phase 5 hardening live-path miss (audit follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (targeted fix)
**Depends On:** None — independent hardening
**Objective:** Narrow `BattleStateCapture._capture_state` class-method `except Exception` to `except OSError`. Phase 5 narrowed the module-level `capture_battle_state()` but missed the class method — which is the LIVE production path invoked by `test_executor.py:247` via the context manager.

## Context

Architecture skeptic audit (2026-04-13) found C1: Phase 5 hardening missed the live path. The module-level `capture_battle_state()` was narrowed, but the `BattleStateCapture` class (context manager) uses its own `_capture_state` method at `combat_lab/battle_state_capture.py:267` with the same broad `except Exception` pattern that swallowed the `mode=` TypeError for months. The live caller at `game/ui/screens/test_lab/test_executor.py:247` uses the class, not the function. Same failure mode still possible.

## Tasks

### Task 6.1: Failing test for class-method narrowing [Simple]
**File:** `tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py`
**Tests:** `pytest tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py --tb=short`

- [x] Added `test_battle_state_capture_class_method_does_not_swallow_programming_errors` — text-guard on `_capture_state` body.
- [x] Added `test_battle_state_capture_class_method_propagates_type_error` — behavioral: `BattleStateCapture(BrokenEngine())._capture_state("final")` must raise `AttributeError`/`TypeError`, not return None.
- [x] Run — 2 new tests FAIL for the right reason (class method still uses `except Exception`).

**Notes:** Mirror of Phase 5.3 guards but targeting the class method.

### Task 6.2: Narrow the class-method except [Simple]
**File:** `combat_lab/battle_state_capture.py`

- [x] Change `except Exception as e:` at line 289 → `except OSError as e:`.
- [x] Update warning message to reference disk IO.
- [x] Add comment citing PROJ-271 Phase 6 + audit finding C1.
- [x] Run — 7/7 tests green in `test_battle_state_capture_no_mode_kwarg.py` (7 tests, all passing).

**Notes:** The class-method narrowing is semantically identical to the function narrowing in Phase 5 — the rationale and failure modes are the same.

## Phase Completion Checklist

- [x] All task checkboxes above are checked
- [x] Guard tests cover BOTH the module function AND the class method
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Regression gate: Phase 6 tests green; no broader regressions expected (targeted change)
