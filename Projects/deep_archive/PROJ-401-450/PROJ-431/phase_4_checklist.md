# Phase 4: Polish + docs + dead-code sweep

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-431 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `docs/systems/strategy_layer.md`
- `docs/systems/minefields.md`
- `docs/systems/fighters.md`
- `docs/systems/satellites.md`
- `docs/01_ARCHITECTURE.md` (if applicable)
- `docs/02_PATTERNS.md` (if applicable)
- Any production / test file flagged by the final grep sweep

**Objective:** Final grep sweep, doc sync, full sharded suite. No production behavior changes in this phase — cleanup only.

---

## Tasks

### Task 4.1: Final grep sweep [Simple]
**Files:** none (read-only verification)
**Tests:** none — verification

Run each grep; every command must return zero semantic hits or only documented exceptions:

- [ ] `rg -n "group_kind" game/ tests/`
- [ ] `rg -n "from_any\(" game/ tests/`
- [ ] `rg -n "_split_mine_groups_from_fleets" game/ tests/`
- [ ] `rg -n "_reject_if_non_fleet_group" game/ tests/`
- [ ] `rg -n "synthetic_carrier|mine_carrier_synthetic|_seed_mine_group_carrier" game/ tests/`
- [ ] `rg -n "carried_items" game/ tests/`
- [ ] `rg -n "_iter_mines|_set_mines" game/ tests/`
- [ ] `rg -n "_is_mine_group" game/ tests/`
- [ ] `rg -n "mine_group_filter" game/ tests/` (PROJ-426's temporary parameter)

Any hit that remains must be migrated or deleted before this phase completes. Per TD plan §"Per-Phase Success Criteria" Phase 4: this phase is done only after a full grep confirms there are no remaining semantic uses.

**Notes:** [Per TD plan §"Phase 4" step 1.]

### Task 4.2: Update `docs/systems/strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** none

- [ ] Describe `Empire.deployed_groups` and the typed family
- [ ] Remove `Fleet.group_kind` references
- [ ] Note `_reject_if_non_fleet_group` has been removed — the protection is structural now
- [ ] Skip any content under `docs/_ignore/`

**Notes:** [Per TD plan §"Phase 4" step 2.]

### Task 4.3: Update `docs/systems/minefields.md` [Medium]
**File:** `docs/systems/minefields.md`
**Tests:** none

- [ ] Rewrite the "minefield storage" section — no synthetic carrier, no `Fleet.ships[0].carried_items`
- [ ] Describe `MineGroup` (`mines: list[CarriedVehicle]`, sensitivity, threshold, positions, scatter_seed)
- [ ] Update strategic vs tactical resolution diagram if present

**Notes:** [Per TD plan §"Phase 4" step 2.]

### Task 4.4: Update `docs/systems/fighters.md` + `docs/systems/satellites.md` [Medium]
**Files:** `docs/systems/fighters.md`, `docs/systems/satellites.md`
**Tests:** none

- [ ] Reflect `FighterWing` and `SatelliteConstellation` deployed-group types
- [ ] Reflect `ShipInstance.bay_inventory.bay` substrate (no more `carried_items` discrimination)
- [ ] Update the reboard description to reference `FighterWing` directly

**Notes:** [Per TD plan §"Phase 4" step 2.]

### Task 4.5: Check `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md` [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`
**Tests:** none

- [ ] If `docs/01_ARCHITECTURE.md` describes `Fleet` as the deployable substrate, update
- [ ] If `docs/02_PATTERNS.md` documents the `carried_items` mixed-shape pattern, remove or replace with the typed `BayInventory` pattern

**Notes:** [Per TD plan §"Phase 4" step 3.]

### Task 4.6: Run the full sharded suite [Simple]
**Files:** none — verification
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite
- [ ] Must be green per TD plan §"Acceptance Criteria" final bullet
- [ ] Capture the timing as a baseline for the cumulative review

**Notes:** [Per TD plan §"Phase 4" step 4.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full grep confirms no remaining semantic uses of `group_kind`, `carried_items`, `_reject_if_non_fleet_group`, or `_split_mine_groups_from_fleets` (per TD plan §"Per-Phase Success Criteria" Phase 4)
- [ ] All docs reflect the new model
- [ ] `python Tools/test_sharded/test_sharded.py` is green
- [ ] `python Projects/scripts/validate_phase.py PROJ-431 4` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — project ready for final audit
