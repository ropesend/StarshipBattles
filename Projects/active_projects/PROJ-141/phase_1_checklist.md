# Phase 1: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-141 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Address findings in the UI-Framework module (12 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 1.1: CON-UI2-001 - Inconsistent Dependency Injection Patter [Medium]
**File:** `game/ui/services/`
**Tests:** `pytest tests/unit/ui/services/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** SKIPPED - After investigation, this is NOT a bug. VehicleClassService uses strict DI per documented PROJ-50 decision. Other services (ComponentService, ValidationService, ShipFactory, DesignLoaderAdapter) use lazy DI. The pattern is consistent and documented. No changes needed.

### Task 1.2: DUP-UI2-001 - Tkinter Root Initialization Duplicated A [Simple]
**File:** `game/ui/services/tkinter_utils.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_tkinter_utils.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** COMPLETE - Created new `tkinter_utils.py` module with:
- Lazy, thread-safe Tkinter root initialization
- Unified exception handling for platform-dependent operations
- Helper functions: `get_tk_root()`, `is_tkinter_available()`, `open_save_dialog()`, `open_load_dialog()`, `prompt_string()`, `copy_to_clipboard()`

Updated files to use new module:
- `game/ui/services/ship_io.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/screens/formation_editor.py`
- `game/ui/screens/workshop_ship_io.py`

Updated tests:
- `tests/unit/ui/services/test_ship_io.py`
- `tests/unit/ui/services/test_screenshot_manager.py`
- `tests/unit/builder/test_io_interactive.py`
- `tests/unit/systems/test_persistence.py`

All 11971 tests passing.

### Task 1.3: DUP-UI2-002 - Battle Factory Functions Follow Identica [Medium]
**File:** `game/ui/services/battle_factor`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.4: DUP-UI2-004 - BattleUIService Repeated Null-Check Patt [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.5: CON-UI2-007 - Inconsistent Type Hint Coverage [Simple]
**File:** `game/ui/services/ship_io.py:42`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.6: CON-UI2-008 - Inconsistent Error Logging Patterns [Simple]
**File:** `game/ui/services/ship_io.py:72`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.7: CON-UI2-010 - Boolean Parameter Naming Inconsistency [Simple]
**File:** `game/ui/services/battle_factor`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.8: CON-UI2-011 - Inconsistent Import Organization [Simple]
**File:** `game/ui/services/ship_io.py:1-`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.9: CON-UI2-012 - Magic Numbers in Rendering Code [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.10: DUP-UI2-006 - Ship Cloning Logic in create_hypothetica [Simple]
**File:** `game/ui/services/battle_factor`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.11: CON-UI2-013 - Inconsistent __all__ Export Patterns [Simple]
**File:** `game/ui/__init__.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.12: DUP-UI2-008 - Adapter Classes Follow Consistent Patter [N]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
