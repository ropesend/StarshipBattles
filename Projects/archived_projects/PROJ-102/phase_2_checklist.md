# Phase 2: Order Types & Command Definitions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extend the order/command system with 6 new OrderTypes and 11 command dataclasses.

---

## Tasks

### Task 2.1: Add OrderType Enum Values [Simple]
**File:** `game/strategy/data/fleet.py` (line ~15, OrderType enum)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [x] Add `IMPLODE_PLANET = auto()` after TRANSFER
- [x] Add `STELLERATE_STAR = auto()`
- [x] Add `OPEN_WARP_POINT = auto()`
- [x] Add `CLOSE_WARP_POINT = auto()`
- [x] Add `CREATE_DYSON_SPHERE = auto()`
- [x] Add `SELF_DESTRUCT = auto()`

**Notes:** All 6 OrderType enum values added.

### Task 2.2: Update FleetOrder Serialization [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

In `FleetOrder.to_dict()` (line ~32):
- [x] Add handling for new order types. For IMPLODE_PLANET, serialize planet target as `{'type': 'planet_ref', 'id': target.id}` if target has `.id`
- [x] For SELF_DESTRUCT, serialize ship ID list as `{'type': 'ship_id_list', 'value': self.target}`
- [x] For OPEN_WARP_POINT, serialize dict target as `{'type': 'warp_params', 'value': self.target}`
- [x] For STELLERATE_STAR, CREATE_DYSON_SPHERE: target may be None (system inferred from location) or system name string

In `Fleet.from_dict()` (line ~361):
- [x] Add deserialization for `'planet_ref'` type: store `{'_planet_ref': id}` for later resolution
- [x] Add deserialization for `'ship_id_list'` type: store list directly
- [x] Add deserialization for `'warp_params'` type: store dict directly

**Notes:** All serialization/deserialization handlers added.

### Task 2.3: Create Direct Command Dataclasses [Medium]
**File:** `game/strategy/engine/commands.py`
**Pattern:** Follow `IssueColonizeCommand` (line 19)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [x] `IssueImplodePlanetCommand(fleet_id: int, planet_id: int)` - set `type = CommandType.ISSUE_ORDER`
- [x] `IssueStellerateStarCommand(fleet_id: int)` - no target needed (inferred from location)
- [x] `IssueOpenWarpPointCommand(fleet_id: int, target_hex: Any, target_system_name: str)`
- [x] `IssueCloseWarpPointCommand(fleet_id: int, warp_point_destination_id: str)`
- [x] `IssueCreateDysonSphereCommand(fleet_id: int)` - no target needed
- [x] `IssueSelfDestructCommand(fleet_id: int, ship_ids: list)`

**Notes:** All 6 direct command dataclasses created.

### Task 2.4: Create Mission Command Dataclasses [Medium]
**File:** `game/strategy/engine/commands.py`
**Pattern:** Follow `QueueColonizeMissionCommand` (line 83)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [x] `QueueImplodePlanetMissionCommand(fleet_id: int, target_hex: Any, planet_id: int)`
- [x] `QueueStellerateStarMissionCommand(fleet_id: int, target_hex: Any)`
- [x] `QueueOpenWarpPointMissionCommand(fleet_id: int, target_hex: Any, target_system_name: str)`
- [x] `QueueCloseWarpPointMissionCommand(fleet_id: int, target_hex: Any, warp_point_destination_id: str)`
- [x] `QueueCreateDysonSphereMissionCommand(fleet_id: int, target_hex: Any)`
- [x] (No mission command for SelfDestruct - it's instant, no movement needed)

**Notes:** All 5 mission command dataclasses created.

### Task 2.5: Write Phase 2 Unit Tests [Simple]
**New File:** `tests/unit/strategy/data/test_superweapon_orders.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py -v`

- [x] Test all 6 OrderType enum values exist (e.g., `OrderType.IMPLODE_PLANET`)
- [x] Test FleetOrder.to_dict() / from_dict() round-trip for IMPLODE_PLANET with planet target
- [x] Test FleetOrder round-trip for SELF_DESTRUCT with ship ID list
- [x] Test FleetOrder round-trip for OPEN_WARP_POINT with dict target
- [x] Test each command dataclass `.name` property returns class name
- [x] Test each command `.type == CommandType.ISSUE_ORDER`
- [x] Verify: `pytest tests/unit/strategy/data/test_superweapon_orders.py` - all pass

**Notes:** 26 tests created, all pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes (used full suite instead - 7896 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
