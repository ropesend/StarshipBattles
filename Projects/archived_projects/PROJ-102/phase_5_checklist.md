# Phase 5: Command Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create command handlers that wire commands to validators and create fleet orders.

---

## Tasks

### Task 5.1: Create Direct Command Handlers [Medium]
**New File:** `game/strategy/engine/superweapon_command_handlers.py`
**Pattern:** Follow `game/strategy/engine/command_handlers.py` (ColonizeCommandHandler at line 72)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

Each handler follows this pattern:
1. Resolve fleet via `session._get_fleet_by_id(cmd.fleet_id)`
2. Validate via `SuperweaponValidator.validate_*()`
3. Create `FleetOrder(OrderType.X, target=...)` and add to fleet
4. Log and return `ValidationResult`

- [x] `ImplodePlanetCommandHandler.execute(session, cmd)`:
  - Resolve fleet and planet (via `session._get_planet_by_id(cmd.planet_id)`)
  - Validate with `SuperweaponValidator.validate_implode_planet()`
  - Add `FleetOrder(OrderType.IMPLODE_PLANET, target=planet)`

- [x] `StellerateStarCommandHandler.execute(session, cmd)`:
  - Resolve fleet
  - Validate with `SuperweaponValidator.validate_stellerate_star()`
  - Add `FleetOrder(OrderType.STELLERATE_STAR, target=None)` (system inferred from location)

- [x] `OpenWarpPointCommandHandler.execute(session, cmd)`:
  - Resolve fleet
  - Validate with `SuperweaponValidator.validate_open_warp_point()`
  - Add `FleetOrder(OrderType.OPEN_WARP_POINT, target={'target_hex': cmd.target_hex, 'target_system_name': cmd.target_system_name})`

- [x] `CloseWarpPointCommandHandler.execute(session, cmd)`:
  - Resolve fleet
  - Validate with `SuperweaponValidator.validate_close_warp_point()`
  - Add `FleetOrder(OrderType.CLOSE_WARP_POINT, target=cmd.warp_point_destination_id)`

- [x] `CreateDysonSphereCommandHandler.execute(session, cmd)`:
  - Resolve fleet
  - Validate with `SuperweaponValidator.validate_create_dyson_sphere()`
  - Add `FleetOrder(OrderType.CREATE_DYSON_SPHERE, target=None)`

- [x] `SelfDestructCommandHandler.execute(session, cmd)`:
  - Resolve fleet
  - Validate with `SuperweaponValidator.validate_self_destruct()`
  - Add `FleetOrder(OrderType.SELF_DESTRUCT, target=cmd.ship_ids)`

**Notes:** Created superweapon_command_handlers.py with 6 direct handlers.

### Task 5.2: Create Mission Command Handlers [Medium]
**File:** `game/strategy/engine/superweapon_command_handlers.py` (same file)
**Pattern:** Follow `ColonizeMissionCommandHandler` at line 227 of `command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

Each mission handler:
1. Resolve fleet
2. Calculate path via `find_hybrid_path(session.galaxy, start_hex, cmd.target_hex)`
3. Add MOVE order first, then action order
4. Set fleet.path if it's the active order

- [x] `ImplodePlanetMissionCommandHandler` - MOVE + IMPLODE_PLANET
- [x] `StellerateStarMissionCommandHandler` - MOVE + STELLERATE_STAR
- [x] `OpenWarpPointMissionCommandHandler` - MOVE + OPEN_WARP_POINT (with target dict)
- [x] `CloseWarpPointMissionCommandHandler` - MOVE + CLOSE_WARP_POINT
- [x] `CreateDysonSphereMissionCommandHandler` - MOVE + CREATE_DYSON_SPHERE

**Notes:** All 5 mission handlers created following ColonizeMissionCommandHandler pattern.

### Task 5.3: Register All Handlers in Factory [Simple]
**File:** `game/strategy/engine/command_handlers.py` (in `create_default_registry()` at line 360)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [x] Add import of all 11 handler classes from `superweapon_command_handlers`
- [x] Register all 11 in the factory:
  ```python
  registry.register('IssueImplodePlanetCommand', ImplodePlanetCommandHandler())
  registry.register('QueueImplodePlanetMissionCommand', ImplodePlanetMissionCommandHandler())
  registry.register('IssueStellerateStarCommand', StellerateStarCommandHandler())
  registry.register('QueueStellerateStarMissionCommand', StellerateStarMissionCommandHandler())
  registry.register('IssueOpenWarpPointCommand', OpenWarpPointCommandHandler())
  registry.register('QueueOpenWarpPointMissionCommand', OpenWarpPointMissionCommandHandler())
  registry.register('IssueCloseWarpPointCommand', CloseWarpPointCommandHandler())
  registry.register('QueueCloseWarpPointMissionCommand', CloseWarpPointMissionCommandHandler())
  registry.register('IssueCreateDysonSphereCommand', CreateDysonSphereCommandHandler())
  registry.register('QueueCreateDysonSphereMissionCommand', CreateDysonSphereMissionCommandHandler())
  registry.register('IssueSelfDestructCommand', SelfDestructCommandHandler())
  ```

**Notes:** All 11 handlers registered in create_default_registry().

### Task 5.4: Write Phase 5 Unit Tests [Medium]
**New File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py -v`

- [x] Test each direct handler with mock session and valid command -> returns valid result
- [x] Test each direct handler adds correct FleetOrder type to fleet
- [x] Test each handler returns invalid when fleet not found
- [x] Test each handler returns invalid when validation fails (missing ability)
- [x] Test each mission handler creates MOVE + action order pair
- [x] Test mission handler sets fleet.path when it's the first order
- [x] Test all 11 handlers are registered in `create_default_registry()`
- [x] Verify: all tests pass

**Notes:** 25 tests written and passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (7921 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
