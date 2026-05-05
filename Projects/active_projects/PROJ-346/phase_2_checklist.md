# Phase 2: PROJ-338 vacuous purges

**Status:** Not Started
**Objective:** Replace 4 vacuous tests across 3 PROJ-338 files.

---

## Tasks

### Task 2.1: `test_build_queue_drag_handler.py:121, 126` (constructor tautologies) [Simple]
**File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py`

- [ ] Read lines 121, 126. Each likely asserts something like `handler.field == value` where `value` is what was passed to `__init__`.
- [ ] Replace with a behavioral assertion: trigger a drag interaction and pin the resulting queue state.

### Task 2.2: Commit T2.1
- [ ] Stage only the file. Commit: `test(PROJ-346): replace drag_handler constructor tautologies with drag-behavior pins`

### Task 2.3: `test_planet_report_panel_characterization.py:403` (arithmetic-only) [Medium]
**File:** `tests/unit/ui/panels/test_planet_report_panel_characterization.py`

- [ ] Read line 403. `test_resource_grid_scrollable_area_dimensions_match_layout_constants` does pure arithmetic on layout constants, never building a panel.
- [ ] Replace: build the panel, assert resulting `scrollable_area.relative_rect` matches the layout-constants expectation.

### Task 2.4: Commit T2.3
- [ ] Stage only the file. Commit: `test(PROJ-346): pin planet_report_panel scrollable area against actual panel construction`

### Task 2.5: `test_system_tree_panel_hazard.py:23` (duplicate body) [Simple]
**File:** `tests/unit/ui/panels/test_system_tree_panel_hazard.py`

- [ ] Read line 23 and the surrounding test. The body duplicates an earlier test's body.
- [ ] Identify what unique assertion this test SHOULD make (likely a hazard-row variant the duplicate mistakenly skipped).
- [ ] Rewrite. If the test is genuinely redundant: delete with rationale.

### Task 2.6: Commit T2.5
- [ ] Stage only the file. Commit: `test(PROJ-346): replace system_tree_panel hazard duplicate-body test with distinct variant`

### Task 2.7: Phase 2 verification
- [ ] `pytest tests/unit/ui/panels/test_build_queue_drag_handler.py tests/unit/ui/panels/test_planet_report_panel_characterization.py tests/unit/ui/panels/test_system_tree_panel_hazard.py -x` — all pass.
- [ ] Update Current State to Phase 3.

---

## Phase Completion Checklist
- [ ] All tasks checked, 3 commits landed
- [ ] plan.md phase row → `Complete`
