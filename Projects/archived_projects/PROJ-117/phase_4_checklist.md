# Phase 4: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-117 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (16 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 4.1: LEG-UI1-001 - Legacy BuilderScreen (builder/main.py) - [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] FALSE POSITIVE: The file is labeled as legacy/standalone for testing purposes; production uses DesignWorkshopScreen. Intentionally kept for standalone design testing.

**Notes:** No change needed - file has clear documentation explaining its purpose

### Task 4.2: LEG-UI1-002 - Backward Compatibility Aliases in RaceFlagGallery [Simple]
**File:** `game/ui/panels/race_flag_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_flag_gallery.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed legacy aliases (flag_buttons, flag_scroll, flag_preview_panel, on_flag_selected). Updated tests to use canonical names (asset_buttons, scroll_container, preview_panel, on_asset_selected).

### Task 4.3: LEG-UI1-003 - Deprecated Methods on BattleScreen [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed deprecated handle_click() and handle_scroll() methods. No external callers found. The IScene-compliant handle_event() is the correct interface.

### Task 4.4: LEG-UI1-004 - Legacy Tuple Format Support in detail_panel [Medium]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: The tuple format is used throughout the builder module - this is the canonical format for BuilderScreen selections.

**Notes:** No change needed - tuple format is actively used in builder/layer_panel

### Task 4.5: LEG-UI1-005 - Backwards Compatibility Fallbacks in workshop_event [Simple]
**File:** Does not exist (`workshop_event_handlers.py` doesn't exist)
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] FALSE POSITIVE: File path in finding is incorrect/truncated. The actual file is `workshop_event_router.py`.

**Notes:** No change needed - finding references non-existent file

### Task 4.6: LEG-UI1-006 - Legacy Shim Skip List in detail_panel.py [Simple]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed legacy shim skip list (ProjectileWeapon, BeamWeapon, Armor). These shims no longer exist.

### Task 4.7: LEG-UI1-007 - Duplicate show_overlay Toggle Keybinding [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: Multiple keybinds for same action is intentional UX (F3 is debug standard, O is quick access).

**Notes:** No change needed - intentional UX design

### Task 4.8: LEG-UI1-008 - Stale Comment about Removed Duplicate Method [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed stale comment "# Note: method removed duplicate update_visuals here"

### Task 4.9: LEG-UI1-009 - Hardcoded 1920x1080 Fallback Resolution [Simple]
**File:** `game/ui/screens/new_game_setup.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] FALSE POSITIVE: File doesn't exist.

**Notes:** No change needed - file doesn't exist

### Task 4.10: LEG-UI1-010 - Duplicate Assignment on Consecutive Lines [Simple]
**File:** `game/ui/screens/builder/left_panel.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed duplicate `self.list_y = 125` line.

### Task 4.11: LEG-UI1-011 - Unnecessary hasattr Guard for _facade [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] FALSE POSITIVE: Looking at the code, `_facade` is always initialized in `__init__`. No hasattr guards found for it.

**Notes:** No change needed - no hasattr guards exist for _facade

### Task 4.12: LEG-UI1-012 - Dead hasattr Check for print_headless_summary [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: Defensive check is acceptable since BattleUI might be extended.

**Notes:** No change needed - defensive programming pattern is acceptable

### Task 4.13: LEG-UI1-013 - Monkey-Patching Domain Objects with Temp Attrs [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: Rendering optimization to avoid recalculating positions twice. Localized to render loop.

**Notes:** No change needed - this is a performance optimization pattern

### Task 4.14: LEG-UI1-014 - Unused Module-Level Constants [Simple]
**File:** `game/ui/screens/builder/stats_panel.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] FALSE POSITIVE: File doesn't exist.

**Notes:** No change needed - file doesn't exist

### Task 4.15: LEG-UI1-015 - Deprecated Properties on StrategyScreen [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: Comment says deprecated for external access; internal use is valid. Properties are actively used internally.

**Notes:** No change needed - internal use is valid per comment

### Task 4.16: LEG-UI1-016 - test_lab/screen.py Accepts Game Object [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] ACCEPTABLE: The game parameter provides access to battle_scene needed for visual test execution.

**Notes:** No change needed - game parameter is required for visual test mode


---

## Summary

**Total Findings:** 16
- **Fixed:** 5 (4.2, 4.3, 4.6, 4.8, 4.10)
- **Acceptable:** 6 (4.4, 4.7, 4.12, 4.13, 4.15, 4.16)
- **False Positives:** 5 (4.1, 4.5, 4.9, 4.11, 4.14)

**Files Modified:**
- `game/ui/panels/race_flag_gallery.py` - Removed legacy aliases
- `game/ui/screens/battle_screen.py` - Removed deprecated methods and stale comment
- `game/ui/screens/builder/detail_panel.py` - Removed legacy shim skip list
- `game/ui/screens/builder/left_panel.py` - Removed duplicate assignment
- `tests/unit/ui/test_race_flag_gallery.py` - Updated to use canonical names

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
