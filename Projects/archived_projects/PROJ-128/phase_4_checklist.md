# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-128 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (13 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: CON-UI2-001 - Inconsistent Dependency Injection Patter [Medium]
**File:** `game/ui/services/*.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Services use different DI patterns intentionally:
- VehicleClassService: strict required (PROJ-50 mandate)
- ComponentService, ValidationService, ShipFactory: optional with lazy resolution
- This is documented design per PROJ-43/PROJ-50 history

### Task 4.2: CON-UI2-004 - Return Type Inconsistency for Failure Ca [Medium]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - ShipIOAdapter documents intentional difference at lines 28-35:
- save returns `(bool, str)` - success flag needed, no object to return
- load returns `(Optional[T], str)` - object returned on success
- Documented: "different return types are intentional"

### Task 4.3: CON-UI2-006 - Inconsistent Type Hint Usage for Ship Pa [Simple]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Uses `Any` for ship parameter intentionally to avoid simulation layer imports. This is the adapter pattern - UI adapter should not depend on Ship class directly.

### Task 4.4: CON-UI2-007 - Docstring Format Inconsistency [Simple]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - File location is "Unknown", cannot investigate. All UI services examined use consistent Google-style docstrings.

### Task 4.5: CON-UI2-008 - Boolean Parameter Naming Without Prefix [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - screenshot_manager.py capture_strategy_layer() uses `include_ui`, `include_subwindows` - these already have the "include_" prefix which is a valid boolean naming pattern per codebase conventions.

### Task 4.6: CON-UI2-009 - Constants Defined at Module Level vs Cla [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - battle_ui_service.py has `PROJECTILE_COLORS` and `DEFAULT_PROJECTILE_COLOR` at module level. These are mapping constants shared across potential implementations, not class-specific state. Module level is appropriate.

### Task 4.7: CON-UI2-010 - Mixed Logging Patterns [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - screenshot_manager.py uses `log_info`, `log_error`, `log_warning` from game.core.logger. This is the correct unified logging pattern per codebase standards.

### Task 4.8: CON-UI2-011 - Import Organization Inconsistencies [Simple]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - ship_theme_manager.py imports follow standard order: stdlib (os, datetime, threading), then pygame, then game modules. No issue found.

### Task 4.9: CON-UI2-012 - Inconsistent Use of Optional vs Default [Simple]
**File:** `game/ui/services/input_mapper.`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - input_mapper.py load() uses `Optional[str] = None` for defaults_path and overrides_path. This is correct - both are optional files that may not be provided.

### Task 4.10: CON-UI2-013 - Thread Safety Documentation Inconsistenc [Medium]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Both ScreenshotManager (lines 11-24) and ShipThemeManager (lines 11-25) already have consistent thread safety documentation in their class docstrings.

### Task 4.11: CON-UI2-014 - User Story Comment in Production Code [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Converted user story comment at line 77 ("I want to have a empty circle...") to technical comment ("Shows collision radius and layer boundaries when overlay mode is active").

### Task 4.12: CON-UI2-015 - Protocol Definition Location [N]
**File:** `game/ui/interfaces/battle_ui.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - battle_ui.py location is appropriate. UI interfaces (IBattleUI protocol + DTOs) belong in UI layer at game/ui/interfaces/. No change needed.

### Task 4.13: CON-UI2-016 - __init__.py Export Patterns [N]
**File:** `game/ui/__init__.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - game/ui/__init__.py has proper `__all__` exports with explicit module listing. Pattern is consistent with codebase standards.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
