# PROJ-431 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> Derived from [TD-10_deployable_substrate.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-10_deployable_substrate.md) §"Concrete File Touch Plan" and §"Affected Code".

## Files

### Production — added (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/bay_inventory.py` | Production (new) | New file. `DropPod` dataclass + `BayInventory` (`bay: list[CarriedVehicle]`, `pods: list[DropPod]`) with `to_dict()` / `from_dict()`. |

### Production — added (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/deployed_group.py` | Production (new) | `DeployedGroup` abstract base + `MineGroup` concrete (sensitivity, threshold, mines, positions, scatter_seed). Expanded in Phase 3 with `FighterWing` and `SatelliteConstellation`. |
| `game/strategy/facade/dto/mine_group_dto.py` | Production (new — likely) | Separate `MineGroupDTO`; the mine-specific defaults are removed from `FleetDTO`. |

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Replace `carried_items: List[Dict[str, Any]]` with `bay_inventory: BayInventory`. Remove `from_any`-based pod-storage filter; `get_pod_storage_used` becomes `sum(p.mass for p in bay_inventory.pods)`. |
| `game/strategy/data/ship_cargo_manager.py` | Production | `_assign_carried_to_bays`, `get_vehicle_bay_capacity`, `can_accept_vehicle`, `load_vehicle`, `unload_vehicle`, `get_carried_vehicles`, `get_carried_vehicles_by_type` all switch to `bay_inventory.bay`. Drop the `CarriedVehicle.from_any()` discriminator from every accessor. |
| `game/strategy/data/ship_instance_serializer.py` | Production | Round-trip `bay_inventory` instead of `carried_items`. Saves disposable; no migration shim. |
| `game/strategy/data/carried_vehicle.py` | Production | **Delete `from_any()`** — bay is homogeneous typed list, no discriminator needed. |
| `game/strategy/engine/order_handlers/colonize.py` | Production | `_deploy_drop_pod` walks `bay_inventory.pods`. `ColonizeValidator.find_ship_with_drop_pod` checks `bay_inventory.pods`. |
| `game/strategy/engine/order_handlers/lay_mines.py` | Production | Read/write `bay_inventory.bay` for mine source. (`_seed_mine_group_carrier` survives Phase 1 — deleted in Phase 2.) |
| `game/strategy/engine/order_handlers/launch_fighters.py` | Production | Read/write `bay_inventory.bay` for fighter source. |
| `game/strategy/engine/order_handlers/launch_satellites.py` | Production | Read/write `bay_inventory.bay` for satellite source. |
| `game/strategy/engine/order_handlers/recover_fighters.py` | Production | Push recovered fighters into `bay_inventory.bay`. |
| `game/strategy/engine/order_handlers/recover_satellites.py` | Production | Push recovered satellites into `bay_inventory.bay`. |
| `game/strategy/engine/order_handlers/transfer_branches.py` | Production | Inventory transfers operate on `bay_inventory.bay` / `bay_inventory.pods`. |
| `game/strategy/engine/issuer_adapter.py` | Production | `IIssuerAdapter`, `FleetShipIssuerAdapter`, `PlanetStagingYardIssuerAdapter` read/write `bay_inventory.bay`. The `_matches` helper becomes trivial type-equality. |
| `game/strategy/services/mine_group_service.py` | Production | Read/write `bay_inventory.bay` for mine enumeration. (Service is rewritten in Phase 2 to operate on `MineGroup` directly.) |

### Production — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/empire.py` | Production | Add `deployed_groups: list[DeployedGroup]`; `add_deployed_group` / `remove_deployed_group`. Serialise/deserialise alongside `fleets`. Likely also add `IDeployedGroupSource` accessor for AI controllers. |
| `game/strategy/data/fleet.py` | Production | Remove `"mine_group"` from `group_kind` legal-values set. Move mine-specific dataclass attributes (`sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`) to `MineGroup`. Drop mine branches in `to_dict` / `from_dict`. |
| `game/strategy/data/fleet_capability_calculator.py` | Production | Mine-group early-return becomes moot once mines are not fleets; leave `group_kind` fighter/satellite branches for Phase 3. |
| `game/strategy/engine/minefield_resolver.py` | Production | Rewrite to iterate `empire.deployed_groups` filtered to `MineGroup`. **Delete `_iter_mines` / `_set_mines` synthetic-carrier helpers**; iterate `mine_group.mines` directly. |
| `game/strategy/engine/order_handlers/lay_mines.py` | Production | Construct a `MineGroup`, NOT a `Fleet`. **Delete `_seed_mine_group_carrier`**. Adjust `_mint_fleet_id` (or rename) to mint a deployed-group id. |
| `game/strategy/services/mine_group_service.py` | Production | Operate on `MineGroup`. **Drop `_is_mine_group`** — the runtime type is the check. |
| `game/strategy/combat/spec_compiler.py` | Production | **Delete `_split_mine_groups_from_fleets`**. Assembler consumes `empire.deployed_groups` (MineGroup subset) explicitly through a typed parameter. The temporary `mine_group_filter` parameter added by PROJ-426 simplifies out. |
| `game/strategy/engine/turn_phase_registry.py` | Production | Filter at `:186-225` (`getattr(f, "group_kind", "fleet") == "fleet"`) becomes moot — drop it. (If PROJ-428 has already extracted this hook into a dedicated phase class, the change lands inside the class.) |
| `game/strategy/facade/dto/fleet_dto.py` | Production | Drop mine-specific defaults; the new `MineGroupDTO` carries them. |
| `game/ui/screens/fleet_menu_items.py` | Production | Render deployed groups from `empire.deployed_groups`, not by filtering `empire.fleets`. Dispatch table keyed on the deployed-group runtime type. |
| `game/ui/screens/strategy_detail_fmt.py` | Production | Same — replace `group_kind` checks with `isinstance(g, MineGroup)`. |

### Production — modified (Phase 3)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/deployed_group.py` | Production | Add `FighterWing` and `SatelliteConstellation` classes, each owning `ships: list[ShipInstance]`. |
| `game/strategy/data/empire.py` | Production | Serialise/deserialise the new families. |
| `game/strategy/data/fleet.py` | Production | **Drop `"fighter_group"` and `"satellite_group"`** from `group_kind`. **Delete `group_kind` entirely** — every Fleet is a real fleet now. |
| `game/strategy/data/fleet_capability_calculator.py` | Production | **Drop the `group_kind` early-return** — fleets no longer carry deployed-group state. |
| `game/strategy/engine/handlers/base.py` | Production | **Delete `_reject_if_non_fleet_group` (lines 208-230).** |
| `game/strategy/engine/handlers/movement.py` | Production | Remove guard call at `:106` (Move), `:154` (Intercept), `:197` (Join Fleet), `:248` (Warp). |
| `game/strategy/engine/handlers/build.py` | Production | Remove guard call at `:54`. |
| `game/strategy/engine/handlers/lay_mines.py` | Production | Remove guard call at `:52`. |
| `game/strategy/engine/handlers/launch_fighters.py` | Production | Remove guard call at `:59`. |
| `game/strategy/engine/handlers/launch_satellites.py` | Production | Remove guard call at `:57`. |
| `game/strategy/engine/handlers/recover_fighters.py` | Production | Remove guard call at `:56`. |
| `game/strategy/engine/handlers/recover_satellites.py` | Production | Remove guard call at `:55`. |
| `game/strategy/engine/order_handlers/launch_fighters.py` | Production | Construct `FighterWing`, NOT `Fleet`. `_create_fighter_group` returns the new type. |
| `game/strategy/engine/order_handlers/launch_satellites.py` | Production | Construct `SatelliteConstellation`. `_create_satellite_group` returns the new type. |
| `game/strategy/engine/order_handlers/recover_fighters.py` | Production | Find target wing via type, not `getattr(f, "group_kind") == "fighter_group"`. |
| `game/strategy/engine/order_handlers/recover_satellites.py` | Production | Same — find by type. |
| `game/strategy/combat/spec_compiler.py` | Production | Combat spec assembler walks `empire.deployed_groups` (FighterWing subset) and adds those ships as combat participants alongside `empire.fleets`. |
| `game/strategy/adapters/simulation_adapter.py` | Production | Consume new `MineGroup` / `FighterWing` inputs. |
| `game/simulation/systems/fighter_reboard.py` | Production | Reboard target is a `FighterWing`, not a `Fleet`. |
| `game/simulation/systems/tactical_mine_resolver.py` | Production | Consume `MineGroup` directly. |
| `game/ai/carrier_controller.py` | Production | Read `empire.deployed_groups` filtered to `FighterWing`. |
| `game/ai/fighter_controller.py` | Production | Same — type-filtered access. |
| `game/ai/satellite_controller.py` | Production | Same. |

### Production — modified (Phase 4)

| File | Type | Notes |
|------|------|-------|
| Final grep cleanup | Production | Any remaining `group_kind`, `from_any(`, `_split_mine_groups_from_fleets`, `_reject_if_non_fleet_group`, `synthetic_carrier`, `carried_items` references. Each should be deleted or migrated. |

### Tests — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_bay_inventory.py` | Test (new) | Phase 1. Construction, drop-pod load/use, CarriedVehicle load/use, mass accounting, save/load round-trip, explicit rejection of cross-slot leakage (drop pod in bay slot, CV in pods slot). |
| `tests/unit/strategy/data/test_mine_group.py` | Test (new) | Phase 2. Identity, sensitivity/threshold, mine list, positions/seed, serialisation round-trip. |
| `tests/unit/strategy/data/test_fighter_wing.py` | Test (new) | Phase 3. Identity, ships list, reboard state. |
| `tests/unit/strategy/data/test_satellite_constellation.py` | Test (new) | Phase 3. Identity, ships list. |
| `tests/unit/strategy/data/test_empire_deployed_groups.py` | Test (new) | Phase 2. Empire owns a separate `deployed_groups` collection; serialisation; add/remove helpers. |

### Tests — modified (already dirty in `git status`)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py` | Test | Phase 1. Drop the `from_any` discrimination layer; switch fixtures to `bay_inventory.bay`. |
| `tests/unit/strategy/data/test_vehicle_bay.py` | Test | Phase 1. Same. |
| `tests/integration/test_fms_a_e2e.py` | Test | Phase 1. Update inventory accessors. |
| `tests/integration/test_fms_c_carrier_ai_launch.py` | Test | Phase 1. |
| `tests/integration/test_fms_cd_isolation.py` | Test | Phase 1. |

### Tests — modified

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/test_minefield_resolver.py` | Test | Phase 2. Adapt all fixtures to `MineGroup`. |
| Every `test_*launch_*.py` / `test_*recover_*.py` / `test_lay_mines*.py` | Test | Phase 2/3. Switch assertions from "fleet with `group_kind="..."`" to "deployed-group of the right type." |

### Docs — modified (Phase 4)

| File | Type | Notes |
|------|------|-------|
| `docs/systems/strategy_layer.md` | Doc | Describe `Empire.deployed_groups` and the typed family; remove `Fleet.group_kind` references. |
| `docs/systems/minefields.md` | Doc | Rewrite "minefield storage" section — no synthetic carrier. |
| `docs/systems/fighters.md` | Doc | Reflect `FighterWing` and `bay_inventory.bay`. |
| `docs/systems/satellites.md` | Doc | Reflect `SatelliteConstellation` and `bay_inventory.bay`. |
| `docs/01_ARCHITECTURE.md` | Doc | If it describes Fleet as the deployable substrate, update. |
| `docs/02_PATTERNS.md` | Doc | If it documents the `carried_items` substrate, update. |
