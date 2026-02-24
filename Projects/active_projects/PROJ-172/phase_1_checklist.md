# Phase 1: Quick Wins (BattleStateViewer + FormationEditor)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract reusable components from BattleStateViewer and extract toolbar builder from FormationEditor. These are the lowest-risk files with fewest dependencies, building confidence in the extraction pattern before tackling re-offenders.

---

## Tasks

### Task 1.1: Extract JSON diff algorithm from BattleStateViewer [Simple]
**File:** `game/ui/screens/battle_state_viewer.py`
**New File:** `game/ui/utils/json_diff.py`
**Tests:** `pytest tests/unit/ui/battle_state_viewer/test_json_diff.py`

- [ ] Read `battle_state_viewer.py` fully to understand structure
- [ ] Create `game/ui/utils/json_diff.py` with:
  - [ ] Move `DiffResult` enum
  - [ ] Move `compute_json_diff()` function
  - [ ] Move `_mark_all_paths()` helper function
  - [ ] Add module docstring explaining the diff algorithm
- [ ] Update `battle_state_viewer.py` to import from new location:
  ```python
  from game.ui.utils.json_diff import compute_json_diff, DiffResult
  ```
- [ ] Run existing tests: `pytest tests/unit/ui/battle_state_viewer/ -v`
- [ ] Verify: all 29 json_diff tests still pass unchanged

**Notes:**

---

### Task 1.2: Extract ScrollableJsonPanel from BattleStateViewer [Medium]
**File:** `game/ui/screens/battle_state_viewer.py`
**New File:** `game/ui/widgets/scrollable_json_panel.py`
**Tests:** `pytest tests/unit/ui/battle_state_viewer/`

- [ ] Read remaining BattleStateViewer code to identify ScrollableJsonPanel class boundaries
- [ ] Identify the JSON tree rendering logic (syntax highlighting, recursive formatting)
- [ ] Create `game/ui/widgets/scrollable_json_panel.py` with:
  - [ ] Move `ScrollableJsonPanel` class (scroll position, thumb dragging, viewport management)
  - [ ] Move JSON tree rendering methods (syntax highlighting, color management, recursive formatting)
  - [ ] Ensure no back-references to BattleStateViewer
- [ ] Update `battle_state_viewer.py` to import from new location
- [ ] BattleStateViewer should become a thin coordinator: creates two panels, passes diff data, handles layout
- [ ] Run tests: `pytest tests/unit/ui/battle_state_viewer/ -v`
- [ ] Verify: BattleStateViewer is now <200 lines
- [ ] Verify: ScrollableJsonPanel is independently importable

**Notes:**

---

### Task 1.3: Extract FormationToolbarBuilder [Medium]
**File:** `game/ui/screens/formation_editor.py`
**New File:** `game/ui/screens/formation/toolbar_builder.py`
**Tests:** `pytest tests/unit/ui/screens/test_formation_editor_screen.py`

- [ ] Read `formation_editor.py` fully, locate `_create_ui()` method (~147 lines)
- [ ] Identify all toolbar-related constants (button labels, sizes, positions)
- [ ] Create `game/ui/screens/formation/toolbar_builder.py` with:
  - [ ] `FormationToolbarBuilder` class
  - [ ] `build_toolbar(ui_manager, screen_width, toolbar_height) -> ToolbarWidgets` method
  - [ ] `ToolbarWidgets` dataclass/namedtuple holding references to all created UI elements
  - [ ] Move all button creation code from `_create_ui()` into builder
  - [ ] Move toolbar layout constants
- [ ] Update `FormationEditorScreen._create_ui()` to use builder:
  ```python
  def _create_ui(self):
      builder = FormationToolbarBuilder()
      self.toolbar = builder.build_toolbar(self.ui_manager, self.width, self.toolbar_height)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_formation_editor_screen.py -v`
- [ ] Verify: FormationEditorScreen is now <600 lines
- [ ] Verify: 30 formation tests still pass

**Notes:**

---

### Task 1.4: Phase 1 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `battle_state_viewer.py` < 200 lines
  - [ ] `formation_editor.py` < 600 lines
  - [ ] New files exist: `json_diff.py`, `scrollable_json_panel.py`, `toolbar_builder.py`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
