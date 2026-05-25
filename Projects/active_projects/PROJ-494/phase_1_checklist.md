# Phase 1: CAT-9 simplification (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace remaining CAT-9 simplification patterns in UI-family tests. Inherited from PROJ-480 Phase 1.

Line refs below are **advisory** — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 1.1: test_save_selection.py — 3 setup_tmpdir wrappers + 2 fuller fixtures
**File:** `tests/unit/ui/test_save_selection.py` (retargeted from `tests/unit/ui/screens/test_save_selection.py`)
**Tests:** `pytest tests/unit/ui/test_save_selection.py`
**Origin:** PROJ-480 T1.5

- [x] Replace the 3 per-class thin `setup_tmpdir` wrappers (now lines 49, 145, 222 — just yield from `_patched_saves_tmpdir`) by making the module-level `_patched_saves_tmpdir` autouse. Also fold in the 2 fuller fixtures at lines 253 (TestSaveSelectionWindowButtons) and 333 (TestSaveSelectionTimestampParsing) by extracting a `_pygame_manager` autouse fixture (Option B per orchestrator). _(PROJ-322/PROJ-479 partially absorbed: `_patched_saves_tmpdir` is already module-level.)_
- [x] Verify: passes; LOC delta ≈ -40. **14 tests pass.**

### Task 1.2: test_strategy_input_handler_transfer.py — consolidate 3 mode-test classes (LARGEST single task)
**File:** `tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_transfer.py`
**Origin:** PROJ-480 T1.11

- [x] Consolidated 3 mode-test classes (TRANSFER / DROP_CARGO / LOAD_CARGO) into a single `TestStrategyInputHandlerCargoModes` class with 5 parametrized test methods covering hotkey-sets-mode / hotkey-ignored-no-fleet / left-click-opens-dialog / right-click-cancels / escape-cancels. The dialog-call shape difference (transfer takes 2 args, drop/load take 3) is handled by a per-case `dialog_extra_args` tuple.
- [x] Verify: passes; LOC delta ≈ -130 (276 → 138 LOC). **15 tests pass (3 modes × 5 tests).**

### Task 1.3a: test_colonization_facade.py — 8 (actually 9) in-method MockPlanetType defs
**File:** `tests/integration/ui/test_colonization_facade.py` (retargeted from PROJ-480's `tests/unit/strategy/services/test_colonization_facade.py`)
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py`
**Origin:** PROJ-480 T1.7

- [x] Defined a single module-level `MockPlanetType(Enum)` carrying the union of all member names (CONTINENTAL, ICE_DWARF). Removed 9 inline definitions (PROJ-480 said 8 — actual count was 9). Removed the 9 in-method `from enum import Enum` imports.
- [x] Verify: passes; LOC delta ≈ -36. **26 tests pass.**

**Notes:** Path retargeted from PROJ-480's stale `tests/unit/strategy/services/test_colonization_facade.py`. File contains UI/screen logic (`from game.ui.screens.strategy_colonization import ColonizationSystem`) so it belongs in PROJ-494, not PROJ-496.

### Task 1.3: test_race_setup_screen.py — repeated inline mock function defs
**File:** `tests/unit/ui/screens/test_race_setup_screen.py` (retargeted from PROJ-480's `tests/unit/ui/test_race_setup_screen.py`)
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`
**Origin:** PROJ-480 T1.14

- [x] Extracted 3 module-level helper factories for the 3 paired duplicates: `_install_mock_show_step` (lines 155/173), `_install_mock_update_tab_highlighting` (lines 521/538), `_install_mock_update_navigation` (lines 566/582). The 4 `mock_validate_for_save` definitions were NOT extracted because each has unique per-test behavior. Other inline mocks (mock_update_config, mock_save_race, mock_load_race, mock_open/close_browser, mock_on_save/cancel) are one-off and were left in place.
- [x] Verify: passes; LOC delta ≈ -55. **68 tests pass.**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (CAT-8 needless complexity)
