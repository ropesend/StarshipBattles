# Phase 4: Replace hasattr Type Discrimination [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~25 `hasattr` type-checking patterns with `isinstance` checks using concrete types or existing protocols.

---

## Tasks

### Task 4.1: Galaxy registry and spatial index (8 instances) [Simple]
**Files:** `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/ -n 12`

- [ ] `galaxy_entity_registry.py` L56: Remove `hasattr(planet, 'diameter_hexes')` guard — Planet dataclass always has this (default 0.0), just check `planet.diameter_hexes > 0`
- [ ] `galaxy_entity_registry.py` L82: Same as above
- [ ] `galaxy_entity_registry.py` L111: Same as above
- [ ] `galaxy_entity_registry.py` L161: `hasattr(obj, 'occupied_hexes')` → `is_zone_occupant(obj)` from `game.core.protocols`
- [ ] `galaxy_entity_registry.py` L180: Same as above
- [ ] `galaxy_spatial_index.py` L49: `hasattr(obj, 'location')` → keep or use specific type check (context-dependent)
- [ ] `galaxy_spatial_index.py` L164: `hasattr(star, 'location')` → direct access `star.location` (Star always has this)
- [ ] `galaxy_spatial_index.py` L167: `hasattr(star, 'occupied_hexes')` → `is_zone_occupant(star)` or direct access
- [ ] Run tests

**Notes:** Add `from game.core.protocols import is_zone_occupant` where needed.

### Task 4.2: Validators and fleet_order_processor (8 instances) [Simple]
**Files:** `game/strategy/validation/colonize_validator.py`, `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/validation/ tests/unit/strategy/ -k "colonize or fleet_order" -n 12`

- [ ] `colonize_validator.py` L88: Remove `hasattr(galaxy, 'get_zones_at_global_hex')` — Galaxy always has this
- [ ] `colonize_validator.py` L92: `hasattr(zone_obj, 'planet_type')` → `isinstance(zone_obj, Planet)` (add import)
- [ ] `colonize_validator.py` L117: `hasattr(candidate, 'planet_type')` → `isinstance(candidate, Planet)`
- [ ] `colonize_validator.py` L248: `hasattr(target, 'planet_type')` → `isinstance(target, Planet)`
- [ ] `fleet_order_processor.py` L149: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [ ] `fleet_order_processor.py` L222: `hasattr(candidate, 'planet_type')` → `isinstance(candidate, Planet)` (add import)
- [ ] `fleet_order_processor.py` L694: `hasattr(target_fleet, 'location')` → `target_fleet is not None`
- [ ] Run tests

**Notes:**

### Task 4.3: superweapon_order_processor.py (7 instances) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k superweapon`

- [ ] L97: Remove `hasattr(target_planet, 'owner_id')` — Planet always has `owner_id` (None for unowned)
- [ ] L99: Remove `hasattr(empire, 'colonies')` — Empire always has `colonies` list
- [ ] L172: Remove `hasattr(planet, 'owner_id')`
- [ ] L174: Remove `hasattr(emp, 'colonies')`
- [ ] L182: Remove `hasattr(galaxy, 'unregister_fleet')` — Galaxy always has this method
- [ ] L445: Remove `hasattr(planet, 'owner_id')`
- [ ] L446: Remove `hasattr(empire, 'colonies')`
- [ ] Run tests

**Notes:** When removing hasattr guards, keep the condition logic but remove the hasattr wrapper. E.g., `if hasattr(planet, 'owner_id') and planet.owner_id is not None:` → `if planet.owner_id is not None:`

### Task 4.4: FleetOrder.to_dict serialization (3 instances) [Medium]
**File:** `game/strategy/data/fleet.py` (lines 74-108)
**Tests:** `pytest tests/unit/strategy/data/ tests/unit/strategy/ -k fleet -n 12`

- [ ] L81: `hasattr(self.target, 'id')` → `isinstance(self.target, Planet)` (add `from game.strategy.data.planet import Planet` in TYPE_CHECKING block)
- [ ] L93: `hasattr(self.target, 'to_dict')` → handle explicitly: if target is a Planet, call to_dict(); if Fleet, store fleet_ref
- [ ] L95: `hasattr(self.target, 'id')` → `isinstance(self.target, Fleet)` (self-reference handled via forward ref)
- [ ] Verify save/load round-trip: the serialized format must NOT change (only the branching logic changes)
- [ ] Run tests

**Notes:** This is the highest-risk change in the project. The serialized output format (target_data dict structure) must remain identical. Only the if/elif branching logic changes from hasattr checks to isinstance checks.

### Task 4.5: fleet_dto.py order target conversion (3 instances) [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py` (lines 128-135)
**Tests:** `pytest tests/unit/strategy/facade/ -n 12`

- [ ] L128: `hasattr(order.target, "name")` → `isinstance(order.target, Planet)` (Planet has .name)
- [ ] L131: `hasattr(order.target, "location")` → `order.target.location` (after isinstance check)
- [ ] L135: `hasattr(order.target, "id")` → `isinstance(order.target, Fleet)` for MOVE_TO_FLEET/JOIN_FLEET
- [ ] Add TYPE_CHECKING imports for Planet, Fleet
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — baseline maintained (12699+ passed)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
