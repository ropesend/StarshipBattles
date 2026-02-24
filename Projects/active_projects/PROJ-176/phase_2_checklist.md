# Phase 2: Foundation Abstractions (BaseCommandHandler)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-176 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create BaseCommandHandler mixin with fleet/planet resolution helpers, migrate all 19 handler classes
**Priority:** High
**Estimated Time:** ~1 day
**Net Lines Saved:** ~53
**Dependencies:** Phase 1 complete (uses `ValidationResult.error()` in resolution helpers)

---

## Tasks

### Task 2.1: Create BaseCommandHandler Mixin [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

- [ ] Read `game/strategy/engine/command_handlers.py` to understand current `ICommandHandler` protocol and `CommandHandlerRegistry`
- [ ] Add `BaseCommandHandler` class above the first handler class with:
  - `_resolve_fleet(session, fleet_id, empire_id) -> tuple[Fleet | None, ValidationResult | None]` — static method
  - `_resolve_planet(session, planet_id) -> tuple[Planet | None, ValidationResult | None]` — static method
  - Both use `ValidationResult.error()` factory method (from Phase 1)
- [ ] Write unit tests in `tests/unit/strategy/engine/test_base_command_handler.py`:
  - `test_resolve_fleet_not_found()` — returns `(None, error_result)`
  - `test_resolve_fleet_wrong_owner()` — returns `(None, error_result)`
  - `test_resolve_fleet_success()` — returns `(fleet, None)`
  - `test_resolve_planet_not_found()` — returns `(None, error_result)`
  - `test_resolve_planet_success()` — returns `(planet, None)`
- [ ] Verify: `pytest tests/unit/strategy/engine/test_base_command_handler.py -v` — all pass

**Notes:** [Filled during implementation]

### Task 2.2: Migrate Core Command Handlers to BaseCommandHandler [Medium]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

Migrate these 8 handler classes (one at a time, test after each):
- [ ] `ColonizeCommandHandler` — add `BaseCommandHandler` to bases, replace inline fleet/planet resolution with `_resolve_fleet()` / `_resolve_planet()`
- [ ] `MoveCommandHandler` — replace inline fleet resolution
- [ ] `BuildShipCommandHandler` — replace inline planet resolution
- [ ] `InterceptCommandHandler` — replace inline fleet resolution
- [ ] `JoinCommandHandler` — replace inline fleet resolution (2 fleets)
- [ ] `ColonizeMissionCommandHandler` — replace inline fleet/planet resolution
- [ ] `ClearOrdersCommandHandler` — replace inline fleet resolution
- [ ] `TransferCommandHandler` — replace inline fleet resolution
- [ ] Verify after each: `pytest tests/unit/strategy/engine/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 2.3: Migrate Superweapon Command Handlers to BaseCommandHandler [Medium]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

Migrate these 11 handler classes (one at a time, test after each):
- [ ] `ImplodePlanetCommandHandler` — add `BaseCommandHandler`, replace inline resolution
- [ ] `StellerateStarCommandHandler` — replace inline resolution
- [ ] `OpenWarpPointCommandHandler` — replace inline resolution
- [ ] `CloseWarpPointCommandHandler` — replace inline resolution
- [ ] `CreateDysonSphereCommandHandler` — replace inline resolution
- [ ] `SelfDestructCommandHandler` — replace inline resolution
- [ ] `ImplodePlanetMissionCommandHandler` — replace inline resolution
- [ ] `StellerateStarMissionCommandHandler` — replace inline resolution
- [ ] `OpenWarpPointMissionCommandHandler` — replace inline resolution
- [ ] `CloseWarpPointMissionCommandHandler` — replace inline resolution
- [ ] `CreateDysonSphereMissionCommandHandler` — replace inline resolution
- [ ] Verify after each: `pytest tests/unit/strategy/engine/ -n 4` — all pass

**Notes:** [Filled during implementation]

### Task 2.4: Phase 2 Full Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12` — all pass
- [ ] Verify no handler class still has inline `_get_fleet_by_id` + error return pattern (grep check)
- [ ] Verify all 19 handler classes inherit from `BaseCommandHandler` (grep check)
- [ ] Record test count — should match or exceed baseline

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
