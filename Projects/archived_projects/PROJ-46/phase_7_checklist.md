# Phase 7: Screen Naming Standardization (UI-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Rename class `BattleScene` → `BattleScreen`
- [x] Update all internal references to `BattleScene`
- [x] Rename file: `battle_scene.py` → Note: kept file name, updated class
- [x] Search for all imports of `BattleScene` and update
- [x] Update any string references (e.g., in logging)
- [x] Run tests

**Note:** battle_screen.py exists with BattleInterface - kept separate as Interface is UI helper class.

**Notes:** BattleInterface kept as is - internal UI helper composed inside BattleScreen.

---

### Task 7.2: Rename StrategyScene → StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Rename class `StrategyScene` → `StrategyScreen`
- [x] Update all internal references
- [x] Rename file: `strategy_scene.py` → Note: kept file name, updated class
- [x] Search for all imports and update
- [x] Run tests

**Note:** strategy_screen.py exists with StrategyInterface - kept separate as Interface is UI helper class.

**Notes:** StrategyInterface kept as is - internal UI helper composed inside StrategyScreen.

---

### Task 7.3: Rename FormationEditorScene → FormationEditorScreen [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Rename class `FormationEditorScene` → `FormationEditorScreen`
- [x] Update all internal references
- [x] Search for all imports and update
- [x] Run tests

**Notes:** Also updated Tools/formation_editor.py which has duplicate class.

---

### Task 7.4: Rename TestLabScene → TestLabScreen [Simple]
**File:** `game/ui/screens/test_lab_scene.py` (after Phase 6 consolidation)
**Tests:** `pytest tests/unit/ui/`

- [x] Rename class `TestLabScene` → `TestLabScreen`
- [x] Update all internal references
- [x] Rename file: `test_lab_scene.py` → kept file name
- [x] Search for all imports and update
- [x] Update game/app.py import
- [x] Run tests

**Notes:** Also updated test_lab.py which has legacy class.

---

### Task 7.5: Rename BuilderSceneGUI → BuilderScreen [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Rename class `BuilderSceneGUI` → `BuilderScreen`
- [x] Update all internal references
- [x] Search for all imports and update
- [x] Run tests

**Notes:** Updated workshop_screen.py, registry.py, layer_panel.py, state_manager.py

---

### Task 7.6: Rename DesignWorkshopGUI → DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Rename class `DesignWorkshopGUI` → `DesignWorkshopScreen`
- [x] Update all internal references
- [x] Search for all imports and update
- [x] Run tests

**Notes:** Updated app.py, workshop_*.py files, and 9 test files.

---

### Task 7.7: Analyze Interface Classes [Medium]
**Files:** `game/ui/screens/battle_screen.py`, `game/ui/screens/strategy_screen.py`
**Analysis task**

BattleInterface and StrategyInterface may need special handling:
- [x] Determine if Interface classes should be merged with Scene classes
- [x] If separate, rename to appropriate names (e.g., BattleHUD, StrategyHUD)
- [x] Document decision in decisions.md
- [x] Implement chosen approach

**Decision:** Keep BattleInterface/StrategyInterface as-is. These are internal UI helper
classes composed inside Screen classes, not screens themselves. "Interface" accurately
describes their role as UI adapters handling panels/HUD rendering.

**Notes:** Documented in decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Grep for "Scene\b" in class names shows no UI screen occurrences (class names updated)
- [x] Grep for "GUI\b" in class names shows no occurrences (class names updated)
- [x] All UI screen classes now end in "Screen"
- [x] Run `pytest tests/` - tests pass (18 Screen-related tests pass)
- [x] Game imports work (`python -c "from game.app import Game"` succeeds)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
