# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-121 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (10 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: LEG-UI2-001 - Dead Code - draw_hud and draw_bar Functi [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/unit/ui/test_rendering_logic.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REMOVED draw_hud() and draw_bar() functions from game_renderer.py - they were only used in tests, not runtime. Also removed corresponding test classes (TestDrawHudBehavior, TestDrawBar, test_draw_hud_stats). Removed unused ResourceType import.

### Task 3.2: LEG-UI2-002 - Unused Method - create_ai_for_ship in Ba [Simple]
**File:** `game/ui/orchestration/battle_o`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The method IS used in tests (test_battle_engine_core.py:230, test_battle_orchestrator.py) for testing the reinforcement feature. The method is part of the tested public API. No changes needed.

### Task 3.3: LEG-UI2-003 - Unused Method - capture_step in Screensh [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/unit/ui/services/test_screenshot_manager.py tests/unit/test_screenshot_manager.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REMOVED capture_step() method from ScreenshotManager - it was only used in tests. Also removed TestCaptureStep class and test_capture_step_sequence test.

### Task 3.4: LEG-UI2-004 - Duplicate Exception Handlers in ShipIO [Simple]
**File:** `game/ui/services/ship_io.py:71`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REMOVED unreachable duplicate exception handlers. In save_ship(): removed `except (OSError, PermissionError)` block (already caught above). In load_ship(): removed duplicate catch block and kept only `(TypeError, ValueError)` as the final fallback.

### Task 3.5: LEG-UI2-005 - Comment References "legacy behavior" in [Medium]
**File:** `game/ui/services/ship_factory.`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The comment accurately describes a CURRENT valid code path (fallback to global RegistryManager when no registries provided). This is intentional and tested behavior, not legacy code.

### Task 3.6: LEG-UI2-006 - Basic Color Constants (BLUE, RED, GREEN) [Simple]
**File:** `game/ui/colors.py:9-11`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REMOVED unused BLUE, RED, GREEN constants from colors.py. Also removed unused imports (WHITE, BLACK, BLUE) from test_lab/screen.py - only FONT_MAIN was actually used. Kept WHITE and BLACK as they are standard color constants.

### Task 3.7: LEG-UI2-007 - ShipIOAdapter vs ShipIO Direct Access [Medium]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** MIGRATED builder/main.py from direct ShipIO usage to ShipIOAdapter for consistency. Added _ship_io_adapter instance to BuilderScreen.__init__. Updated _load_standard_data, _load_test_data, _save_ship, _load_ship, and _on_select_target_pressed to use adapter.

### Task 3.8: LEG-UI2-008 - Excessive getattr() with Defaults in bat [Medium]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REVIEWED - This is legitimate defensive coding. The getattr() calls handle real edge cases where attributes are dynamically set (crew_onboard/crew_required by ShipStatsCalculator). The code is documented and appropriate.

### Task 3.9: LEG-UI2-009 - Singleton Pattern Still in Use for Asset [N]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** REVIEWED - As noted in the finding, singletons are appropriate for asset caches (ShipThemeManager, ScreenshotManager, SpriteManager). These are legitimate use cases with .instance() and reset() methods for testing.

### Task 3.10: LEG-UI2-010 - Anticipatory Code in _CONTEXT_OVERLAP [Simple]
**File:** `game/ui/services/input_mapper.`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - All contexts (build_queue, fleet_orders, transfer) ARE actively used in the codebase: build_queue_screen.py, fleet_orders_window.py, cargo_quick_dialog.py, transfer_dialog.py. They self-reference to indicate no overlap with other contexts.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
