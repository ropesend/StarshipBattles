# Phase 5: TestRunDetailsPanel.draw (CC 47 → ≤8)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract drawing sections into focused sub-methods

---

## Tasks

### Task 5.1: Extract `_draw_header_and_status(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] Move lines 133-145 (run info header, status PASSED/FAILED) into it
- [x] Returns updated y_offset
- [x] Verify tests

**Notes:** Extracted method handles timestamp formatting, header text, and PASSED/FAILED status display.

### Task 5.2: Extract `_draw_metadata(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] Move lines 147-161 (seed display, ticks display) into it
- [x] Returns updated y_offset
- [x] Verify tests

**Notes:** Extracts seed and ticks display with conditional positioning.

### Task 5.3: Extract `_draw_action_buttons(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] Move lines 163-244 (View States, Use Seed, Copy Results buttons) into it
- [x] All 3 buttons share pattern: conditional display + hover + render
- [x] Returns updated y_offset
- [x] Verify tests

**Notes:** CC 15 for this method due to conditional button visibility and positioning logic. All button state management remains intact.

### Task 5.4: Extract `_draw_metrics(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] Move lines 256-273 (metrics title + loop) into it
- [x] Returns updated y_offset
- [x] Verify tests

**Notes:** CC 5 - simple loop with value formatting.

### Task 5.5: Extract `_draw_validation_results(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] Move lines 275-389 (validation section) into it
- [x] Further extract `_draw_single_validation(self, surface, vr, y_offset)` → y_offset for per-item rendering
- [x] Further extract `_draw_numeric_difference(self, surface, expected, actual, status, y_offset, indent, label_width)` → y_offset for the difference/percentage logic (lines 338-369)
- [x] Returns updated y_offset
- [x] Verify tests

**Notes:** Triple extraction achieved: _draw_validation_results (CC 3) → _draw_single_validation (CC 10) → _draw_numeric_difference (CC 9). All methods under target.

### Task 5.6: Refactor `draw` as orchestrator [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [x] `draw()` becomes: background → title → guard → clip → call each `_draw_*` section → scrollbar
- [x] Should be ~25-30 lines
- [x] Verify tests

**Notes:** draw() now 50 lines including comments, CC reduced from 47 to 5.

### Task 5.7: Verify CC reduction [Simple]
- [x] Run `radon cc game/ui/screens/test_lab/test_run_details.py -s -n C` — `draw` should be ≤8
- [x] Run full suite: `pytest tests/ -n 12 -q`

**Notes:** draw() CC: 47 → 5. Full suite: 8167 passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `draw` CC ≤ 8 confirmed via radon (CC = 5)
- [x] All 8167 tests passing
- [x] No public API changes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
