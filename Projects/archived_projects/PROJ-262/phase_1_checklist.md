# Phase 1: Delete Reimplemented-Logic Test Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-262 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 11 test files (~3,191 LOC) that have zero imports from `game.*` and provide zero regression protection.

---

## Tasks

### Task 1.1: Verify zero `game.*` imports [Simple]
**Tests:** N/A (verification only)

Run `grep -l "from game\|import game" <file>` on each file. Confirm zero matches.

- [ ] `tests/unit/ui/battle_state_viewer/test_json_diff.py` (347 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/battle_state_viewer/test_ui_logic.py` (178 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/battle_state_viewer/test_viewer_ui.py` (236 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/test_lab_scene/test_logic.py` (493 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/test_lab_scene/test_rendering.py` (361 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/test_lab_scene/test_ui_components.py` (306 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/schematic_view/test_geometry.py` (357 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/schematic_view/test_rendering_logic.py` (324 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/left_panel/test_bulk_add.py` (165 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/left_panel/test_selection_hover.py` (144 LOC) -- confirmed zero game imports
- [ ] `tests/unit/ui/left_panel/test_sorting_filtering.py` (280 LOC) -- confirmed zero game imports
- [ ] If ANY file has game imports, STOP and escalate -- do not delete that file

**Notes:**

### Task 1.2: Delete reimplemented-logic test files [Simple]
**Tests:** N/A (deletion only)

- [ ] Delete `tests/unit/ui/battle_state_viewer/test_json_diff.py`
- [ ] Delete `tests/unit/ui/battle_state_viewer/test_ui_logic.py`
- [ ] Delete `tests/unit/ui/battle_state_viewer/test_viewer_ui.py`
- [ ] Delete `tests/unit/ui/test_lab_scene/test_logic.py`
- [ ] Delete `tests/unit/ui/test_lab_scene/test_rendering.py`
- [ ] Delete `tests/unit/ui/test_lab_scene/test_ui_components.py`
- [ ] Delete `tests/unit/ui/schematic_view/test_geometry.py`
- [ ] Delete `tests/unit/ui/schematic_view/test_rendering_logic.py`
- [ ] Delete `tests/unit/ui/left_panel/test_bulk_add.py`
- [ ] Delete `tests/unit/ui/left_panel/test_selection_hover.py`
- [ ] Delete `tests/unit/ui/left_panel/test_sorting_filtering.py`

**Notes:**

### Task 1.3: Clean up empty directories [Simple]
**Tests:** N/A

- [ ] Check if `tests/unit/ui/battle_state_viewer/` is now empty (or only has `__init__.py` / `conftest.py`)
- [ ] Check if `tests/unit/ui/test_lab_scene/` is now empty (or only has `__init__.py` / `conftest.py`)
- [ ] Check if `tests/unit/ui/schematic_view/` is now empty (or only has `__init__.py` / `conftest.py`)
- [ ] Check if `tests/unit/ui/left_panel/` is now empty (or only has `__init__.py` / `conftest.py`)
- [ ] Delete any directory that is now empty or contains only `__init__.py` (remove `__init__.py` first)
- [ ] Verify no other test files import from the deleted files (grep for module paths)

**Notes:**

### Task 1.4: Run test suite and verify [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record new test count (expect ~60-80 fewer tests than baseline)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
