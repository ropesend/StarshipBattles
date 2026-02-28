# Phase 2: Superweapon Validation & Execution

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close superweapon validation gaps and eliminate ships[0] fallback pattern
**Priority:** High (allows invalid orders + wrong ship destruction)

---

## Tasks

### Task 2.1: VC-001 - Pass component_registry to Superweapon Validators [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** All 5 direct superweapon handlers call their validator WITHOUT passing
`component_registry`. The validator's ability check (line 58 of `superweapon_validator.py`)
is guarded by `if component_registry is not None:`, so it's entirely skipped. Fleets without
the required superweapon ability can issue superweapon orders.

- [ ] In `ImplodePlanetCommandHandler.execute()` (line 46): Add `component_registry=session.turn_engine._registries.components` to validator call
- [ ] In `StellerateStarCommandHandler.execute()` (line 70): Same fix
- [ ] In `OpenWarpPointCommandHandler.execute()` (line 94): Same fix
- [ ] In `CloseWarpPointCommandHandler.execute()` (line 122): Same fix
- [ ] In `CreateDysonSphereCommandHandler.execute()` (line 146): Same fix
- [ ] Write test: Fleet without DestroyPlanet ability tries to issue implode order → ValidationResult.error
- [ ] Verify: existing superweapon tests still pass

**Notes:** `SelfDestructCommandHandler` is excluded because `validate_self_destruct()` validates ship IDs, not abilities, and does not accept a `component_registry` parameter. The correct registry accessor is `session.turn_engine._registries.components` (matching `ColonizeMissionCommandHandler` pattern at command_handlers.py line 388).

### Task 2.2: VC-002/CP-005 - Add Validation to Superweapon Mission Handlers [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** All 5 superweapon mission handlers (lines 223-344) skip validation entirely.
They only resolve fleet/planet and call `_setup_mission_move()`. Unlike direct handlers,
they don't call any `SuperweaponValidator.validate_*()` method. A fleet without the ability
can queue a multi-turn mission to destroy a planet.

- [ ] In `ImplodePlanetMissionCommandHandler.execute()` (line 226): Add validator call with `component_registry=session.turn_engine._registries.components` before `_setup_mission_move()`
- [ ] In `StellerateStarMissionCommandHandler.execute()` (line 254): Same pattern
- [ ] In `OpenWarpPointMissionCommandHandler.execute()` (line 277): Same pattern
- [ ] In `CloseWarpPointMissionCommandHandler.execute()` (line 304): Same pattern
- [ ] In `CreateDysonSphereMissionCommandHandler.execute()` (line 327): Same pattern
- [ ] Write test: Fleet without ability tries to queue superweapon mission → error returned
- [ ] Verify: existing mission tests still pass

**Notes:** Registry accessor is `session.turn_engine._registries.components` (same as Task 2.1).

### Task 2.3: VC-007 - Eliminate ships[0] Fallback in SuperweaponOrderProcessor [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** When `component_registry` is None or no ship has the required ability, the processor
falls back to `fleet.ships[0]` at 4 locations (lines 97, 265, 357, 435). Combined with the
validation gaps (VC-001/VC-002), this means the wrong ship can be destroyed.

- [ ] At line 97 (`process_implode_planet`): Replace `fleet.ships[0]` fallback with error handling — log warning and cancel order if no ship has the ability
- [ ] At line 265 (`process_open_warp_point`): Same fix
- [ ] At line 357 (`process_close_warp_point`): Same fix
- [ ] At line 435 (`process_create_dyson_sphere`): Same fix
- [ ] For each: When no valid ship found, call `fleet.pop_order()` and return a result indicating failure
- [ ] Write test: Fleet with validated ability processes correctly (no regression)
- [ ] Write test: If registry not available, order cancels gracefully instead of using ships[0]

**Notes:** After Task 2.1/2.2, these fallbacks should rarely trigger. But belt-and-suspenders — don't silently destroy the wrong ship.

### Task 2.4: Fix Enemy Colony Cleanup in Superweapon Processors [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "superweapon"`

**Problem:** `process_implode_planet()` (line 99-104) and `process_create_dyson_sphere()` (lines 446-450)
only remove the destroyed planet from the attacking empire's `colonies` list, not the victim empire's.
`process_stellerate_star()` (line 176) correctly iterates all empires because it receives an `empires`
parameter. After imploding an enemy planet, the enemy empire retains a stale colony reference — any code
iterating enemy colonies (growth, production, maintenance, UI) could crash or process a ghost planet.

- [ ] Add `empires` parameter to `process_implode_planet()` signature
- [ ] In `process_implode_planet()`: Iterate all empires to remove destroyed planet from colonies (matching `process_stellerate_star()` pattern at line 176)
- [ ] Add `empires` parameter to `process_create_dyson_sphere()` signature
- [ ] In `process_create_dyson_sphere()`: Same iteration pattern for colony cleanup
- [ ] Update callers in `fleet_order_processor.py` (lines 650, 660) to pass `empires`
- [ ] Write test: Implode enemy planet → verify enemy empire's colonies list no longer contains the destroyed planet
- [ ] Verify: no regressions in existing superweapon tests

**Notes:** Found during project review (SG-002). This is a data corruption bug — galaxy removes the planet but the victim empire keeps a stale reference.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
