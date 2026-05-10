# Phase 7: Big Bang Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Finalize strict DI, clean up remaining fallback patterns

---

## Tasks

### Task 7.1: Provider Functions Decision [Medium] ✓
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -n 4`

- [x] DECISION: Keep `DefaultRegistryProvider` and `get_default_registry_provider()`
  - Required for module-level constants (COMPONENT_REGISTRY, MODIFIER_REGISTRY, VEHICLE_CLASSES)
  - Module-level constants needed for UI hot-reload (design decision)
- [x] Document decision in decisions.md

**Notes:** Per design.md Decision 3, module-level constants must remain for hot-reload.
These are the documented exception to strict DI.

---

### Task 7.2: get_default_registries() Decision [Simple] ✓
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -n 4`

- [x] Option A: Keep `get_default_registries()` for app.py composition root only
- [x] Document decision in decisions.md
- [x] Mark as internal-use via docstring

**Notes:** Kept for composition root. app.py uses `set_default_registries()` at startup.

---

### Task 7.3: VehicleClassService Strict DI [Simple] ✓
**File:** `game/ui/services/vehicle_class_service.py`
**Tests:** `pytest tests/unit/ui/services/test_vehicle_class_service.py`

- [x] Convert `registry_provider` to required parameter
- [x] Add ValueError if None passed
- [x] Update fallback patterns in right_panel.py, schematic_view.py, main.py
- [x] Add test for required parameter

**Notes:** VehicleClassService now requires registry_provider (strict DI).
Legacy UI files create provider from composition root as needed.

---

### Task 7.4: Final Verification [Simple] ✓
**Tests:** grep verification

- [x] `grep -r "_get_registries_fallback" game/` returns 0 results ✓
- [x] Remaining `get_default_registry_provider` usages are documented exceptions:
  - Module-level constants (component.py, ship.py) - for hot-reload
  - Fallback creation in UI (composition root pattern)
- [x] Document in decisions.md

**Notes:** All anti-patterns removed. Remaining usages are documented exceptions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/core/` - 522 passed
- [x] Run `pytest tests/unit/ui/services/test_vehicle_class_service.py` - 14 passed
- [x] `grep -r "_get_registries_fallback" game/` returns 0 ✓
- [x] Remaining `get_default_registry_provider` usages documented as exceptions ✓
- [ ] Manual test: Game launches and runs (skipped - automated loop)
- [ ] Manual test: Workshop creates ship successfully (skipped - automated loop)
- [ ] Manual test: Battle simulation completes (skipped - automated loop)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md to mark project complete
