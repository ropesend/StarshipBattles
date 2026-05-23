# Phase 1: CAT-9 simplification (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace remaining CAT-9 simplification patterns in UI-family tests. Inherited from PROJ-480 Phase 1.

Line refs below are **advisory** — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 1.1: test_save_selection.py — 3 setup_tmpdir wrappers
**File:** `tests/unit/ui/screens/test_save_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_save_selection.py`
**Origin:** PROJ-480 T1.5

- [ ] Replace the 3 per-class `setup_tmpdir` wrappers (PROJ-480 cited lines 65, 164, 241) with a single module-level autouse fixture. _(coordination note: tied to HLP-005 in PROJ-479 Phase 6; if HLP-005 sweep absorbs this, no separate action required.)_
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 1.2: test_strategy_input_handler_transfer.py — consolidate 3 mode-test classes (LARGEST single task)
**File:** `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Origin:** PROJ-480 T1.11

- [ ] Consolidate the 3 transfer/drop/load mode-test classes (PROJ-480 cited lines 44-275, ~230 LOC) into one parametrized class testing the shared key-sets-mode / left-click-opens-dialog / right-click-cancels / escape-cancels pattern.
- [ ] Verify: passes; LOC delta ≈ -150.

**Notes:** This is the single largest pending CAT-9 task across all of PROJ-480. Codex consult 2026-05-23 advised treating it as the first real execution phase milestone in this project. Do it FIRST in this phase — failure cost is lowest while context is freshest.

### Task 1.3a: test_colonization_facade.py — 8 in-method MockPlanetType defs
**File:** `tests/integration/ui/test_colonization_facade.py` (retargeted from PROJ-480's `tests/unit/strategy/services/test_colonization_facade.py`)
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py`
**Origin:** PROJ-480 T1.7

- [ ] Define a single `MockPlanetType(Enum)` at module level; remove the 8 inline definitions inside test methods. PROJ-480 cited lines 71, 377, 438, 488, 571, 625, 724, 787; Codex spot-check 2026-05-23 saw repeats at `:71, :380, :441, :494, :583, :642, :697, :751, :819`. _(coordination note: tied to HLP-002 in PROJ-479 Phase 6. If shared `tests/fixtures/colonization_fixtures.py` is created first, import from there.)_
- [ ] Verify: passes; LOC delta ≈ -30.

**Notes:** File-location category check: if the test body has zero UI/pygame interaction (only colonization facade logic), this may belong in PROJ-496 (non-UI integration). Phase 0 should make the call.

### Task 1.3: test_race_setup_screen.py — repeated inline mock function defs
**File:** `tests/unit/ui/screens/test_race_setup_screen.py` (retargeted from PROJ-480's `tests/unit/ui/test_race_setup_screen.py`)
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`
**Origin:** PROJ-480 T1.14

- [ ] Extract shared fixtures for the inline mock function definitions repeated in 4+ tests. PROJ-480 cited lines 155-167, 173-190, 304-309, 345-352. Codex spot-check 2026-05-23 saw repeats at `:155, :173, :305, :321, :345, :365, :380` — Phase 0 must re-grep to confirm.
- [ ] Verify: passes; LOC delta ≈ -40.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (CAT-8 needless complexity)
