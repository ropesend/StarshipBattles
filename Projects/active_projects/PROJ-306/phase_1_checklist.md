# Phase 1: Eliminate `battle_runner` fallback

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-306 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete `_default_ship_builder_from_context()` in `battle_runner.py`. Migrate every production caller of `run_battle` / `BattleController.start_from_spec` to pass `ship_builder` explicitly (or fetch it from `ApplicationContext` themselves).

---

## Tasks

### Task 1.1: Survey all callers [Simple]
**File:** Investigation only — output to `Projects/active_projects/PROJ-306/findings/caller_inventory.md`
**Tests:** None.

- [ ] `grep -rn "run_battle\|start_from_spec" game/ tests/ combat_lab/` — list every call site
- [ ] For each, record: file:line, whether `ship_builder` is currently passed, whether the caller already imports `get_default_ship_materializer` from `ApplicationContext`
- [ ] Categorize callers as:
  - **A — already passes `ship_builder` explicitly** (no action needed)
  - **B — relies on the fallback** (must be migrated)
- [ ] Save inventory to `findings/caller_inventory.md`

**Notes:**

---

### Task 1.2: Choose the migration pattern [Simple]
**File:** Update `decisions.md` with final choice
**Tests:** None.

Two viable patterns:
- **Pattern A — required parameter:** make `ship_builder` non-Optional; every caller must pass it
- **Pattern B — context fetch:** in `run_battle` / `BattleController.start_from_spec`, replace the `_default_ship_builder_from_context()` call with an inline `get_default_ship_materializer()` lookup (same as line 197 already does for the materializer)

- [ ] Read inventory from Task 1.1
- [ ] If most B-callers exist → Pattern B (less churn)
- [ ] If only a couple of B-callers exist → Pattern A (cleaner DI)
- [ ] Record the choice in `decisions.md`

**Notes:**

---

### Task 1.3: TDD — write a regression test for the chosen pattern [Simple]
**File:** `tests/unit/simulation/test_battle_runner_di.py` (NEW or extend existing)
**Tests:** Run after writing — should fail.

- [ ] Write a test asserting that `run_battle` (or `BattleController.start_from_spec`) functions correctly when called with the new contract
- [ ] If Pattern A: also write a test confirming `TypeError` (missing required arg) when `ship_builder` is omitted
- [ ] Run the test — confirm appropriate failure mode

**Notes:**

---

### Task 1.4: Migrate B-callers [Medium]
**File:** Per inventory from Task 1.1
**Tests:** Targeted tests for each caller

- [ ] For each B-caller in the inventory, apply the chosen pattern
- [ ] Run targeted tests after each change
- [ ] Re-grep `run_battle` / `start_from_spec` calls — all should now pass `ship_builder` (Pattern A) or no longer matter (Pattern B)

**Notes:**

---

### Task 1.5: Delete the fallback function [Simple]
**File:** `game/simulation/battle_runner.py` (lines ~170-220)
**Tests:** Full targeted suite for `tests/unit/simulation/`

- [ ] Delete `_default_ship_builder_from_context()` outright
- [ ] Delete the `from game.core.registry import get_default_registry_provider` import (now unused)
- [ ] If Pattern B: replace its call site (was the line where `_default_ship_builder_from_context()` was invoked) with the chosen replacement
- [ ] **Verification:** `grep -n "_default_ship_builder_from_context\|get_default_registry_provider" game/simulation/battle_runner.py` returns zero results
- [ ] **Verification:** `python -c "from game.simulation.battle_runner import _default_ship_builder_from_context"` raises `ImportError`
- [ ] Run targeted tests — all pass

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "get_default_registry_provider" game/simulation/battle_runner.py` returns zero results
- [ ] All B-callers from Task 1.1 inventory updated
- [ ] Targeted suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
