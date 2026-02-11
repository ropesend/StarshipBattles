# Phase 2: Order Types & Command Definitions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extend the order/command system with 6 new OrderTypes and 11 command dataclasses.

---

## Tasks

### Task 2.1: Add OrderType Enum Values [Simple]
**File:** `game/strategy/data/fleet.py` (line ~15, OrderType enum)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [ ] Add `IMPLODE_PLANET = auto()` after TRANSFER
- [ ] Add `STELLERATE_STAR = auto()`
- [ ] Add `OPEN_WARP_POINT = auto()`
- [ ] Add `CLOSE_WARP_POINT = auto()`
- [ ] Add `CREATE_DYSON_SPHERE = auto()`
- [ ] Add `SELF_DESTRUCT = auto()`

**Notes:**

### Task 2.2: Update FleetOrder Serialization [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

In `FleetOrder.to_dict()` (line ~32):
- [ ] Add handling for new order types. For IMPLODE_PLANET, serialize planet target as `{'type': 'planet_ref', 'id': target.id}` if target has `.id`
- [ ] For SELF_DESTRUCT, serialize ship ID list as `{'type': 'ship_id_list', 'value': self.target}`
- [ ] For OPEN_WARP_POINT, serialize dict target as `{'type': 'warp_params', 'value': self.target}`
- [ ] For STELLERATE_STAR, CREATE_DYSON_SPHERE: target may be None (system inferred from location) or system name string

In `Fleet.from_dict()` (line ~361):
- [ ] Add deserialization for `'planet_ref'` type: store `{'_planet_ref': id}` for later resolution
- [ ] Add deserialization for `'ship_id_list'` type: store list directly
- [ ] Add deserialization for `'warp_params'` type: store dict directly

**Notes:**

### Task 2.3: Create Direct Command Dataclasses [Medium]
**File:** `game/strategy/engine/commands.py`
**Pattern:** Follow `IssueColonizeCommand` (line 19)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [ ] `IssueImplodePlanetCommand(fleet_id: int, planet_id: int)` - set `type = CommandType.ISSUE_ORDER`
- [ ] `IssueStellerateStarCommand(fleet_id: int)` - no target needed (inferred from location)
- [ ] `IssueOpenWarpPointCommand(fleet_id: int, target_hex: Any, target_system_name: str)`
- [ ] `IssueCloseWarpPointCommand(fleet_id: int, warp_point_destination_id: str)`
- [ ] `IssueCreateDysonSphereCommand(fleet_id: int)` - no target needed
- [ ] `IssueSelfDestructCommand(fleet_id: int, ship_ids: list)`

**Notes:**

### Task 2.4: Create Mission Command Dataclasses [Medium]
**File:** `game/strategy/engine/commands.py`
**Pattern:** Follow `QueueColonizeMissionCommand` (line 83)
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [ ] `QueueImplodePlanetMissionCommand(fleet_id: int, target_hex: Any, planet_id: int)`
- [ ] `QueueStellerateStarMissionCommand(fleet_id: int, target_hex: Any)`
- [ ] `QueueOpenWarpPointMissionCommand(fleet_id: int, target_hex: Any, target_system_name: str)`
- [ ] `QueueCloseWarpPointMissionCommand(fleet_id: int, target_hex: Any, warp_point_destination_id: str)`
- [ ] `QueueCreateDysonSphereMissionCommand(fleet_id: int, target_hex: Any)`
- [ ] (No mission command for SelfDestruct - it's instant, no movement needed)

**Notes:**

### Task 2.5: Write Phase 2 Unit Tests [Simple]
**New File:** `tests/unit/strategy/data/test_superweapon_orders.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py -v`

- [ ] Test all 6 OrderType enum values exist (e.g., `OrderType.IMPLODE_PLANET`)
- [ ] Test FleetOrder.to_dict() / from_dict() round-trip for IMPLODE_PLANET with planet target
- [ ] Test FleetOrder round-trip for SELF_DESTRUCT with ship ID list
- [ ] Test FleetOrder round-trip for OPEN_WARP_POINT with dict target
- [ ] Test each command dataclass `.name` property returns class name
- [ ] Test each command `.type == CommandType.ISSUE_ORDER`
- [ ] Verify: `pytest tests/unit/strategy/data/test_superweapon_orders.py` - all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
