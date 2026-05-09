# Phase 1: Fix call site + add construction-path coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-400 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the production `AttributeError` path in `NewGameSetupScreen._create_ui()` and add a regression test that catches missing-static blind spots in the future.

---

## Tasks

### Task 1.1: Read the call sites and confirm canonical fix [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:348`
**Tests:** N/A (read-only)

- [ ] Read `game/ui/screens/new_game_setup_screen.py:340-360` to see the surrounding `_create_ui()` body and what `self` provides.
- [ ] Read `game/ui/screens/new_game_setup_controller.py` for the canonical `generate_default_save_name(...)` signature and required arguments.
- [ ] Confirm whether the screen has a controller attribute (e.g. `self._controller`, `self.controller`) already, or whether the static helper should be called via the class (`NewGameSetupController.generate_default_save_name(...)`).
- [ ] Document the chosen call shape in `decisions.md`.

**Notes:**

### Task 1.2: TDD — write failing regression test [Medium]
**File:** `tests/unit/ui/screens/test_new_game_setup_screen.py` (or the closest existing test module — check first)
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v`

- [ ] Find an existing test module that already constructs `NewGameSetupScreen` or routes through `NewGameSetupUiBuilder.build(...)`. If none exists, create one.
- [ ] Write a test that builds the screen far enough that `_create_ui()` actually runs (the bug only triggers during widget construction, not import). It should fail with `AttributeError: 'NewGameSetupScreen' object has no attribute 'generate_default_save_name'` on the unfixed code.
- [ ] Run the test and confirm it fails for the expected reason. Do not skip this confirmation step — TDD requires seeing the red.

**Notes:**

### Task 1.3: Implement the fix [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:348`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v`

- [ ] Replace `self.generate_default_save_name()` with the canonical controller call decided in Task 1.1.
- [ ] Verify the replacement uses the canonical argument shape (the controller version is the one PROJ-392 migrated tests + other callers to).
- [ ] Run the focused test from Task 1.2 — should now pass.
- [ ] Run `pytest tests/ -k new_game_setup` — should pass without regressions.

**Notes:**

### Task 1.4: Search for any other unmigrated `self.generate_default_save_name` / `self.validate_save_name` callers [Simple]
**File:** repo-wide
**Tests:** N/A

- [ ] `rg -n "self\.generate_default_save_name|self\.validate_save_name" game/` — should return zero hits after the fix.
- [ ] If any hit appears, repeat the same migration pattern.

**Notes:**

### Task 1.5: Update plan + close phase
**Tests:** `python Projects/scripts/validate_phase.py PROJ-400 1` then `python Projects/scripts/validate_audit_ready.py PROJ-400`

- [ ] Update Phase 1 status to `Complete` at top of this file.
- [ ] Update plan.md Quick Status row + Current State.
- [ ] Update `Projects/projects_index.md` row for PROJ-400 to `Complete`.
- [ ] Both validators pass.
- [ ] Commit with message format `PROJ-400 phase 1: fix _create_ui call to deleted generate_default_save_name + regression`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase or closeout
- [ ] `pytest tests/ -k new_game_setup` passes (post-fix, post-regression-test)
- [ ] `python Projects/scripts/validate_phase.py PROJ-400 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-400` PASSED
