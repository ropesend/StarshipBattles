# Phase 3: Extract WeaponsInputHandler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-180 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move tooltip hover geometry calculations from WeaponsReportPanel into a new WeaponsInputHandler, completing MVVM separation

---

## Tasks

### Task 3.1: Create WeaponsInputHandler [Medium]
**File:** `game/ui/screens/builder/weapons_input_handler.py` (new file)
**Tests:** `pytest tests/unit/ui/builder/ -x`

- [x] Create `WeaponsInputHandler` class with module docstring explaining MVVM role
- [x] Implement `detect_tooltip_hover()` method with geometry logic from `_check_tooltip_hover`:
  - content_rect collision check
  - hit_rect collision check (with BAR_HEIGHT + padding)
  - pixel-to-ratio mapping (dist_px / bar_width)
  - ratio-to-range mapping (dist_ratio * max_range, clamped to [0, weapon_range])
  - ViewModel tooltip data call: `viewmodel.calculate_tooltip_data(weapon, ship, hover_range)`
- [x] Accept Rect-like objects and tuple coordinates (avoid direct pygame dependency if possible)

**Notes:** Created 96-line WeaponsInputHandler with detect_tooltip_hover method. No pygame imports - uses duck typing for rect.collidepoint.

### Task 3.2: Write unit tests for WeaponsInputHandler [Simple]
**File:** `tests/unit/ui/builder/test_weapons_input_handler.py` (new file)
**Tests:** `pytest tests/unit/ui/builder/test_weapons_input_handler.py -x`

- [x] Test returns None when mouse outside content_rect
- [x] Test returns None when mouse outside hit_rect (but inside content_rect)
- [x] Test correctly maps pixel position to hover range
- [x] Test clamps hover_range to [0, weapon_range]
- [x] Test returns tooltip_data with 'pos' key set to mouse_pos

**Notes:** 17 tests covering imports, boundary conditions, edge cases, and padding detection.

### Task 3.3: Wire WeaponsInputHandler into WeaponsReportPanel [Simple]
**File:** `game/ui/screens/builder/weapons_panel.py`
**Tests:** `pytest tests/unit/ui/builder/ -x`

- [x] Import `WeaponsInputHandler` at top of file
- [x] Create `self._input_handler = WeaponsInputHandler()` in `__init__`
- [x] Replace `self._check_tooltip_hover(...)` call with `self._input_handler.detect_tooltip_hover(...)`
- [x] Delete `_check_tooltip_hover` method (lines 316-335)
- [x] Update module docstring to include WeaponsInputHandler in MVVM listing

**Notes:** weapons_panel.py now 316 lines (was 336). Passes max_range from viewmodel to input_handler for pixel-to-range conversion.

### Task 3.4: Full regression test [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite
- [x] Verify 12338+ tests pass, 0 failures

**Notes:** 12375 passed, 1 skipped (+17 from baseline)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (full suite)
- [x] `_check_tooltip_hover` deleted from weapons_panel.py
- [x] `weapons_input_handler.py` has full test coverage
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
