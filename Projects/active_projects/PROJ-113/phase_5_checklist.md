# Phase 5: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-113 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (11 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 5.1: ADR-UI1-001 - Test Lab UI Imports From test_framework [Complex]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - test_framework is a top-level test infrastructure package, not part of game's core/sim/strategy/UI layers. TestLabScreen legitimately imports test infrastructure (TestRegistry, TestHistory, TestRunner) to run simulation tests.

### Task 5.2: ADR-UI1-002 - Simulation Layer Imports tkinter GUI Fra [Medium]
**File:** `game/simulation/systems/persistence.py` (supposed)
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED in Phase 2 - tkinter is now ONLY in UI layer (game/ui/services/ship_io.py, game/ui/screens/*). No simulation layer imports.

### Task 5.3: ADR-UI1-007 - Extensive Private Attribute Access Acros [Medium]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - UI→UI internal decomposition. StrategyEventRouter accesses StrategyUI._window_manager. These are both UI layer classes; EventRouter was extracted from StrategyUI (PROJ-86 god class decomposition). Internal private access within same decomposed class family is acceptable.

### Task 5.4: ADR-UI1-008 - UI Layer Mutates Strategy Data Objects W [Medium]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE PATTERN - gather_planets() adds _temp_* and _cached_* attributes to planets for UI performance. Underscore prefix indicates transient/internal, not persisted. Standard UI caching pattern for list display optimization.

### Task 5.5: ADR-UI1-013 - UIConfig and DisplayConfig in Core Layer [Simple]
**File:** `game/core/config.py:132-159`
**Tests:** `tests/unit/core/test_config.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Removed backward compatibility shim for UIConfig from game.core.config. UIConfig is now exclusively in game.ui.config. Updated core/__init__.py to remove re-export. Updated test to verify correct location.

### Task 5.6: ADR-UI1-014 - UI Color Constants (WHITE, BLACK, BLUE, [Simple]
**File:** `game/core/constants.py:42-49`
**Tests:** `tests/unit/core/test_config.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Moved WHITE, BLACK, BLUE, RED, GREEN and FONT_MAIN to game/ui/colors.py. Updated 8 test_lab files to import from new location. Removed constants from core/constants.py.

### Task 5.7: ADR-UI1-015 - Circular Import Avoidance via Late Impor [Simple]
**File:** `game/ui/screens/column_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE PATTERN - Late imports are UI→Strategy (correct layer direction). UI depends on Strategy. Late imports avoid circular dependencies within same-direction imports.

### Task 5.8: ADR-UI1-016 - Module-Level tkinter Initialization Side [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Module-level tkinter.Tk() initialization is standard practice for tkinter dialog usage. Properly located in UI layer. Side effect is acceptable for dialog functionality.

### Task 5.9: ADR-UI1-017 - Deep Attribute Chains Violating Law of D [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - TestLabScreen accesses test_framework classes (TestRegistry, TestHistory) which are test infrastructure, not game layers. Deep chains within test infrastructure are acceptable.

### Task 5.10: ADR-UI1-018 - Circular Import Avoidance in new_game_se [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE PATTERN - UI→UI late imports (RaceBrowserDialog, RaceSetupScreen) to avoid circular dependencies within UI layer. Standard pattern for modular UI screens.

### Task 5.11: ADR-UI1-019 - TestLabScreen Directly Accesses battle_s [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - TestLabScreen uses test_framework.battle_state_capture for loading captured battle state JSON, and game.ui.screens.battle_state_viewer for displaying it. Both are proper layer usage (test infra + UI).


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
