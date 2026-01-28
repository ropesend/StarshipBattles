# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-33 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: UI-01 - Direct entity mutation by screens [Complete]
**File:** `game/ui/screens/workshop_screen.py`, `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- The review finding identified direct Ship mutation in UI screens.
- The codebase already had a `DesignWorkshopGUI` replacing the old `BuilderSceneGUI` with MVVM architecture.
- The `DesignWorkshopGUI` uses `WorkshopViewModel` which wraps `VehicleDesignService`.
- Remaining direct mutations in `workshop_screen.py` were refactored:
  1. Added `set_ship_name(name)` and `set_ship_theme(theme_id)` methods to `WorkshopViewModel`
  2. Updated `workshop_screen.py` to use ViewModel methods instead of direct mutations:
     - `self.ship.theme_id = ...` → `self.viewmodel.set_ship_theme(...)`
     - `self.ship.name = ...` → `self.viewmodel.set_ship_name(...)`
     - `_on_modifier_change()` → `self.viewmodel.sync_modifiers_to_selection()`
     - `_clear_design()` → `self.viewmodel.clear_design()`
- All 4 new tests pass, all 108 builder tests pass, all 65 services tests pass, all 87 UI tests pass.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
