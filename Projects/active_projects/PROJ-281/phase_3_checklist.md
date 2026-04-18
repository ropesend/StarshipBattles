# Phase 3: Delete `BattleScreen.start()` shim + `_build_fallback_outcome`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete the deprecated `BattleScreen.start(team0, team1)` method and the `_build_fallback_outcome` helper (~90 LOC) now that Phase 2 has migrated every caller. After Phase 3, `BattleScreen` has exactly one entry: `start_battle(controller)` consuming a running `BattleController`.

**Prerequisite:** Phase 2 complete — zero callers of `BattleScreen.start(team0, team1)` remain in production or test code.

---

## Tasks

### Task 3.1: Pre-deletion verification [Simple]
**File:** N/A
**Tests:** Full PROJ-281 scope + Combat Lab simulation

- [ ] Grep `BattleScreen.start(` across `game/` and `tests/` — confirm only the method definition at `game/ui/screens/battle_screen.py:227` remains (plus historical docs)
- [ ] Grep `scene\.start(\[`, `screen\.start(\[` across all test files — zero hits (Phase 2 should have eliminated all)
- [ ] Grep `_build_fallback_outcome` — map every caller
- [ ] Grep `test_unified_entry_guard.py` for any tests that check the shim's presence — these may need updating in Task 3.4

**Notes:** If any callers remain, STOP and complete Phase 2 first. Deleting the shim before migration is complete would break CI.

### Task 3.2: Delete `BattleScreen.start()` method [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Locate the `start(self, team0_ships, team1_ships, seed=None, headless=False, start_paused=False, test_mode=False)` method (starts at line 227)
- [ ] Delete the entire method body including docstring
- [ ] Verify no internal references to it remain inside `BattleScreen` itself (private helpers used only by `start()`)
- [ ] Run `pytest tests/unit/ui/` — verify nothing breaks unexpectedly

**Notes:**

### Task 3.3: Delete `_build_fallback_outcome()` and companions [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Locate `_build_fallback_outcome` method (~90 LOC per project plan estimate)
- [ ] Delete the method + any private helpers it uses exclusively
- [ ] Verify `_on_battle_ended` (or equivalent) no longer has a branch for "no spec attached" — the fallback path no longer exists
- [ ] Any comments referencing "legacy test-convenience shim" / "pre-spec-contract callers" should be deleted too
- [ ] Run `pytest tests/unit/ui/`

**Notes:** Check whether `_build_fallback_outcome` is also referenced by `test_unified_entry_guard.py` — that guard test may need updating (Task 3.4).

### Task 3.4: Update unified-entry guard test [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Read the current state of the guard — there's a test around line 565 that documents the shim's retention
- [ ] Update the test to enforce the NEW contract: `BattleScreen.start(team0_ships, ...)` MUST NOT exist; `_build_fallback_outcome` MUST NOT exist; `BattleScreen` has exactly one `start_battle(controller)` entry
- [ ] Flip the assertion direction where needed

**Notes:** The existing guard was a "this-is-retained-intentionally" marker. After Phase 3 it becomes a "this-is-deleted-intentionally" marker. Preserve the institutional knowledge in the test's docstring.

### Task 3.5: Regression sweep [Simple]
**Tests:** Full affected scope

- [ ] `pytest tests/unit/ui/ tests/unit/simulation/ tests/unit/combat_lab/ tests/unit/test_lab/` — all pass
- [ ] Combat Lab simulation: `python -m combat_lab.run_tests --fast` — 162 passed / 0 failed / 0 skipped
- [ ] Line-count check: `wc -l game/ui/screens/battle_screen.py` — should be ~90 LOC less than before

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BattleScreen.start(team0, team1)` DELETED
- [ ] `_build_fallback_outcome` DELETED
- [ ] `BattleScreen` has exactly ONE production entry: `start_battle(controller)`
- [ ] Unified-entry guard test updated to enforce the deletion
- [ ] Full regression sweep passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4 (documentation)
