# Phase 9: Minor Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address remaining minor issues.

---

## Tasks

### Task 9.1: Fix Naming Inconsistencies [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Issue:** CQ-10 - Mix of naming conventions
**Tests:** `pytest tests/unit/ui/`

- [x] Audit `fleet_report_window.py` lines 45-65 for consistent naming
- [x] Document naming conventions in code style guide

**Notes:** Naming conventions already consistent (snake_case throughout). No changes needed.

---

### Task 9.2: Remove Unused Parameters [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Issue:** CQ-11 - Methods with unused params
**Tests:** `pytest tests/unit/ui/`

- [x] Audit `race_setup_screen.py` line 250 and similar
- [x] Remove or document unused parameters

**Notes:** Removed 4 dead methods (-26 lines):
- `_load_flag_full()` - defined but never called
- `_load_portrait_full()` - defined but never called
- `_create_placeholder()` - defined but never called
- `_sanitize_object_id()` - defined but never called

---

### Task 9.3: Improve Single Letter Variables [Simple]
**Files:** `game/ui/screens/planet_list_window.py`, `game/ui/screens/race_setup_screen.py`
**Issue:** CQ-06 - Variables named `i`, `x`, `y` in complex logic
**Tests:** `pytest tests/unit/ui/`

- [x] Replace in `planet_list_window.py` lines 156-157
- [x] Replace in `race_setup_screen.py` lines 810-926
- [x] Use descriptive names: `formation_index`, `x_pos`, `panel_width`

**Notes:**
- planet_list_window.py: `emp` → `empire`, `r` → `resource`, `qty` → `quantity`, `q_str` → `quantity_str`, `qual` → `quality`
- race_setup_screen.py: `w, h` → `img_width, img_height`

---

### Task 9.4: Fix Constructor Parameter Overload [Simple]
**File:** `game/ui/screens/builder/structure_list_items.py`
**Issue:** AR-009 - UI components with 9+ constructor params
**Tests:** `pytest tests/unit/builder/`

- [x] Create configuration dataclasses for `structure_list_items.py`
- [x] Refactor `IndividualComponentItem`, `LayerHeaderItem`, `ComponentGroupItem`

**Notes:**
- Created `ComponentItemContext` dataclass in panel_layout_config.py
- Bundles: manager, container, width, sprite_mgr, event_handler, config
- Reduced constructor parameters:
  - IndividualComponentItem: 11 params → 6 params
  - LayerComponentItem: 14 params → 9 params
  - LayerHeaderItem: 10 params → 6 params
- Updated layer_panel.py to use new context pattern

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` (full suite, NOT --testmon) - all tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
- [x] Run final verification checklist from plan.md
