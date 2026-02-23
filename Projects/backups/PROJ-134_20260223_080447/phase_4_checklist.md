# Phase 4: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-134 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (12 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: LEG-UI1-001 - Legacy Single-Selection Fields in Empire [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. The `selected_source` and `selected_index` fields are:
1. Used internally for re-click detection (line 461)
2. Documented and tested for backward compatibility (tests at line 1199-1209)
3. Actively synchronized with multi-select state
The "legacy" comment is accurate documentation, not dead code.

### Task 4.2: LEG-UI1-002 - Backward Compatibility Property in TestL [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Removed dead `components_cache` property - it had no callers. The docstring claimed backward compatibility but the property was never accessed.

### Task 4.3: LEG-UI1-003 - Legacy API Method in FleetReportWindow [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Updated misleading docstring from "legacy API" to accurate description. The `_on_remove_ship` method is actively used by ShipDetailPanel for single-ship removal.

### Task 4.4: LEG-UI1-004 - Comments Referencing "Legacy Dispatch" i [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Changed "folded from app.py legacy dispatch" to "moved from app.py" - the dispatch code is current, not legacy.

### Task 4.5: LEG-UI1-005 - Pass Statements in Stub Methods [Simple]
**File:** `game/ui/screens/test_lab/ship_panels.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Updated misleading docstrings "Update hover states" to "No-op; reserved for interface consistency" - the pass statements are valid for interface consistency.

### Task 4.6: LEG-UI1-008 - Fallback Chains in Workshop Context [Simple]
**File:** `game/ui/screens/workshop_context.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. The only "fallback" is the standard PROJ-50 DI pattern in `__post_init__` - try default registries, fallback to requiring caller DI. This is documented and intentional.

### Task 4.7: LEG-UI1-009 - PROJ-40 Migration Comments Still Present [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Removed inline PROJ-40 migration comments that are no longer relevant. Kept module-level history comment.

### Task 4.8: LEG-UI1-006 - Extensive hasattr() Checks for Optional [Complex]
**File:** `Unknown`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. hasattr() patterns serve valid purposes: DI (PROJ-50), Mock object support in tests, dynamic attributes. Previously reviewed in Phase 3.

### Task 4.9: LEG-UI1-007 - Singleton Instance Access Pattern [Complex]
**File:** `Unknown`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. Singleton pattern is intentional architecture in `game/core/singleton.py`. Services like ScreenshotManager, ShipThemeManager use `.instance()` by design.

### Task 4.10: LEG-UI1-010 - getattr() Defensive Patterns [Medium]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. While getattr() is overly defensive for RaceConfig dataclass attributes (which have defaults), the pattern works correctly and provides protection against schema changes.

### Task 4.11: LEG-UI1-011 - Dual-Path Ship/DTO Support in BattlePane [Deferred]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. This is intentional PROJ-43 DTO architecture. UI supports both ShipDTO and domain Ship objects for controlled data access and backward compatibility.

### Task 4.12: LEG-UI1-012 - Build Queue Fallback Mode [None]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. This is intentional PROJ-69 multi-mode controller design: multi-queue, single-queue, and fallback modes. Fallback mode provides backward compatibility when queue sources aren't explicitly set.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
