# Phase 1: Create LayerData + Update Core Ship Entities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define the LayerData dataclass, update Ship and ShipComponentManager to use it, consolidate duplicated layer initialization.

---

## Tasks

### Task 1.1: Create LayerData dataclass [Simple]
**File:** `game/simulation/entities/layer_data.py` (new)
**Tests:** `pytest tests/unit/entities/test_layer_data.py -x`

- [ ] Create new file `game/simulation/entities/layer_data.py`
- [ ] Define `@dataclass class LayerData` with 7 fields:
  - `components: List[Component] = field(default_factory=list)`
  - `radius_pct: float = 0.5`
  - `restrictions: List[str] = field(default_factory=list)`
  - `max_mass_pct: float = 1.0`
  - `mass: float = 0.0`
  - `hp_pool: int = 0`
  - `max_hp_pool: int = 0`
- [ ] Add `create_hull()` classmethod: returns LayerData with radius_pct=0.0, restrictions=['HullOnly'], max_mass_pct=100.0
- [ ] Add `from_definition(l_def: dict)` classmethod: creates from vehicle class layer definition dict, using `.get()` with same defaults as current code
- [ ] Add `clear()` method: resets components=[], mass=0.0, hp_pool=0, max_hp_pool=0
- [ ] Add LayerData to `game/simulation/entities/__init__.py` exports (if __init__.py exists)

**Notes:**

---

### Task 1.2: Write unit tests for LayerData [Simple]
**File:** `tests/unit/entities/test_layer_data.py` (new)
**Tests:** `pytest tests/unit/entities/test_layer_data.py -x`

- [ ] Test default construction (all defaults)
- [ ] Test construction with explicit values
- [ ] Test `create_hull()` returns correct radius_pct=0.0, restrictions=['HullOnly'], max_mass_pct=100.0
- [ ] Test `from_definition()` with full definition dict
- [ ] Test `from_definition()` with partial dict (missing keys use defaults)
- [ ] Test `clear()` resets mutable fields but preserves radius_pct, restrictions, max_mass_pct
- [ ] Test attribute access (components, radius_pct, etc.)

**Notes:**

---

### Task 1.3: Update Ship._initialize_layers() [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -x`

- [ ] Add import: `from game.simulation.entities.layer_data import LayerData`
- [ ] Change `self.layers` type annotation from `Dict[LayerType, Dict[str, Any]]` to `Dict[LayerType, LayerData]`
- [ ] Replace HULL dict literal (lines 359-365) with `LayerData.create_hull()`
- [ ] Replace loop dict literal (lines 374-380) with `LayerData.from_definition(l_def)`
- [ ] Update radius recalc (line 398): `self.layers[l]['max_mass_pct']` → `.max_mass_pct`
- [ ] Update radius recalc (line 404): `self.layers[l_type]['radius_pct'] = 0.0` → `.radius_pct = 0.0`
- [ ] Update radius recalc (line 406): `self.layers[l_type]['max_mass_pct']` → `.max_mass_pct`
- [ ] Update radius recalc (line 408): `self.layers[l_type]['radius_pct'] = ...` → `.radius_pct = ...`
- [ ] Update ALL component access throughout ship.py:
  - `add_component()`: `self.layers[layer_type]['components'].append(...)` → `.components.append(...)`
  - `remove_component()`: `self.layers[layer_type]['components'].pop(...)` → `.components.pop(...)`
  - `add_components_bulk()`: same pattern
  - `clear_non_hull_components()`: `layer_data['components'].clear()` → `.components.clear()`
  - `get_components_in_layer()`: `layer_data['components']` → `.components`
  - `get_all_components()`: same
  - `iter_components()`: same
  - `get_components_by_ability()`: same
  - `change_class()`: `data['components']` → `.components`
- [ ] Remove any references to dead `'hp'` key
- [ ] Verify: `pytest tests/unit/entities/test_ship.py -x` passes

**Notes:**

---

### Task 1.4: Update ShipComponentManager [Medium]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/ship_component_manager/ -x`

- [ ] Add import: `from game.simulation.entities.layer_data import LayerData`
- [ ] Change `self.layers` type annotation (line 45) to `Dict[LayerType, LayerData]`
- [ ] Replace HULL dict literal (lines 72-78) with `LayerData.create_hull()`
- [ ] Replace loop dict literal (lines 88-94) with `LayerData.from_definition(l_def)`
- [ ] Update `_recalculate_layer_radii()`: all `self.layers[l]['max_mass_pct']` → `.max_mass_pct`, `['radius_pct']` → `.radius_pct`
- [ ] Update all component access methods to use `.components` instead of `['components']`
- [ ] Evaluate consolidation: can Ship delegate to ShipComponentManager.initialize_layers() or both just use LayerData factories?
- [ ] Remove any references to dead `'hp'` key
- [ ] Verify: `pytest tests/unit/simulation/ship_component_manager/ -x` passes

**Notes:**

---

### Task 1.5: Incremental test run [Simple]
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ship_component_manager/ -x`

- [ ] Run combined test suite for Phase 1 scope
- [ ] Fix any failures discovered
- [ ] Verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
