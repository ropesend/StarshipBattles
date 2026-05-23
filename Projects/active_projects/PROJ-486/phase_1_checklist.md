# Phase 1: Delete `load_state` + migrate 4 test callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-486 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete the ~87-LOC `BattleController.load_state` method and reconcile the 4 test callers in `test_state.py`.

---

## Tasks

### Task 1.1: Reconcile 4 test callers of `load_state`
**File:** `tests/unit/simulation/battle_controller/test_state.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/test_state.py`

- [ ] Read each `load_state` invocation at `test_state.py:90, 128, 245, 268`
- [ ] For each: decide whether the test is exercising save/restore round-trip behavior (in which case it's testing dead code and should be deleted) OR asserting against a contract that should be preserved on `save_state` (in which case migrate to construct a new `BattleController` and assert on `save_state` output directly)
- [ ] Record the disposition of each test in this checklist's Notes section below before deleting

### Task 1.2: Delete `BattleController.load_state` from production
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Delete `BattleController.load_state` at `game/simulation/battle_controller.py:509-595` (~87 LOC) — line refs refreshed post-merge `67116932d`
- [ ] Also delete the inline note at line 510 if it references zero callers
- [ ] If `save_state` documents anything about `load_state`-side reconstruction (e.g. in its docstring), update that docstring to reflect that `load_state` is gone

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] `grep -rn "\.load_state\b" game/simulation/battle_controller` returns 0 matches for `BattleController.load_state` (other `load_state` methods on unrelated classes are unaffected)
- [ ] `grep -rn "BattleController.*load_state\|load_state.*BattleController" .` returns 0 matches

**Notes (fill in during Task 1.1):**
- test_state.py:90 — [disposition]
- test_state.py:128 — [disposition]
- test_state.py:245 — [disposition]
- test_state.py:268 — [disposition]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
