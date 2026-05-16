# PROJ-FMS-A File Manifest

Every file in this table appears in at least one phase checklist. Update if implementation discovers additional files.

## Files

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `data/vehicleclasses.json` | Data | Edit | 1 | Add `mine_small`/`medium`/`large`/`heavy` with `signature_bonus`; `type: "Mine"` |
| `data/vehiclelayers.json` | Data | Edit | 1 | Add `Mine_Standard` layer with `allow_ability:` whitelist (`Warhead`, `Laserhead`, `StructuralIntegrity`, `ToHitAttackModifier`). Fighter compatibility for kamikaze designs is per-component via `allowed_vehicle_types`, not a Fighter-layer allow-list. |
| `game/ui/screens/build_queue_panel_factory.py:448-531` | Production | Edit | 1 | Add `btn_category_mine` to the category panel (this is where category buttons are actually created); update returned tuple shape |
| `game/ui/panels/build_queue_portraits.py:57-64` | Production | Edit | 1 | Add `'mine': <color>` to `VEHICLE_TYPE_COLORS` |
| `data/components.json` | Data | Edit | 1, 2, 5 | Add `Warhead`/`Laserhead`/`SmallTargetingSensor`/`RamTarget`, `vehicle_bay_*`, launch/recovery components |
| `data/design_roles.json` | Data | Edit | 1 | Add mine entries with `vehicle_type_filter: ["Mine"]` |
| `game/ui/panels/build_queue_controller.py:150-163` | Production | Edit | 1 | Add `"mine": "Mine"` to the category map |
| `game/ui/screens/build_queue_screen.py:655-662` | Production | Edit | 1 | Add Mines category button |
| `game/strategy/data/build_context.py:51-61` | Production | Edit | 1 | Extend `can_build_type()` docstring to include `"mine"` |
| `game/strategy/services/planet_query_service.py:71-81` | Production | Edit | 1 | Extend `can_build_type()` to allow `"mine"` |
| `game/strategy/data/fleet_capability_calculator.py:126-148` | Production | Edit | 1, 4 | Extend `can_build_type()` to allow `"mine"`; defensive guards for non-fleet `group_kind` |
| `game/simulation/components/component_loader.py:278-303` | Production | Verify | 2 | Confirm `create_component()` instantiates new abilities correctly |
| `game/strategy/data/order_types.py` | Production | Edit | 5 | Reserve `OrderType` enum values for `LAY_MINES`, `LAUNCH_FIGHTERS`, `LAUNCH_SATELLITES`, `RECOVER_FIGHTERS`, `RECOVER_SATELLITES` |
| `game/simulation/components/abilities/__init__.py` | Production | Edit | 2, 3, 5 | Register new abilities |
| `game/strategy/engine/handlers/movement.py:87-225` | Production | Edit | 4 | Reject `IssueMoveCommand`/`IssueInterceptCommand`/`IssueJoinFleetCommand`/`IssueWarpCommand` for non-fleet `group_kind` |
| `game/strategy/engine/handlers/build.py:26-53` | Production | Edit | 4 | Reject `IssueBuildOrderCommand` for non-fleet `group_kind` |
| `game/simulation/components/abilities/markers.py` | Production | Edit | 5 | Keep existing `VehicleLaunchAbility`; register `TacticalFighterLaunchAbility` alongside |
| `game/simulation/components/abilities/weapons.py` (or new `warhead.py`/`laserhead.py`) | Production | Edit/Add | 2 | `WarheadAbility`, `LaserheadAbility(BeamWeaponAbility)`, `RamTargetAbility` |
| `game/simulation/components/abilities/cargo.py` (or new `vehicle_bay.py`) | Production | Edit/Add | 3 | `VehicleBayAbility` |
| `game/simulation/components/abilities/launch.py` (new) | Production | Add | 5 | Six launch ability skeletons |
| `game/simulation/components/abilities/recovery.py` (new) | Production | Add | 5 | `RecoverFightersAbility`, `RecoverSatellitesAbility` skeletons |
| `game/simulation/entities/stat_contributors/launch.py` | Production | Edit | 3 | Add bay capacity stat contribution |
| `game/simulation/entities/ship_stats.py:424-444` | Production | Edit | 4 | Wire `signature_bonus` into `total_defense_score` |
| `game/strategy/data/ship_instance.py:135-136` | Production | Edit | 3 | Typed `carried_items` for vehicles or add `carried_vehicles` field |
| `game/strategy/data/ship_cargo_manager.py` | Production | Edit | 3 | `load_vehicle()`, `unload_vehicle()`, `get_vehicle_bay_capacity()` |
| `game/strategy/data/fleet.py:39-93` | Production | Edit | 4 | `group_kind` field + `can_strategic_move` property |
| `game/strategy/data/planet.py` | Production | Edit | 3 | Verify `staging_yard` accepts `CarriedVehicle` entries |
| `game/strategy/data/fleet_capability_calculator.py` | Production | Edit (defensive) | 4 | Guard against non-fleet kinds |
| `game/strategy/engine/order_handlers/transfer_branches.py:128-281` | Production | Edit | 3 | Generalise staging transfer for generic carried vehicles |
| `game/strategy/engine/production_spawner.py:107-117` | Production | Edit | 4 | Output normalisation: planet→staging, fleet→bay |
| `game/strategy/facade/dto/fleet_dto.py:96-100,187-218` | Production | Edit | 3, 4 | Surface `group_kind` + carried-vehicle breakdown |
| `game/ui/screens/transfer_view_model.py:264-303` | Production | Edit | 3 | Render generic carried-vehicle rows |
| `tests/data/test_mine_design.py` (new) | Test | Add | 1 | Validate whitelist + invalid-component rejection |
| `tests/unit/strategy/services/test_planet_query_service_mines.py` (new) | Test | Add | 1 | `can_build_type("mine")` for planets |
| `tests/unit/strategy/data/test_fleet_capability_calculator_mines.py` (new) | Test | Add | 1 | `can_build_type("mine")` for fleets |
| `tests/unit/ui/panels/test_build_queue_controller_mines.py` (new) | Test | Add | 1 | Mine category loading |
| `tests/unit/simulation/components/abilities/test_warhead.py` (new) | Test | Add | 2 | `WarheadAbility` field round-trip |
| `tests/unit/simulation/components/abilities/test_laserhead.py` (new) | Test | Add | 2 | `LaserheadAbility` MRO + beam family detection + sensor stack |
| `tests/unit/simulation/components/abilities/test_ram_target.py` (new) | Test | Add | 2 | `RamTargetAbility` registration |
| `tests/unit/strategy/data/test_vehicle_bay.py` (new) | Test | Add | 3 | Load/unload, capacity, round-trip |
| `tests/unit/strategy/data/test_fleet_group_kind.py` (new) | Test | Add | 4 | `group_kind` serialisation + move rejection |
| `tests/unit/simulation/entities/test_signature_bonus.py` (new) | Test | Add | 4 | `signature_bonus` reaches `total_defense_score` |
| `tests/unit/strategy/engine/test_production_normalisation.py` (new) | Test | Add | 4 | Planet→staging vs fleet→bay paths |
| `tests/integration/test_fms_a_e2e.py` (new) | Test | Add | 5 | Phase 1–4 rollup integration |
| `docs/systems/ability_reference.md` | Docs | Edit | 5 | Add new ability surfaces |
