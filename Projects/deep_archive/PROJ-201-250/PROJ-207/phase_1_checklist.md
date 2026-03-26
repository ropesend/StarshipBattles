# Phase 1: Save/Load Data Integrity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix save/load serialization bugs that cause data loss or crashes when loading saved games with fleet orders
**Priority:** Immediate (Critical bugs)

---

## Tasks

### Task 1.1: ODM-001 - Fix _fleet_ref/_planet_ref Resolution After Deserialization [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet" && pytest tests/integration/ -k "save"`

**Problem:** When `Fleet.from_dict()` deserializes orders targeting other fleets or planets, it stores
temporary marker dicts (`{'_fleet_ref': id}`, `{'_planet_ref': id}`) at lines 456/462. No code
anywhere in the codebase resolves these markers back to actual Fleet/Planet objects. This means
after save/load, any MOVE_TO_FLEET, JOIN_FLEET, or IMPLODE_PLANET order will have a dict target
instead of a Fleet/Planet object, causing AttributeError when processors access `.location` or `.id`.

- [x] Write test: Save a fleet with a MOVE_TO_FLEET order targeting another fleet, load it back, verify target is a Fleet object (not a dict)
- [x] Write test: Save a fleet with a COLONIZE order targeting a planet (via _planet_ref), load it back, verify target is a Planet object
- [x] Add a `resolve_order_references(galaxy, empires)` method to Fleet class that:
  - Iterates `self.orders`
  - For each order with `{'_fleet_ref': id}` target, looks up the fleet by ID across empires
  - For each order with `{'_planet_ref': id}` target, looks up the planet via `galaxy.get_planet_by_id()`
  - Replaces the dict marker with the resolved object
  - Logs a warning if resolution fails (fleet/planet no longer exists) and pops that order
- [x] Call `resolve_order_references()` in the game session load path, after all empires and galaxy are fully restored
- [x] Verify: `pytest tests/unit/strategy/ -k "fleet"` — all pass, no regressions

**Notes:**
- Added `resolve_order_references(galaxy, empires)` method to Fleet class
- Added resolution call in `GameSession.from_dict()` after empires are loaded
- Created 12 tests in `tests/unit/strategy/data/test_fleet_order_resolution.py`

### Task 1.2: ODM-003 - Fix Planet Target Serialization Round-Trip [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet_order"`

**Problem:** In `to_dict()` (line 97-99), COLONIZE orders serialize their Planet target via
`self.target.to_dict()`, producing a full Planet dict. In `from_dict()` (lines 450-471), this dict
has no `q`/`r` keys and no `type` key, so it doesn't match any recognition pattern and falls through.
The target becomes `None` after save/load.

- [x] Write test: Create FleetOrder(COLONIZE, target=planet), call to_dict(), call from_dict(), verify target resolves correctly
- [x] In `to_dict()` (line 97-99): Change Planet serialization to use `_planet_ref` format instead of full dict:
  ```python
  # Change from:
  target_data = self.target.to_dict()
  # To:
  target_data = {'type': 'planet_ref', 'id': self.target.id}
  ```
- [x] Ensure `from_dict()` already handles `_planet_ref` (line 460-462 should cover this)
- [x] This will be resolved by Task 1.1's resolution pass after loading
- [x] Verify: round-trip test passes, existing fleet serialization tests pass

**Notes:**
- Changed `to_dict()` to use `{'type': 'planet_ref', 'id': ...}` format for all Planet targets
- This makes COLONIZE orders consistent with IMPLODE_PLANET orders

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — full suite passes (12,827 passed, 1 skipped + 4 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
