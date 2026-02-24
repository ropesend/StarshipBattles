# Phase 1: Normalize BaseGallery to 2-Tuples

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-166 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Change `asset_buttons` from 3-tuple `(btn, img, id)` to 2-tuple `(btn, id)` throughout BaseGallery and update existing subclass tests to match.

---

## Tasks

### Task 1.1: Change asset_buttons type annotation and storage [Simple]
**File:** `game/ui/panels/base_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py -v`

- [x] Change type annotation (lines 77-79) from:
  ```python
  self.asset_buttons: List[
      Tuple[pygame_gui.elements.UIButton, pygame_gui.elements.UIImage, str]
  ] = []
  ```
  To:
  ```python
  self.asset_buttons: List[Tuple[pygame_gui.elements.UIButton, str]] = []
  ```
- [x] Update import on line 14: remove `pygame_gui.elements.UIImage` from the Tuple type hint if needed (it's just a string annotation, may not need change)
- [x] Change `_populate_gallery` storage (line 202) from:
  ```python
  self.asset_buttons.append((btn, img, asset_id))
  ```
  To:
  ```python
  self.asset_buttons.append((btn, asset_id))
  ```
  (The `img` UIImage element is still created on lines 195-200 for visual rendering — it just isn't stored in the tuple)
- [x] Change `on_asset_selected` iteration (line 233) from:
  ```python
  for btn, img, aid in self.asset_buttons:
  ```
  To:
  ```python
  for btn, aid in self.asset_buttons:
  ```
- [x] Change `handle_button_click` iteration (line 259) from:
  ```python
  for btn, img, asset_id in self.asset_buttons:
  ```
  To:
  ```python
  for btn, asset_id in self.asset_buttons:
  ```
- [x] Verify: `grep -n "img" game/ui/panels/base_gallery.py` — no remaining references to `img` in tuple unpacking

**Notes:**

### Task 1.2: Update portrait gallery test tuples [Simple]
**File:** `tests/unit/ui/test_race_portrait_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py -v`

- [x] Line 218-221: Change 3-tuples to 2-tuples:
  ```python
  # FROM:
  gallery.asset_buttons = [
      (btn1, MagicMock(), "portrait_001.png"),
      (btn2, MagicMock(), "portrait_002.png"),
  ]
  # TO:
  gallery.asset_buttons = [
      (btn1, "portrait_001.png"),
      (btn2, "portrait_002.png"),
  ]
  ```
- [x] Line 246-250: Same change for the 3-button test case (remove `MagicMock()` middle elements)
- [x] Verify: `pytest tests/unit/ui/test_race_portrait_gallery.py -v` — all tests pass

**Notes:**

### Task 1.3: Update flag gallery test tuples [Simple]
**File:** `tests/unit/ui/test_race_flag_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_flag_gallery.py -v`

- [x] Line 221-224: Change 3-tuples to 2-tuples (same pattern as portrait tests)
- [x] Line 249-253: Same change for the 3-button test case
- [x] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py -v` — all tests pass

**Notes:**

### Task 1.4: Run combined gallery tests [Simple]
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py -v`

- [x] All portrait gallery tests pass
- [x] All flag gallery tests pass
- [x] No other test regressions: `pytest tests/ -n 12 -q --tb=short`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
