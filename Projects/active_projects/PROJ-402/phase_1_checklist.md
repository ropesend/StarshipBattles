# Phase 1: Catch ValidationException + restore the originally-required test

**Status:** Not Started
**Objective:** Make `SimulationBattleResolver` preserve battle context for both exception types `run_battle` can raise, and pin the missing case with a regression test.

---

## Tasks

### Task 1.1: Read the wrapper and the underlying raisers [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py:280-310`, `game/simulation/battle_runner.py:630-660`

- [ ] Read the current `try/except` block in `SimulationBattleResolver`.
- [ ] Read where `run_battle` raises `ValidationException` to confirm it's the same class as imported in the adapter (or where it's importable from).
- [ ] Confirm the import path for `ValidationException` (likely `game.core.exceptions` or similar).

**Notes:**

### Task 1.2: TDD — write the originally-required regression test [Medium]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v`

- [ ] Replace the substituted "custom SimulationException" test (around line 391-404) with one that:
  - patches `run_battle` to raise `ValidationException("invalid component")`.
  - asserts `BattleResolutionError` is raised (not raw `ValidationException`).
  - asserts the wrapped error carries `fleet_ids`, `empire_ids`, `hex_coord` in its context.
- [ ] Run the test against unmodified production — confirm it fails (raw `ValidationException` propagates).
- [ ] Keep an additional test (or assertion) that exercises the existing `SimulationException` path so we don't lose that coverage.

**Notes:**

### Task 1.3: Widen the catch tuple [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py:292-300`

- [ ] Change `except SimulationException as e:` to `except (SimulationException, ValidationException) as e:`.
- [ ] Add an import for `ValidationException` if not already present.
- [ ] Run the regression test from Task 1.2 — should now pass.
- [ ] Run the full module — should pass.

**Notes:**

### Task 1.4: Cross-check no other adapters need the same fix
**Tests:** `rg -n "except SimulationException" game/strategy/adapters/`

- [ ] Search shows zero remaining bare `except SimulationException:` catches in adapters that wrap `run_battle`.
- [ ] If any exist with the same exposure, narrow scope is OK — flag them in `decisions.md` for follow-up but do not expand the project here.

**Notes:**

### Task 1.5: Closeout
- [ ] Update Phase 1 status to `Complete`
- [ ] Update plan.md Quick Status + Current State
- [ ] Update `Projects/projects_index.md` row for PROJ-402 to `Complete`
- [ ] Validators pass
- [ ] Commit `PROJ-402 phase 1: SimulationBattleResolver wraps ValidationException + restored regression`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] `pytest tests/unit/strategy/adapters/test_simulation_adapter.py` passes
- [ ] `python Projects/scripts/validate_phase.py PROJ-402 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-402` PASSED
