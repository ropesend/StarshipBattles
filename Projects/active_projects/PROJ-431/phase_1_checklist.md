# Phase 1: Typed `BayInventory` on `ShipInstance`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-431 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** **PROJ-426 (TD-01) verified.** This project's Phase 1 cannot start until PROJ-426 completes.
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/bay_inventory.py` (new)
- `game/strategy/data/ship_instance.py`
- `game/strategy/data/ship_cargo_manager.py`
- `game/strategy/data/ship_instance_serializer.py`
- `game/strategy/data/carried_vehicle.py`
- `game/strategy/engine/order_handlers/colonize.py`
- `game/strategy/engine/order_handlers/lay_mines.py`
- `game/strategy/engine/order_handlers/launch_fighters.py`
- `game/strategy/engine/order_handlers/launch_satellites.py`
- `game/strategy/engine/order_handlers/recover_fighters.py`
- `game/strategy/engine/order_handlers/recover_satellites.py`
- `game/strategy/engine/order_handlers/transfer_branches.py`
- `game/strategy/engine/issuer_adapter.py`
- `game/strategy/services/mine_group_service.py` (partial — full rewrite in Phase 2)
- `tests/unit/strategy/data/test_bay_inventory.py` (new)
- `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py`
- `tests/unit/strategy/data/test_vehicle_bay.py`
- `tests/integration/test_fms_a_e2e.py`
- `tests/integration/test_fms_c_carrier_ai_launch.py`
- `tests/integration/test_fms_cd_isolation.py`

**Objective:** Eliminate `ShipInstance.carried_items: List[Dict[str, Any]]` and its mixed-shape discrimination. Replace with `bay_inventory: BayInventory` exposing two typed slots (`bay: list[CarriedVehicle]`, `pods: list[DropPod]`). Delete `CarriedVehicle.from_any()`. This phase is independently shippable.

> **PHASE-COMPLETION SIDE EFFECT — DO NOT FORGET:**
> **Unblocks PROJ-425 cargo/deployable forwarder-demolition batch on completion.** Per [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) §"Phase Gates" rule 2: `TD-10 Phase 1 must land before the deferred TD-06 cargo/deployable cleanup batch resumes.` Notify PROJ-425 owners when this phase is `verified`.

---

## Tasks

### Task 1.1: Read foundation docs + reconfirm verification baseline [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
**Tests:** none — discovery work

- [ ] Read `docs/README.md` (documentation index)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read TD-10 plan §A–§E to reconfirm verification numbers (4 families, `carried_items` two-shape list, `from_any` discriminator)
- [ ] Re-enumerate overload sites per TD-10 §"Execution Preconditions" rule 2:
  ```
  rg -n "group_kind|carried_items|from_any\(|_reject_if_non_fleet_group|synthetic_carrier|mine_group" game/strategy game/ui tests
  ```
- [ ] Confirm PROJ-426 is `verified` before starting any code work

**Notes:** [Filled during implementation]

### Task 1.2: RED — author `test_bay_inventory.py` [Medium]
**File:** `tests/unit/strategy/data/test_bay_inventory.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_bay_inventory.py -q` — MUST fail (module does not exist yet)

- [ ] Test: construct empty `BayInventory()` — `bay` and `pods` are empty lists
- [ ] Test: load a `CarriedVehicle` into `bay`; readback returns it
- [ ] Test: load a `DropPod` into `pods`; readback returns it
- [ ] Test: mass accounting — `bay_inventory.total_mass == sum(bay) + sum(pods)`
- [ ] Test: `to_dict()` → `from_dict()` round-trip preserves both slots
- [ ] Test: **explicit rejection** of cross-slot leakage — passing a `DropPod` to `bay` raises `TypeError`; passing a `CarriedVehicle` to `pods` raises `TypeError`
- [ ] Run test, confirm it fails for the right reason: `bay_inventory` module does not exist

**Notes:** [Per TD plan §"Phase 1" step 1.]

### Task 1.3: GREEN — add `bay_inventory.py` + `bay_inventory` field on `ShipInstance` [Medium]
**Files:** `game/strategy/data/bay_inventory.py` (new), `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/test_bay_inventory.py -q` (green)

- [ ] Create `game/strategy/data/bay_inventory.py` with `DropPod` dataclass + `BayInventory` dataclass
- [ ] Add `to_dict()` / `from_dict()` on `BayInventory`
- [ ] Add `bay_inventory: BayInventory = field(default_factory=BayInventory)` to `ShipInstance`
- [ ] `test_bay_inventory.py` is green
- [ ] Verify: file under 500 LOC ceiling

**Notes:** [Per TD plan §"Phase 1" step 2.]

### Task 1.4: RED + GREEN — migrate `ShipCargoManager` to `bay_inventory.bay` [Complex]
**File:** `game/strategy/data/ship_cargo_manager.py`
**Tests:** `pytest tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py -q`

- [ ] RED: add failing tests in `test_ship_cargo_manager_per_bay.py` (already dirty per `git status`) for the bay-only path operating on `bay_inventory.bay`
- [ ] GREEN: rewrite `_assign_carried_to_bays`, `get_vehicle_bay_capacity`, `can_accept_vehicle`, `load_vehicle`, `unload_vehicle`, `get_carried_vehicles`, `get_carried_vehicles_by_type` to read `bay_inventory.bay` directly
- [ ] **Drop the `CarriedVehicle.from_any()` discriminator** from every accessor — bay is homogeneous typed list
- [ ] Verify: `test_ship_cargo_manager_per_bay.py` green; `test_vehicle_bay.py` green

**Notes:** [Per TD plan §"Phase 1" steps 3–4.]

### Task 1.5: RED + GREEN — migrate `ColonizeOrderHandler._deploy_drop_pod` to `bay_inventory.pods` [Medium]
**File:** `game/strategy/engine/order_handlers/colonize.py`
**Tests:** existing colonize tests touching drop-pod storage

- [ ] RED: add failing tests for `_deploy_drop_pod` operating on `bay_inventory.pods`
- [ ] GREEN: update `_deploy_drop_pod` to walk `bay_inventory.pods`
- [ ] GREEN: update `ColonizeValidator.find_ship_with_drop_pod` to walk `bay_inventory.pods`
- [ ] Verify: colonize tests green

**Notes:** [Per TD plan §"Phase 1" steps 5–6.]

### Task 1.6: GREEN — migrate `IssuerAdapter`, `MineGroupService`, FMS handlers to `bay_inventory.bay` [Complex]
**Files:** `issuer_adapter.py`, `mine_group_service.py`, `order_handlers/{lay_mines,launch_fighters,launch_satellites,recover_fighters,recover_satellites,transfer_branches}.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers tests/integration/test_fms_*`

- [ ] `IssuerAdapter` and its two concrete classes (`FleetShipIssuerAdapter`, `PlanetStagingYardIssuerAdapter`) read/write `bay_inventory.bay`
- [ ] `_matches` helper in `issuer_adapter.py` becomes trivial type-equality (no more `from_any()` runtime check)
- [ ] All five FMS order handlers (lay_mines, launch_fighters, launch_satellites, recover_fighters, recover_satellites) read/write `bay_inventory.bay`
- [ ] `MineGroupService` reads/writes `bay_inventory.bay` for the mine-source path (full rewrite to `MineGroup` is Phase 2)
- [ ] `transfer_branches.py` inventory transfers operate on `bay_inventory.bay` / `bay_inventory.pods`
- [ ] Verify: FMS unit + integration tests green

**Notes:** [Per TD plan §"Phase 1" step 7.]

### Task 1.7: GREEN — round-trip `bay_inventory` in `ShipInstanceSerializer` [Medium]
**File:** `game/strategy/data/ship_instance_serializer.py`
**Tests:** save/load round-trip tests

- [ ] Serialise `bay_inventory` via `BayInventory.to_dict()`
- [ ] Deserialise via `BayInventory.from_dict()`
- [ ] **No migration shim.** Saves predating this change won't load — per CLAUDE.md, that's acceptable.
- [ ] Document in the phase 1 PR description that save format changes.

**Notes:** [Per TD plan §"Phase 1" step 8.]

### Task 1.8: GREEN — remove `carried_items` + `CarriedVehicle.from_any()` + pod-storage filtering [Medium]
**Files:** `game/strategy/data/ship_instance.py`, `game/strategy/data/carried_vehicle.py`
**Tests:** full focused suite + grep gates

- [ ] Remove the `carried_items: List[Dict[str, Any]]` field from `ShipInstance`
- [ ] **Delete `CarriedVehicle.from_any()`** — bay is homogeneous; no discriminator needed
- [ ] `get_pod_storage_used()` becomes `sum(p.mass for p in self.bay_inventory.pods)` — no more filtering of a mixed list
- [ ] Grep gate (must return zero hits):
  ```
  rg -n "carried_items|from_any\(" game/ tests/
  ```
- [ ] Run focused suites:
  ```
  pytest tests/unit/strategy/data tests/unit/strategy/engine/order_handlers tests/integration/test_fms_*
  ```

**Notes:** [Per TD plan §"Phase 1" step 9.]

### Task 1.9: Doc updates [Simple]
**Files:** `docs/systems/fighters.md`, `docs/systems/satellites.md`, `docs/systems/minefields.md`, `docs/02_PATTERNS.md` (if applicable)
**Tests:** none

- [ ] Update `docs/systems/fighters.md` substrate description
- [ ] Update `docs/systems/satellites.md` substrate description
- [ ] Update `docs/systems/minefields.md` to note the mine-source-from-bay change (full minefield doc rewrite is Phase 4)
- [ ] Check `docs/02_PATTERNS.md` for the old `carried_items` substrate pattern; update if present

**Notes:** [Per TD plan §"Phase 1" step 10.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ShipInstance` no longer relies on `List[Dict[str, Any]]` for both drop pods and carried vehicles (per TD plan §"Per-Phase Success Criteria" Phase 1)
- [ ] Grep gates green: `carried_items` and `from_any(` return zero hits in `game/` and `tests/`
- [ ] Focused suites green: `pytest tests/unit/strategy/data tests/unit/strategy/engine/order_handlers tests/integration/test_fms_*`
- [ ] `python Projects/scripts/validate_phase.py PROJ-431 1` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] **Notify PROJ-425 owners — cargo/deployable forwarder-demolition batch is unblocked**
