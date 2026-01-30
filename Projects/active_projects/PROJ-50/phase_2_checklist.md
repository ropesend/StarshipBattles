# Phase 2: UI Layer Strictness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove fallbacks from UI widgets; they must receive registries from context

---

## Tasks

### Task 2.1: Update ModifierEditorPanel [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 10)
- [ ] Change `registries: Optional[GameRegistries] = None` to required parameter
- [ ] Remove `_get_modifiers()` fallback method (lines 59-63)
- [ ] Update `__init__` to store `self._registries = registries`
- [ ] Update all usages to access `self._registries.modifiers`

**Notes:**

---

### Task 2.2: Update DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/test_workshop_*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 18)
- [ ] Remove fallback in `_get_vehicle_classes()` method (lines 160-163)
- [ ] Always use `self.context.registries.vehicle_classes`
- [ ] Verify all widget creations pass registries from context

**Notes:**

---

### Task 2.3: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 18)
- [ ] Remove fallback in methods that access vehicle_classes (line ~43)
- [ ] Always access via `self.gui.context.registries`

**Notes:**

---

### Task 2.4: Update WorkshopDataLoader [Simple]
**File:** `game/ui/screens/workshop_data_loader.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 13)
- [ ] Update methods to receive registries as parameter
- [ ] Remove any fallback patterns (line ~209)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/builder/ -v` - all pass
- [ ] Run `grep -r "get_default_registry_provider" game/ui/` - returns 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
