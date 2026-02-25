# Phase 4: Replace hasattr Type Discrimination [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace ~25 `hasattr` type-checking patterns with `isinstance` checks using concrete types or existing protocols.

---

## Tasks

### Task 4.1: Galaxy registry and spatial index (8 instances) [Simple]
**Files:** `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/ -n 12`

- [x] `galaxy_entity_registry.py` L56: Remove `hasattr(planet, 'diameter_hexes')` guard — Planet dataclass always has this (default 0.0), just check `planet.diameter_hexes > 0`
- [x] `galaxy_entity_registry.py` L82: Same as above
- [x] `galaxy_entity_registry.py` L111: Same as above
- [x] `galaxy_entity_registry.py` L161: `hasattr(obj, 'occupied_hexes')` → `is_zone_occupant(obj)` from `game.core.protocols`
- [x] `galaxy_entity_registry.py` L180: Same as above
- [x] `galaxy_spatial_index.py` L49: `hasattr(obj, 'location')` → kept (generic `Any` type, legitimate guard)
- [x] `galaxy_spatial_index.py` L164: `hasattr(star, 'location')` → direct access `star.location` (Star always has this)
- [x] `galaxy_spatial_index.py` L167: `hasattr(star, 'occupied_hexes')` → `is_zone_occupant(star)`
- [x] Run tests

**Notes:** Added `from game.core.protocols import is_zone_occupant` where needed.

### Task 4.2: Validators and fleet_order_processor (8 instances) [Simple]
**Files:** `game/strategy/validation/colonize_validator.py`, `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/validation/ tests/unit/strategy/ -k "colonize or fleet_order" -n 12`

- [x] `colonize_validator.py` L88: Remove `hasattr(galaxy, 'get_zones_at_global_hex')` — Galaxy always has this
- [x] `colonize_validator.py` L92: `hasattr(zone_obj, 'planet_type')` → `isinstance(zone_obj, Planet)` (add import)
- [x] `colonize_validator.py` L117: `hasattr(candidate, 'planet_type')` → `isinstance(candidate, Planet)`
- [x] `colonize_validator.py` L248: `hasattr(target, 'planet_type')` → `is_planet(target)` for protocol-based check (allows test mocks)
- [x] `fleet_order_processor.py` L149: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [x] `fleet_order_processor.py` L222: `hasattr(candidate, 'planet_type')` → `isinstance(candidate, Planet)` (add import)
- [x] `fleet_order_processor.py` L694: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [x] Run tests

**Notes:** Used `is_planet()` protocol for order.target checks to support test mocks that satisfy IPlanet.

### Task 4.3: superweapon_order_processor.py (7 instances) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k superweapon`

- [x] L97: Remove `hasattr(target_planet, 'owner_id')` — Planet always has `owner_id` (None for unowned)
- [x] L99: Remove `hasattr(empire, 'colonies')` — Empire always has `colonies` list
- [x] L172: Remove `hasattr(planet, 'owner_id')`
- [x] L174: Remove `hasattr(emp, 'colonies')`
- [x] L182: Remove `hasattr(galaxy, 'unregister_fleet')` — Galaxy always has this method
- [x] L445: Remove `hasattr(planet, 'owner_id')`
- [x] L446: Remove `hasattr(empire, 'colonies')`
- [x] Run tests

**Notes:** Removed hasattr guards, keeping condition logic. E.g., `if hasattr(planet, 'owner_id') and planet.owner_id is not None:` → `if planet.owner_id is not None:`

### Task 4.4: FleetOrder.to_dict serialization (3 instances) [Medium]
**File:** `game/strategy/data/fleet.py` (lines 74-108)
**Tests:** `pytest tests/unit/strategy/data/ tests/unit/strategy/ -k fleet -n 12`

- [x] L81: `hasattr(self.target, 'id')` → `isinstance(self.target, Planet)` (add `from game.strategy.data.planet import Planet` runtime import)
- [x] L93: `hasattr(self.target, 'to_dict')` → handle explicitly: if target is Planet, call to_dict()
- [x] L95: `hasattr(self.target, 'id')` → `isinstance(self.target, Fleet)`
- [x] Verify save/load round-trip: the serialized format must NOT change (only the branching logic changes)
- [x] Run tests

**Notes:** Used runtime import to avoid circular dependency. All serialization tests pass.

### Task 4.5: fleet_dto.py order target conversion (3 instances) [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py` (lines 128-135)
**Tests:** `pytest tests/unit/strategy/facade/ -n 12`

- [x] L128: `hasattr(order.target, "name")` → `isinstance(order.target, Planet)` (Planet has .name)
- [x] L131: `hasattr(order.target, "location")` → `order.target.location` (after isinstance check)
- [x] L135: `hasattr(order.target, "id")` → `isinstance(order.target, Fleet)` for MOVE_TO_FLEET/JOIN_FLEET
- [x] Add imports for Planet, Fleet
- [x] Run tests

**Notes:** All facade tests pass.

---

## Additional Test Fixes

Updated test mocks to comply with protocol requirements:
- Added `get_zones_at_global_hex()` to MockGalaxy classes in multiple test files
- Added `resources = {}` attribute to mock planets for IPlanet protocol compliance
- Used `MagicMock(spec=Planet)` with required attributes for isinstance checks

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` — 12701 passed, 1 skipped
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
