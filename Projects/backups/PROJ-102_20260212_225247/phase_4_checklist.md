# Phase 4: Validators

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create business logic validators for each superweapon order.

---

## Tasks

### Task 4.1: Create SuperweaponValidator [Medium]
**New File:** `game/strategy/validation/superweapon_validator.py`
**Pattern:** Follow existing validators in `game/strategy/validation/`
**Tests:** `pytest tests/unit/strategy/validation/test_superweapon_validator.py`

- [x] Create `SuperweaponValidator` class with static methods
- [x] `find_ship_with_ability(fleet, ability_name, component_registry) -> Optional[ShipInstance]`:
  - Generic helper: iterate `fleet.get_combat_capable_ships()` -> `ship.design_data["layers"]` -> components -> abilities
  - Check if ability_name key exists in component's abilities dict
  - Return first matching ship or None
  - Pattern from `ColonizeValidator.find_ship_with_colony_pod()`

- [x] `validate_implode_planet(galaxy, fleet, target_planet, component_registry=None) -> ValidationResult`:
  - Fleet must have ship with `DestroyPlanet` ability
  - Target planet must exist
  - Fleet must be at planet's global hex (or fleet will move there via mission command)
  - Return `validation_result(True/False, message)`

- [x] `validate_stellerate_star(galaxy, fleet, component_registry=None) -> ValidationResult`:
  - Fleet must have ship with `DestroyStar` ability
  - Fleet must be in a star system (find system at fleet location)
  - System must have at least one star

- [x] `validate_open_warp_point(galaxy, fleet, target_system_name, component_registry=None) -> ValidationResult`:
  - Fleet must have ship with `OpenWarpPoint` ability
  - Target system must exist in `galaxy.name_map`
  - Current system must not already have warp link to target system
  - Fleet must be in a star system

- [x] `validate_close_warp_point(galaxy, fleet, warp_point_dest_id, component_registry=None) -> ValidationResult`:
  - Fleet must have ship with `CloseWarpPoint` ability
  - Warp point with matching destination_id must exist at fleet's hex
  - Fleet must be in a star system

- [x] `validate_create_dyson_sphere(galaxy, fleet, component_registry=None) -> ValidationResult`:
  - Fleet must have ship with `CreateDysonSphere` ability
  - Fleet must be at a star system with at least one star
  - System must have stars (not already a Dyson Sphere)

- [x] `validate_self_destruct(fleet, ship_ids, component_registry=None) -> ValidationResult`:
  - Fleet must exist and have ships
  - All ship_ids must correspond to ships in the fleet
  - All specified ships must have `SelfDestruct` ability in their design_data

**Notes:** Created _find_system_at_location() helper to check both direct system location and offsets (planet/star/warp point hexes).

### Task 4.2: Register in Validation Package [Simple]
**File:** `game/strategy/validation/__init__.py`
**Tests:** Import test

- [x] Add `from .superweapon_validator import SuperweaponValidator`
- [x] Add to `__all__` if it exists

**Notes:**

### Task 4.3: Write Phase 4 Unit Tests [Medium]
**New File:** `tests/unit/strategy/validation/test_superweapon_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_superweapon_validator.py -v`

- [x] Test `find_ship_with_ability()` finds ship with matching ability
- [x] Test `find_ship_with_ability()` returns None when no ship has ability
- [x] Test `validate_implode_planet()` - valid case: fleet at planet hex with ability
- [x] Test `validate_implode_planet()` - invalid: no DestroyPlanet ability
- [x] Test `validate_stellerate_star()` - valid case
- [x] Test `validate_stellerate_star()` - invalid: not at star system
- [x] Test `validate_open_warp_point()` - valid case
- [x] Test `validate_open_warp_point()` - invalid: target system doesn't exist
- [x] Test `validate_open_warp_point()` - invalid: warp link already exists
- [x] Test `validate_close_warp_point()` - valid case
- [x] Test `validate_close_warp_point()` - invalid: no warp point at location
- [x] Test `validate_create_dyson_sphere()` - valid case
- [x] Test `validate_self_destruct()` - valid case with matching ship IDs
- [x] Test `validate_self_destruct()` - invalid: ship ID not in fleet
- [x] Test `validate_self_destruct()` - invalid: ship lacks SelfDestruct ability
- [x] Verify: all tests pass

**Notes:** 25 tests total, covering all validators and edge cases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
