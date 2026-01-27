# Phase 1: Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create DI infrastructure without breaking existing code

---

## Tasks

### Task 1.1: Create GameRegistries Container [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py`

- [ ] Add import for `dataclass` from dataclasses module (after line 17)
- [ ] Add `GameRegistries` frozen dataclass after imports:
  ```python
  @dataclass(frozen=True)
  class GameRegistries:
      """Immutable container for all game data registries."""
      components: Dict[str, Any]
      modifiers: Dict[str, Any]
      vehicle_classes: Dict[str, Any]
      resources: Dict[str, Any]
  ```
- [ ] Add module-level `_default_registries: Optional[GameRegistries] = None`
- [ ] Add `set_default_registries(registries: GameRegistries) -> None` function
- [ ] Add `get_default_registries() -> GameRegistries` function with RuntimeError if not set
- [ ] Verify: `pytest tests/unit/core/test_registry.py` passes

**Notes:**

---

### Task 1.2: Create Pure Loading Functions for Components/Modifiers [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Create `load_components_data(filepath: str) -> Dict[str, 'Component']` function
  - Move core loading logic from `load_components()` into this function
  - Return the component dictionary instead of modifying global state
- [ ] Create `load_modifiers_data(filepath: str) -> Dict[str, 'Modifier']` function
  - Move core loading logic from `load_modifiers()` into this function
  - Return the modifier dictionary instead of modifying global state
- [ ] Refactor existing `load_components()` as thin wrapper:
  ```python
  def load_components(filepath="data/components.json"):
      data = load_components_data(filepath)
      RegistryManager.instance().components.update(data)
  ```
- [ ] Refactor existing `load_modifiers()` as thin wrapper
- [ ] Verify: `pytest tests/` passes (no behavior change)

**Notes:**

---

### Task 1.3: Create Pure Loading Function for Vehicle Classes [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/`

- [ ] Create `load_vehicle_classes_data(filepath: str, layers_filepath: str = None) -> Dict[str, Any]` function
  - Move core loading logic from `load_vehicle_classes()` into this function
  - Return the vehicle classes dictionary
- [ ] Refactor existing `load_vehicle_classes()` as thin wrapper
- [ ] Verify: `pytest tests/unit/entities/` passes

**Notes:**

---

### Task 1.4: Create Pure Loading Function for Resources [Simple]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_resources_registry.py`

- [ ] Create `load_resources_data(filepath: str) -> Dict[str, Any]` function
  - Move core loading logic from `load_resources()` into this function
  - Return the resources dictionary
- [ ] Refactor existing `load_resources()` as thin wrapper
- [ ] Verify: `pytest tests/unit/core/test_resources_registry.py` passes

**Notes:**

---

### Task 1.5: Update Composition Root [Medium]
**File:** `game/app.py`
**Tests:** Manual - launch game and verify main menu works

- [ ] Add import: `from game.core.registry import GameRegistries, set_default_registries`
- [ ] Add imports for new pure loading functions:
  ```python
  from game.simulation.components.component import load_components_data, load_modifiers_data
  from game.simulation.entities.ship_loader import load_vehicle_classes_data
  from game.core.resources import load_resources_data
  ```
- [ ] After line 114 (after `initialize_ship_data`), create `GameRegistries` instance:
  ```python
  self.registries = GameRegistries(
      components=RegistryManager.instance().components,
      modifiers=RegistryManager.instance().modifiers,
      vehicle_classes=RegistryManager.instance().vehicle_classes,
      resources=RegistryManager.instance().resources
  )
  set_default_registries(self.registries)
  ```
- [ ] Verify: Launch game, main menu displays correctly
- [ ] Verify: Can open Design Workshop
- [ ] Verify: `pytest tests/` passes

**Notes:**

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
