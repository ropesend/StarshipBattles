# Phase 7: Screen Naming Standardization (UI-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize Scene/Interface/GUI → Screen for all UI classes

---

## Background

**Current Naming Patterns:**
| Pattern | Count | Examples |
|---------|-------|----------|
| Scene | 4 | BattleScene, StrategyScene, FormationEditorScene, TestLabScene |
| Screen | 6 | NewGameSetupScreen, RaceSetupScreen, BattleSetupScreen |
| Interface | 2 | BattleInterface, StrategyInterface |
| GUI | 2 | BuilderSceneGUI, DesignWorkshopGUI |

**Target:** Standardize to "Screen" (most common, pygame_gui convention)

---

## Tasks

### Task 7.1: Rename BattleScene → BattleScreen [Medium]
**File:** `game/ui/screens/battle_scene.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename class `BattleScene` → `BattleScreen`
- [ ] Update all internal references to `BattleScene`
- [ ] Rename file: `battle_scene.py` → Note: may conflict with existing battle_screen.py
- [ ] Search for all imports of `BattleScene` and update
- [ ] Update any string references (e.g., in logging)
- [ ] Run tests

**Note:** Check if `battle_screen.py` already exists with `BattleInterface` - may need merge analysis.

**Notes:**

---

### Task 7.2: Rename StrategyScene → StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename class `StrategyScene` → `StrategyScreen`
- [ ] Update all internal references
- [ ] Rename file: `strategy_scene.py` → Note: may conflict with existing strategy_screen.py
- [ ] Search for all imports and update
- [ ] Run tests

**Note:** Check if `strategy_screen.py` already exists with `StrategyInterface` - may need merge analysis.

**Notes:**

---

### Task 7.3: Rename FormationEditorScene → FormationEditorScreen [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename class `FormationEditorScene` → `FormationEditorScreen`
- [ ] Update all internal references
- [ ] Search for all imports and update
- [ ] Run tests

**Notes:**

---

### Task 7.4: Rename TestLabScene → TestLabScreen [Simple]
**File:** `game/ui/screens/test_lab_scene.py` (after Phase 6 consolidation)
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename class `TestLabScene` → `TestLabScreen`
- [ ] Update all internal references
- [ ] Rename file: `test_lab_scene.py` → `test_lab_screen.py`
- [ ] Search for all imports and update
- [ ] Update game/app.py import
- [ ] Run tests

**Notes:**

---

### Task 7.5: Rename BuilderSceneGUI → BuilderScreen [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Rename class `BuilderSceneGUI` → `BuilderScreen`
- [ ] Update all internal references
- [ ] Search for all imports and update
- [ ] Run tests

**Notes:**

---

### Task 7.6: Rename DesignWorkshopGUI → DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Rename class `DesignWorkshopGUI` → `DesignWorkshopScreen`
- [ ] Update all internal references
- [ ] Search for all imports and update
- [ ] Run tests

**Notes:**

---

### Task 7.7: Analyze Interface Classes [Medium]
**Files:** `game/ui/screens/battle_screen.py`, `game/ui/screens/strategy_screen.py`
**Analysis task**

BattleInterface and StrategyInterface may need special handling:
- [ ] Determine if Interface classes should be merged with Scene classes
- [ ] If separate, rename to appropriate names (e.g., BattleHUD, StrategyHUD)
- [ ] Document decision in decisions.md
- [ ] Implement chosen approach

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Grep for "Scene\b" in class names shows no UI screen occurrences
- [ ] Grep for "GUI\b" in class names shows no occurrences
- [ ] All UI screen classes now end in "Screen"
- [ ] Run `pytest tests/` - all tests pass
- [ ] Game launches and all screens work
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
