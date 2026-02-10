# Phase 1: Create LayerData + Update Core Ship Entities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Define the LayerData dataclass, update Ship and ShipComponentManager to use it, consolidate duplicated layer initialization.

---

## Tasks

### Task 1.1: Create LayerData dataclass [Simple]
**File:** `game/simulation/entities/layer_data.py` (new)
**Tests:** `pytest tests/unit/entities/test_layer_data.py -x`

- [x] Create new file `game/simulation/entities/layer_data.py`
- [x] Define `@dataclass class LayerData` with 7 fields:
  - `components: List[Component] = field(default_factory=list)`
  - `radius_pct: float = 0.5`
  - `restrictions: List[str] = field(default_factory=list)`
  - `max_mass_pct: float = 1.0`
  - `mass: float = 0.0`
  - `hp_pool: int = 0`
  - `max_hp_pool: int = 0`
- [x] Add `create_hull()` classmethod: returns LayerData with radius_pct=0.0, restrictions=['HullOnly'], max_mass_pct=100.0
- [x] Add `from_definition(l_def: dict)` classmethod: creates from vehicle class layer definition dict, using `.get()` with same defaults as current code
- [x] Add `clear()` method: resets components=[], mass=0.0, hp_pool=0, max_hp_pool=0
- [x] Add LayerData to `game/simulation/entities/__init__.py` exports (if __init__.py exists) - N/A, no __init__.py

**Notes:** Implemented with full docstrings and type hints.

---

### Task 1.2: Write unit tests for LayerData [Simple]
**File:** `tests/unit/entities/test_layer_data.py` (new)
**Tests:** `pytest tests/unit/entities/test_layer_data.py -x`

- [x] Test default construction (all defaults)
- [x] Test construction with explicit values
- [x] Test `create_hull()` returns correct radius_pct=0.0, restrictions=['HullOnly'], max_mass_pct=100.0
- [x] Test `from_definition()` with full definition dict
- [x] Test `from_definition()` with partial dict (missing keys use defaults)
- [x] Test `clear()` resets mutable fields but preserves radius_pct, restrictions, max_mass_pct
- [x] Test attribute access (components, radius_pct, etc.)

**Notes:** 24 tests written, all passing.

---

### Task 1.3: Update Ship._initialize_layers() [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -x`

- [x] Add import: `from game.simulation.entities.layer_data import LayerData`
- [x] Change `self.layers` type annotation from `Dict[LayerType, Dict[str, Any]]` to `Dict[LayerType, LayerData]`
- [x] Replace HULL dict literal with `LayerData.create_hull()`
- [x] Replace loop dict literal with `LayerData.from_definition(l_def)`
- [x] Update radius recalc: `.max_mass_pct` and `.radius_pct`
- [x] Update ALL component access throughout ship.py: `.components` instead of `['components']`
- [x] Remove any references to dead `'hp'` key
- [x] Verify: tests pass

**Notes:** All 17 methods updated to use LayerData attribute access.

---

### Task 1.4: Update ShipComponentManager [Medium]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/ship_component_manager/ -x`

- [x] Add import: `from game.simulation.entities.layer_data import LayerData`
- [x] Change `self.layers` type annotation to `Dict[LayerType, LayerData]`
- [x] Replace HULL dict literal with `LayerData.create_hull()`
- [x] Replace loop dict literal with `LayerData.from_definition(l_def)`
- [x] Update `_recalculate_layer_radii()`: `.max_mass_pct`, `.radius_pct`
- [x] Update all component access methods to use `.components`
- [x] Remove any references to dead `'hp'` key
- [x] Verify: tests pass

**Notes:** Updated all methods. Ship and ShipComponentManager now share LayerData factories.

---

### Task 1.5: Incremental test run [Simple]
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ship_component_manager/ -x`

- [x] Run combined test suite for Phase 1 scope
- [x] Fix any failures discovered
- [x] Verify all pass

**Notes:** 377 tests passing for core entity tests. Also updated dependent files:
- ship_stats.py - layer attribute access
- ship_serialization.py - layer attribute access
- ship_validator.py - layer attribute access
- damage_calculator.py - layer sorting and component access
- vehicle_design_service.py - layer component access
- UI files (workshop_event_router.py, layer_panel.py, etc.) - cascading updates

---

## Additional Updates (Cascading Changes)

The following files were also updated to maintain compatibility:
- game/simulation/entities/ship_stats.py
- game/simulation/entities/ship_serialization.py
- game/simulation/validation/ship_validator.py
- game/simulation/combat/damage_calculator.py
- game/simulation/services/vehicle_design_service.py
- game/ui/screens/workshop_event_router.py
- game/ui/screens/workshop_viewmodel.py
- game/ui/screens/builder_selection.py
- game/ui/screens/builder/layer_panel.py
- game/ui/screens/builder/stats_config.py
- game/ui/screens/builder/main.py
- game/ui/screens/builder/schematic_view.py
- game/ui/screens/builder/state_manager.py
- game/ui/screens/builder/weapons_panel.py
- game/ui/renderer/game_renderer.py
- game/ui/panels/ship_stats_renderer.py

Many test files also updated with LayerData usage.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

**Final Test Status:** 7375 passed (100% passing)
