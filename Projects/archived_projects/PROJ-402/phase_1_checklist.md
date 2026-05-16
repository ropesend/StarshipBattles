# Phase 1: Catch ValidationException + restore the originally-required test

**Status:** Complete
**Objective:** Make `SimulationBattleResolver` preserve battle context for both exception types `run_battle` can raise, and pin the missing case with a regression test.

---

## Tasks

### Task 1.1: Read the wrapper and the underlying raisers [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py:280-310`, `game/simulation/battle_runner.py:630-660`

- [x] Read the current `try/except` block in `SimulationBattleResolver`.
- [x] Read where `run_battle` raises `ValidationException` to confirm it's the same class as imported in the adapter (or where it's importable from).
- [x] Confirm the import path for `ValidationException` (likely `game.core.exceptions` or similar).

**Notes:** Confirmed both classes live at `game.core.exceptions` (`ValidationException` at line 145; `SimulationException` already imported there). Wrapper had a function-local lazy import — extended it to also import `ValidationException`.

### Task 1.2: TDD — write the originally-required regression test [Medium]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v`

- [x] Replace the substituted "custom SimulationException" test (around line 391-404) with one that:
  - patches `run_battle` to raise `ValidationException("invalid component")`.
  - asserts `BattleResolutionError` is raised (not raw `ValidationException`).
  - asserts the wrapped error carries `fleet_ids`, `empire_ids`, `hex_coord` in its context.
- [x] Run the test against unmodified production — confirm it fails (raw `ValidationException` propagates).
- [x] Keep an additional test (or assertion) that exercises the existing `SimulationException` path so we don't lose that coverage.

**Notes:** RED confirmed before fix: `game.core.exceptions.ValidationException: invalid component` propagated unwrapped. Kept the original `_BoomSim` `SimulationException` subclass test as a sibling test method `test_simulation_exception_wrapped_with_battle_context`.

### Task 1.3: Widen the catch tuple [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py:292-300`

- [x] Change `except SimulationException as e:` to `except (SimulationException, ValidationException) as e:`.
- [x] Add an import for `ValidationException` if not already present.
- [x] Run the regression test from Task 1.2 — should now pass.
- [x] Run the full module — should pass.

**Notes:** 19/19 tests pass in `tests/unit/strategy/adapters/test_simulation_adapter.py` after the fix.

### Task 1.4: Cross-check no other adapters need the same fix
**Tests:** `rg -n "except SimulationException" game/strategy/adapters/`

- [x] Search shows zero remaining bare `except SimulationException:` catches in adapters that wrap `run_battle`.
- [x] If any exist with the same exposure, narrow scope is OK — flag them in `decisions.md` for follow-up but do not expand the project here.

**Notes:** Grep returned zero matches under `game/strategy/adapters/` after the fix — `simulation_adapter.py` was the only call site; no follow-up needed.

### Task 1.5: Closeout
- [x] Update Phase 1 status to `Complete`
- [x] Update plan.md Quick Status + Current State
- [x] Update `Projects/projects_index.md` row for PROJ-402 to `Complete`
- [x] Validators pass
- [x] Commit `PROJ-402 phase 1: SimulationBattleResolver wraps ValidationException + restored regression`

**Notes:** See `findings/verification_report.md` for full closeout details.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] `pytest tests/unit/strategy/adapters/test_simulation_adapter.py` passes
- [x] `python Projects/scripts/validate_phase.py PROJ-402 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-402` PASSED
