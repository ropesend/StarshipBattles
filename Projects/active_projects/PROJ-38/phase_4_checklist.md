# Phase 4: UI Layer Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Pass registries through UI components via context objects

---

## Tasks

### Task 4.1: Update WorkshopContext [Simple]
**File:** `game/ui/screens/workshop_context.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Add `registries: Optional[GameRegistries] = None` to `__init__` signature
- [ ] Store `self.registries = registries or get_default_registries()`
- [ ] Update `standalone()` factory method to accept and pass registries parameter
- [ ] Update `for_strategy()` factory method if it exists
- [ ] Verify: `pytest tests/unit/builder/` passes

**Notes:**

---

### Task 4.2: Update WorkshopViewModel [Simple]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py`

- [ ] Accept registries via context: `self._registries = context.registries`
- [ ] Pass registries when creating `VehicleDesignService` (line 49)
- [ ] Pass registries when creating ships via service
- [ ] Replace any `get_modifier_registry()` calls (line 15) with `self._registries.modifiers`
- [ ] Verify: `pytest tests/unit/builder/test_builder_viewmodel.py` passes

**Notes:**

---

### Task 4.3: Update WorkshopDataLoader [Simple]
**File:** `game/ui/screens/workshop_data_loader.py`
**Tests:** Manual - test workshop reload functionality

- [ ] Accept registries parameter or access via parent reference
- [ ] Remove `clear_registry()` import and call (line 11, ~195) - no longer needed with DI
- [ ] Replace `get_vehicle_classes()` call (line 195) with passed registries
- [ ] Verify: Workshop reload functionality works correctly

**Notes:**

---

### Task 4.4: Update DesignWorkshopGUI [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** Manual - launch Design Workshop

- [ ] Remove `RegistryManager` import (line 18)
- [ ] Access registries via context: `self.context.registries`
- [ ] Replace `get_component_registry()` calls (line 412) with context registries
- [ ] Replace `get_vehicle_classes()` calls (lines 631, 649) with context registries
- [ ] Pass registries to child components as needed
- [ ] Verify: Design Workshop opens and functions correctly

**Notes:**

---

### Task 4.5: Update Builder Widgets [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Accept registries in constructor or via parent reference
- [ ] Replace `get_modifier_registry()` calls (lines 90, 108) with passed registries
- [ ] Verify: `pytest tests/unit/builder/` passes

**Notes:**

---

### Task 4.6: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** Manual - test workshop interactions

- [ ] Access registries via context or parent reference
- [ ] Replace `get_vehicle_classes()` call (line 386) with registries
- [ ] Verify: Workshop event handling works correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` passes (full suite)
- [ ] Game launches and main menu works
- [ ] Design Workshop fully functional:
  - [ ] Can create new ships
  - [ ] Can add/remove components
  - [ ] Can change ship class
  - [ ] Can save/load designs
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
