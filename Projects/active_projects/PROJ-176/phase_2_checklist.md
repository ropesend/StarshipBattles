# Phase 2: Foundation Abstractions (BaseCommandHandler)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-176 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Read `game/strategy/engine/command_handlers.py` to understand current `ICommandHandler` protocol and `CommandHandlerRegistry`
- [x] Add `BaseCommandHandler` class above the first handler class with:
  - `_resolve_fleet(session, fleet_id, empire_id) -> tuple[Fleet | None, ValidationResult | None]` — static method
  - `_resolve_planet(session, planet_id) -> tuple[Planet | None, ValidationResult | None]` — static method
  - Both use `ValidationResult.error()` factory method (from Phase 1)
- [x] Write unit tests in `tests/unit/strategy/engine/test_base_command_handler.py`:
  - `test_resolve_fleet_not_found()` — returns `(None, error_result)`
  - `test_resolve_fleet_wrong_owner()` — returns `(None, error_result)`
  - `test_resolve_fleet_success()` — returns `(fleet, None)`
  - `test_resolve_planet_not_found()` — returns `(None, error_result)`
  - `test_resolve_planet_success()` — returns `(planet, None)`
- [x] Verify: `pytest tests/unit/strategy/engine/test_base_command_handler.py -v` — all pass

**Notes:** Added BaseCommandHandler with static methods _resolve_fleet and _resolve_planet. 6 unit tests written and passing. Also added test_resolve_fleet_success_no_owner_check for optional ownership validation.

### Task 2.2: Migrate Core Command Handlers to BaseCommandHandler [Medium]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

Migrate these 8 handler classes (one at a time, test after each):
- [x] `ColonizeCommandHandler` — add `BaseCommandHandler` to bases, replace inline fleet/planet resolution with `_resolve_fleet()` / `_resolve_planet()`
- [x] `MoveCommandHandler` — replace inline fleet resolution
- [x] `BuildShipCommandHandler` — replace inline planet resolution
- [x] `InterceptCommandHandler` — replace inline fleet resolution
- [x] `JoinCommandHandler` — replace inline fleet resolution (2 fleets)
- [x] `ColonizeMissionCommandHandler` — replace inline fleet/planet resolution
- [x] `ClearOrdersCommandHandler` — replace inline fleet resolution
- [x] `TransferCommandHandler` — replace inline fleet resolution
- [x] Verify after each: `pytest tests/unit/strategy/engine/ -n 4` — all pass

**Notes:** All 8 core handlers migrated. Updated 2 tests (TestColonizeCommandHandler) to mock _get_fleet_by_id instead of empires iteration. Updated 1 integration test (test_colonize_command_adds_load_order) similarly.

### Task 2.3: Migrate Superweapon Command Handlers to BaseCommandHandler [Medium]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -n 4`

Migrate these 11 handler classes (one at a time, test after each):
- [x] `ImplodePlanetCommandHandler` — add `BaseCommandHandler`, replace inline resolution
- [x] `StellerateStarCommandHandler` — replace inline resolution
- [x] `OpenWarpPointCommandHandler` — replace inline resolution
- [x] `CloseWarpPointCommandHandler` — replace inline resolution
- [x] `CreateDysonSphereCommandHandler` — replace inline resolution
- [x] `SelfDestructCommandHandler` — replace inline resolution
- [x] `ImplodePlanetMissionCommandHandler` — replace inline resolution
- [x] `StellerateStarMissionCommandHandler` — replace inline resolution
- [x] `OpenWarpPointMissionCommandHandler` — replace inline resolution
- [x] `CloseWarpPointMissionCommandHandler` — replace inline resolution
- [x] `CreateDysonSphereMissionCommandHandler` — replace inline resolution
- [x] Verify after each: `pytest tests/unit/strategy/engine/ -n 4` — all pass

**Notes:** All 11 superweapon handlers migrated. Added import for BaseCommandHandler from command_handlers module.

### Task 2.4: Phase 2 Full Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12` — all pass
- [x] Verify no handler class still has inline `_get_fleet_by_id` + error return pattern (grep check)
- [x] Verify all 19 handler classes inherit from `BaseCommandHandler` (grep check)
- [x] Record test count — should match or exceed baseline

**Notes:** 12159 passed, 1 skipped (baseline was 12153, +6 new tests). All 19 handler classes inherit from BaseCommandHandler. No inline fleet/planet resolution patterns remain outside BaseCommandHandler itself.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
