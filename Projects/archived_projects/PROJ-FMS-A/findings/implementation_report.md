# PROJ-FMS-A Implementation Report

**Status:** All 5 phases complete (2026-05-15). Audit fix pass applied
(2026-05-16) — see `findings/audit_fix_report.md` and the
"2026-05-16 — Audit fix pass" section in `decisions.md`.
**Scope:** Foundation plumbing for the four-project Fighters/Mines/Satellites
sequence. No user-facing behavior in this project — everything is data,
components, ability skeletons, and substrate.

## Per-Phase Summary

### Phase 1: Data — mine classes, layer, components

- Added 4 mine vehicle classes (`Mine (Small/Medium/Large/Heavy)`) with
  `type:"Mine"`, `layer_config:"Mine_Standard"`, `signature_bonus:3.0`.
- New `Mine_Standard` layer (single CORE, mass_pct=1.0) with
  `allow_ability:` whitelist for `Warhead`, `Laserhead`,
  `StructuralIntegrity`, `ToHitAttackModifier`.
- New components: `hull_mine_{small,medium,large,heavy}`,
  `warhead_{small,medium,large}`, `laserhead_{small,medium,large}`,
  `small_targeting_sensor`, `small_targeting_sensor_advanced`,
  `ram_target_module`.
- `mini_sensor` confirmed unchanged (still has
  `RequiresCommandAndControl: true`).
- Build-path plumbing:
  - `build_queue_controller`: added `"mine": "Mine"` to category map.
  - `build_queue_panel_factory`: added `btn_category_mine`, bumped
    tuple shape.
  - `build_queue_screen.py`: wired the Mines button handler.
  - `build_queue_portraits.VEHICLE_TYPE_COLORS`: added `'mine'`.
  - `build_context.py`: docstring updated.
  - `planet_query_service.can_build_type()`: accepts `"mine"`.
  - `fleet_capability_calculator.can_build_type()`: accepts `"mine"`.
  - `design_roles.json`: added `mine_warhead` + `mine_laserhead` roles,
    extended `general_purpose` filter.

### Phase 2: Abilities — Warhead / Laserhead / RamTarget

- New file `game/simulation/components/abilities/warhead.py` containing
  `WarheadAbility`, `LaserheadAbility(BeamWeaponAbility)`,
  `RamTargetAbility`.
- `LaserheadAbility` inherits from `BeamWeaponAbility` so the existing
  family detection at `weapon_registry.py:78-94` (`isinstance` /
  `has_ability('BeamWeaponAbility')` via MRO) recognises it without
  modification. Adds `consume_on_fire: bool = True`.
- `SmallTargetingSensor` is a component-only addition — it carries the
  existing `ToHitAttackModifier` ability with **no**
  `RequiresCommandAndControl` (the explicit design point of the new
  sensor vs the legacy `mini_sensor`).
- All three registered in `ABILITY_REGISTRY` (`Warhead`, `Laserhead`,
  `RamTarget`) and exported through `abilities/__init__.py`.

### Phase 3: VehicleBay substrate

- `CarriedVehicle` dataclass at
  `game/strategy/data/carried_vehicle.py` (design_id, design_data,
  vehicle_type, mass, current_hp, component_states). Validation rejects
  unknown vehicle_type at construction. `from_any()` distinguishes
  CarriedVehicle-shaped dicts from drop-pod dicts.
- `VehicleBayAbility` at
  `game/simulation/components/abilities/vehicle_bay.py`. STRATEGIC
  layer. Two attributes: `capacity_mass` + `allowed_types`.
- Stat contributor `contribute_vehicle_bay` added to
  `stat_contributors/launch.py`; registered in
  `stat_contributors/registry.py` at hangar phase order. Aggregates
  `ship.bay_capacity_mass`.
- `bay_capacity_mass` added to `calculate_design_stats` output so the
  cargo manager can read max-mass without materializing a live Ship.
- `ShipCargoManager` extensions: `load_vehicle`, `unload_vehicle`,
  `get_vehicle_bay_capacity`, `can_accept_vehicle`,
  `get_carried_vehicles`, `get_carried_vehicles_by_type`.
- `ShipInstance` thin facade methods: `get_carried_vehicles`,
  `get_carried_vehicles_by_type`, `get_carried_vehicle_mass`,
  `get_vehicle_bay_capacity`.
- `ShipInstance.carried_items` documented to hold either drop-pod or
  CarriedVehicle-serialized entries (no schema migration; entries
  remain `Dict[str, Any]`).
- Planet staging yard already accepts dicts — verified
  CarriedVehicle.to_dict() round-trips correctly.
- New transfer branches: `_dispatch_carried_vehicle_load` /
  `_dispatch_carried_vehicle_unload` (cargo_type `"vehicle"`).
- `transfer_view_model._build_pod_rows` extended to emit
  `vehicle:<name>` cargo_keys for CarriedVehicle entries
  (vs `drop_pod:<name>` for the legacy path).
- New bay components: `vehicle_bay_{small,medium,large}` (250/750/2000
  mass capacity).
- `FleetInfo` DTO surface extended with `carried_vehicles_by_type`,
  `vehicle_bay_capacity_used/max`, and `group_kind` fields.

### Phase 4: group_kind + signature_bonus + production normalisation

- `Fleet.group_kind` init param + serialisation round-trip. Default
  `"fleet"`. Validation rejects unknown values at construction.
  Legacy saves missing the field default to `"fleet"` — no migration.
- `Fleet.can_strategic_move` property.
- `BaseCommandHandler._reject_if_non_fleet_group(fleet, action)`
  helper used by Move / Intercept / Join / Warp / Build handlers.
  Resilient to mocked fleets in tests (only string discriminators in
  the recognised set trigger rejection).
- `signature_bonus` read from `vehicle_classes[ship_class]` in
  `ship_stats._phase_sensor_defense_scores`. Added to
  `total_defense_score`. Default 0.0 keeps existing classes unchanged.
- Production normalisation in `production_spawner`:
  - Planet-built mine/fighter/satellite -> `Planet.staging_yard` via
    `_spawn_to_staging_yard` (extended to include mine + satellite;
    drop_pod path untouched).
  - Fleet-built mine/fighter/satellite -> new
    `_spawn_fleet_carried_vehicle`. Bay-selection rule:
    flagship first (`fleet.ships[0]`), then canonical fleet order.
    If no bay accepts, log a clear "no bay capacity" warning + emit
    a production event (queue item is consumed; matches existing
    "staging overflow" semantics).
- `current_hp` on staging entries populated from
  `calculate_design_stats['max_hp']` for typed vehicle types.

### Phase 5: Launch/recovery skeletons + OrderType + integration tests

- 6 launch ability skeletons in
  `game/simulation/components/abilities/launch.py`:
  `StrategicMineLayerAbility`, `StrategicFighterLaunchAbility`,
  `StrategicSatelliteLaunchAbility`, `TacticalMineLayerAbility`,
  `TacticalFighterLaunchAbility`, `TacticalSatelliteLaunchAbility`.
  All share `_LaunchAbilityBase` parsing for `capacity_per_action`
  + `cycle_time`. No execution methods.
- 2 recovery ability skeletons in `recovery.py`:
  `RecoverFightersAbility`, `RecoverSatellitesAbility`. Parse
  `recovery_per_action`.
- All 8 registered in `ABILITY_REGISTRY`.
- 5 new `OrderType` enum reservations: `LAY_MINES`, `LAUNCH_FIGHTERS`,
  `LAUNCH_SATELLITES`, `RECOVER_FIGHTERS`, `RECOVER_SATELLITES`. No
  handlers yet — reserved for PROJ-FMS-B/C/D.
- 5 new component definitions to slot the skeletons:
  `mine_launcher_small`, `fighter_launch_bay_small`,
  `satellite_launch_bay_small`, `fighter_recovery_bay_small`,
  `satellite_recovery_bay_small`. **Superseded by Round 4 Obs C:**
  these were consolidated to `mine_deployer`, `fighter_launch_bay`
  (now collocates `RecoverFighters`), and `satellite_launch_bay`
  (now collocates `RecoverSatellites`); the two standalone
  `*_recovery_bay_small` components were deleted. New mine-only
  `mine_bay` was added alongside `fighter_bay` / `satellite_bay`.
  See `PROJ-FMS-shared/design.md` "Status update (Round 4, 2026-05-17)".
- `docs/systems/ability_reference.md` updated with the PROJ-FMS-A
  section (data shapes, layer, file, "where behavior lands later").
- `test_command_registry_contract.py` updated to exempt the five new
  reservations from the "every OrderType must have a command path"
  invariant; future projects move them into the strict set when
  handlers land.

## Tests Added

| File | Tests | Phase |
|---|---|---|
| `tests/unit/data/test_mine_design.py` | 12 | 1 |
| `tests/unit/strategy/data/test_build_context.py` (extended) | 2 new | 1 |
| `tests/unit/ui/panels/test_build_queue_controller.py` (extended) | 1 new | 1 |
| `tests/unit/simulation/components/abilities/test_warhead.py` | 11 | 2 |
| `tests/unit/strategy/data/test_vehicle_bay.py` | 12 | 3 |
| `tests/unit/strategy/data/test_fleet_group_kind.py` | 8 | 4 |
| `tests/unit/simulation/entities/test_signature_bonus.py` | 3 | 4 |
| `tests/unit/strategy/engine/test_production_normalisation.py` | 5 | 4 |
| `tests/integration/test_fms_a_e2e.py` | 12 | 5 |
| `tests/unit/strategy/engine/test_command_registry_contract.py` (extended) | 1 modified | 5 |

**Total added/modified: ~67 tests across 9 files.** All pass individually.

## Sharded Suite Status

- **Pre-FMS-A baseline (main):** 20305 tests, 15 failed, 6 errors, 4 skipped.
- **Post-FMS-A:** 20460 tests (+155), **9 failed (-6)**, 6 errors (same), 4 skipped.
- **Headline:** added 155 new passing tests, 0 new failures, *cleared 6 pre-existing failures* by making FleetInfo DTO surface defensive against mocked test fleets.
- **Remaining failures are all pre-existing on main and unrelated to FMS-A:**
  - `test_ship_instance_damage::test_iter_keys_match_full_hp_builder_for_cross_layer_design` (known flake)
  - 3 `test_ship_stats_golden` (`qs_escort`, `qs_frigate_gc`, `qs_battleship` — `acceleration_rate` drift, predates FMS-A)
  - 5 `test_quickstart_designs::test_design_has_metadata` (missing `_metadata` on certain quickstart designs, predates FMS-A)
  - 6 errors in `test_selection_refinements` (unchanged from baseline)

## Decisions captured

See `Projects/active_projects/PROJ-FMS-A/decisions.md` — five sections,
one per phase, covering tier values (mass/damage/range), file-layout
choices, fallback semantics for missing `group_kind` saves, the
flagship-first bay-selection rule, and the "carried_items overlaps two
dict shapes" decision (no schema migration).

## Limitations / Known Issues for codex consult

1. **Bay-selection ordering**: production spawner uses
   `fleet.ships[0]` as the "flagship". There's no explicit
   `fleet.flagship` accessor in the current codebase; if a true
   flagship concept exists in `fleet_hierarchy.py`, the implementation
   could be tightened. The docstring calls this out.
2. **No bay capacity = silent drop**: when `_spawn_fleet_carried_vehicle`
   finds no compatible bay, the build is dropped with a warning + event.
   This matches the existing "staging overflow" semantics but might
   surprise players. A surfacing-as-error path is left for PROJ-FMS-B/C/D.
3. **CarriedVehicle component_states**: round-trips through
   `to_dict/from_dict` but is never populated by Phase 4 production.
   Will be populated by fighter/satellite recovery in PROJ-FMS-C/D.
4. **Transfer validation for `cargo_type="vehicle"`**: ~~the existing
   `TransferValidator.validate(...)` is invoked with the new
   `vehicle` cargo type and `skip_location_check=True`. Behavior should
   pass through the same validation that drop_pod uses; if
   `TransferValidator` enforces an explicit cargo-type whitelist this
   would need an extension. The integration test does not exercise the
   end-to-end transfer flow; just the cargo-manager round-trip.~~
   **Resolved in audit fix pass (2026-05-16).** `"vehicle"` added to
   `TransferValidator.VALID_CARGO_TYPES` with dedicated load/unload
   validators (`_validate_vehicle_load`, `_validate_vehicle_unload`);
   end-to-end TransferHandler tests added at
   `tests/integration/test_fms_a_e2e.py::TestTransferHandlerVehicleE2E`.
5. **No save round-trip integration test for CarriedVehicle**:
   ~~a round-trip through `SaveGameService` would validate the
   carried_items dict serializes/deserializes intact, but is beyond
   scope for FMS-A.~~ **Partially resolved in audit fix pass
   (2026-05-16).** ShipInstance-level serializer round-trip test
   added at
   `tests/unit/strategy/data/test_fms_a_audit_fixes.py::TestCarriedVehicleSerializerRoundtrip`.
   A full `SaveGameService` round-trip remains future work.
6. **`_iter_vehicle_bays` redundancy**: the cargo manager's
   `_allowed_vehicle_types` walks a fresh `Ship.from_dict()` for each
   load attempt. For high-volume production loops this could be cached
   — left for PROJ-FMS-B/C/D where the strategic launch handlers will
   need similar information.
7. **Ship.bay_capacity_mass = 0 when bay is non-operational**: a bay
   component without active C&C / crew aggregates to 0 capacity. The
   test fixture (`TestShipCargoManagerVehicles`) wires bridge + crew
   to keep the bay operational. This is correct behavior but means
   designs need a working backbone for bays to function.
8. **Pre-existing test `test_iter_keys_match_full_hp_builder_for_cross_layer_design`**:
   already flaky on main. Not addressed.
9. **Phase 1 checklist asked for `signature_bonus` as "suggested initial +3"**:
   implemented as 3.0 on all four mine tiers. May want per-tier
   variation (small mines more evasive than heavy) — left as a
   PROJ-FMS-B balance task.

## File List — every file touched

### Data
- `data/vehicleclasses.json` — added 4 mine classes
- `data/vehiclelayers.json` — added `Mine_Standard` layer
- `data/components.json` — added 4 mine hulls + 3 warhead tiers +
  3 laserhead tiers + 2 sensor tiers + RamTarget + 3 vehicle bays +
  5 skeleton-launcher/recovery components
- `data/design_roles.json` — added `mine_warhead`/`mine_laserhead`
  roles + extended `general_purpose` Mine filter

### Production code
- `game/simulation/components/abilities/__init__.py` — registered
  11 new abilities (`Warhead`, `Laserhead`, `RamTarget`, `VehicleBay`,
  6 launch + 2 recovery skeletons)
- `game/simulation/components/abilities/warhead.py` (NEW)
- `game/simulation/components/abilities/vehicle_bay.py` (NEW)
- `game/simulation/components/abilities/launch.py` (NEW)
- `game/simulation/components/abilities/recovery.py` (NEW)
- `game/simulation/entities/ship_stats.py` — signature_bonus +
  bay_capacity_mass reset (the original `bay_current_mass` field
  was dead code and was removed in the audit fix pass — bay
  current mass is a strategy-layer runtime value, exposed via
  `ShipInstance.bay_current_mass`)
- `game/simulation/entities/ship_design_stats.py` — exposes
  bay_capacity_mass in stats dict
- `game/simulation/entities/stat_contributors/launch.py` — new
  `contribute_vehicle_bay` function
- `game/simulation/entities/stat_contributors/registry.py` —
  registers VehicleBay contributor
- `game/strategy/data/carried_vehicle.py` (NEW)
- `game/strategy/data/fleet.py` — group_kind init / property /
  serialise / deserialise
- `game/strategy/data/ship_cargo_manager.py` — 6 new methods for
  CarriedVehicle handling
- `game/strategy/data/ship_instance.py` — carried_items docstring +
  4 facade methods
- `game/strategy/data/order_types.py` — 5 reserved OrderType values
- `game/strategy/data/build_context.py` — docstring extended
- `game/strategy/data/fleet_capability_calculator.py` — `"mine"` accepted
- `game/strategy/services/planet_query_service.py` — `"mine"` accepted
- `game/strategy/engine/handlers/base.py` — `_reject_if_non_fleet_group`
- `game/strategy/engine/handlers/movement.py` — reject for non-fleet kinds
- `game/strategy/engine/handlers/build.py` — reject for non-fleet kinds
- `game/strategy/engine/order_handlers/transfer.py` — `"vehicle"` cargo route
- `game/strategy/engine/order_handlers/transfer_branches.py` — 2 new
  dispatch branches
- `game/strategy/engine/production_spawner.py` — output normalisation +
  `_spawn_fleet_carried_vehicle`
- `game/strategy/facade/dto/fleet_dto.py` — 4 new DTO fields + 3 helpers
- `game/ui/screens/build_queue_panel_factory.py` — Mines category button +
  tuple-shape bump
- `game/ui/screens/build_queue_screen.py` — handler wiring
- `game/ui/panels/build_queue_controller.py` — category map extended
- `game/ui/panels/build_queue_portraits.py` — `'mine'` color
- `game/ui/screens/transfer_view_model.py` — vehicle:<name> cargo_key

### Tests
- `tests/unit/data/test_mine_design.py` (NEW, 12 tests)
- `tests/unit/strategy/data/test_build_context.py` (+2 tests)
- `tests/unit/ui/panels/test_build_queue_controller.py` (+1 test)
- `tests/unit/simulation/components/abilities/test_warhead.py` (NEW, 11)
- `tests/unit/strategy/data/test_vehicle_bay.py` (NEW, 12)
- `tests/unit/strategy/data/test_fleet_group_kind.py` (NEW, 8)
- `tests/unit/simulation/entities/test_signature_bonus.py` (NEW, 3)
- `tests/unit/strategy/engine/test_production_normalisation.py` (NEW, 5)
- `tests/integration/test_fms_a_e2e.py` (NEW, 12)
- `tests/unit/strategy/engine/test_command_registry_contract.py` (modified)

### Docs / project
- `docs/systems/ability_reference.md` — PROJ-FMS-A section appended
- `Projects/active_projects/PROJ-FMS-A/decisions.md` — five phase sections
- `Projects/active_projects/PROJ-FMS-A/plan.md` — Quick Status table updated
- `Projects/active_projects/PROJ-FMS-A/phase_{1..5}_checklist.md` — all `[x]`
- `Projects/active_projects/PROJ-FMS-A/findings/implementation_report.md` (this file, NEW)

## Postscript (2026-05-17 final state)

The sharded-suite numbers in "Sharded Suite Status" above (20460
tests / 9 failed / 6 errors / 4 skipped) are an accurate snapshot at
PROJ-FMS-A ship time. All four FMS projects, plus four QA rounds and
a dedicated test-baseline cleanup pass, have shipped since. The final
clean baseline is **20840 / 20840 passed / 0 failed / 0 errors /
0 skipped** — see `PROJ-FMS-D/decisions.md` "Post-PROJ-FMS
test-baseline cleanup pass" for the per-failure resolution detail.
The intermediate baselines quoted in B/C/D implementation reports
(20525, 20568, 20646) are also correct at their respective snapshot
times.
