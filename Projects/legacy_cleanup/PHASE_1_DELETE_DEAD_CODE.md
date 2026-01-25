# Phase 1: Delete Dead Code

**Project:** Legacy Code Cleanup
**Phase:** 1 of 8
**Risk Level:** Very Low
**Dependencies:** None

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| **1** | **Delete Dead Code** | **THIS PHASE** |
| 2 | Remove Shims & Aliases | Pending |
| 3 | Consolidate Re-exports | Pending |
| 4 | Enforce Layer Boundaries | Pending |
| 5 | Standardize Registry Access | Pending |
| 6 | Type Safety via Protocols | Pending |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 1 Objectives

1. Delete files and directories already marked for deletion
2. Remove log files from the repository root
3. Delete debug and temporary tools
4. Remove commented/dead code from production files
5. Migrate legacy UI Button class to pygame_gui and delete legacy UI file

---

## Detailed Tasks

### 1.1 Delete Marked Directories

Delete these directories entirely:

**Directory 1:** `Debugging/Marked_for_Deletion_2026-01-20/`
Contains:
- `inspect_bug_08.py`
- `repro_stats_fix.py`
- `reproduce_logistics.py`
- `reproduce_rendering.py`
- `test_import_debug.py`
- `test_validation_final.py`

**Directory 2:** `Marked_For_Deletion_2026-01-21_07-33/`
Contains:
- `test_hightick_debug.py`
- `test_registry_check.py`
- `test_tost.py`
- `test_updated_beams.py`
- `verify_ui.py`

**Directory 3:** `MagicMock/` (test artifacts)
- Contains mock design JSON files from test runs

### 1.2 Delete Log Files

Delete these log files from the repository root:
- `battle.log` (~420KB)
- `combat_lab.log` (~109KB)
- `collect_log.txt` (~72KB)
- `collect_log_2.txt` (~308KB)
- `crash_log.txt` (~1.7KB)

### 1.3 Delete Debug Tools

Delete these files from `Tools/` directory:

**Debug Scripts:**
- `Tools/debug_automation.py`
- `Tools/debug_devastator.py`
- `Tools/debug_patch.py`
- `Tools/debug_test.py`
- `Tools/debug_test_clamping.py`
- `Tools/debug_ui_import.py`

**Bug Reproduction Scripts:**
- `Tools/reproduce_missile_issue.py`
- `Tools/reproduce_mock_error.py`
- `Tools/reproduce_seeker.py`

**Visual Test Scripts:**
- `Tools/visual_test_beam_weapon.py`
- `Tools/visual_test_sprites.py`

**Superseded Scripts:**
- `Tools/fix_modifiers.py` (superseded by v2)
- `Tools/cleanup_pygame.py` (one-time executed)
- `Tools/update_paths.py` (no-op template)

**Note:** Do NOT delete these migration tools yet - they may be needed for reference:
- `Tools/migrate_data.py`
- `Tools/migrate_legacy_components.py`
- `Tools/refactor_phase*.py`
- `Tools/audit_components.py`

### 1.4 Remove Commented/Dead Code

**File: `ui/test_lab_scene.py`**
- Lines 3657-3741: Delete entire method `_draw_seed_controls_OLD()` (85 lines marked as deprecated reference)
- Lines 1941-1942, 2167-2168, 2585-2586, 2718-2719: Remove inline debug imports (`import traceback; traceback.print_exc()`)

**File: `game/core/logger.py`**
- Line 38: Remove commented `# ch = logging.StreamHandler(sys.stdout)`

**File: `game/core/profiling.py`**
- Line 108: Remove commented debug logging

**File: `simulation_tests/tests/test_example_scenarios.py`**
- Lines 93, 97: Remove commented test method definitions

**File: `tests/unit/combat/test_pdc.py`**
- Lines 130-131: Remove commented debug print statements

**File: `Tools/process_planet_images.py`**
- Lines 28-32: Remove commented nested loops

### 1.5 Migrate Legacy UI to pygame_gui

**Current State:**
- `ui/components.py` contains legacy `Button`, `Label`, and `Slider` classes
- `Button` is actively used in `game/app.py` (main menu, ~10 instances) and `ui/test_lab_scene.py`
- `Label` and `Slider` are unused

**Migration Steps:**

1. **Identify all Button usages:**
   - `game/app.py`: Lines 127-136 (10 main menu buttons)
   - `ui/test_lab_scene.py`: Lines 52, 153-157, 2321

2. **Replace with pygame_gui.elements.UIButton:**
   - The codebase already uses pygame_gui extensively (86 files)
   - Use existing theme from `data/builder_theme.json`
   - Match visual appearance of existing pygame_gui buttons

3. **Delete `ui/components.py`** after migration is complete

**Example migration pattern:**
```python
# Before (legacy):
from ui.components import Button
button = Button(x, y, width, height, text, callback)

# After (pygame_gui):
from pygame_gui.elements import UIButton
import pygame
button = UIButton(
    relative_rect=pygame.Rect(x, y, width, height),
    text=text,
    manager=ui_manager
)
# Handle click in event loop via pygame_gui.UI_BUTTON_PRESSED
```

---

## Verification Checklist

After completing all tasks:

- [ ] All marked directories deleted
- [ ] All log files deleted
- [ ] All debug tool files deleted
- [ ] Commented code removed from listed files
- [ ] Legacy Button migrated to pygame_gui
- [ ] `ui/components.py` deleted
- [ ] All unit tests pass: `pytest tests/`
- [ ] All integration tests pass: `pytest tests/integration/`
- [ ] Application launches successfully
- [ ] Main menu displays and buttons work
- [ ] No import errors or missing module errors

---

## Files Modified/Deleted Summary

**Directories Deleted:** 3
**Files Deleted:** ~25+
**Files Modified:** ~8 (commented code removal + Button migration)

---

## Notes for Next Phase

Phase 2 (Remove Shims & Aliases) will:
- Remove deprecated Builder → Workshop shim files
- Remove method aliases in fleet.py, fleet_movement.py, ship_stats.py
- Remove singleton accessor aliases (get_instance → instance)

Ensure all tests pass before proceeding to Phase 2.

---

*End of Phase 1 Plan*
