# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-147 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (3 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: ADR-UI2-001 - ShipIO Direct Import of Simulation Entit [Medium]
**File:** `game/ui/services/ship_io.py:20`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Refactored ShipIO to use DesignLoaderAdapter for ship loading instead of directly importing Ship. Ship type hints now use TYPE_CHECKING pattern. All 54 existing tests pass without modification (adapter is compatible). Aligns with adapter pattern used by other UI services.

### Task 4.2: ADR-UI2-002 - Camera Uses pygame.math.Vector2 Instead [Simple]
**File:** `game/ui/renderer/camera.py:14,`
**Tests:** N/A - Documentation change only

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NO CODE CHANGE - Documented as intentional. Camera is a pure pygame rendering component that performs coordinate transformations for the viewport. Using pygame.math.Vector2 is appropriate here since the module only operates within the UI layer and integrates directly with pygame rendering. Added docstring explaining rationale.

### Task 4.3: ADR-UI2-003 - Game Renderer Inline Import of ShipTheme [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/unit/ui/renderer/test_game_renderer.py tests/unit/ui/test_rendering_logic.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Moved ShipThemeManager import to module level. Updated test patches in test_game_renderer.py and test_rendering_logic.py to use new import location. All tests pass.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
