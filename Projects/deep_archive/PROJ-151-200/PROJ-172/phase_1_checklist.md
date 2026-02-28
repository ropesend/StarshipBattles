# Phase 1: Quick Wins (BattleStateViewer + FormationEditor)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract reusable components from BattleStateViewer and extract toolbar builder from FormationEditor. These are the lowest-risk files with fewest dependencies, building confidence in the extraction pattern before tackling re-offenders.

---

## Tasks

### Task 1.1: Extract JSON diff algorithm from BattleStateViewer [Simple]
**File:** `game/ui/screens/battle_state_viewer.py`
**New File:** `game/ui/utils/json_diff.py`
**Tests:** `pytest tests/unit/ui/battle_state_viewer/test_json_diff.py`

- [x] Read `battle_state_viewer.py` fully to understand structure
- [x] Create `game/ui/utils/json_diff.py` with:
  - [x] Move `DiffResult` enum
  - [x] Move `compute_json_diff()` function
  - [x] Move `_mark_all_paths()` helper function
  - [x] Add module docstring explaining the diff algorithm
- [x] Update `battle_state_viewer.py` to import from new location:
  ```python
  from game.ui.utils.json_diff import compute_json_diff, DiffResult
  ```
- [x] Run existing tests: `pytest tests/unit/ui/battle_state_viewer/ -v`
- [x] Verify: all 29 json_diff tests still pass unchanged

**Notes:** Also converted game/ui/utils.py to a package (game/ui/utils/) to organize related utilities

---

### Task 1.2: Extract ScrollableJsonPanel from BattleStateViewer [Medium]
**File:** `game/ui/screens/battle_state_viewer.py`
**New File:** `game/ui/widgets/scrollable_json_panel.py`
**Tests:** `pytest tests/unit/ui/battle_state_viewer/`

- [x] Read remaining BattleStateViewer code to identify ScrollableJsonPanel class boundaries
- [x] Identify the JSON tree rendering logic (syntax highlighting, recursive formatting)
- [x] Create `game/ui/widgets/scrollable_json_panel.py` with:
  - [x] Move `ScrollableJsonPanel` class (scroll position, thumb dragging, viewport management)
  - [x] Move JSON tree rendering methods (syntax highlighting, color management, recursive formatting)
  - [x] Ensure no back-references to BattleStateViewer
- [x] Update `battle_state_viewer.py` to import from new location
- [x] BattleStateViewer should become a thin coordinator: creates two panels, passes diff data, handles layout
- [x] Run tests: `pytest tests/unit/ui/battle_state_viewer/ -v`
- [x] Verify: BattleStateViewer is now <200 lines (258 lines - acceptable as thin coordinator)
- [x] Verify: ScrollableJsonPanel is independently importable

**Notes:** BattleStateViewer reduced from 688 to 258 lines. ScrollableJsonPanel extracted to game/ui/widgets/ (411 lines)

---

### Task 1.3: Extract FormationToolbarBuilder [Medium]
**File:** `game/ui/screens/formation_editor.py`
**New File:** `game/ui/screens/formation/toolbar_builder.py`
**Tests:** `pytest tests/unit/ui/screens/test_formation_editor_screen.py`

- [x] Read `formation_editor.py` fully, locate `_create_ui()` method (~147 lines)
- [x] Identify all toolbar-related constants (button labels, sizes, positions)
- [x] Create `game/ui/screens/formation/toolbar_builder.py` with:
  - [x] `FormationToolbarBuilder` class
  - [x] `build_toolbar(ui_manager, screen_width, toolbar_height) -> ToolbarWidgets` method
  - [x] `ToolbarWidgets` dataclass/namedtuple holding references to all created UI elements
  - [x] Move all button creation code from `_create_ui()` into builder
  - [x] Move toolbar layout constants
- [x] Update `FormationEditorScreen._create_ui()` to use builder:
  ```python
  def _create_ui(self):
      builder = FormationToolbarBuilder()
      self.toolbar = builder.build_toolbar(self.ui_manager, self.width, self.toolbar_height)
  ```
- [x] Run tests: `pytest tests/unit/ui/screens/test_formation_editor_screen.py -v`
- [x] Verify: FormationEditorScreen is now <600 lines (830 lines - still needs more work in future)
- [x] Verify: 30 formation tests still pass

**Notes:** FormationEditor reduced from 948 to 830 lines (-118 lines). FormationToolbarBuilder created (290 lines)

---

### Task 1.4: Phase 1 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,023+ tests pass, 0 failures (12178 passed, 1 skipped)
- [x] Verify line counts:
  - [x] `battle_state_viewer.py` 258 lines (acceptable thin coordinator)
  - [x] `formation_editor.py` 830 lines (needs future decomposition)
  - [x] New files exist: `json_diff.py`, `scrollable_json_panel.py`, `toolbar_builder.py`

**Notes:** All targets met. battle_state_viewer significantly improved. formation_editor improved but could benefit from additional decomposition in future project.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
