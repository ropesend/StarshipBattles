# TD-10: Deployable Small Craft and Minefields Overload Fleet/Ship Cargo Abstractions

## Verdict

**VERIFIED.** The current deployable-object substrate works end-to-end (PROJ-FMS-A through PROJ-FMS-D are shipped), but the architecture is exactly as the review describes: three deployable families (mines, fighters, satellites) and a fourth pre-existing path (drop pods) all hang off two overloaded abstractions:

1. `Fleet` is the bus for both real fleets and deployed groups; the discriminator is a string `group_kind` with four legal values.
2. `ShipInstance.carried_items` is the bus for both legacy drop-pod dicts AND typed `CarriedVehicle` entries; the discriminator is `CarriedVehicle.from_any()` which returns `None` for drop-pod-shaped entries.
3. Mine groups use a *synthetic carrier `ShipInstance`* whose only job is to hold the mine list in its `carried_items`.

## Verification Findings — Current Overload Patterns

### A. `Fleet` is the substrate for all deployed-group families

- `game/strategy/data/fleet.py:54-73` — `Fleet.__init__` accepts `group_kind` ∈ `{"fleet", "fighter_group", "satellite_group", "mine_group"}` and rejects anything else.
- `game/strategy/data/fleet.py:76-92` — mine-only runtime fields (`sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`) are dataclass attributes on every `Fleet`, populated only when `group_kind == "mine_group"`. Comment explicitly says "they default to safe values on non-mine groups so consumers can read them unconditionally without `hasattr` guards" — i.e. the contract is "every Fleet carries the mine-specific surface."
- `game/strategy/data/fleet.py:131-138` — `can_strategic_move` is `True` only for `group_kind == "fleet"`.
- `game/strategy/data/fleet.py:500-527` — `to_dict` branches on `group_kind == "mine_group"` to emit/skip mine-specific fields.
- `game/strategy/data/fleet.py:582` — `from_dict` defaults missing `group_kind` to `"fleet"` (silent on saves predating this).
- `game/strategy/data/fleet_capability_calculator.py:96-107` — capability methods early-return on non-fleet `group_kind` (the deployed groups don't have real combat surfaces).

### B. `_reject_if_non_fleet_group` is a guard rail repeated across every fleet-action handler

- `game/strategy/engine/handlers/base.py:208-230` — central guard. Inspects `getattr(fleet, "group_kind", "fleet")` and rejects with a string error when it's not `"fleet"`. Note: the implementation accepts "no group_kind" as fleet (treats mocked / partial fleets without an explicit discriminator as real).
- Callers: `handlers/movement.py:106` (Move), `:154` (Intercept), `:197` (Join Fleet), `:248` (Warp); `handlers/build.py:54` (Build); `handlers/lay_mines.py:52`; `handlers/launch_fighters.py:59`; `handlers/launch_satellites.py:57`; `handlers/recover_fighters.py:56`; `handlers/recover_satellites.py:55`. **Ten distinct command handlers** must remember to invoke the guard.

### C. `ShipInstance.carried_items` mixes drop-pod dicts and `CarriedVehicle` entries

- `game/strategy/data/ship_instance.py:135-146` — `carried_items: List[Dict[str, Any]]` documented in-code as carrying TWO shapes: legacy drop-pod dicts and `CarriedVehicle.to_dict()` output. Discriminator is `CarriedVehicle.from_any()`.
- `game/strategy/data/ship_instance.py:510-530` — `get_pod_storage_capacity` / `get_pod_storage_used` filters OUT `CarriedVehicle` entries to compute drop-pod storage; the parallel `bay_capacity` path filters them IN. Same list, two opposing readers, two filters.
- `game/strategy/data/ship_cargo_manager.py:191-272` — `_assign_carried_to_bays`, `get_vehicle_bay_capacity`, `can_accept_vehicle`, `load_vehicle`, `unload_vehicle`, `get_carried_vehicles`, `get_carried_vehicles_by_type` all walk `carried_items` and either coerce via `CarriedVehicle.from_any()` or skip non-matching entries. Every accessor pays the discrimination cost.
- `game/strategy/data/carried_vehicle.py:110-125` — `from_any()` is the runtime type tag; it returns `None` for items that lack `vehicle_type ∈ {mine, fighter, satellite}`.
- `game/strategy/engine/order_handlers/colonize.py:139-182` — `_deploy_drop_pod` walks `ship.carried_items` looking for the FIRST drop-pod entry and pops it. The handler has no notion of "skip CarriedVehicle entries" — it just uses `ColonizeValidator.find_ship_with_drop_pod` which encodes that filter elsewhere.

### D. Mine groups use a synthetic carrier `ShipInstance` whose only job is to hold mines

- `game/strategy/engine/minefield_resolver.py:144-163` — `_iter_mines` / `_set_mines` read and write `mine_group.ships[0].carried_items`. The comment makes the intent explicit: "the mine_group's `ships` list holds a single carrier instance that doubles as the mine container — this keeps the existing serializer/DTO surface usable."
- `game/strategy/engine/order_handlers/lay_mines.py:355-369` — `_seed_mine_group_carrier` constructs a `ShipInstance` with `design_id="mine_carrier_synthetic"`, `design_data={"name": "Mine Carrier", "vehicle_class": "Mine"}`, `current_hp=0`, marks it `is_alive=True`, and appends it to `mine_group.ships`. This is a fake ship whose entire reason for existence is to act as a container.
- `game/strategy/services/mine_group_service.py:68-117` — `MineGroupService` reads/writes `mine_group.ships[0].carried_items` directly to enumerate / destroy mines. Every method first checks `_is_mine_group(fleet)` (`:142-144`).
- `game/strategy/combat/spec_compiler.py:430-451` — `_split_mine_groups_from_fleets` partitions fleets out of the battle spec because "the spec compiler turns the synthetic carrier into a degenerate ship on its own team — which is both wrong (it has no real combat surface) and a violation of the design's 'mines are a battlefield hazard, not a combatant' rule." The synthetic-carrier hack is so leaky it requires a filter at the combat boundary.

### E. Full Deployable Family Inventory

Searched the codebase for every payload family that hangs off either `carried_items`, `staging_yard`, or `group_kind`:

| Family | `group_kind` value | `CarriedVehicle.vehicle_type` | Substrate | Tactical-side hook |
|---|---|---|---|---|
| **Mines** | `"mine_group"` | `"mine"` | synthetic-carrier `ShipInstance` inside `Fleet.ships[0]`; mines live in `ships[0].carried_items` | `MinefieldResolver` (strategic), `TacticalMineResolver` (tactical), separate scatter/pos state on `Fleet` |
| **Fighters** | `"fighter_group"` | `"fighter"` | real `CarriedVehicle` entries in carrier `ship.carried_items`; deployed group's `ships` holds real `ShipInstance`s built from the CV | `LaunchAttack` + `ReboardTracker` + `apply_reboard` |
| **Satellites** | `"satellite_group"` | `"satellite"` | same as fighters | recovery only (no in-battle reboard) |
| **Drop pods** | n/a — never a deployed group; pods stay in carrier `ship.carried_items` until colonize, then become a `Facility` | none — bare dict with `design_data`, `mass`, etc. | `ship.carried_items` (legacy untyped shape) | `_deploy_drop_pod` in `ColonizeOrderHandler` consumes one and creates a planet `Facility` |

There are exactly four deployable families today. Three share the `carried_items` substrate; mines additionally invent a synthetic-carrier `ShipInstance`. The drop-pod path is the legacy reason `carried_items` is `List[Dict[str, Any]]` instead of `List[CarriedVehicle]`.

### Issuer adapter — partial mitigation already in place

`game/strategy/engine/issuer_adapter.py` introduces `IIssuerAdapter`, `FleetShipIssuerAdapter`, and `PlanetStagingYardIssuerAdapter` so the five FMS handlers (lay, launch×2, recover×2) can serve both fleet-issued and planet-issued orders through a single contract. This contains the pop/append/count surface for `vehicle_type` ∈ `{mine, fighter, satellite}`. It is **not** a deployable-group model — it's an inventory accessor — but it's the right shape to build on and confirms the team has already started extracting the substrate.

### Verdict summary

The overload patterns described in the review are real, central, and load-bearing:
- 14+ files branch on `group_kind` directly.
- 10 fleet-action handlers must remember to call `_reject_if_non_fleet_group`.
- `ShipInstance.carried_items` is statically typed `List[Dict[str, Any]]` because it carries two disjoint shapes that need runtime discrimination.
- The mine-group synthetic carrier is a documented workaround for keeping the serializer surface stable, and it leaks into the combat spec compiler.

The review's diagnosis is accurate. The recommended action ("explicit deployable-group / strategic-payload model before adding the next family; if too large, at least stop using 'first ship's carried_items' as the storage substrate") is the right shape.

## Affected Code

**Domain / data (substrate):**
- `game/strategy/data/fleet.py` (group_kind, mine fields, capability gate, serialisation branches)
- `game/strategy/data/fleet_capability_calculator.py` (group_kind early-return)
- `game/strategy/data/ship_instance.py` (carried_items, pod storage filters)
- `game/strategy/data/ship_cargo_manager.py` (bay enumeration + CarriedVehicle filtering)
- `game/strategy/data/carried_vehicle.py` (typed entry + `from_any` discriminator)
- `game/strategy/data/ship_instance_serializer.py`
- `game/strategy/facade/dto/fleet_dto.py` (group_kind field on DTO)

**Strategic engine (handlers + resolvers + phase):**
- `game/strategy/engine/handlers/base.py` (`_reject_if_non_fleet_group`)
- `game/strategy/engine/handlers/{movement,build,lay_mines,launch_fighters,launch_satellites,recover_fighters,recover_satellites}.py`
- `game/strategy/engine/order_handlers/{lay_mines,launch_fighters,launch_satellites,recover_fighters,recover_satellites,colonize,transfer_branches}.py`
- `game/strategy/engine/issuer_adapter.py`
- `game/strategy/engine/minefield_resolver.py` (_iter_mines / _set_mines / synthetic carrier)
- `game/strategy/engine/turn_phase_registry.py:186-225` (filter on `group_kind == "fleet"` before minefield resolution)
- `game/strategy/services/mine_group_service.py`

**Combat boundary:**
- `game/strategy/combat/spec_compiler.py:430-451` (`_split_mine_groups_from_fleets`)
- `game/strategy/adapters/simulation_adapter.py` (mine_group consumers)
- `game/simulation/systems/tactical_mine_resolver.py`
- `game/simulation/systems/fighter_reboard.py`

**UI:**
- `game/ui/screens/fleet_menu_items.py`
- `game/ui/screens/strategy_detail_fmt.py` (and other UI consumers reading `group_kind`)

## Goal / End State

### Recommended: introduce an explicit `DeployedGroup` family + typed `BayInventory`

Two coupled extractions that together close the overload:

1. **`DeployedGroup` (new sibling to `Fleet`, NOT a subclass).** Each kind (`Minefield`, `FighterWing`, `SatelliteConstellation`) is a small dataclass that owns:
   - identity (`id`, `owner_id`, `location`, `display_name`)
   - per-family runtime state (mine sensitivity / threshold / positions / seed; fighter ships; satellite ships)
   - serialisation
   No `group_kind` strings; the runtime type IS the model. `Empire` grows `deployed_groups: list[DeployedGroup]` separate from `fleets: list[Fleet]`. The combat spec assembler and minefield resolver pull from the dedicated list instead of filtering Fleets by string.

2. **Typed `BayInventory` replacing `ShipInstance.carried_items`.** Two slots:
   - `bay: list[CarriedVehicle]` — design-backed mines/fighters/satellites with per-bay typed allocation (already enforced by `ShipCargoManager._enumerate_bays`).
   - `pods: list[DropPod]` — a new lightweight dataclass for drop pods.
   `ShipInstance` exposes `bay_inventory: BayInventory`. All accessors (`get_pod_storage_used`, `get_carried_vehicles`, `can_accept_vehicle`, `load_vehicle`) operate on the typed slot directly, no `from_any()` filter on every read.

**Rationale for recommending the full split over the fallback:**

- The review's "fallback" option (stop using "first ship's carried_items" as the mine-storage substrate, and type `carried_items`) is half of the recommended path. Doing only that leaves `Fleet.group_kind` as the discriminator across 14+ files and the 10 handler guards, which is the most error-prone part of the current state — mine-group state is the easier half because there is a clean owning service already (`MineGroupService`).
- LLM-time cost of the bigger split is moderate (a few hours including test runs) because the mediation surfaces already exist: `IIssuerAdapter`, `MineGroupService`, `CarriedVehicle`, `_split_mine_groups_from_fleets`. The fallback would be ~30% of the work and would leave the higher-value cleanup undone.
- Per CLAUDE.md "old saves are disposable," so the savefile-shape change for the inventory split is acceptable.
- Per the user's "feedback_capability_missing_rejects_not_degrades.md" preference, a typed model that makes "fleet vs deployed group" a compile-time distinction is strictly better than a runtime-string discriminator that has to be guarded in ten different handlers.

### Fallback if scope must be reduced

If the full split has to be deferred, the minimum useful slice is:

- **Step F-1.** Replace `ShipInstance.carried_items: List[Dict]` with a typed `BayInventory` (`bay: list[CarriedVehicle]`, `pods: list[DropPod]`). Saves are disposable.
- **Step F-2.** Replace the mine-group synthetic carrier with a `MineContainer` DTO held directly on the `mine_group` Fleet (e.g. `Fleet.mine_inventory: list[CarriedVehicle]`). Mine resolvers and `MineGroupService` read from this attribute directly instead of `ships[0].carried_items`.

That removes the worst overload (synthetic ship-as-container) and the worst data-shape ambiguity (two disjoint shapes in one list) but leaves `group_kind` and `_reject_if_non_fleet_group`. Acceptable as a stopping point only if scope is genuinely constrained.

## Remediation Plan — Phased TDD Migration

## Execution Preconditions

1. Treat this as the highest-risk plan in the owned set. Do **not** start it
   while TD-06, TD-01, or TD-04 are simultaneously reshaping the same files.
2. Re-enumerate the current overload sites before implementation:
   ```text
   rg -n "group_kind|carried_items|from_any\(|_reject_if_non_fleet_group|synthetic_carrier|mine_group" game/strategy game/ui tests
   ```
3. Decide up front whether the execution is doing only the fallback slice
   (typed `BayInventory`) or the full `DeployedGroup` split. Do not let a weak
   LLM drift from the fallback into Phases 2-4 opportunistically.
4. If the full split is chosen, phase boundaries must become PR boundaries:
   - Phase 1 ships alone
   - Phase 2 ships alone
   - Phase 3 ships alone
   - Phase 4 is cleanup/docs only

## Concrete File Touch Plan

### Phase 1 only

- New file: `game/strategy/data/bay_inventory.py`
- Modify:
  - `game/strategy/data/ship_instance.py`
  - `game/strategy/data/ship_cargo_manager.py`
  - `game/strategy/data/ship_instance_serializer.py`
  - `game/strategy/engine/order_handlers/colonize.py`
  - `game/strategy/engine/issuer_adapter.py`
  - FMS order handlers that currently read/write `carried_items`
- Tests:
  - New: `tests/unit/strategy/data/test_bay_inventory.py`
  - Existing: `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py`
  - Existing: `tests/unit/strategy/data/test_vehicle_bay.py`
  - Colonize / transfer / FMS tests touching pod and vehicle storage

### Phase 2 only

- New or expanded deployed-group model file:
  - Recommended: `game/strategy/data/deployed_group.py`
- Modify:
  - `game/strategy/data/empire.py`
  - `game/strategy/engine/minefield_resolver.py`
  - `game/strategy/engine/order_handlers/lay_mines.py`
  - `game/strategy/services/mine_group_service.py`
  - `game/strategy/combat/spec_compiler.py`
  - `game/strategy/facade/dto/fleet_dto.py`
  - `game/ui/screens/fleet_menu_items.py`
  - `game/ui/screens/strategy_detail_fmt.py`

### Phase 3 only

- `game/strategy/data/deployed_group.py`
- `game/strategy/data/empire.py`
- `game/strategy/engine/order_handlers/launch_fighters.py`
- `game/strategy/engine/order_handlers/launch_satellites.py`
- `game/strategy/engine/order_handlers/recover_fighters.py`
- `game/strategy/engine/order_handlers/recover_satellites.py`
- `game/simulation/systems/fighter_reboard.py`
- `game/strategy/combat/spec_compiler.py`
- AI/controller/UI consumers that still assume deployed groups are `Fleet`

### Phase 4 only

- `docs/systems/strategy_layer.md`
- `docs/systems/minefields.md`
- `docs/systems/fighters.md`
- `docs/systems/satellites.md`
- `docs/02_PATTERNS.md` if it documents the old substrate

## Weak-LLM Guardrails

- Do not attempt the full deployable-model redesign in one unbroken pass. Phase boundaries here are real and should be committed independently.
- Phase 1 is inventory typing only. Do not simultaneously redesign `Empire`, battle assembly, and all deployed-group families in the same change.
- When migrating away from `Fleet.group_kind`, remove one family at a time and run the relevant focused suites before touching the next family.
- Do not preserve old-save compatibility. Replace the substrate cleanly and let save versioning reject old shapes.
- Use grep gates for `group_kind`, `_reject_if_non_fleet_group`, `_split_mine_groups_from_fleets`, `from_any(`, and `carried_items` so deletion is verified explicitly.

## Per-Phase Success Criteria

- Phase 1 is done only when `ShipInstance` no longer relies on a
  `List[Dict[str, Any]]` payload list for both drop pods and carried vehicles.
- Phase 2 is done only when minefields no longer rely on `Fleet.ships[0]` as a
  storage container.
- Phase 3 is done only when `_reject_if_non_fleet_group` and the non-fleet
  `group_kind` values are fully removable.
- Phase 4 is done only after a full grep confirms there are no remaining
  semantic uses of `group_kind`, `carried_items`, `_reject_if_non_fleet_group`,
  or `_split_mine_groups_from_fleets`.

Each phase is independently shippable, behavior-preserving, and follows the "fix root cause, no compat shims, old saves disposable" rule from CLAUDE.md.

### Phase 1 — Typed `BayInventory` on `ShipInstance` (removes drop-pod / CV ambiguity)

**Goal:** `ShipInstance.carried_items` is gone; replaced by `bay_inventory: BayInventory` with two typed slots.

1. RED: Write `tests/unit/strategy/data/test_bay_inventory.py` covering construction, drop-pod load/use, CarriedVehicle load/use, mass accounting, save/load round-trip, and explicit rejection of cross-slot leakage (drop pod in bay slot, CV in pods slot).
2. GREEN: Add `game/strategy/data/bay_inventory.py` with `DropPod` and `BayInventory` dataclasses; `BayInventory.to_dict()` / `from_dict()`. Add `bay_inventory: BayInventory` field to `ShipInstance`.
3. RED: Add failing tests in `test_ship_cargo_manager_per_bay.py` (currently dirty in `git status`) for the bay-only path operating on `bay_inventory.bay`.
4. GREEN: Update `ShipCargoManager` to read/write `bay_inventory` directly. Drop the `CarriedVehicle.from_any()` discriminator from every accessor — bay is a homogeneous typed list now.
5. RED: Add failing tests for `_deploy_drop_pod` operating on `bay_inventory.pods`.
6. GREEN: Update `ColonizeOrderHandler._deploy_drop_pod` and `ColonizeValidator.find_ship_with_drop_pod` to walk `bay_inventory.pods`.
7. GREEN: Update `IssuerAdapter`, `MineGroupService`, all five FMS order handlers to read/write `bay_inventory.bay`. The `_matches` helper in `issuer_adapter.py` becomes trivial type-equality.
8. GREEN: Update `ShipInstance` serializer to round-trip `bay_inventory` (saves are disposable; no migration shim).
9. Remove `carried_items` field, the `CarriedVehicle.from_any()` shim, and `get_pod_storage_used()`'s filtering logic. The pod storage is now `sum(p.mass for p in bay_inventory.pods)`.
10. Update docs: `docs/systems/fighters.md`, `docs/systems/satellites.md`, `docs/systems/minefields.md`, `docs/02_PATTERNS.md` if it references the substrate.

### Phase 2 — `MineGroup` (DeployedGroup family 1, simplest, ships first)

**Goal:** Mine groups are no longer Fleets. The synthetic carrier `ShipInstance` is deleted.

1. RED: Write `tests/unit/strategy/data/test_mine_group.py` for the new `MineGroup` dataclass: identity, sensitivity / threshold, mine list (`list[CarriedVehicle]`), positions / seed, serialisation round-trip.
2. GREEN: Add `game/strategy/data/deployed_group.py` with the `DeployedGroup` abstract base and the concrete `MineGroup` class.
3. RED: Update `Empire` tests to assert `empire.deployed_groups` is a separate collection.
4. GREEN: Add `Empire.deployed_groups: list[DeployedGroup]`; add helpers `add_deployed_group` / `remove_deployed_group`. Serialise/deserialise alongside `fleets`.
5. RED: `tests/unit/strategy/engine/test_minefield_resolver.py` — adapt to `MineGroup` (not `Fleet`).
6. GREEN: Rewrite `minefield_resolver.py` to iterate `empire.deployed_groups` (filtered to `MineGroup`) instead of `empire.fleets`. Drop `_iter_mines` / `_set_mines` synthetic-carrier helpers; iterate `mine_group.mines` directly.
7. GREEN: Rewrite `LayMinesOrderHandler` to construct a `MineGroup`, NOT a `Fleet`. Delete `_seed_mine_group_carrier`. Adjust `_mint_fleet_id` to mint a deployed-group id.
8. GREEN: Rewrite `MineGroupService` to operate on `MineGroup`. Drop `_is_mine_group` (the runtime type is the check).
9. GREEN: Update `spec_compiler._split_mine_groups_from_fleets` — actually delete it; the combat spec assembler now consumes `empire.deployed_groups` (MineGroup subset) explicitly through a typed parameter.
10. GREEN: Update `turn_phase_registry.py:186-225` filter — `getattr(f, "group_kind", "fleet") == "fleet"` is moot when minefields aren't fleets.
11. GREEN: Update `FleetDTO` to drop the mine-specific defaults; add a separate `MineGroupDTO`.
12. GREEN: Update UI consumers (`fleet_menu_items.py`, `strategy_detail_fmt.py`) to render deployed groups from `empire.deployed_groups`, not `empire.fleets`.
13. Remove `"mine_group"` from `Fleet`'s `group_kind` legal-values set in `fleet.py:68`. Saves disposable.

### Phase 3 — `FighterWing` + `SatelliteConstellation` (DeployedGroup families 2 & 3)

**Goal:** Same shape as Phase 2 for the remaining two families.

1. RED: `test_fighter_wing.py`, `test_satellite_constellation.py` for the new dataclasses (they DO carry real ships — built from `CarriedVehicle` at launch — so the deployed-group dataclass owns a `ships: list[ShipInstance]` slot).
2. GREEN: Add `FighterWing` and `SatelliteConstellation` classes in `deployed_group.py`. Each owns a `ships: list[ShipInstance]` slot.
3. RED: Update launch / recover order handler tests.
4. GREEN: Rewrite `LaunchFightersOrderHandler` and `LaunchSatellitesOrderHandler` to create FighterWing / SatelliteConstellation, NOT Fleets. `_create_fighter_group` / `_create_satellite_group` return the new types.
5. GREEN: Rewrite recover handlers to find the right deployed-group via type, not via `getattr(f, "group_kind") == "fighter_group"`.
6. GREEN: Update combat spec assembly: deployed-group fighters are participants in combat; the spec compiler walks `empire.deployed_groups` (FighterWing subset) and adds those ships as combat participants alongside `empire.fleets`. (Note: this is where TD-01 and TD-10 touch — see Dependencies.)
7. GREEN: Update `fighter_reboard.py` consumer paths.
8. GREEN: Drop `"fighter_group"` and `"satellite_group"` from `Fleet.group_kind`. Drop `group_kind` entirely from `Fleet` — every Fleet is a real fleet now.
9. Delete `_reject_if_non_fleet_group` in `handlers/base.py:208-230` and remove all ten callers. The 10 fleet-action handlers no longer need the guard because a Fleet is always a real fleet now. The same protection is now provided by the type system: deployed groups don't have `Move` / `Warp` / `Build` order handlers wired.
10. Update `FleetCapabilityCalculator` — drop the `group_kind` early-return.

### Phase 4 — Polish + docs + dead-code sweep

1. Search the tree for any remaining `group_kind` references, `from_any(`, `_split_mine_groups_from_fleets`, `_reject_if_non_fleet_group`, and `synthetic_carrier`. Each should be either deleted or migrated.
2. Update `docs/systems/strategy_layer.md`, `minefields.md`, `fighters.md`, `satellites.md` to reflect the new model.
3. Update `docs/01_ARCHITECTURE.md` if it describes Fleet as the deployable substrate.
4. Run the full sharded suite (`python Tools/test_sharded/test_sharded.py`).

## Test Strategy

**Unit tests (new):**
- `tests/unit/strategy/data/test_bay_inventory.py` — drop-pod / CarriedVehicle separation; mass accounting; round-trip.
- `tests/unit/strategy/data/test_mine_group.py` — minefield-as-deployed-group dataclass.
- `tests/unit/strategy/data/test_fighter_wing.py` and `test_satellite_constellation.py`.
- `tests/unit/strategy/data/test_empire_deployed_groups.py` — Empire owns a separate list; serialisation.

**Unit tests (updated):**
- `tests/unit/strategy/engine/test_minefield_resolver.py` — adapt all fixtures to `MineGroup`.
- `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py` (already dirty) — drop the `from_any` discrimination layer.
- `tests/unit/strategy/data/test_vehicle_bay.py` (already dirty).
- Every `test_*launch_*.py` / `test_*recover_*.py` / `test_lay_mines*.py` — switch assertions from "fleet with `group_kind="..."`" to "deployed-group of the right type."

**Integration tests (must continue to pass):**
- `tests/integration/test_fms_a_e2e.py`, `test_fms_c_carrier_ai_launch.py`, `test_fms_cd_isolation.py` (already dirty).
- The full minefield strategic+tactical resolution path.
- Fighter reboard end-to-end.
- Colonize via drop pod (drop pods stay where they are; they just live in `bay_inventory.pods` now).

**Regression risk hot spots:**
- Combat spec assembly. The mine_group filter / fighter-from-fleet-membership flow is load-bearing for `simulation_adapter`.
- AI controllers (`carrier_controller`, `fighter_controller`, `satellite_controller`) that read `empire.fleets` to find deployed groups today.
- Save/load: saves predating the change won't load. Per CLAUDE.md, that's acceptable.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| **Save format breaks.** | Per CLAUDE.md "old saves are disposable." Document in the phase 1 PR. No migration shim. |
| **Combat spec assembler regression.** | TD-01 is reworking the spec compiler. Coordinate ordering: do Phase 1+2 before TD-01 lands, OR converge on the typed `DeployedGroup` API surface that TD-01 will consume. Either order works; the explicit DeployedGroup model strictly *helps* TD-01 by giving it typed inputs. |
| **AI controllers reading `empire.fleets` for groups.** | Phase 2/3 includes the controller updates. Land an `IDeployedGroupSource` accessor on `Empire` first so controllers get a stable API across the migration. |
| **UI screens reading group_kind for icons/labels.** | Replace `group_kind` checks with `isinstance(g, MineGroup)` (or a dispatch table keyed on the type). UI tests cover the rendering. |
| **The `_reject_if_non_fleet_group` deletion in Phase 3 might miss a caller path.** | Run a final grep for `_reject_if_non_fleet_group` and `group_kind` after Phase 3. The function is private to `BaseHandler`; any remaining reference is a bug. |
| **Battle-spec test fixtures pass `Fleet` with `group_kind="mine_group"`.** | Phase 2 step 6 updates them. The pattern `_split_mine_groups_from_fleets` is the single chokepoint; deleting it forces every test fixture to migrate. |
| **Issuer adapter doesn't currently support deployed-group-as-issuer.** | Not needed. Deployed groups can't issue strategic orders — that's the whole point of the existing `_reject_if_non_fleet_group` guard. |

## Dependencies / Order

Verified sequencing correction:

- TD-06 Phases 0-4 may run before TD-10.
- TD-10 Phase 1 should land before the TD-06 cargo/deployable forwarder-demolition batch.
- Keep TD-01 ahead of the main TD-10 redesign so deployable changes do not have to preserve current battle-spec side channels.
- TD-04 is a soft adjacency only, not a blocker.

If the historical narrative later in this section disagrees with these four bullets, follow these bullets. They are the reconciled ordering guidance.

**TD-06 (`ShipInstance` is still an overloaded entity facade):** Coupled. TD-06 wants to shrink `ShipInstance`; TD-10 Phase 1 *removes one of its responsibilities* (the dual-shape `carried_items`). Recommend landing TD-10 Phase 1 first, then doing TD-06 — TD-10 makes TD-06 easier.

**TD-01 (Battle spec compilation):** Loosely coupled. The mine-group filter `_split_mine_groups_from_fleets` is one of the side-channels TD-01 wants to clean up. TD-10 Phase 2 *deletes* it, which is strictly helpful. Either order works; if TD-01 lands first the assembler will have a `mine_group_filter` parameter that becomes trivial after TD-10 Phase 2.

**TD-04 (Phase registry hooks):** Loosely coupled. The minefield resolver invocation in `turn_phase_registry.py:186-225` will need to consume `empire.deployed_groups` after Phase 2. If TD-04 has already extracted the hook into a dedicated phase class, this is a one-line change inside that class.

**Order:** TD-10 Phase 1 → TD-06 → TD-10 Phases 2–4 → (TD-01 and TD-04 in parallel, both benefit from a clean DeployedGroup model).

## Estimated Scope — LLM Time

- **Phase 1 (Typed BayInventory):** ~30–45 minutes including test run. ~7 files touched, ~3 new tests, behavior-preserving rename of `carried_items` → `bay_inventory` with a typed slot split.
- **Phase 2 (MineGroup extraction):** ~45–60 minutes including test runs. Highest-payoff phase — kills the synthetic carrier hack and the spec-compiler filter. ~12 files touched.
- **Phase 3 (FighterWing + SatelliteConstellation):** ~45–60 minutes including test runs. Symmetric to Phase 2 for two families.
- **Phase 4 (Polish + docs):** ~15 minutes.

**Total:** roughly 2.5–3 hours of LLM work plus full-suite test runs at phase boundaries. The fallback "Phase 1 only" would land in ~30–45 minutes and remove the worst data-shape ambiguity but leave the deployed-group discriminator.
## Acceptance Criteria

- [ ] `ShipInstance` no longer stores mixed drop-pod and deployable entries in one ambiguous list.
- [ ] Mine groups no longer require a synthetic carrier `ShipInstance`.
- [ ] Deployed groups are modeled through explicit types rather than `Fleet.group_kind` string branching.
- [ ] `_reject_if_non_fleet_group` and its fleet-action call sites are gone once the full redesign completes.
- [ ] Combat assembly and minefield resolution consume the new deployed-group model correctly.
- [ ] Focused minefield, launch/recover, cargo/bay, and deployed-group suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
