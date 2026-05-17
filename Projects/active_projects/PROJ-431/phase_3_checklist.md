# Phase 3: `FighterWing` + `SatelliteConstellation` (DeployedGroup families 2 & 3)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-431 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/deployed_group.py`
- `game/strategy/data/empire.py`
- `game/strategy/data/fleet.py`
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/engine/handlers/base.py`
- `game/strategy/engine/handlers/movement.py`
- `game/strategy/engine/handlers/build.py`
- `game/strategy/engine/handlers/lay_mines.py`
- `game/strategy/engine/handlers/launch_fighters.py`
- `game/strategy/engine/handlers/launch_satellites.py`
- `game/strategy/engine/handlers/recover_fighters.py`
- `game/strategy/engine/handlers/recover_satellites.py`
- `game/strategy/engine/order_handlers/launch_fighters.py`
- `game/strategy/engine/order_handlers/launch_satellites.py`
- `game/strategy/engine/order_handlers/recover_fighters.py`
- `game/strategy/engine/order_handlers/recover_satellites.py`
- `game/strategy/combat/spec_compiler.py`
- `game/strategy/adapters/simulation_adapter.py`
- `game/simulation/systems/fighter_reboard.py`
- `game/simulation/systems/tactical_mine_resolver.py`
- `game/ai/carrier_controller.py`
- `game/ai/fighter_controller.py` (if present)
- `game/ai/satellite_controller.py` (if present)
- `tests/unit/strategy/data/test_fighter_wing.py` (new)
- `tests/unit/strategy/data/test_satellite_constellation.py` (new)

**Objective:** Symmetric to Phase 2 for the remaining two families. After this phase: `_reject_if_non_fleet_group` is deleted, all ten guard call sites are gone, `Fleet.group_kind` is deleted entirely, and `FleetCapabilityCalculator`'s `group_kind` early-return is dropped.

---

## Tasks

### Task 3.1: RED — author `test_fighter_wing.py` + `test_satellite_constellation.py` [Medium]
**Files:** `tests/unit/strategy/data/test_fighter_wing.py` (new), `tests/unit/strategy/data/test_satellite_constellation.py` (new)
**Tests:** both — MUST fail (classes don't exist yet)

- [ ] `test_fighter_wing.py`: identity, owner, location, `ships: list[ShipInstance]`, reboard state, serialisation round-trip
- [ ] `test_satellite_constellation.py`: identity, owner, location, `ships: list[ShipInstance]`, serialisation round-trip
- [ ] Note: both families carry **real ships** built from `CarriedVehicle` at launch, unlike `MineGroup` which only carries the `CarriedVehicle` list

**Notes:** [Per TD plan §"Phase 3" step 1.]

### Task 3.2: GREEN — add `FighterWing` + `SatelliteConstellation` to `deployed_group.py` [Medium]
**File:** `game/strategy/data/deployed_group.py`
**Tests:** the two new test files (green)

- [ ] Add `FighterWing` class — `ships: list[ShipInstance]`, optional reboard state
- [ ] Add `SatelliteConstellation` class — `ships: list[ShipInstance]`
- [ ] Both inherit from `DeployedGroup`
- [ ] `to_dict()` / `from_dict()` for both
- [ ] Update `Empire.deployed_groups` serialisation to dispatch on type tag

**Notes:** [Per TD plan §"Phase 3" step 2.]

### Task 3.3: RED + GREEN — rewrite launch handlers to construct deployed-group types [Complex]
**Files:** `game/strategy/engine/order_handlers/launch_fighters.py`, `launch_satellites.py`
**Tests:** launch handler unit tests

- [ ] RED: update launch order-handler tests to expect `FighterWing` / `SatelliteConstellation`, not `Fleet`
- [ ] GREEN: `LaunchFightersOrderHandler` creates a `FighterWing` (added to `empire.deployed_groups`), NOT a `Fleet`
- [ ] GREEN: `LaunchSatellitesOrderHandler` creates a `SatelliteConstellation`
- [ ] `_create_fighter_group` / `_create_satellite_group` return the new types

**Notes:** [Per TD plan §"Phase 3" steps 3–4.]

### Task 3.4: GREEN — rewrite recover handlers to find by type [Medium]
**Files:** `game/strategy/engine/order_handlers/recover_fighters.py`, `recover_satellites.py`
**Tests:** recover handler unit tests

- [ ] Find target wing via `isinstance(g, FighterWing)`, not `getattr(f, "group_kind") == "fighter_group"`
- [ ] Same for satellites
- [ ] Push recovered vehicles back into carrier `bay_inventory.bay`

**Notes:** [Per TD plan §"Phase 3" step 5.]

### Task 3.5: GREEN — update combat spec assembler for FighterWing participation [Complex]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** spec-compiler integration tests + fighter reboard end-to-end

- [ ] Assembler walks `empire.deployed_groups_of(FighterWing)` and adds those ships as combat participants alongside `empire.fleets`
- [ ] Update `simulation_adapter.py` to consume `FighterWing` correctly
- [ ] Verify: fighter combat participation works end-to-end

**Notes:** [Per TD plan §"Phase 3" step 6. This is where TD-01 and TD-10 touch — PROJ-426 should have left a clean typed-parameter surface here.]

### Task 3.6: GREEN — update `fighter_reboard.py` + `tactical_mine_resolver.py` [Medium]
**Files:** `game/simulation/systems/fighter_reboard.py`, `game/simulation/systems/tactical_mine_resolver.py`
**Tests:** fighter reboard + tactical mine resolver tests

- [ ] `fighter_reboard.py` consumer paths: reboard target is a `FighterWing`, not a `Fleet`
- [ ] `tactical_mine_resolver.py` consumes `MineGroup` directly (cleanup carried over from Phase 2)

**Notes:** [Per TD plan §"Phase 3" step 7.]

### Task 3.7: GREEN — drop `fighter_group` + `satellite_group`; delete `group_kind` entirely [Complex]
**File:** `game/strategy/data/fleet.py`
**Tests:** fleet construction tests; all `group_kind`-touching tests

- [ ] Remove `"fighter_group"` and `"satellite_group"` from legal-values
- [ ] **Delete the `group_kind` field entirely** — every Fleet is a real fleet now
- [ ] Drop `from_dict` default-to-`"fleet"` logic (`:582`) — there's no field to default
- [ ] Update `fleet_dto.py` to drop `group_kind`
- [ ] Grep gate: `rg -n "group_kind" game/ tests/` returns zero semantic hits

**Notes:** [Per TD plan §"Phase 3" step 8.]

### Task 3.8: GREEN — **delete `_reject_if_non_fleet_group` + all 10 call sites** [Complex]
**File:** `game/strategy/engine/handlers/base.py` + 7 caller files
**Tests:** every fleet-action handler suite

- [ ] **Delete `_reject_if_non_fleet_group` (lines 208-230) in `handlers/base.py`**
- [ ] Remove guard call in `handlers/movement.py:106` (Move)
- [ ] Remove guard call in `handlers/movement.py:154` (Intercept)
- [ ] Remove guard call in `handlers/movement.py:197` (Join Fleet)
- [ ] Remove guard call in `handlers/movement.py:248` (Warp)
- [ ] Remove guard call in `handlers/build.py:54` (Build)
- [ ] Remove guard call in `handlers/lay_mines.py:52`
- [ ] Remove guard call in `handlers/launch_fighters.py:59`
- [ ] Remove guard call in `handlers/launch_satellites.py:57`
- [ ] Remove guard call in `handlers/recover_fighters.py:56`
- [ ] Remove guard call in `handlers/recover_satellites.py:55`
- [ ] Verify all ten removed: `rg -n "_reject_if_non_fleet_group" game/ tests/` returns zero hits
- [ ] Run the focused handler suites; confirm no regression

**Notes:** [Per TD plan §"Phase 3" step 9. Single best signal that the migration is complete. The protection is now structural — deployed groups don't have Move/Warp/Build order handlers wired.]

### Task 3.9: GREEN — drop `group_kind` early-return in `FleetCapabilityCalculator` [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** fleet-capability calculator unit tests

- [ ] Remove the `group_kind` early-return at `:96-107`
- [ ] All fleets are now real fleets, so capability methods compute their normal results

**Notes:** [Per TD plan §"Phase 3" step 10.]

### Task 3.10: GREEN — AI controllers read `empire.deployed_groups` [Medium]
**Files:** `game/ai/carrier_controller.py`, `game/ai/fighter_controller.py` (if present), `game/ai/satellite_controller.py` (if present)
**Tests:** AI controller unit tests

- [ ] `carrier_controller` reads `empire.deployed_groups_of(FighterWing)` to find owned wings
- [ ] `fighter_controller` (if it exists as a separate controller) — same
- [ ] `satellite_controller` (if it exists as a separate controller) — same
- [ ] Grep gate: `rg -n "group_kind" game/ai/` returns zero hits

**Notes:** [Per TD plan §"Regression risk hot spots" — AI controllers reading `empire.fleets` for groups are the risk.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_reject_if_non_fleet_group` and the non-fleet `group_kind` values are fully removed (per TD plan §"Per-Phase Success Criteria" Phase 3)
- [ ] Grep gates green:
  - `rg -n "_reject_if_non_fleet_group" game/ tests/` returns zero hits
  - `rg -n "group_kind" game/ tests/` returns zero semantic hits (string-literal hits in old test fixture migration may remain — flag them for Phase 4 cleanup)
  - `rg -n '"fighter_group"|"satellite_group"' game/ tests/` returns zero hits
- [ ] Focused suites green: every fleet-action handler suite, AI controllers, fighter reboard, launch + recover handlers
- [ ] `python Projects/scripts/validate_phase.py PROJ-431 3` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
