# Phase 1: Fix call site + add construction-path coverage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-400 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate the production `AttributeError` path in `NewGameSetupScreen._create_ui()` and add a regression test that catches missing-static blind spots in the future.

---

## Tasks

### Task 1.1: Read the call sites and confirm canonical fix [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:348`
**Tests:** N/A (read-only)

- [x] Read `game/ui/screens/new_game_setup_screen.py:340-360` to see the surrounding `_create_ui()` body and what `self` provides.
- [x] Read `game/ui/screens/new_game_setup_controller.py` for the canonical `generate_default_save_name(...)` signature and required arguments.
- [x] Confirm whether the screen has a controller attribute (e.g. `self._controller`, `self.controller`) already, or whether the static helper should be called via the class (`NewGameSetupController.generate_default_save_name(...)`).
- [x] Document the chosen call shape in `decisions.md`.

**Notes:** Controller is at `self._controller` (line 171). `generate_default_save_name` is a `@staticmethod` taking no args (controller.py:268-271). Chose the class-static call form `NewGameSetupController.generate_default_save_name()` to mirror the existing `NewGameSetupController.validate_save_name(...)` pattern at line 162 of the same file — same import already present at line 66, no instance dependency.

### Task 1.2: TDD — write failing regression test [Medium]
**File:** `tests/unit/ui/screens/test_new_game_setup_screen.py` (or the closest existing test module — check first)
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v`

- [x] Find an existing test module that already constructs `NewGameSetupScreen` or routes through `NewGameSetupUiBuilder.build(...)`. If none exists, create one.
- [x] Write a test that builds the screen far enough that `_create_ui()` actually runs (the bug only triggers during widget construction, not import). It should fail with `AttributeError: 'NewGameSetupScreen' object has no attribute 'generate_default_save_name'` on the unfixed code.
- [x] Run the test and confirm it fails for the expected reason. Do not skip this confirmation step — TDD requires seeing the red.

**Notes:** Extended `tests/unit/ui/screens/test_new_game_setup_extended.py` with class `TestCreateUiConstructionPath` (2 tests). Existing fixture path uses `bypass_init` + `MockNewGameSetupUiBuilder` which never calls `_create_ui` — so the new tests build with `NullNewGameSetupUiBuilder`, mock `screen.get_container()` + patch `pygame_gui.elements` constructors to MagicMocks, then invoke `screen._create_ui()` directly. RED confirmed: `AttributeError: 'NewGameSetupScreen' object has no attribute 'generate_default_save_name'` at `new_game_setup_screen.py:348`. Verified via `pytest tests/unit/ui/screens/test_new_game_setup_extended.py::TestCreateUiConstructionPath -v`.

### Task 1.3: Implement the fix [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:348`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v`

- [x] Replace `self.generate_default_save_name()` with the canonical controller call decided in Task 1.1.
- [x] Verify the replacement uses the canonical argument shape (the controller version is the one PROJ-392 migrated tests + other callers to).
- [x] Run the focused test from Task 1.2 — should now pass.
- [x] Run `pytest tests/ -k new_game_setup` — should pass without regressions.

**Notes:** Replaced line 348 with `NewGameSetupController.generate_default_save_name()` (no args). Same import already at module top (line 66). Focused TDD pair GREEN. `pytest tests/ -k new_game_setup -q` → 104 passed in 9.47s, zero regressions.

### Task 1.4: Search for any other unmigrated `self.generate_default_save_name` / `self.validate_save_name` callers [Simple]
**File:** repo-wide
**Tests:** N/A

- [x] `rg -n "self\.generate_default_save_name|self\.validate_save_name" game/` — should return zero hits after the fix.
- [x] If any hit appears, repeat the same migration pattern.

**Notes:** Grep against `game/` returned zero matches — the deleted-static blind spot was a single site.

### Task 1.5: Update plan + close phase
**Tests:** `python Projects/scripts/validate_phase.py PROJ-400 1` then `python Projects/scripts/validate_audit_ready.py PROJ-400`

- [x] Update Phase 1 status to `Complete` at top of this file.
- [x] Update plan.md Quick Status row + Current State.
- [x] Update `Projects/projects_index.md` row for PROJ-400 to `Complete`.
- [x] Both validators pass.
- [x] Commit with message format `PROJ-400 phase 1: fix _create_ui call to deleted generate_default_save_name + regression`.

**Notes:** All artefacts updated; validators run post-commit step.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase or closeout
- [x] `pytest tests/ -k new_game_setup` passes (post-fix, post-regression-test)
- [x] `python Projects/scripts/validate_phase.py PROJ-400 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-400` PASSED
