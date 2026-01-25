# Phase 6: Builder Shims [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove Builder→Workshop shim files and update all callers

---

## Tasks

### Task 6.1: Update game/app.py [Medium]
**File:** `game/app.py`
**Tests:** Manual - application should launch

- [ ] Line 18: Change import:
  ```python
  # FROM:
  from game.ui.screens.builder_screen import BuilderSceneGUI
  # TO:
  from game.ui.screens.workshop_screen import DesignWorkshopGUI
  from game.ui.screens.workshop_context import WorkshopContext
  ```
- [ ] Lines 118 and/or 150: Update instantiation:
  ```python
  # FROM:
  self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)

  # TO:
  context = WorkshopContext.standalone(tech_preset_name="default")
  context.on_return = self.on_builder_return
  self.builder_scene = DesignWorkshopGUI(WIDTH, HEIGHT, context)
  ```
- [ ] Verify: `python -c "from game.app import Game"` works

**Notes:**

---

### Task 6.2: Update game/ui/__init__.py [Simple]
**File:** `game/ui/__init__.py`
**Tests:** `python -c "import game.ui"`

- [ ] Line 9: Change `builder_screen` to `workshop_screen`
- [ ] Line 19 (in __all__): Update if present

**Notes:**

---

### Task 6.3: Update Builder Test Files (9 files) [Medium]
**Tests:** `pytest tests/unit/builder/ -v`

All files need import changes from:
```python
from game.ui.screens.builder_screen import BuilderSceneGUI
```
To:
```python
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_context import WorkshopContext
```

- [ ] `tests/unit/builder/test_selection_refinements.py:4` - Update import and instantiation
- [ ] `tests/unit/builder/test_multi_selection_logic.py:6` - Update import and instantiation
- [ ] `tests/unit/builder/test_builder_warning_logic.py:10` - Update import and instantiation
- [ ] `tests/unit/builder/test_builder_improvements.py:6` - Update import and instantiation
- [ ] `tests/unit/builder/test_builder_structure_features.py:6` - Update import and instantiation
- [ ] `tests/unit/builder/test_builder_io_integration.py:3` - Update import and instantiation
- [ ] `tests/unit/builder/test_builder_drag_drop_real.py:12` - Update import and instantiation
- [ ] `tests/repro_issues/test_bug_13_clear_removes_hull.py:6` - Update import and instantiation

**Notes:**

---

### Task 6.4: Update test_mandatory_modifiers.py [Simple]
**File:** `tests/unit/entities/test_mandatory_modifiers.py`
**Tests:** `pytest tests/unit/entities/test_mandatory_modifiers.py -v`

- [ ] Line 7: Change import source:
  ```python
  # FROM:
  from game.ui.screens.builder_screen import ModifierEditorPanel
  # TO:
  from game.ui.panels.builder_widgets import ModifierEditorPanel
  ```

**Notes:**

---

### Task 6.5: Update test_builder_data_loader.py [Medium]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

Update all dynamic imports (8 locations):
- [ ] Lines 59, 72, 84, 95, 105, 116, 145, 161: Change from:
  ```python
  from game.ui.screens.builder_data_loader import BuilderDataLoader
  ```
  To:
  ```python
  from game.ui.screens.workshop_data_loader import WorkshopDataLoader
  ```
- [ ] Update test code to use `WorkshopDataLoader` (or alias as `BuilderDataLoader` for minimal changes)

**Notes:**

---

### Task 6.6: Update test_builder_viewmodel.py [Simple]
**File:** `tests/unit/builder/test_builder_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -v`

- [ ] Line 58: Change import:
  ```python
  # FROM:
  from game.ui.screens.builder_viewmodel import BuilderViewModel
  # TO:
  from game.ui.screens.workshop_viewmodel import WorkshopViewModel
  ```
- [ ] Update test code to use `WorkshopViewModel` (or alias)

**Notes:**

---

### Task 6.7: Delete Shim Files [Simple]
**Files to delete:** 4 files
**Tests:** `pytest tests/unit/builder/ tests/repro_issues/ -v`

- [ ] Delete `game/ui/screens/builder_screen.py`
- [ ] Delete `game/ui/screens/builder_viewmodel.py`
- [ ] Delete `game/ui/screens/builder_data_loader.py`
- [ ] Delete `game/ui/screens/builder_event_router.py`
- [ ] Verify: `python -c "from game.ui.screens.workshop_screen import DesignWorkshopGUI"` works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 4 builder shim files are deleted
- [ ] No remaining Builder* imports: `grep -r "builder_screen\|builder_viewmodel\|builder_data_loader\|builder_event_router" game/ tests/ --include="*.py" | grep -v __pycache__`
- [ ] Run: `pytest tests/unit/builder/ tests/repro_issues/ tests/unit/entities/test_mandatory_modifiers.py -v`
- [ ] Manual test: `python -m game.app` and navigate to Design Workshop
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
