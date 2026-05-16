# PROJ-FMS-A Phase 1: Data — mine vehicle classes + layer + components

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Add data definitions for mines and the four new components. No code, no behavior — just data and schema. Workshop should reject invalid mine designs at validation time after this phase.

## Tasks

### Vehicle classes
- [x] Add `mine_small`, `mine_medium`, `mine_large`, `mine_heavy` to [`data/vehicleclasses.json`](../../../data/vehicleclasses.json). Approximate masses 5 / 15 / 40 / 100.
- [x] Each mine class includes `signature_bonus` field (suggested initial value +3, tunable later) feeding `total_defense_score` via PROJ-FMS-A Phase 4.
- [x] Mine classes set `type: "Mine"` (new value).

### Layer
- [x] Add `Mine_Standard` layer config to [`data/vehiclelayers.json`](../../../data/vehiclelayers.json). Single CORE layer.
- [x] **Component whitelist mechanism**: the validator supports `block_classification`, `block_id`, `deny_ability`, `allow_classification`, `allow_id`, `allow_ability` ([`ship_validator.py:27-37`](../../../game/simulation/validation/ship_validator.py#L27)). The `major_classification` values used in [`data/components.json`](../../../data/components.json) are coarse (`Weapons`, `Sensors`, `Special`, `Crewsupport`, …), so `allow_classification` is not granular enough for the mine whitelist. Use `allow_ability` instead, listing the ability keys each whitelisted component carries:
  - `allow_ability:Warhead` (Warhead components)
  - `allow_ability:Laserhead` (Laserhead components)
  - `allow_ability:StructuralIntegrity` (Hull components — confirm this is the ability key Hull components actually carry; if not, use the ability key Hull carries today)
  - `allow_ability:ToHitAttackModifier` (SmallTargetingSensor components)
- [x] Mass budget for CORE = 100% of vehicle mass.
- [x] Map `mine_*` vehicle classes to `Mine_Standard` layer.
- [x] Vehicle-type compatibility for new components is enforced via each component's `allowed_vehicle_types` field (see [`ship_validator.py:65-67`](../../../game/simulation/validation/ship_validator.py#L65)). For kamikaze fighter designs, ensure `Warhead` and `RamTarget` component definitions list `"Fighter"` in their `allowed_vehicle_types`. There is no `Fighter_Standard` allow-list mechanism — per-component vehicle-type compatibility is the component's own `allowed_vehicle_types` field.

### Components
- [x] Add `Warhead` component to [`data/components.json`](../../../data/components.json) in 3 tier sizes (e.g., `warhead_small`, `warhead_medium`, `warhead_large`). Each carries `type: "Warhead"`, `mass` per tier, `damage` per tier, `allowed_vehicle_types: ["Mine", "Fighter", "Ship"]`, `abilities: {"Warhead": {"damage": <value>}}`, `major_classification: "Weapons"`.
- [x] Add `Laserhead` component in 3 tier sizes (e.g., `laserhead_small`, `laserhead_medium`, `laserhead_large`). Carries `abilities: {"Laserhead": {<beam attrs>, "consume_on_fire": true}}`. Inherits all `BeamWeaponAbility` attrs (range, damage, accuracy, falloff). `allowed_vehicle_types: ["Mine"]`. `major_classification: "Weapons"`.
- [x] Add `SmallTargetingSensor` component (1–2 tiers). Type `"Sensor"`, `abilities: {"ToHitAttackModifier": {"value": ..., "stack_group": "Sensor"}}`. **Must NOT carry `RequiresCommandAndControl`** — that's the whole point of the new component. `allowed_vehicle_types: ["Mine", "Fighter"]`. `major_classification: "Sensors"`.
- [x] Add `RamTarget` component (single tier). Type `"RamTarget"`, `abilities: {"RamTarget": {}}`. `allowed_vehicle_types: ["Fighter", "Ship"]`. `major_classification: "Special"` (or appropriate existing classification — see [`docs/01_ARCHITECTURE.md`](../../../docs/01_ARCHITECTURE.md) and [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md), or the existing `major_classification` values used in [`data/components.json`](../../../data/components.json), for the taxonomy).

### Mine build-path / workshop / yard plumbing

The build queue, planet build context, fleet capability calculator, and design-role data all currently allow `complex | ship | satellite | fighter | drop_pod` and do not know about `mine`. Without these updates mines will be designable in the workshop but not constructible through the existing yard / build-queue UI.

- [x] Add `"mine"` to the build-queue category map in [`game/ui/panels/build_queue_controller.py:158-164`](../../../game/ui/panels/build_queue_controller.py#L158) (`"mine": "Mine"`).
- [x] Add `btn_category_mine` to the category panel in [`game/ui/screens/build_queue_panel_factory.py:448-531`](../../../game/ui/screens/build_queue_panel_factory.py#L448) — this is where category buttons are **actually created** (the screen file only wires handlers). Extend the returned tuple to include `btn_mine` (note: this is a tuple-shape change; callers must update). Add the button geometry slot below `btn_drop_pod` and bump `set_scrollable_area_dimensions` accordingly.
- [x] Update the `BuildQueuePanels` shape (wherever the panel factory's return tuple is consumed) so the new `btn_mine` is held and exposed.
- [x] Wire the Mines button handler in [`game/ui/screens/build_queue_screen.py:655-662`](../../../game/ui/screens/build_queue_screen.py#L655) alongside Ships / Fighters / Satellites / Complex / Drop Pods handlers.
- [x] Add a mine placeholder portrait color in [`game/ui/panels/build_queue_portraits.py:57-64`](../../../game/ui/panels/build_queue_portraits.py#L57) `VEHICLE_TYPE_COLORS` — `'mine': <appropriate color constant>`. Pick a constant analogous to `VEHICLE_FIGHTER` for visual consistency.
- [x] Extend [`game/strategy/data/build_context.py:51-61`](../../../game/strategy/data/build_context.py#L51) `BuildContext.can_build_type()` docstring + signature to include `"mine"`.
- [x] Update [`game/strategy/services/planet_query_service.py:71-81`](../../../game/strategy/services/planet_query_service.py#L71) `can_build_type()` to allow `"mine"` for planets with shipyard capacity (mirrors existing fighter/satellite rule).
- [x] Update [`game/strategy/data/fleet_capability_calculator.py:126-148`](../../../game/strategy/data/fleet_capability_calculator.py#L126) `can_build_type()` to allow `"mine"` for fleets with `SpaceShipyard` capacity.
- [x] Add mine entries to [`data/design_roles.json`](../../../data/design_roles.json) with `vehicle_type_filter: ["Mine"]` so the design-role classifier knows about mine designs (mirror the Fighter / Satellite role entries).
- [x] Tests: `pytest tests/unit/strategy -k 'build or can_build_type'` — the existing tests for fighter/satellite build should not regress; add equivalent assertions for the `"mine"` category.

### Tests
- [x] Add tests under `tests/data/` or equivalent that:
  - Load every mine vehicle class and verify it parses.
  - Design a mine with each allowed component → validates.
  - Design a mine with a forbidden component (e.g., `Engine`) → fails validation with a clear error.
  - Design a fighter with `Warhead` + `RamTarget` → validates (after layer allow-list extension).
- [x] Verify `mini_sensor` still has `RequiresCommandAndControl: true` (unchanged) and the new `SmallTargetingSensor` does not.

## Verification
- `pytest tests/data/ -k mine` (or whatever paths get added)
- `python Tools/test_sharded/test_sharded.py` — must pass after this phase.
- Spot-check by opening the design workshop in dev mode if available and trying to design a mine; the four allowed components should appear, others should not.

## Exit criteria
- Mine vehicle classes load, layer enforces whitelist, all four components are designable on appropriate vehicle types, tests green.
- No code-side behavior wired in yet (ability classes are added in Phase 2; behavior in PROJ-FMS-B).
