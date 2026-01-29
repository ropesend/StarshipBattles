# Phase 6: UI Directory Consolidation (NS-01)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Merge `ui/` into `game/ui/`, update ~40 import statements

---

## Background

**Current State:**
- `ui/` directory has 18 Python files with active cross-references
- `game/ui/` imports FROM `ui/` (12 files)
- No reverse dependencies (safe to consolidate)

**Files in ui/ to relocate:**
```
ui/
├── __init__.py              → DELETE (empty or merge)
├── test_lab_scene.py        → game/ui/screens/test_lab_scene.py
├── battle_state_viewer.py   → game/ui/screens/battle_state_viewer.py
└── builder/                 → game/ui/screens/builder/ (merge)
    ├── __init__.py
    ├── modifier_logic.py
    ├── event_bus.py
    ├── interaction_controller.py
    ├── modifier_config.py
    ├── panel_layout_config.py
    ├── modifier_row.py
    ├── stats_config.py
    ├── detail_panel.py
    ├── layer_panel.py
    ├── left_panel.py
    ├── schematic_view.py
    ├── weapons_panel.py
    ├── right_panel.py
    └── structure_list_items.py
```

---

## Sub-phase 6A: Move Builder Files

### Task 6A.1: Analyze Duplicates [Simple]
**Analysis task - no file changes yet**

- [ ] Compare `ui/builder/__init__.py` with `game/ui/screens/builder/__init__.py`
- [ ] Identify any files that exist in BOTH locations
- [ ] Document which version should be kept (prefer game/ui/screens/builder/)
- [ ] Create merge strategy for `__init__.py` exports

**Notes:**

---

### Task 6A.2: Move Builder Files to game/ui/screens/builder/ [Complex]
**Files:** 14 files in ui/builder/
**Tests:** `pytest tests/unit/builder/`

For each file, either move or merge:
- [ ] `modifier_logic.py` - Move to game/ui/screens/builder/
- [ ] `event_bus.py` - Move to game/ui/screens/builder/
- [ ] `interaction_controller.py` - Move to game/ui/screens/builder/
- [ ] `modifier_config.py` - Move to game/ui/screens/builder/
- [ ] `panel_layout_config.py` - Move to game/ui/screens/builder/
- [ ] `modifier_row.py` - Move to game/ui/screens/builder/
- [ ] `stats_config.py` - Move to game/ui/screens/builder/
- [ ] `detail_panel.py` - Move to game/ui/screens/builder/
- [ ] `layer_panel.py` - Move to game/ui/screens/builder/
- [ ] `left_panel.py` - Move to game/ui/screens/builder/
- [ ] `schematic_view.py` - Move to game/ui/screens/builder/
- [ ] `weapons_panel.py` - Move to game/ui/screens/builder/
- [ ] `right_panel.py` - Move to game/ui/screens/builder/
- [ ] `structure_list_items.py` - Move to game/ui/screens/builder/

**Notes:**

---

### Task 6A.3: Merge __init__.py Exports [Simple]
**File:** `game/ui/screens/builder/__init__.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Add any missing exports from `ui/builder/__init__.py`
- [ ] Verify all public classes are exported
- [ ] Run import tests

**Notes:**

---

## Sub-phase 6B: Move Standalone Files

### Task 6B.1: Move test_lab_scene.py [Simple]
**Source:** `ui/test_lab_scene.py`
**Destination:** `game/ui/screens/test_lab_scene.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Copy file to new location
- [ ] Update internal imports if needed (change `ui.` to `game.ui.screens.` etc.)
- [ ] Delete original after verifying tests pass

**Notes:**

---

### Task 6B.2: Move battle_state_viewer.py [Simple]
**Source:** `ui/battle_state_viewer.py`
**Destination:** `game/ui/screens/battle_state_viewer.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Copy file to new location
- [ ] Update internal imports if needed
- [ ] Delete original after verifying tests pass

**Notes:**

---

## Sub-phase 6C: Update All Imports

### Task 6C.1: Update game/ui/ Imports [Complex]
**Files:** ~12 files in game/ui/
**Tests:** `pytest tests/unit/ui/`

Key files to update:
- [ ] `game/ui/panels/builder_widgets.py` (lines 13-15)
  - Change `from ui.builder.modifier_logic` to `from game.ui.screens.builder.modifier_logic`
  - Change `from ui.builder.modifier_config` to `from game.ui.screens.builder.modifier_config`
  - Change `from ui.builder.modifier_row` to `from game.ui.screens.builder.modifier_row`
- [ ] `game/ui/panels/design_report_panel.py` (lines 19-20)
  - Update all `ui.builder` imports
- [ ] `game/ui/screens/workshop_screen.py` (lines 25-29, 59)
  - Update all `ui.builder` imports

Search and update all remaining imports.

**Notes:**

---

### Task 6C.2: Update game/app.py Import [Simple]
**File:** `game/app.py`
**Tests:** Manual test - launch game

- [ ] Line 29: Update import of TestLabScene
- [ ] Change `from ui.test_lab_scene` to `from game.ui.screens.test_lab_scene`
- [ ] Test that game launches successfully

**Notes:**

---

### Task 6C.3: Update Test Imports [Complex]
**Files:** ~31 test files
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ tests/unit/entities/ tests/repro_issues/`

Test directories to update:
- [ ] `tests/unit/ui/` - All files importing from `ui.`
- [ ] `tests/unit/builder/` - All files importing from `ui.builder`
- [ ] `tests/unit/entities/` - Files like test_modifier_row.py
- [ ] `tests/repro_issues/` - Multiple bug reproduction tests
- [ ] `tests/unit/research/` - Research UI tests

For each file, change:
- `from ui.` → `from game.ui.screens.`
- `from ui.builder.` → `from game.ui.screens.builder.`

**Notes:**

---

## Sub-phase 6D: Cleanup

### Task 6D.1: Delete ui/ Directory [Simple]
**Directory:** `ui/`
**Tests:** `pytest tests/`

- [ ] Verify all imports updated (grep for "from ui\." and "import ui\.")
- [ ] Run full test suite
- [ ] Delete `ui/builder/` directory
- [ ] Delete `ui/__init__.py`
- [ ] Delete `ui/` directory
- [ ] Verify game still launches

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ui/` directory no longer exists
- [ ] Grep for "from ui\." shows no production code occurrences
- [ ] Grep for "from ui\.builder" shows no occurrences
- [ ] Run `pytest tests/` - all tests pass
- [ ] Game launches successfully
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
