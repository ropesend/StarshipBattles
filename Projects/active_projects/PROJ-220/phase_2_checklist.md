# Phase 2: TriStateFilterWidget (Pygame Component)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the reusable `TriStateFilterWidget` pygame component with 3 radio buttons per filter attribute.

---

## Tasks

### Task 2.1: Create `game/ui/components/filters/` package [Simple]
**File:** `game/ui/components/filters/__init__.py` (new)
**Tests:** N/A (package creation only)

- [ ] Create directory `game/ui/components/filters/`
- [ ] Create `game/ui/components/filters/__init__.py`:
  ```python
  from game.ui.components.filters.tri_state_widget import TriStateFilterWidget
  __all__ = ["TriStateFilterWidget"]
  ```
  (Will be populated after Task 2.2)

**Notes:**

---

### Task 2.2: Create TriStateFilterWidget [Medium]
**File:** `game/ui/components/filters/tri_state_widget.py` (new)
**Tests:** `pytest tests/unit/ui/components/filters/test_tri_state_widget.py`

- [ ] Create `game/ui/components/filters/tri_state_widget.py`:
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
- [ ] Update `game/ui/components/filters/__init__.py` with export
- [ ] Create test directory `tests/unit/ui/components/filters/`
- [ ] Create `tests/unit/ui/components/filters/__init__.py`
- [ ] Create `tests/unit/ui/components/filters/test_tri_state_widget.py`:
  - Test initialization creates widget in IGNORE state
  - Test `set_state(FilterState.YES)` updates `current_state`
  - Test `set_state(FilterState.NO)` updates `current_state`
  - Test `set_state(FilterState.IGNORE)` updates `current_state`
  - Test `kill()` cleans up child widgets
  - Note: Button press testing requires pygame_gui event simulation — test what's feasible without full pygame init
- [ ] Verify: `pytest tests/unit/ui/components/filters/` passes

**Notes:** Widget tests may need a pygame/pygame_gui mock fixture. Check existing UI component tests (e.g., `tests/unit/ui/`) for patterns.

---

### Task 2.3: Add tri-state radio theme entry [Simple]
**File:** `data/builder_theme.json`
**Tests:** Manual — visual inspection when widget renders

- [ ] Add `@tri_state_radio` button theme to `data/builder_theme.json`:
  - Compact button style (smaller padding, font size 12-13)
  - Selected state: distinct background (e.g., `accent_primary` blue), white text
  - Normal state: `bg_elevated` background, `text_normal` text
  - Hover state: `bg_hover` background
  - Use existing color values from the theme, keep consistent with design language
- [ ] Verify: no JSON parse errors (run `python -c "import json; json.load(open('data/builder_theme.json'))"`)

**Notes:**

---

### Task 2.4: Verify no test regressions [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Run incremental test suite: `pytest tests/ --testmon`
- [ ] Verify no existing tests broken
- [ ] Verify new tests discovered and pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `TriStateFilterWidget` creates 3 radio buttons and manages state
- [ ] Theme entry for `@tri_state_radio` exists
- [ ] All new tests pass
- [ ] No existing tests broken
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
