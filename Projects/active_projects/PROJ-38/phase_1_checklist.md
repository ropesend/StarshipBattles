# Phase 1: Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Create DI infrastructure without breaking existing code

---

## Tasks

### Task 1.1: Create GameRegistries Container [Simple] ✓ COMPLETE
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py`

- [x] Add import for `dataclass` from dataclasses module (after line 17)
- [x] Add `GameRegistries` frozen dataclass after imports:
  ```python
  @dataclass(frozen=True)
  class GameRegistries:
      """Immutable container for all game data registries."""
      components: Dict[str, Any]
      modifiers: Dict[str, Any]
      vehicle_classes: Dict[str, Any]
      resources: Dict[str, Any]
  ```
- [x] Add module-level `_default_registries: Optional[GameRegistries] = None`
- [x] Add `set_default_registries(registries: GameRegistries) -> None` function
- [x] Add `get_default_registries() -> GameRegistries` function with RuntimeError if not set
- [x] Verify: `pytest tests/unit/core/test_registry.py` passes

**Notes:** Added 7 new tests in TestGameRegistries and TestDefaultRegistries classes. All 5005 tests pass.

---

### Task 1.2: Create Pure Loading Functions for Components/Modifiers [Medium] ✓ COMPLETE
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py`

- [x] Create `load_components_data(filepath: str) -> Dict[str, 'Component']` function
  - Move core loading logic from `load_components()` into this function
  - Return the component dictionary instead of modifying global state
- [x] Create `load_modifiers_data(filepath: str) -> Dict[str, 'Modifier']` function
  - Move core loading logic from `load_modifiers()` into this function
  - Return the modifier dictionary instead of modifying global state
- [x] Refactor existing `load_components()` as thin wrapper:
  ```python
  def load_components(filepath="data/components.json"):
      data = load_components_data(filepath)
      RegistryManager.instance().components.update(data)
  ```
- [x] Refactor existing `load_modifiers()` as thin wrapper
- [x] Verify: `pytest tests/` passes (no behavior change)

**Notes:** Added 12 tests in tests/unit/core/test_pure_loaders.py. Both pure functions work independently of registry. Existing load functions refactored to use pure functions internally for cache population.

---

### Task 1.3: Create Pure Loading Function for Vehicle Classes [Simple] ✓ COMPLETE
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py`

- [x] Create `load_vehicle_classes_data(filepath: str, layers_filepath: str = None) -> Dict[str, Any]` function
  - Move core loading logic from `load_vehicle_classes()` into this function
  - Return the vehicle classes dictionary
- [x] Refactor existing `load_vehicle_classes()` as thin wrapper
- [x] Verify: `pytest tests/unit/core/test_pure_loaders.py` passes

**Notes:** Added 6 tests in TestLoadVehicleClassesData class. Pure function correctly loads and returns deep copies without modifying global state. Layer config resolution preserved.

---

### Task 1.4: Create Pure Loading Function for Resources [Simple] ✓ COMPLETE
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py`, `pytest tests/unit/core/test_resources_registry.py`

- [x] Create `load_resources_data(filepath: str) -> Dict[str, Any]` function
  - Move core loading logic from `load_resources()` into this function
  - Return the resources dictionary
- [x] Refactor existing `load_resources()` as thin wrapper
- [x] Verify: `pytest tests/unit/core/test_resources_registry.py` passes

**Notes:** Added 6 tests in TestLoadResourcesData class. Pure function handles path resolution and fallback to defaults. Wrapper preserves original logging behavior. All 39 existing tests still pass.

---

### Task 1.5: Update Composition Root [Medium] ✓ CODE COMPLETE (Pending Manual Verification)
**File:** `game/app.py`
**Tests:** Manual - launch game and verify main menu works

- [x] Add import: `from game.core.registry import GameRegistries, set_default_registries, RegistryManager`
- [ ] ~~Add imports for new pure loading functions~~ (Not needed - existing wrappers handle loading, composition root just wraps the result)
- [x] After `initialize_ship_data`, create `GameRegistries` instance:
  ```python
  self.registries = GameRegistries(
      components=registry.components,
      modifiers=registry.modifiers,
      vehicle_classes=registry.vehicle_classes,
      resources=registry.resources
  )
  set_default_registries(self.registries)
  ```
- [ ] Verify: Launch game, main menu displays correctly
- [x] Verify: `pytest tests/` passes

**Notes:** Code changes complete. Imports added, GameRegistries instance created and set as default after data loading. Manual verification pending (game launch test).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` passes (full suite)
- [ ] Game launches and main menu works
- [ ] Design Workshop opens correctly
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
