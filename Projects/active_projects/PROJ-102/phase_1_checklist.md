# Phase 1: Ability Classes & Component Definitions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create all 6 strategic marker abilities and their component JSON entries. Zero runtime dependencies - fully unit-testable.

---

## Tasks

### Task 1.1: Create Superweapon Ability Classes [Simple]
**New File:** `game/simulation/components/abilities/superweapons.py`
**Pattern:** Follow `game/simulation/components/abilities/colonize.py` (ColonizePlanet)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py`

- [ ] Create `DestroyPlanet(Ability)`:
  - `layer = AbilityLayer.STRATEGIC`
  - `allowed_scopes = [AbilityScope.SELF]`
  - `default_scope = AbilityScope.SELF`
  - `STAT_BINDINGS = []`
  - `__init__` calls `super().__init__(component, data)` only
  - `get_ui_rows()` returns `[{'label': 'Superweapon', 'value': 'Planet Imploder', 'color_hint': '#FF4444'}]`
  - `get_primary_value()` returns `0.0`
- [ ] Create `DestroyStar(Ability)` - same pattern, value "Stellerator"
- [ ] Create `OpenWarpPoint(Ability)` - same pattern, value "Warp Point Creator"
- [ ] Create `CloseWarpPoint(Ability)` - same pattern, value "Warp Point Closer"
- [ ] Create `CreateDysonSphere(Ability)` - same pattern, value "Dyson Sphere Constructor"
- [ ] Create `SelfDestruct(Ability)` - same pattern, value "Self-Destruct Device"

**Notes:**

### Task 1.2: Register Abilities in Registry [Simple]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py`

- [ ] Add import: `from .superweapons import DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct`
- [ ] Add to `ABILITY_REGISTRY` dict (after `"CargoStorage": CargoStorage`):
  ```python
  "DestroyPlanet": DestroyPlanet,
  "DestroyStar": DestroyStar,
  "OpenWarpPoint": OpenWarpPoint,
  "CloseWarpPoint": CloseWarpPoint,
  "CreateDysonSphere": CreateDysonSphere,
  "SelfDestruct": SelfDestruct,
  ```
- [ ] Add all 6 to `__all__` list

**Notes:**

### Task 1.3: Add Component JSON Entries [Simple]
**File:** `data/components.json`
**Tests:** Manual verification - load components, check ability instantiation

- [ ] Add "planet_imploder" component:
  ```json
  {
      "id": "planet_imploder",
      "name": "Planet Imploder",
      "type": "Superweapon",
      "mass": 2000,
      "hp": 500,
      "allowed_vehicle_types": ["Ship"],
      "sprite_index": 230,
      "abilities": { "DestroyPlanet": true },
      "major_classification": "Superweapon",
      "resource_cost": { "Metals": 2000, "Radioactives": 1000, "Exotics": 500 }
  }
  ```
- [ ] Add "stellerator" component with `"DestroyStar": true`
- [ ] Add "quantum_tunneling_inverter" with `"OpenWarpPoint": true`
- [ ] Add "quantum_tunneling_diverter" with `"CloseWarpPoint": true`
- [ ] Add "dyson_sphere_constructor" with `"CreateDysonSphere": true`
- [ ] Add "self_destruct_device" with `"SelfDestruct": true` (low mass: 50, low cost)

**Notes:**

### Task 1.4: Write Phase 1 Unit Tests [Simple]
**New File:** `tests/unit/simulation/components/abilities/test_superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py -v`

- [ ] Test each ability class instantiates without error (mock component, data=True)
- [ ] Test `layer == AbilityLayer.STRATEGIC` for each
- [ ] Test `STAT_BINDINGS == []` for each
- [ ] Test `get_primary_value() == 0.0` for each
- [ ] Test `get_ui_rows()` returns non-empty list with expected label for each
- [ ] Test all 6 exist in `ABILITY_REGISTRY` by name
- [ ] Test `create_ability('DestroyPlanet', mock_component, True)` creates valid instance
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_superweapons.py` - all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
