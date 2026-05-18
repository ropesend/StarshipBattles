# PROJ-FMS-A Decisions Log

Project-local decisions made during foundation implementation. Cross-project decisions live in [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md).

## 2026-05-15 — Project scaffolded

Source: claude/codex inter-agent discussion at `AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`, consensus reached at message 5, plan revision `merged_plan_r003.md`.

All design decisions resolved in the discussion are recorded in the shared design doc. This file accumulates any *implementation-time* decisions that don't fit the design doc (e.g., concrete tier values, file-layout choices, refactor scopes).

## Implementation decisions

### Phase 1 (Data — mine classes, layer, components)

- **Mine tiers and masses**: small=5, medium=15, large=40, heavy=100 (per spec).
  Each mine tier has `signature_bonus=3.0` as the recommended starting value.
- **Mine_Standard layer**: single CORE layer, mass_pct=1.0, whitelist via
  `allow_ability:` for `Warhead`, `Laserhead`, `StructuralIntegrity`,
  `ToHitAttackModifier`. No fighter "kamikaze allowlist" needed at the layer
  level — `Warhead` and `RamTarget` carry `Fighter` in their per-component
  `allowed_vehicle_types`.
- **Warhead component tiers**: small (mass 2, damage 50), medium (mass 6,
  damage 200), large (mass 18, damage 800). Quadratic-ish damage scaling.
- **Laserhead component tiers**: small/medium/large mirroring warhead masses;
  damage 30/120/480, range 600/900/1200, falloff 0.002/0.0015/0.001. Each
  carries `consume_on_fire: true`. Inherits all `BeamWeaponAbility` attrs
  through MRO; subclass adds the consume flag only.
- **SmallTargetingSensor tiers**: two tiers (basic = +0.3 ToHit, advanced =
  +0.6). NO `RequiresCommandAndControl` — that's the purpose of this new
  component vs the existing `mini_sensor`. `mini_sensor` is unchanged.
- **RamTarget**: single tier, mass 1, allowed on Fighter and Ship.
- **Mine hulls**: 4 tiers carrying `StructuralIntegrity: true` only (no
  C&C / combat-movement requirement — mines are crewless).
- **Build-path plumbing**: added `"mine"` to `build_queue_controller`
  category map, `build_queue_panel_factory` (new `btn_category_mine` slot
  + tuple shape bump), `build_queue_screen.py` handler, `build_context.py`,
  `planet_query_service.can_build_type()`, and
  `fleet_capability_calculator.can_build_type()`. Mine portrait color
  reuses `VEHICLE_FIGHTER` (visual grouping with small craft).
- **Design roles**: added `general_purpose` `Mine` filter, plus two new
  mine-only roles (`mine_warhead`, `mine_laserhead`).

### Phase 2 (Abilities — Warhead, Laserhead, RamTarget)

- **File location**: new `warhead.py` module under
  `game/simulation/components/abilities/`. Keeps `weapons.py` under the
  500-LOC ceiling and consolidates all three mine-specific abilities in
  one discoverable file.
- **WarheadAbility**: `AbilityLayer.BOTH`. Single `damage` attribute.
  No `apply()` method (base class has no such method). Behavior wires
  into PROJ-FMS-B Phase 3 mine resolver + ram pipeline.
- **LaserheadAbility(BeamWeaponAbility)**: subclasses BeamWeaponAbility
  so `isinstance` checks and the MRO-based family detection at
  `weapon_registry.py:78-94` work transparently. Adds `consume_on_fire`
  (bool, default True).
- **RamTargetAbility**: `AbilityLayer.COMBAT`. Single `target_id` runtime
  field (None until combat engine assigns). No serialization needed —
  combat-only state.
- **SmallTargetingSensor**: no new ability class. The component carries
  the existing `ToHitAttackModifier` ability, which already flows through
  the stat aggregator. The "no C&C requirement" point lives in the
  component data, not the ability.

### Phase 3 (VehicleBay substrate)

- **CarriedVehicle dataclass**: new `game/strategy/data/carried_vehicle.py`.
  Six fields (design_id, design_data, vehicle_type, mass, current_hp,
  component_states). Vehicle_type validated to one of mine/fighter/satellite.
  `from_any()` distinguishes CarriedVehicle-shaped dicts from drop-pod
  dicts so the cargo manager can coexist with the existing pod path.
- **VehicleBayAbility**: new `vehicle_bay.py`. `AbilityLayer.STRATEGIC`.
  Two attributes: `capacity_mass` (int) and `allowed_types` (defaults to
  all three small-craft kinds). Designed to be additive across components.
- **carried_items vs new field**: kept the existing
  `ShipInstance.carried_items: List[Dict[str, Any]]` field; entries can
  now be either drop-pod-shaped or CarriedVehicle-serialized dicts.
  This avoids a parallel `carried_vehicles` field and lets the existing
  fleet save/load path round-trip CarriedVehicle entries without a schema
  change. Helpers on the cargo manager filter by `from_any()`.
- **ShipCargoManager helpers**: `load_vehicle`, `unload_vehicle`,
  `get_vehicle_bay_capacity`, `can_accept_vehicle`, `get_carried_vehicles`,
  `get_carried_vehicles_by_type`. The bay-capacity lookup uses the cached
  stats path (`bay_capacity_mass` added to `calculate_design_stats`
  output) so the cargo manager doesn't have to materialize a live Ship.
- **Bay components**: 3 tiers (small=200/250-mass-cap, medium=500/750-cap,
  large=1200/2000-cap) on Ship/Planetary Complex.
- **transfer_branches.py**: added `_dispatch_carried_vehicle_load` and
  `_dispatch_carried_vehicle_unload` branches; `transfer.py` routes
  `cargo_type == "vehicle"` to them. Drop-pod path untouched.
- **transfer_view_model**: extended `_build_pod_rows` to emit
  `vehicle:<name>` cargo_keys for CarriedVehicle entries (vs
  `drop_pod:<name>` for the legacy path). Single-pass over the existing
  carried_items_summary tuple.
- **FleetInfo DTO**: added `carried_vehicles_by_type`,
  `vehicle_bay_capacity_used/max`, `group_kind` fields. Defensive
  capacity sum tolerates mocked fleets used in older tests.

### Phase 4 (group_kind + signature_bonus + production normalisation)

- **Fleet.group_kind**: new init parameter, default "fleet". Valid values
  rejected at construction time. Serialised through `to_dict`/`from_dict`;
  legacy saves missing the field default to "fleet" (no migration).
- **can_strategic_move**: simple property returning
  `group_kind == "fleet"`.
- **Command-validation invariant**: new
  `BaseCommandHandler._reject_if_non_fleet_group` helper; called from
  Move / Intercept / Join / Warp / Build handlers. Helper is resilient
  to mocked fleets (group_kind set to a Mock) — only string values in
  the recognised set trigger rejection; otherwise treats as real fleet.
- **signature_bonus**: read from `vehicle_classes[ship_class]` in
  `ship_stats._phase_sensor_defense_scores`. Defaults to 0.0 (no change
  for ships/fighters/satellites). Added to `total_defense_score`
  alongside size/maneuver/ecm.
- **Production normalisation**: planet-built mine/fighter/satellite
  routed through `_spawn_to_staging_yard` (existing path; extended to
  include "mine" and "satellite"). Fleet-built mine/fighter/satellite
  routed through new `_spawn_fleet_carried_vehicle` method. Bay
  selection: flagship first (fleet.ships[0]), then canonical fleet
  order. If no bay accepts, production output is logged + an event
  emitted with the "no bay capacity" message — the queue item is
  still consumed (no resource refund — matches the existing "build
  failed" semantics for planet staging overflow).
- **CarriedVehicle current_hp at production**: planet-built small craft
  get `current_hp = max_hp` from `calculate_design_stats`. Fleet-built
  same.

### Phase 5 (Launch / recover skeletons + OrderType reservations)

_(see Phase 5 implementation notes)_

## 2026-05-16 — Audit fix pass

Codex audited the just-completed PROJ-FMS-A implementation
(`AgentCoordination/Scratchpad/Consult/20260516T060235Z_proj-fms-a-audit/response.md`)
and surfaced one P1 blocker plus three P2 follow-ups. The fixes were
applied on top of the existing PROJ-FMS-A working tree without
reverting any earlier work.

### Fix 1 (P1) — `cargo_type="vehicle"` was unreachable

- **Root cause:** `transfer.py:138` already routed `vehicle` past
  `skip_location_check`, but `TransferValidator.VALID_CARGO_TYPES` did
  not contain `"vehicle"`. Every order with `cargo_type="vehicle"`
  failed validation with `INVALID_CARGO_TYPE` before reaching the
  `_dispatch_carried_vehicle_*` branches.
- **Fix:** added `"vehicle"` to `VALID_CARGO_TYPES`, mirrored the
  drop-pod handling in the `NOT_COLONIZED` planet check, and added
  two new validators: `TransferValidator._validate_vehicle_load`
  (planet → fleet) and `TransferValidator._validate_vehicle_unload`
  (fleet → planet). The load validator requires at least one
  matching `CarriedVehicle`-shaped entry in the planet staging yard
  and at least one ship with `VehicleBay` capacity for it. The
  unload validator requires at least one matching carried vehicle on
  the fleet and pre-checks the planet's `max_staging_mass`.
- **New error codes:** `NO_STAGING_VEHICLE`, `NO_BAY_CAPACITY`,
  `NO_STAGING_CAPACITY` (last one fires for full staging yards).
- **Tests:** unit coverage in
  `tests/unit/strategy/data/test_fms_a_audit_fixes.py::TestTransferValidatorAcceptsVehicleCargoType`;
  full TransferHandler end-to-end (load + unload) in
  `tests/integration/test_fms_a_e2e.py::TestTransferHandlerVehicleE2E`.

### Fix 2 (P2) — Pod-storage / vehicle-bay cross-bleed

- **Root cause:** `ShipInstance.get_pod_storage_used()` summed every
  `carried_items` entry. Once PROJ-FMS-A allowed `CarriedVehicle`-
  shaped entries into the same list, a ship carrying fighters/
  mines/satellites lost valid drop-pod capacity and
  `can_carry_pod(...)` failed for the wrong reason. The drop-pod
  transfer branches had the symmetric problem (they'd try to unload
  CarriedVehicle entries to the staging yard as if they were pods,
  or count them in the `to_unload` total).
- **Fix:** `get_pod_storage_used()` now filters out
  `CarriedVehicle.from_any(item) is not None` entries. The
  `_dispatch_drop_pod_load` and `_dispatch_drop_pod_unload`
  branches in `transfer_branches.py` also skip CarriedVehicle-
  shaped entries so the two paths are fully disjoint. The bay-side
  accounting in `ShipCargoManager.get_vehicle_bay_capacity()`
  already filtered correctly via `CarriedVehicle.from_any`; no
  change needed there.
- **Tests:** unit coverage in
  `TestPodStorageBleedRegression` — a ship with 2 drop pods + 3
  fighters reports pod_storage_used = 18 (drop-pod masses only) and
  bay_current_mass = 75 (fighter masses only).

### Fix 3 (P2) — Capability/UI did not gate on `group_kind`

- **Root cause:** handler-side rejection via
  `BaseCommandHandler._reject_if_non_fleet_group` worked, but
  `FleetCapabilityCalculator` and `fleet_menu_items.py` still
  reported "yes you can move/build/warp" for non-`fleet`
  `group_kind` Fleets. When PROJ-FMS-B/C/D start creating
  `fighter_group` / `satellite_group` / `mine_group` Fleets, the UI
  would advertise actions that fail at execution.
- **Fix:** added a `FleetCapabilityCalculator._is_real_fleet()`
  predicate (`group_kind == "fleet"`, resilient to Mock fleets) and
  gated `has_space_shipyard`, `can_build_type`, and `can_use_warp`
  through it. Added `_can_strategic_move()` to
  `fleet_menu_items.py` so the Move and Join Fleet menu rows are
  omitted entirely for non-fleet groups.
- **Tests:** unit coverage in
  `TestCapabilityCalculatorGatesOnGroupKind` (parametrised across
  `fighter_group` / `satellite_group` / `mine_group` for warp,
  build, and shipyard) and
  `TestFleetMenuItemsGateOnGroupKind`.

### Fix 4 (P2) — Artifact accuracy + missing tests

- **`bay_current_mass` is not a design stat.** The original
  implementation reset `ship.bay_current_mass = 0.0` in
  `ship_stats.py` and added a stat contributor for
  `bay_capacity_mass`, but `bay_current_mass` was never written
  anywhere — it can't be, because it depends on the runtime
  contents of `ShipInstance.carried_items`, which the simulation
  Ship cannot see. **Root-cause fix:** dropped the dead
  `ship.bay_current_mass = 0.0` reset from the simulation Ship and
  exposed two clean strategy-layer properties on `ShipInstance`:
  `bay_capacity_mass` (delegates to the cached
  `bay_capacity_mass` design stat) and `bay_current_mass`
  (delegates to `ShipCargoManager.get_vehicle_bay_capacity()`).
- **Carried-vehicle serializer round-trip test added.** See
  `TestCarriedVehicleSerializerRoundtrip`: mixes drop-pod and
  CarriedVehicle entries, runs them through
  `ShipInstanceSerializer.to_dict` / `from_dict`, and asserts the
  CarriedVehicle entries come back with `design_id`, `current_hp`,
  `mass`, `vehicle_type`, and `design_data` intact, alongside the
  preserved drop-pod entry.
- **Phase-5 end-to-end transfer-order test added.** See
  `TestTransferHandlerVehicleE2E` in
  `tests/integration/test_fms_a_e2e.py`.
- **Checklist corrections.** `phase_3_checklist.md` line 21 and
  `phase_5_checklist.md` task on transfer-order coverage were
  amended with explicit notes pointing to the new tests and
  describing the corrected approach.

