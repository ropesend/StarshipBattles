# Phase 2: Complete PROJ-38 Registry Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Migrate all deprecated registry access to GameRegistries DI pattern
**Complexity:** Complex

---

## Pre-Phase Checklist
- [x] Phase 1 complete
- [x] Read [design.md](design.md) - review "Dual Registry System Analysis" section
- [x] Verify: `pytest tests/` passes

---

## Task 2.1: Update ShipStatsService to GameRegistries [Medium] ✅
**Issues:** BCD-001
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/services/test_ship_stats_service_di.py`

### Subtasks
- [x] Remove `try/except` fallback chain in `__init__` - extracted to `_get_registries_fallback()` static method
- [x] Make `registries` parameter use fallback when None - via `_get_registries_fallback()`
- [x] Remove all calls to `get_vehicle_classes()` - static paths now use `_get_registries_fallback().vehicle_classes`
- [x] Remove all calls to `get_component_registry()` - static paths now use `_get_registries_fallback().components`
- [x] Remove all calls to `get_modifier_registry()` - static paths now use `_get_registries_fallback().modifiers`
- [x] Update `calculate_stats()` static path - uses `_iterate_design_components_with_registries()` for clean fallback
- [x] Run tests: `pytest tests/unit/services/test_ship_stats_service*.py` - 8 passed

**Notes:** Added `_get_registries_fallback()` helper that tries `get_default_registries()` first, then falls back to provider (which shares mutable dict refs). Added `_iterate_design_components_with_registries()` for clean static path.

---

## Task 2.2: Update ModifierService to GameRegistries [Medium]
**Issues:** LPH-001
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service_di.py`

### Subtasks
- [ ] Remove `try/except` fallback chain in `__init__` (lines 48-52)
- [ ] Remove all calls to `get_modifier_registry()` - use `self._registries.modifiers`
- [ ] Update methods to use instance `_registries` instead of global functions:
  - `is_modifier_allowed()` (line 93-98)
  - `get_initial_value()` (line 274-279)
  - `get_local_min_max()` (line 382-387)
- [ ] Run tests: `pytest tests/unit/services/test_modifier_service*.py`

**Notes:**

---

## Task 2.3: Update Ship Entity to GameRegistries [Medium]
**Issues:** BCD-001
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship*.py`

### Subtasks
- [ ] Remove `try/except` fallback chain in `__init__` (lines 67-74)
- [ ] Remove all calls to `get_vehicle_classes()`:
  - Line 80: `class_def = get_vehicle_classes()...`
  - Line 363: In `_initialize_layers()`
  - Line 617: In stats calculator creation
- [ ] Fix bug at line 467: Add `registries=self._registries` to `create_component()` call
- [ ] Update `_ValidatorProxy` to use registries if possible, or document why proxy is still needed
- [ ] Run tests: `pytest tests/unit/entities/test_ship*.py tests/unit/simulation/`

**Notes:**

---

## Task 2.4: Update Component to GameRegistries [Medium]
**Issues:** BCD-001
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/test_component*.py`

### Subtasks
- [ ] Remove module-level `COMPONENT_REGISTRY = get_component_registry()` (line 74)
- [ ] Remove module-level `MODIFIER_REGISTRY = get_modifier_registry()` (line 75)
- [ ] Remove `try/except` fallback in `__init__` (lines 94-101)
- [ ] Update all methods to use `self._registries` instead of module-level registries:
  - Modifier loading (lines 151-163)
  - `add_modifier()` (lines 414-417)
- [ ] Run tests: `pytest tests/unit/simulation/test_component*.py`

**Notes:**

---

## Task 2.5: Update VehicleDesignService [Medium]
**Issues:** BCD-001
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/services/test_vehicle_design_service_di.py`

### Subtasks
- [ ] Remove dual constructor support (lines 56-86)
- [ ] Remove `registry: Optional['IRegistryProvider']` parameter
- [ ] Keep only `registries: Optional[GameRegistries]` parameter
- [ ] Remove fallback to `get_default_registry_provider()`
- [ ] Update all internal methods to use `self._registries`
- [ ] Run tests: `pytest tests/unit/services/test_vehicle_design_service*.py`

**Notes:**

---

## Task 2.6: Update UI Layer Files [Medium]
**Files:**
- `game/ui/screens/workshop_screen.py` (4 occurrences)
- `game/ui/screens/workshop_event_router.py` (2 occurrences)
- `game/ui/screens/workshop_data_loader.py`
- `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/`

### Subtasks
- [ ] In `workshop_screen.py`: Replace `get_vehicle_classes()` with registry access
- [ ] In `workshop_event_router.py`: Replace `get_vehicle_classes()` with registry access
- [ ] In `workshop_data_loader.py`: Replace `get_vehicle_classes()` with registry access
- [ ] In `builder_widgets.py`: Replace `get_modifier_registry()` with registry access
- [ ] Ensure registries are passed from App to UI screens during construction
- [ ] Run tests: `pytest tests/unit/ui/`

**Notes:**

---

## Task 2.7: Update Remaining Files [Medium]
**Files:**
- `game/simulation/entities/ship_loader.py`
- `game/simulation/entities/ship_serialization.py`
- `game/simulation/ship_validator.py`
- `game/core/resources.py`
- `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/` after each file

### Subtasks
- [ ] Update `ship_loader.py`: Replace `get_validator()`, `get_vehicle_classes()`
- [ ] Update `ship_serialization.py`: Replace `get_component_registry()`, `get_modifier_registry()`
- [ ] Update `ship_validator.py`: Replace `get_vehicle_classes()`
- [ ] Update `resources.py`: Replace `get_resource_registry()`
- [ ] Update `resource_management_engine.py`: Replace `get_component_registry()`
- [ ] Run tests after each: `pytest tests/unit/`

**Notes:**

---

## Task 2.8: Remove Deprecated Utility Functions [Complex]
**Issue:** BCD-002
**File:** `game/core/registry.py` (lines 298-364)
**Tests:** `pytest tests/` (full suite)

### Subtasks
- [ ] Verify no remaining calls to deprecated functions in production code:
  ```bash
  grep -r "get_component_registry\|get_modifier_registry\|get_vehicle_classes\|get_validator\|get_resource_registry" game/ --include="*.py" | grep -v "def get_"
  ```
- [ ] Remove function `get_component_registry()` (lines 298-312)
- [ ] Remove function `get_modifier_registry()` (lines 314-325)
- [ ] Remove function `get_vehicle_classes()` (lines 327-338)
- [ ] Remove function `get_validator()` (lines 340-351)
- [ ] Remove function `get_resource_registry()` (lines 353-364)
- [ ] Run full test suite: `pytest tests/`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all tests pass
- [ ] Count deprecation warnings - should be SIGNIFICANTLY reduced (target: ~0 from registry functions)
- [ ] Verify no remaining calls to deprecated registry functions in production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
- [ ] Commit: "PROJ-42 Phase 2: Complete PROJ-38 GameRegistries DI migration"
