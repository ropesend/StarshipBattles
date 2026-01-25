# Phase 5: BuilderSceneGUI Wrapper [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove BuilderSceneGUI wrapper class and update all callers to use DesignWorkshopGUI directly

---

## Tasks

### Task 5.1: Update Production Code [Medium]
**File to Delete:** `game/ui/screens/builder_screen.py`
**Tests:** `python -c "from game.app import Game; print('Import OK')"`

- [x] Update `game/app.py` imports (line 18):
  - Remove: `from game.ui.screens.builder_screen import BuilderSceneGUI`
  - Add:
    ```python
    from game.ui.screens.workshop_screen import DesignWorkshopGUI
    from game.ui.screens.workshop_context import WorkshopContext
    ```
- [x] Update `game/app.py` `__init__` method (around line 118):
  - Change from: `self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)`
  - To:
    ```python
    context = WorkshopContext.standalone(tech_preset_name="default")
    context.on_return = self.on_builder_return
    self.builder_scene = DesignWorkshopGUI(WIDTH, HEIGHT, context)
    ```
- [x] Update `game/app.py` `start_builder` method (around line 150):
  - Change from: `self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return, context)`
  - To:
    ```python
    if context is None:
        context = WorkshopContext.standalone(tech_preset_name="default")
    context.on_return = self.on_builder_return
    self.builder_scene = DesignWorkshopGUI(WIDTH, HEIGHT, context)
    ```
- [x] Verify: Run import check - should succeed

**Notes:** Also updated `game/ui/__init__.py` to import `workshop_screen` instead of `builder_screen`

---

### Task 5.2: Update Test Files [Complex]
**Files:** 8 test files in `tests/unit/builder/` and 1 in `tests/repro_issues/`
**Tests:** `pytest tests/unit/builder/ tests/repro_issues/ -v`

**For each file, change:**
- Import: `from game.ui.screens.builder_screen import BuilderSceneGUI`
- To: `from game.ui.screens.workshop_screen import DesignWorkshopGUI`
- And update instantiation to use `WorkshopContext`

**Files to update:**
- [x] `tests/unit/builder/test_builder_warning_logic.py`:
  - Update import and instantiation pattern
- [x] `tests/unit/builder/test_selection_refinements.py`:
  - Update import and instantiation pattern
- [x] `tests/unit/builder/test_builder_structure_features.py`:
  - Update import and instantiation pattern
- [x] `tests/unit/builder/test_builder_io_integration.py`:
  - Update import, instantiation pattern, and patch paths
- [x] `tests/unit/builder/test_builder_improvements.py`:
  - Update import, instantiation pattern, and patch paths
- [x] `tests/unit/builder/test_builder_drag_drop_real.py`:
  - Update import and instantiation pattern
- [x] `tests/unit/builder/test_multi_selection_logic.py`:
  - Update import and instantiation pattern
- [x] `tests/repro_issues/test_bug_13_clear_removes_hull.py`:
  - Update import and instantiation pattern
  - Note: Uses `__new__` pattern - worked without changes

**Common instantiation pattern:**
```python
# Old:
builder = BuilderSceneGUI(800, 600, MagicMock())

# New:
from game.ui.screens.workshop_context import WorkshopContext
context = WorkshopContext.standalone(tech_preset_name="default")
context.on_return = MagicMock()
workshop = DesignWorkshopGUI(800, 600, context)
```

- [x] Verify: Run all tests - 171 passed

**Notes:** Patch paths also updated from `game.ui.screens.builder_screen.ShipIO` to `game.ui.screens.workshop_screen.ShipIO`

---

### Task 5.3: Delete Wrapper File [Simple]
**File:** `game/ui/screens/builder_screen.py`

- [x] Confirm no remaining imports of `BuilderSceneGUI` in codebase:
  - Run: `grep -r "BuilderSceneGUI" --include="*.py"` - Only comments found
- [x] Delete `game/ui/screens/builder_screen.py`
- [x] Verify: Run full test suite - 171 passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/builder/ tests/repro_issues/ -v` - 171 passed
- [x] Run `python -c "from game.app import Game"` - succeeds
- [x] Confirm `builder_screen.py` deleted
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
