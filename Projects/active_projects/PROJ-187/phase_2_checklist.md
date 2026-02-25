# Phase 2: action_time on Component Abilities [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `action_time` field to strategic abilities (ColonizePlanet, superweapon markers) and create an `ActionTimeResolver` that reads action_time from a fleet's component abilities for a given order type.

---

## Tasks

### Task 2.1: Add action_time to ColonizePlanet ability [Simple]
**File:** `game/simulation/components/abilities/colonize.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k "colonize"`

- [x] In `ColonizePlanet.__init__()`, parse `action_time` from data dict: `self.action_time = data.get('action_time', 1) if isinstance(data, dict) else 1`
- [x] String shorthand (`"ColonizePlanet": "CONTINENTAL"`) defaults to action_time=1
- [x] Dict format supports: `"ColonizePlanet": {"planet_type": "CONTINENTAL", "action_time": 2}`

**Notes:**

### Task 2.2: Add action_time to SuperweaponMarker base class [Simple]
**File:** `game/simulation/components/abilities/superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k "superweapon"`

- [x] In `SuperweaponMarker.__init__()`, override to parse `action_time`: `self.action_time = data.get('action_time', 1) if isinstance(data, dict) else 1`
- [x] Boolean marker (`"DestroyPlanet": true`) defaults to action_time=1
- [x] Dict format supports: `"DestroyPlanet": {"action_time": 5}`

**Notes:**

### Task 2.3: Update components.json with action_time values [Simple]
**File:** `data/components.json`
**Tests:** Validate JSON loads correctly

- [x] Update `stellerator` component: `"DestroyStar": {"action_time": 5}`
- [x] Update `dyson_sphere_constructor`: `"CreateDysonSphere": {"action_time": 5}`
- [x] Update `planet_imploder`: `"DestroyPlanet": {"action_time": 3}`
- [x] Update `quantum_tunneling_inverter`: `"OpenWarpPoint": {"action_time": 3}`
- [x] Update `quantum_tunneling_diverter`: `"CloseWarpPoint": {"action_time": 3}`
- [x] Colony pods and self-destruct keep defaults (action_time=1, no JSON change needed)

**Notes:**

### Task 2.4: Create ActionTimeResolver service [Medium]
**File:** `game/strategy/services/action_time_resolver.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_action_time_resolver.py` (new)

- [x] Create `ActionTimeResolver` class with method: `resolve_action_time(fleet: Fleet, order: FleetOrder, component_registry=None) -> int`
- [x] For COLONIZE: find ship with ColonizePlanet ability, return its `action_time`
- [x] For superweapon orders: find ship with matching superweapon ability, return its `action_time`
- [x] For TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION, JOIN_FLEET: return 1 (default)
- [x] For WARP: return 1 (default)
- [x] Fallback: return 1 for any unknown order type
- [x] Write unit tests with mock fleets and component data

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (12,415 passed, 1 skipped)
- [x] No behavior changes — existing tests still pass without modification
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
