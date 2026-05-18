# PROJ-FMS-A Design — Foundation slice

This project's slice of the shared design. **See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the canonical, end-to-end design.** Only PROJ-FMS-A-specific notes go here.

## In scope
- Vehicle classes: mines (new) + minor allow-list extensions on fighters.
- Layers: `Mine_Standard` (new).
- Components: `Warhead`, `Laserhead`, `SmallTargetingSensor`, `RamTarget` (new); `vehicle_bay_*` and launch/recovery components (new).
- Abilities: `WarheadAbility`, `LaserheadAbility(BeamWeaponAbility)`, `RamTargetAbility`, `VehicleBayAbility` (new behavior); six launch + two recovery skeletons (no behavior).
- Strategic state: `group_kind` field on `Fleet` with `can_strategic_move` invariant.
- Defense calc: `signature_bonus` aggregation into `total_defense_score`.
- Production: planet→staging vs fleet→bay normalisation.
- Storage: generalise `carried_items` / `Planet.staging_yard` to hold design-backed `CarriedVehicle`.

## Out of scope
- Any launch behavior (the six launch abilities raise `NotImplementedError` until PROJ-FMS-B/C/D).
- Mine detonation math, ramming behavior, sector scatter — all PROJ-FMS-B.
- Tactical AI for fighters/sats — PROJ-FMS-C/D.
- UI for sensitivity sliders, self-destruct, recovery actions — those land in the project that owns the corresponding behavior.

## Key risks
- **Backwards compatibility of `carried_items`**: existing drop-pod transfers must keep working through the generalisation. Strategy: keep `carried_items` shape permissive (Dict-shaped entries with a `vehicle_type` discriminator) and add the typed `CarriedVehicle` helpers around it. Migrate drop-pod call sites only if it's cheap.
- **`group_kind` propagation**: many places in the codebase iterate `empire.fleets` assuming every fleet has movement and crew. Defensive guards in capability calculators are required.
- **Production normalisation regression**: changing the spawner output target could break existing save files mid-flight. Strategy: explicitly inspect colony/fleet/satellite paths at [`production_spawner.py:107-117`](../../../game/strategy/engine/production_spawner.py#L107) before refactoring; add migration tests against existing saves if needed.
- **Sensor C&C**: `SmallTargetingSensor` must explicitly NOT carry `RequiresCommandAndControl` or mines will fail the C&C gate.

## Open implementation choices (Phase 1 owners decide)
- Concrete `signature_bonus` value per mine size — design doc proposes +3 but values to be confirmed during balance pass.
- Tier values for `Warhead.damage` and `Laserhead.<beam attrs>` — initial values can be placeholder; final balance in PROJ-FMS-B.
- Whether to add `carried_vehicles: List[CarriedVehicle]` as a sibling field or to migrate `carried_items` entirely. Phase 3 decides based on the call-site count for `carried_items`.
