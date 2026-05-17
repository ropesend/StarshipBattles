# Phase 2: `MineGroup` (DeployedGroup family 1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-431 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/deployed_group.py` (new)
- `game/strategy/data/empire.py`
- `game/strategy/data/fleet.py`
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/engine/minefield_resolver.py`
- `game/strategy/engine/order_handlers/lay_mines.py`
- `game/strategy/services/mine_group_service.py`
- `game/strategy/combat/spec_compiler.py`
- `game/strategy/engine/turn_phase_registry.py`
- `game/strategy/facade/dto/fleet_dto.py`
- `game/strategy/facade/dto/mine_group_dto.py` (new — likely)
- `game/ui/screens/fleet_menu_items.py`
- `game/ui/screens/strategy_detail_fmt.py`
- `tests/unit/strategy/data/test_mine_group.py` (new)
- `tests/unit/strategy/data/test_empire_deployed_groups.py` (new)
- `tests/unit/strategy/engine/test_minefield_resolver.py`

**Objective:** Mine groups are no longer `Fleet`s. The synthetic mine-carrier `ShipInstance` is deleted. `_split_mine_groups_from_fleets` is deleted. `"mine_group"` is removed from `Fleet.group_kind`'s legal-values set. This phase is independently shippable.

---

## Tasks

### Task 2.1: RED — author `test_mine_group.py` + `test_empire_deployed_groups.py` [Medium]
**Files:** `tests/unit/strategy/data/test_mine_group.py` (new), `tests/unit/strategy/data/test_empire_deployed_groups.py` (new)
**Tests:** both files — MUST fail (modules don't exist yet)

- [ ] `test_mine_group.py`: identity (id, owner_id, location, display_name), sensitivity, expected_hit_chance_threshold, `mines: list[CarriedVehicle]`, `mine_positions`, `scatter_seed`, `to_dict()` / `from_dict()` round-trip
- [ ] `test_empire_deployed_groups.py`: `Empire.deployed_groups` is a separate list; `add_deployed_group` / `remove_deployed_group`; serialisation round-trip alongside `fleets`
- [ ] Run tests, confirm they fail for the right reason

**Notes:** [Per TD plan §"Phase 2" steps 1, 3.]

### Task 2.2: GREEN — add `deployed_group.py` with `DeployedGroup` + `MineGroup` [Medium]
**File:** `game/strategy/data/deployed_group.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_mine_group.py -q`

- [ ] Add `DeployedGroup` abstract base (identity + owner + location + serialisation contract)
- [ ] Add `MineGroup` concrete class — owns `mines: list[CarriedVehicle]`, `sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`
- [ ] `to_dict()` / `from_dict()` for both
- [ ] `test_mine_group.py` green
- [ ] Verify: file under 500 LOC ceiling

**Notes:** [Per TD plan §"Phase 2" step 2.]

### Task 2.3: GREEN — `Empire.deployed_groups` field + accessors [Medium]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_deployed_groups.py -q`

- [ ] Add `deployed_groups: list[DeployedGroup] = field(default_factory=list)`
- [ ] Add `add_deployed_group(g)` / `remove_deployed_group(g)` helpers
- [ ] Add `deployed_groups_of(cls)` — returns `[g for g in deployed_groups if isinstance(g, cls)]` (used by AI controllers in later phases)
- [ ] Serialise/deserialise alongside `fleets`
- [ ] `test_empire_deployed_groups.py` green

**Notes:** [Per TD plan §"Phase 2" step 4. The `deployed_groups_of` accessor is the `IDeployedGroupSource` mitigation from the design.md risk register.]

### Task 2.4: GREEN — rewrite `MinefieldResolver` on `MineGroup` [Complex]
**File:** `game/strategy/engine/minefield_resolver.py`
**Tests:** `pytest tests/unit/strategy/engine/test_minefield_resolver.py -q`

- [ ] Adapt fixtures in `test_minefield_resolver.py` to `MineGroup` (not `Fleet`)
- [ ] Rewrite resolver to iterate `empire.deployed_groups_of(MineGroup)` instead of filtering `empire.fleets`
- [ ] **Delete `_iter_mines` / `_set_mines`** synthetic-carrier helpers; iterate `mine_group.mines` directly
- [ ] Verify: minefield resolver tests green

**Notes:** [Per TD plan §"Phase 2" steps 5–6.]

### Task 2.5: GREEN — rewrite `LayMinesOrderHandler` to construct `MineGroup` [Complex]
**File:** `game/strategy/engine/order_handlers/lay_mines.py`
**Tests:** lay-mines unit + integration tests

- [ ] Construct a `MineGroup`, NOT a `Fleet`
- [ ] **Delete `_seed_mine_group_carrier`** (the synthetic-carrier `ShipInstance` constructor)
- [ ] Adjust `_mint_fleet_id` (or rename to `_mint_deployed_group_id`) to mint a deployed-group id
- [ ] Add the new `MineGroup` to `empire.deployed_groups`, not `empire.fleets`
- [ ] Verify: lay-mines tests green

**Notes:** [Per TD plan §"Phase 2" step 7. The synthetic carrier `ship_instance.design_id == "mine_carrier_synthetic"` should never be constructed again — grep for `mine_carrier_synthetic` after this task.]

### Task 2.6: GREEN — rewrite `MineGroupService` on `MineGroup` [Medium]
**File:** `game/strategy/services/mine_group_service.py`
**Tests:** mine-group-service unit tests

- [ ] All methods take `MineGroup` directly, not `Fleet`
- [ ] **Drop `_is_mine_group`** — the runtime type is the check
- [ ] Read/write `mine_group.mines` directly (no more `mine_group.ships[0].carried_items`)

**Notes:** [Per TD plan §"Phase 2" step 8.]

### Task 2.7: GREEN — delete `_split_mine_groups_from_fleets`; update combat assembler [Complex]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** spec-compiler unit + integration tests + minefield strategic+tactical resolution path

- [ ] **Delete `_split_mine_groups_from_fleets` entirely**
- [ ] Combat spec assembler consumes `empire.deployed_groups_of(MineGroup)` explicitly through a typed parameter
- [ ] The temporary `mine_group_filter` parameter that PROJ-426 added to the assembler simplifies out — remove it
- [ ] Grep gate (must return zero hits):
  ```
  rg -n "_split_mine_groups_from_fleets|mine_group_filter" game/ tests/
  ```

**Notes:** [Per TD plan §"Phase 2" step 9. This is the highest-payoff deletion in the phase.]

### Task 2.8: GREEN — drop `turn_phase_registry.py:186-225` minefield-fleet filter [Simple]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** turn-engine integration tests

- [ ] Filter `getattr(f, "group_kind", "fleet") == "fleet"` becomes moot — remove it
- [ ] Hook reads `empire.deployed_groups_of(MineGroup)` for the minefield-resolver invocation
- [ ] If PROJ-428 has already extracted this hook into a dedicated phase class, the change lands inside the class (one-line)

**Notes:** [Per TD plan §"Phase 2" step 10.]

### Task 2.9: GREEN — `FleetDTO` cleanup + new `MineGroupDTO` [Medium]
**Files:** `game/strategy/facade/dto/fleet_dto.py`, `game/strategy/facade/dto/mine_group_dto.py` (new — likely)
**Tests:** DTO unit tests

- [ ] Drop the mine-specific defaults from `FleetDTO`
- [ ] Add a separate `MineGroupDTO` (or extend an existing `DeployedGroupDTO` family)
- [ ] Verify: DTO round-trip tests green

**Notes:** [Per TD plan §"Phase 2" step 11.]

### Task 2.10: GREEN — UI consumers switch to `empire.deployed_groups` [Medium]
**Files:** `game/ui/screens/fleet_menu_items.py`, `game/ui/screens/strategy_detail_fmt.py`
**Tests:** UI screen unit tests

- [ ] Render minefields from `empire.deployed_groups_of(MineGroup)`, NOT by filtering `empire.fleets` by `group_kind == "mine_group"`
- [ ] Replace `group_kind == "mine_group"` checks with `isinstance(g, MineGroup)` (or a dispatch-table entry per design.md)
- [ ] Verify: UI tests green

**Notes:** [Per TD plan §"Phase 2" step 12.]

### Task 2.11: GREEN — drop `"mine_group"` from `Fleet.group_kind` legal-values set [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** fleet construction tests; the `to_dict`/`from_dict` mine branch is also deleted

- [ ] Remove `"mine_group"` from the legal-values set in `__init__` validation
- [ ] Move mine-only dataclass attributes (`sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`) off of `Fleet` — they live on `MineGroup` now
- [ ] Drop mine branches in `to_dict` / `from_dict`
- [ ] `fighter_group` and `satellite_group` stay for Phase 3
- [ ] Grep gate: `rg -n '"mine_group"' game/ tests/` returns zero hits

**Notes:** [Per TD plan §"Phase 2" step 13.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Minefields no longer rely on `Fleet.ships[0]` as a storage container (per TD plan §"Per-Phase Success Criteria" Phase 2)
- [ ] Grep gates green:
  - `rg -n "mine_carrier_synthetic|_seed_mine_group_carrier|_split_mine_groups_from_fleets|_iter_mines|_set_mines" game/ tests/` returns zero hits
  - `rg -n '"mine_group"' game/ tests/` returns zero hits
- [ ] Focused suites green: `pytest tests/unit/strategy/engine/test_minefield_resolver.py tests/unit/strategy/data/test_mine_group.py tests/unit/strategy/data/test_empire_deployed_groups.py tests/unit/strategy/combat`
- [ ] `python Projects/scripts/validate_phase.py PROJ-431 2` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
