# Phase 2: UI Layer Strictness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove fallbacks from UI widgets; they must receive registries from context

---

## Tasks

### Task 2.1: Update ModifierEditorPanel [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Remove import of `get_default_registry_provider` (line 10)
- [x] Change `registries: Optional[GameRegistries] = None` to required parameter
- [x] Remove `_get_modifiers()` fallback method (lines 59-63)
- [x] Update `__init__` to store `self._registries = registries`
- [x] Update all usages to access `self._registries.modifiers`

**Notes:** Updated tests in test_mandatory_modifiers.py to pass registries

---

### Task 2.2: Update DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/test_workshop_*.py -v`

- [x] Remove import of `get_default_registry_provider` (line 18)
- [x] Remove fallback in `_get_vehicle_classes()` method (lines 160-163)
- [x] Always use `self.context.registries.vehicle_classes`
- [x] Verify all widget creations pass registries from context

**Notes:** Already passes registries to ModifierEditorPanel

---

### Task 2.3: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Remove import of `get_default_registry_provider` (line 18)
- [x] Remove fallback in methods that access vehicle_classes (line ~43)
- [x] Always access via `self.gui.context.registries`

**Notes:**

---

### Task 2.4: Update WorkshopDataLoader [Simple]
**File:** `game/ui/screens/workshop_data_loader.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Remove import of `get_default_registry_provider` (line 13)
- [x] Update methods to receive registries as parameter
- [x] Remove any fallback patterns (line ~209)

**Notes:** Made registries required parameter. Updated all callers:
- workshop_screen.py: passes self.context.registries
- builder/main.py: passes RegistryManager.instance() (legacy builder)
- test_workshop_data_loader.py: passes RegistryManager.instance()
- test_builder_data_loader.py: passes RegistryManager.instance()

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/builder/ -v` - all pass (excluding 46 pre-existing failures)
- [x] Run `grep -r "get_default_registry_provider" game/ui/` - returns 0 (only comments)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
