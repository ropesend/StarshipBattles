# Phase 2: TriStateFilterWidget (Pygame Component)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the reusable `TriStateFilterWidget` pygame component with 3 radio buttons per filter attribute.

---

## Tasks

### Task 2.1: Create `game/ui/components/filters/` package [Simple]
**File:** `game/ui/components/filters/__init__.py` (new)
**Tests:** N/A (package creation only)

- [x] Create directory `game/ui/components/filters/`
- [x] Create `game/ui/components/filters/__init__.py`:
  ```python
  from game.ui.components.filters.tri_state_widget import TriStateFilterWidget
  __all__ = ["TriStateFilterWidget"]
  ```
  (Will be populated after Task 2.2)

**Notes:** Package created with export for TriStateFilterWidget.

---

### Task 2.2: Create TriStateFilterWidget [Medium]
**File:** `game/ui/components/filters/tri_state_widget.py` (new)
**Tests:** `pytest tests/unit/ui/components/filters/test_tri_state_widget.py`

- [x] Create `game/ui/components/filters/tri_state_widget.py`:
  - `TriStateFilterWidget` class:
    - `__init__(self, attribute_name: str, label: str, rect: pygame.Rect, manager, container)`:
      - Creates `UILabel` for the attribute label (left-aligned)
      - Creates 3 `UIButton` instances: btn_yes ("Yes"), btn_no ("No"), btn_ignore ("Ign")
      - Each button gets `object_id='@tri_state_radio'` for unified theming
      - Default state: IGNORE (btn_ignore selected)
      - Stores `self._current_state = FilterState.IGNORE`
    - `@property current_state -> FilterState` — read current state
    - `set_state(state: FilterState) -> None` — set state and update button visuals
    - `check_pressed() -> Optional[FilterState]` — check if any button was pressed, return new state or None
    - `kill() -> None` — destroy all child widgets (cleanup)
    - `_update_visuals() -> None` — deselect all, select the active one
  - Layout: `[Label (flexible)]  [Yes (40px)] [No (40px)] [Ign (40px)]`
  - Use `UIButton.select()` / `unselect()` for visual toggle
- [x] Update `game/ui/components/filters/__init__.py` with export
- [x] Create test directory `tests/unit/ui/components/filters/`
- [x] Create `tests/unit/ui/components/filters/__init__.py`
- [x] Create `tests/unit/ui/components/filters/test_tri_state_widget.py`:
  - Test initialization creates widget in IGNORE state
  - Test `set_state(FilterState.YES)` updates `current_state`
  - Test `set_state(FilterState.NO)` updates `current_state`
  - Test `set_state(FilterState.IGNORE)` updates `current_state`
  - Test `kill()` cleans up child widgets
  - Note: Button press testing requires pygame_gui event simulation — test what's feasible without full pygame init
- [x] Verify: `pytest tests/unit/ui/components/filters/` passes

**Notes:** 8 tests using @patch mocks for UIButton/UILabel (following virtual_table test pattern). Tests verify state management, visual updates (select/unselect calls), and cleanup. `check_pressed(element)` takes an element arg for event handling integration.

---

### Task 2.3: Add tri-state radio theme entry [Simple]
**File:** `data/builder_theme.json`
**Tests:** Manual — visual inspection when widget renders

- [x] Add `@tri_state_radio` button theme to `data/builder_theme.json`:
  - Compact button style (smaller padding, font size 12-13)
  - Selected state: distinct background (e.g., `accent_primary` blue), white text
  - Normal state: `bg_elevated` background, `text_normal` text
  - Hover state: `bg_hover` background
  - Use existing color values from the theme, keep consistent with design language
- [x] Verify: no JSON parse errors (run `python -c "import json; json.load(open('data/builder_theme.json'))"`)

**Notes:** Added `button.@tri_state_radio` entry with font size 12, 3px corner radius, blue selected state (#2a5090).

---

### Task 2.4: Verify no test regressions [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Run incremental test suite: `pytest tests/ --testmon`
- [x] Verify no existing tests broken
- [x] Verify new tests discovered and pass

**Notes:** Testmon ran 8 new tests, all passed. No regressions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `TriStateFilterWidget` creates 3 radio buttons and manages state
- [x] Theme entry for `@tri_state_radio` exists
- [x] All new tests pass
- [x] No existing tests broken
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
