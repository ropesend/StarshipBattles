# Phase 1: Ability Classes & Component Definitions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create three new ability classes, register them in the ability registry, and add component definitions to `components.json`.

---

## Tasks

### Task 1.1: Create Planetary Ability Classes [Medium]
**File:** `game/simulation/components/abilities/planetary.py` (NEW)
**Tests:** `python -m pytest tests/unit/simulation/components/abilities/test_planetary_abilities.py -v`

Follow the pattern in `game/simulation/components/abilities/harvester.py` (ResourceHarvesterAbility):

- [ ] Create new file `game/simulation/components/abilities/planetary.py`
- [ ] Import: `from .base import Ability`, `from .stat_keys import AbilityStatBinding`, `from .ui_colors import HINT_SHIELD_CAP, HINT_ACCURACY, HINT_DEFAULT`
- [ ] Create `PlanetaryShieldAbility(Ability)`:
  - `STAT_BINDINGS: List[AbilityStatBinding] = []` (strategic marker)
  - `__init__(self, component, data)`: parse `energy_drain_rate` (float), `activation_time` (int, ticks), `deactivation_time` (int, ticks), `shield_hp` (float, default 0, combat placeholder), `shield_regen` (float, default 0, combat placeholder)
  - `get_primary_value()` → returns `self.energy_drain_rate`
  - `get_ui_rows()` → returns rows for Energy Drain, Activation Time, Deactivation Time
- [ ] Create `PlanetaryEnergyGeneratorAbility(Ability)`:
  - `STAT_BINDINGS: List[AbilityStatBinding] = []`
  - `__init__`: parse `generation_rate` (float, energy per turn)
  - `get_primary_value()` → returns `self.generation_rate`
  - `get_ui_rows()` → returns row for Generation Rate
- [ ] Create `PlanetaryEnergyStorageAbility(Ability)`:
  - `STAT_BINDINGS: List[AbilityStatBinding] = []`
  - `__init__`: parse `capacity` (float, max energy units)
  - `get_primary_value()` → returns `self.capacity`
  - `get_ui_rows()` → returns row for Storage Capacity
- [ ] Handle non-dict data gracefully (like `harvester.py` line 19-23)

**Notes:**

---

### Task 1.2: Register Abilities in Registry [Simple]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** `python -m pytest tests/unit/simulation/components/abilities/ -v`

- [ ] Add import after line 68 (harvester imports):
  ```python
  from .planetary import PlanetaryShieldAbility, PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility
  ```
- [ ] Add to `ABILITY_REGISTRY` dict (after line 101, EmpireStorage entry):
  ```python
  "PlanetaryShield": PlanetaryShieldAbility,
  "PlanetaryEnergyGenerator": PlanetaryEnergyGeneratorAbility,
  "PlanetaryEnergyStorage": PlanetaryEnergyStorageAbility,
  ```
- [ ] Add to `__all__` list (after line 172, CargoStorage entry):
  ```python
  'PlanetaryShieldAbility',
  'PlanetaryEnergyGeneratorAbility',
  'PlanetaryEnergyStorageAbility',
  ```

**Notes:**

---

### Task 1.3: Add Component Definitions to components.json [Medium]
**File:** `data/components.json`
**Tests:** `python -m pytest tests/unit/simulation/components/ -v`

Add three new components at end of components array (before the final `]`). Follow existing component structure (see `metal_harvester`, `resource_vault_metals`, `fuel_synthesizer` for examples).

- [ ] Add `planetary_shield_generator` component:
  ```json
  {
      "id": "planetary_shield_generator",
      "name": "Planetary Shield Generator",
      "type": "PlanetaryDefense",
      "mass": 500,
      "hp": 300,
      "allowed_vehicle_types": ["Planetary Complex"],
      "sprite_index": 0,
      "abilities": {
          "PlanetaryShield": {
              "energy_drain_rate": 25.0,
              "activation_time": 50,
              "deactivation_time": 10,
              "shield_hp": 0,
              "shield_regen": 0
          }
      },
      "major_classification": "Defense",
      "resource_cost": {"Metals": 500, "Exotics": 200, "Radioactives": 100}
  }
  ```
- [ ] Add `planetary_energy_generator` component:
  ```json
  {
      "id": "planetary_energy_generator",
      "name": "Planetary Energy Generator",
      "type": "PlanetaryInfrastructure",
      "mass": 200,
      "hp": 150,
      "allowed_vehicle_types": ["Planetary Complex"],
      "sprite_index": 0,
      "abilities": {
          "PlanetaryEnergyGenerator": {"generation_rate": 50.0}
      },
      "major_classification": "Infrastructure",
      "resource_cost": {"Metals": 200, "Radioactives": 50}
  }
  ```
- [ ] Add `planetary_energy_battery` component:
  ```json
  {
      "id": "planetary_energy_battery",
      "name": "Planetary Energy Battery",
      "type": "PlanetaryInfrastructure",
      "mass": 150,
      "hp": 100,
      "allowed_vehicle_types": ["Planetary Complex"],
      "sprite_index": 0,
      "abilities": {
          "PlanetaryEnergyStorage": {"capacity": 5000.0}
      },
      "major_classification": "Infrastructure",
      "resource_cost": {"Metals": 150, "Vapors": 50}
  }
  ```

**Notes:**

---

### Task 1.4: Write Unit Tests for New Abilities [Medium]
**File:** `tests/unit/simulation/components/abilities/test_planetary_abilities.py` (NEW)
**Tests:** `python -m pytest tests/unit/simulation/components/abilities/test_planetary_abilities.py -v`

- [ ] Create test file following pattern of existing ability tests
- [ ] Test `PlanetaryShieldAbility`:
  - Construction from dict data with all fields
  - `get_primary_value()` returns `energy_drain_rate`
  - `get_ui_rows()` returns non-empty list
  - Construction with partial/missing data (defaults applied)
- [ ] Test `PlanetaryEnergyGeneratorAbility`:
  - Construction from dict, `get_primary_value()`, `get_ui_rows()`
- [ ] Test `PlanetaryEnergyStorageAbility`:
  - Construction from dict, `get_primary_value()`, `get_ui_rows()`
- [ ] Test `create_ability()` factory from `__init__.py`:
  - `create_ability("PlanetaryShield", mock_component, data)` returns `PlanetaryShieldAbility`
  - `create_ability("PlanetaryEnergyGenerator", mock_component, data)` returns `PlanetaryEnergyGeneratorAbility`
  - `create_ability("PlanetaryEnergyStorage", mock_component, data)` returns `PlanetaryEnergyStorageAbility`
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 3 ability classes created and registered
- [ ] All 3 component definitions added to `components.json`
- [ ] Ability tests pass
- [ ] `python -m pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
