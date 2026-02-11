# Phase 5: TestRunDetailsPanel.draw (CC 47 → ≤8)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract drawing sections into focused sub-methods

---

## Tasks

### Task 5.1: Extract `_draw_header_and_status(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] Move lines 133-145 (run info header, status PASSED/FAILED) into it
- [ ] Returns updated y_offset
- [ ] Verify tests

**Notes:**

### Task 5.2: Extract `_draw_metadata(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] Move lines 147-161 (seed display, ticks display) into it
- [ ] Returns updated y_offset
- [ ] Verify tests

**Notes:**

### Task 5.3: Extract `_draw_action_buttons(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] Move lines 163-244 (View States, Use Seed, Copy Results buttons) into it
- [ ] All 3 buttons share pattern: conditional display + hover + render
- [ ] Returns updated y_offset
- [ ] Verify tests

**Notes:**

### Task 5.4: Extract `_draw_metrics(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] Move lines 256-273 (metrics title + loop) into it
- [ ] Returns updated y_offset
- [ ] Verify tests

**Notes:**

### Task 5.5: Extract `_draw_validation_results(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] Move lines 275-389 (validation section) into it
- [ ] Further extract `_draw_single_validation(self, surface, vr, y_offset)` → y_offset for per-item rendering
- [ ] Further extract `_draw_numeric_difference(self, surface, expected, actual, status, y_offset, indent, label_width)` → y_offset for the difference/percentage logic (lines 338-369)
- [ ] Returns updated y_offset
- [ ] Verify tests

**Notes:** The validation section is the most complex part (CC ~20 of the original 47). The triple extraction (_draw_validation_results → _draw_single_validation → _draw_numeric_difference) is needed to get each method below CC 10.

### Task 5.6: Refactor `draw` as orchestrator [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`

- [ ] `draw()` becomes: background → title → guard → clip → call each `_draw_*` section → scrollbar
- [ ] Should be ~25-30 lines
- [ ] Verify tests

**Notes:**

### Task 5.7: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/test_lab/test_run_details.py -s -n C` — `draw` should be ≤8
- [ ] Run full suite: `pytest tests/ -n 12 -q`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `draw` CC ≤ 8 confirmed via radon
- [ ] All 8167 tests passing
- [ ] No public API changes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
