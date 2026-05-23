# PROJ-431: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.
>
> **Canonical source:** [TD-10_deployable_substrate.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-10_deployable_substrate.md). This file distills that plan; if the two diverge, the TD plan wins.

## Verification Evidence (already verified before scaffold)

The TD-10 plan independently verified the overload patterns. Reproduced numbers:

| Metric | Confirmed value | Source |
|---|---|---|
| Deployable families today | **4** (mines, fighters, satellites, drop pods) | TD-10 §E |
| `Fleet.group_kind` legal values | **4** (`fleet`, `fighter_group`, `satellite_group`, `mine_group`) | `game/strategy/data/fleet.py:54-73` |
| Fleet-action handlers calling `_reject_if_non_fleet_group` | **10** (Move, Intercept, JoinFleet, Warp, Build, LayMines, LaunchFighters, LaunchSatellites, RecoverFighters, RecoverSatellites) | TD-10 §B |
| Files branching on `group_kind` | **14+** | TD-10 §"Verdict summary" |
| Synthetic mine-carrier `ShipInstance` constructions | **1** (`_seed_mine_group_carrier` in `order_handlers/lay_mines.py:355-369`) | TD-10 §D |
| `ShipInstance.carried_items` type today | `List[Dict[str, Any]]` (carries two disjoint shapes) | `game/strategy/data/ship_instance.py:135-146` |
| Runtime discriminator on `carried_items` | `CarriedVehicle.from_any()` returning `None` for drop-pod-shaped entries | `game/strategy/data/carried_vehicle.py:110-125` |
| Combat-boundary filter that exists because of the synthetic carrier | `_split_mine_groups_from_fleets` in `spec_compiler.py:430-451` | TD-10 §D |

**Verdict (TD-10):** the overloads are real, central, and load-bearing. The recommended action — explicit typed `DeployedGroup` family + typed `BayInventory` — is the correct fix.

## Goal / End State (target architecture)

Two coupled extractions:

### 1. `DeployedGroup` family (sibling to `Fleet`, not subclass)

```
game/strategy/data/deployed_group.py
    DeployedGroup           (abstract base — identity + owner + location)
    MineGroup               (sensitivity, threshold, mines: list[CarriedVehicle], positions, scatter_seed)
    FighterWing             (ships: list[ShipInstance], reboard state)
    SatelliteConstellation  (ships: list[ShipInstance])
```

`Empire` grows `deployed_groups: list[DeployedGroup]` as a separate collection from `fleets: list[Fleet]`. No `group_kind` strings — the runtime type IS the model. The combat spec assembler and minefield resolver pull from the dedicated list (filtered by `isinstance`), not by filtering `Fleet`s on a string.

### 2. Typed `BayInventory` replacing `ShipInstance.carried_items`

```
game/strategy/data/bay_inventory.py
    DropPod          (dataclass — design_data, mass, ...)
    BayInventory:
        bay: list[CarriedVehicle]   # design-backed mines/fighters/satellites
        pods: list[DropPod]         # drop pods only
```

`ShipInstance` exposes `bay_inventory: BayInventory`. Every accessor (`get_pod_storage_used`, `get_carried_vehicles`, `can_accept_vehicle`, `load_vehicle`) operates directly on the typed slot — no `from_any()` filter on every read. The pod-storage and bay-capacity readers stop fighting over the same list.

## Migration shape — by file family

### Substrate

- `ship_instance.py`: replace `carried_items: List[Dict[str, Any]]` with `bay_inventory: BayInventory`. Drop the `from_any`-based pod-storage filter; `get_pod_storage_used` becomes `sum(p.mass for p in bay_inventory.pods)`.
- `ship_cargo_manager.py`: every accessor (`_assign_carried_to_bays`, `get_vehicle_bay_capacity`, `can_accept_vehicle`, `load_vehicle`, `unload_vehicle`, `get_carried_vehicles`, `get_carried_vehicles_by_type`) reads `bay_inventory.bay` directly — no `CarriedVehicle.from_any()` discrimination.
- `carried_vehicle.py`: `from_any()` is **deleted**. Bay is homogeneous.
- `ship_instance_serializer.py`: round-trip `bay_inventory`. Saves are disposable; no migration shim.
- `fleet.py`: `group_kind` shrinks step by step (Phase 2 drops `"mine_group"`; Phase 3 drops `"fighter_group"` + `"satellite_group"` and deletes the field). Mine-only attributes (`sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`) move to `MineGroup` in Phase 2.

### Mine-group migration of `_split_mine_groups_from_fleets`

The filter is **deleted, not refactored**. Combat spec assembly today partitions mine_group `Fleet`s out of the spec because the synthetic carrier is "wrong (it has no real combat surface) and a violation of the design's 'mines are a battlefield hazard, not a combatant' rule." Once mines live in `empire.deployed_groups` (typed `MineGroup`), the assembler walks `empire.fleets` for real fleets and `empire.deployed_groups` (filtered to `FighterWing`) for fighter participants — minefields are addressed by the existing `MinefieldResolver` invocation, not by the spec compiler. The temporary `mine_group_filter` parameter that PROJ-426 (TD-01) adds to the assembler simplifies out.

### AI controllers

- `carrier_controller`, `fighter_controller`, `satellite_controller` today read `empire.fleets` and filter by `group_kind` to find deployed groups they own. Switch them to read `empire.deployed_groups` filtered by `isinstance(g, FighterWing)` / `isinstance(g, SatelliteConstellation)`.
- Land an `IDeployedGroupSource` accessor on `Empire` (or a method `empire.deployed_groups_of(MineGroup)`) first so controllers get a stable API across the migration. This is the Risk-register mitigation for "AI controllers reading `empire.fleets` for groups."

### UI dispatch-table refactor

- `fleet_menu_items.py` and `strategy_detail_fmt.py` today branch on `group_kind` to choose icons and labels. Replace with a dispatch table keyed on the deployed-group runtime type:
  ```
  RENDERERS = {
      MineGroup:              render_minefield,
      FighterWing:            render_fighter_wing,
      SatelliteConstellation: render_satellite_constellation,
  }
  ```
- UI tests cover rendering; the dispatch-table refactor is symbol-preserving from the rendered-output perspective.

### Handler guard collapse

The single best signal that the migration is complete: the `_reject_if_non_fleet_group` helper in `handlers/base.py:208-230` is **deleted**, and all ten callers (Move/Intercept/JoinFleet/Warp/Build/LayMines/LaunchFighters/LaunchSatellites/RecoverFighters/RecoverSatellites) lose the guard call. The protection is now structural: deployed groups don't have Move/Warp/Build order handlers wired, so they cannot be passed in the wrong place.

## Phase boundaries are PR boundaries

Per TD-10 §"Execution Preconditions" rule 4: if the full split is chosen (we are), phase boundaries must become PR boundaries.

- **Phase 1 ships alone.** Typed `BayInventory` only. Do NOT simultaneously redesign `Empire`, battle assembly, and deployed-group families. Phase 1 also unblocks PROJ-425's cargo batch.
- **Phase 2 ships alone.** `MineGroup` only. Do not start `FighterWing` extraction in the same change.
- **Phase 3 ships alone.** `FighterWing` + `SatelliteConstellation`, paired because they share substrate and the `group_kind` deletion is atomic across both.
- **Phase 4 is cleanup/docs only.** No production behavior changes.

## Risk register (from TD-10 §"Risks & Mitigations")

| Risk | Mitigation |
|---|---|
| Save format breaks | Per CLAUDE.md "old saves are disposable." Documented in Phase 1. No migration shim. |
| Combat spec assembler regression | PROJ-426 (TD-01) is reworking the spec compiler and is the hard predecessor. Phase 2 deletes `_split_mine_groups_from_fleets` only after the new assembler interface exists. |
| AI controllers reading `empire.fleets` for groups | Phase 2/3 includes the controller updates. Land an `IDeployedGroupSource` accessor on `Empire` first so controllers get a stable API across the migration. |
| UI screens reading `group_kind` for icons/labels | Replace `group_kind` checks with `isinstance(g, MineGroup)` / dispatch-table keyed on the type. UI tests cover the rendering. |
| `_reject_if_non_fleet_group` deletion in Phase 3 misses a caller path | Final grep for `_reject_if_non_fleet_group` and `group_kind` after Phase 3. Both must return zero semantic hits. |
| Battle-spec test fixtures pass `Fleet` with `group_kind="mine_group"` | Phase 2 step 6 updates them. The `_split_mine_groups_from_fleets` chokepoint forces every test fixture to migrate. |
| Issuer adapter doesn't currently support deployed-group-as-issuer | Not needed. Deployed groups can't issue strategic orders — that's the whole point of the existing guard. |

## Weak-LLM guardrails (TD-10 §"Weak-LLM Guardrails")

- Do not attempt the full deployable-model redesign in one unbroken pass.
- Phase 1 is inventory typing only. Do not also redesign `Empire` and all deployed-group families in the same change.
- When migrating away from `Fleet.group_kind`, remove one family at a time and run the relevant focused suites before touching the next.
- Do not preserve old-save compatibility. Replace the substrate cleanly.
- Use grep gates for `group_kind`, `_reject_if_non_fleet_group`, `_split_mine_groups_from_fleets`, `from_any(`, and `carried_items` so deletion is verified explicitly.
