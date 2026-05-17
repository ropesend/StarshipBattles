# PROJ-FMS: Fighters, Mines, and Satellites — Shared Design

> **Canonical design doc** for the four-project sequence PROJ-FMS-A → PROJ-FMS-D. All four project plans reference this file.

## Context

> **Status update (2026-05-16):** The legacy `VehicleLaunchAbility`
> referenced below was removed in PROJ-FMS-C audit Fix 1. The
> replacement is `TacticalFighterLaunchAbility` (PROJ-FMS-A Phase 5),
> driven by the production-side `CarrierAIController` (PROJ-FMS-C
> audit Fix 1). All `file:line` citations in this document that point
> to since-deleted symbols are annotated inline.

The game already exposes **fighter** and **satellite** vehicle classes in the workshop ([vehicleclasses.json](../../../data/vehicleclasses.json), [vehiclelayers.json](../../../data/vehiclelayers.json)) but has no plumbing to carry, deploy, fight with, or recover them at the unit level. **Mines do not exist at all.** A tactical-only `VehicleLaunchAbility` existed at [markers.py](../../../game/simulation/components/abilities/markers.py) (removed in PROJ-FMS-C audit Fix 1) that auto-launched when a ship had a target, but there is no recovery code anywhere in the repo and nothing at the strategic layer.

This project sequence adds the three unit types end-to-end: workshop → cargo → strategic launch → sector presence → tactical participation → recovery (fighters/sats only — mines are one-way). Construction reuses the existing `SpaceShipyard` component. All deployed units visible to all empires for now; fog-of-war is later, once sensors land.

## Provenance

Design produced via a two-party inter-agent discussion between claude and codex (`AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`, consensus reached at message 5). Both agents independently produced plans and audited each other's `file:line` citations; codex's transcript with the user resolved five originally-open questions.

## Core architectural decisions

1. **Strategic map presence uses `Fleet` with a `group_kind` discriminator.** Values: `fleet | fighter_group | satellite_group | mine_group`. Non-`fleet` kinds carry a `can_strategic_move = False` invariant enforced at order validation. Inherits Fleet's existing location/owner/ship-roster/serialization/DTO/contested-hex inclusion at [`fleet.py::Fleet`](../../../game/strategy/data/fleet.py); [`fleet_dto.py::FleetInfo`](../../../game/strategy/facade/dto/fleet_dto.py); [`conflict_resolution_engine.py`](../../../game/strategy/engine/conflict_resolution_engine.py). **No parallel `global_hex_deployments` store.**
2. **Cargo / storage generalises the existing `carried_items` and `Planet.staging_yard` flows** to hold design-backed vehicles ([`ship_instance.py::ShipInstance.carried_items`](../../../game/strategy/data/ship_instance.py); [`transfer_branches.py`](../../../game/strategy/engine/order_handlers/transfer_branches.py); [`transfer_view_model.py`](../../../game/ui/screens/transfer_view_model.py)). No parallel transport concept.
3. **Production output normalisation**: planet-built fighters/satellites/mines → `Planet.staging_yard`; fleet-yard-built → carried cargo if bay capacity exists. Resolves the current colony-vs-fleet inconsistency at [`production_spawner.py`](../../../game/strategy/engine/production_spawner.py).
4. **Tactical launch deploys actual carried design instances**, not generic-class shells. Replaced the `fighter_class` string path at [`weapon_firing_system.py`](../../../game/simulation/combat/weapon_firing_system.py) (legacy `_process_hangar_launch` removed in PROJ-FMS-C audit Fix 1) and [`attack_processor.py::process_launch_attack`](../../../game/simulation/systems/attack_processor.py) (class-string branch removed in PROJ-FMS-C audit Fix 1).
5. **Construction yard**: existing `SpaceShipyard` component. No new facility.
6. **Visibility**: all deployed groups visible to all empires until a sensor / fog-of-war system lands.

## Vehicle types & component model

- **Fighters & Satellites**: reuse existing classes in `vehicleclasses.json` and `vehiclelayers.json`. Fighter layer allow-list extended to include `Warhead` and `RamTarget` for kamikaze fighter designs.
- **Mines**: new `mine_small / mine_medium / mine_large / mine_heavy` vehicle classes plus a `Mine_Standard` layer with a single CORE layer. **Component whitelist**: `Warhead`, `Laserhead`, `Hull`, `SmallTargetingSensor` (new — see below). Everything else blocked at layer validation.
- **Mine HP** comes from the slotted `Hull` component.
- **Mine class-level `signature_bonus`** feeds `total_defense_score` via [`ship_stats.py`](../../../game/simulation/entities/ship_stats.py) (`signature_bonus` aggregation block); combined with their tiny `size_score`, mines are very hard to hit by conventional weapons.
- **Mixed-design groups supported**: a `mine_group` may contain mines from multiple designs; same for `fighter_group` and `satellite_group`.

### New components / abilities

| Component | Ability class | Layer | Notes |
|---|---|---|---|
| `Warhead` | `WarheadAbility` | BOTH | Single attribute: `damage`. **Always hits when triggered** — no second accuracy roll. Damage via [`damage_calculator.py::apply_damage`](../../../game/simulation/combat/damage_calculator.py). Also placeable on fighters/ships for ramming. |
| `Laserhead` | `LaserheadAbility(BeamWeaponAbility)` | BOTH | Subclass of `BeamWeaponAbility`. Inherits beam targeting / range / hit-chance sigmoid at [`weapons.py::calculate_hit_chance`](../../../game/simulation/components/abilities/weapons.py). MRO-based lookup at [`ability_manager.py`](../../../game/simulation/components/ability_manager.py); family detection at [`weapon_registry.py`](../../../game/simulation/combat/weapon_registry.py) — both transparent to the subclass. Adds `consume_on_fire=True` honored by the tactical fire path. |
| `SmallTargetingSensor` | (uses existing `ToHitAttackModifier`) | COMBAT | New mine/small-craft sensor **without** `RequiresCommandAndControl`. The existing `mini_sensor` (in [`components.json`](../../../data/components.json)) requires C&C which crewless mines fail. Boosts laserhead hit chance via existing stat aggregator. |
| `RamTarget` | `RamTargetAbility` | COMBAT | Explicit "set ram target" action only — no collision-driven auto-detonation. On collision with the assigned target, every `Warhead` on the rammer detonates against it via the damage pipeline; rammer is destroyed. Designs without `RamTargetAbility` carry warheads inertly. |

### New storage / launch / recovery abilities

- **`VehicleBayAbility`** (STRATEGIC, additive): per-instance storage of design-backed vehicles (`design_id`, `design_data`, `current_hp`, optional `component_states`). Mass is the capacity gate. Generalises the current drop-pod-specific `carried_items`.
- **Separate ability gates per unit type**: fighters and satellites each need distinct `*BayAbility` and `Recover*Ability`. Mines need storage only — never recovered.
- **Launch families** — two parallel sets at STRATEGIC and COMBAT layers:
  - `StrategicMineLayerAbility`, `StrategicFighterLaunchAbility`, `StrategicSatelliteLaunchAbility`
  - `TacticalMineLayerAbility`, `TacticalFighterLaunchAbility`, `TacticalSatelliteLaunchAbility`
  - `RecoverFightersAbility`, `RecoverSatellitesAbility` (STRATEGIC, explicit actions only)

## Deployed group behavior

- A strategic launch creates a new `group_kind` Fleet at the launching unit's hex. Multiple groups per owner per hex permitted; no auto-merge.
- **No strategic movement** — non-fleet `group_kind` Fleets reject Move / Path orders at validation.
- **Auto-join contested-hex combat** is free via the existing conflict-resolution scan over `empire.fleets`.
- **Self-destruct**: owner-only action on `mine_group`. Selective — can target a subset.
- **Fighter wing recovery** (strategic): explicit `RecoverFightersAbility` from any friendly ship with bay space in the hex. Pre-existing groups remain unless recovered.
- **Satellite recovery** (strategic): explicit `RecoverSatellitesAbility` (separate ability gate).
- **Tactical fighter recovery**: at end-of-battle, fighters **launched during that battle** auto-reboard onto friendly bays. **Overflow becomes a new `fighter_group`** in the sector (not lost). Pre-existing groups that participated stay until explicitly recovered.

## Mine detonation math

Hooks: strategic entry via [turn_engine.py](../../../game/strategy/engine/turn_engine.py) movement phase before [conflict_resolution_engine.py](../../../game/strategy/engine/conflict_resolution_engine.py); tactical via per-tick movement loop inside [battle_engine.py](../../../game/simulation/systems/battle_engine.py).

**Warhead pass** — per-mine trigger chance reuses defensive scores; **detonation is unconditional once triggered**:

```
p_trigger = sensitivity * sigmoid(k_size * size_score(ship) - k_eva * maneuver_score(ship) - bias)
P_trigger_pass = 1 - (1 - p_trigger)^N         # N = warhead mine count
```

- Asymptotes below 1 → "never 100%, always > 0 with ≥1 mine" invariant.
- Initial constants `k_size=1.0`, `k_eva=0.5`, `bias=2.0` in `data/balance/mines.json` (new). Tunes destroyer at MED to ~5–10% per mine, dreadnought to ~25–30%.
- Sensitivity multipliers: `LOW=0.5`, `MED=1.0`, `HIGH=1.5`.
- On trigger: sample one mine uniformly, apply its `Warhead.damage` through the damage pipeline unconditionally, remove the mine.

**Laserhead pass** — each laserhead mine fires its beam at the entering ship using `BeamWeaponAbility.calculate_hit_chance()`. `SmallTargetingSensor`'s `ToHitAttackModifier` flows through the existing stat aggregator.

- **Continuous threshold gate**: the minefield is configured with `expected_hit_chance_threshold` X (slider, per-field). A laserhead fires only if computed `expected_hit_chance >= X`. Deterministic gate before the standard beam roll. **Not** a size gate, **not** a range gate, **not** a second random-fire probability.
- Consumed regardless of hit / miss after firing.

**Per ship**: each entering enemy ship runs both passes in fleet-entry order; consumed mines unavailable to subsequent ships.

**Friendly fire**: hard rule — not enabled. Mines only roll against enemies.

## Sector scatter

- When a tactical battle map exists for the hex, mines scatter uniformly within that boundary.
- Otherwise, fall back to a fixed deployment-circle radius defined in `data/balance/mines.json`.
- Scatter coords are stored on the `mine_group` Fleet at strategic-launch time so subsequent tactical battles in the hex reuse the same layout. PRNG-deterministic via empire/launch seed.

## Project sequence

| Project | Folder | Scope |
|---|---|---|
| PROJ-FMS-A | `Projects/active_projects/PROJ-FMS-A/` | Foundation — data, components, abilities skeletons, `group_kind`, VehicleBay, production normalisation |
| PROJ-FMS-B | `Projects/active_projects/PROJ-FMS-B/` | Mines end-to-end — strategic+tactical layers, warhead/laserhead behavior, ramming, scatter, sensitivity UI, self-destruct |
| PROJ-FMS-C | `Projects/active_projects/PROJ-FMS-C/` | Fighters end-to-end — design-instance tactical launch, sector wings, recovery, end-of-battle reboard, AI |
| PROJ-FMS-D | `Projects/active_projects/PROJ-FMS-D/` | Satellites end-to-end — stationary tactical AI, separate recovery gate |

Each project ships independently testable behavior. PROJ-FMS-B depends on PROJ-FMS-A; PROJ-FMS-C and PROJ-FMS-D both depend on PROJ-FMS-A but are otherwise independent of each other and of PROJ-FMS-B (fighter/sat work doesn't touch mine code).

## Critical files to modify (by project)

### PROJ-FMS-A (Foundation)
- `data/vehicleclasses.json`, `data/vehiclelayers.json` — mine classes + `Mine_Standard` layer + whitelist + `signature_bonus`
- `data/components.json` — `Warhead`, `Laserhead`, `SmallTargetingSensor`, `RamTarget` definitions
- `game/simulation/components/abilities/__init__.py` — register new abilities
- `game/simulation/components/abilities/markers.py` — refactor `VehicleLaunchAbility`; add new launch families (skeleton)
- `game/simulation/components/abilities/cargo.py` (or new file) — `VehicleBayAbility`
- `game/strategy/data/ship_instance.py::ShipInstance.carried_items` — typed `carried_items` extension or replacement
- `game/strategy/data/ship_cargo_manager.py` — `load_vehicle()`, `unload_vehicle()`
- `game/strategy/data/fleet.py::Fleet` — `group_kind` field + order-validation hook
- `game/simulation/entities/ship_stats.py` — `signature_bonus` wiring (aggregation block)
- `game/strategy/engine/production_spawner.py` — output normalisation
- `game/strategy/engine/order_handlers/transfer_branches.py` — generalise staging transfer
- `game/ui/screens/transfer_view_model.py` — generic carried-vehicle DTO rows
- `game/strategy/facade/dto/fleet_dto.py::FleetInfo` — DTO surface for carried vehicles + `group_kind`

### PROJ-FMS-B (Mines)
- `data/balance/mines.json` — new
- `game/simulation/components/abilities/weapons.py` — `LaserheadAbility(BeamWeaponAbility)` (or new file under `abilities/`)
- `game/simulation/components/abilities/` — `WarheadAbility`, `RamTargetAbility` behavior
- `game/strategy/engine/minefield_resolver.py` — new
- `game/strategy/engine/turn_engine.py` — wire mine resolver into movement phase before conflict detection
- `game/simulation/systems/battle_engine.py` — per-tick mine proximity + laserhead range trigger
- `game/simulation/combat/damage_calculator.py` — reused as-is
- `game/ui/...` — sensitivity slider + threshold slider + self-destruct UI action (paths TBD during PROJ-FMS-B planning)

### PROJ-FMS-C (Fighters)
- `game/simulation/combat/weapon_firing_system.py` — legacy `_process_hangar_launch` auto-launch path removed in PROJ-FMS-C audit Fix 1; replaced with design-instance deploy via `BattleEngine.launch_fighters_in_battle`
- `game/simulation/systems/attack_processor.py::process_launch_attack` — accepts design-instance payload (`carried_vehicle`); class-string branch removed in PROJ-FMS-C audit Fix 1
- `game/simulation/systems/battle_engine.py` — end-of-battle reboard + overflow-to-sector-group hook
- `game/strategy/engine/conflict_resolution_engine.py` — confirm fighter_group inclusion in combat manifest (free if group_kind already a Fleet kind)
- `game/simulation/entities/stat_contributors/launch.py::contribute_vehicle_launch` — updated for new ability shape
- `game/ai/controller.py` — minimal "target nearest enemy" fighter AI

### PROJ-FMS-D (Satellites)
- Same shape as PROJ-FMS-C with stationary AI ([`game/ai/controller.py::AIController`](../../../game/ai/controller.py) short-circuits Satellite-type ships)
- Separate `*BayAbility` / `Recover*Ability` ability gates from fighters

## Verification (per project)

- Sharded test runner: `python Tools/test_sharded/test_sharded.py`
- Targeted: `pytest tests/path/to/test.py -k test_name`
- Combat lab smoke: `python -m combat_lab.run_tests`

Per-project E2E gameplay smoke:
1. Design a mine / fighter / satellite in the workshop, save the design.
2. Build it at a `SpaceShipyard`-equipped ship or planet.
3. Verify it appears in a ship's `VehicleBay` or `Planet.staging_yard`.
4. Strategic-launch into a hex.
5. Move an enemy fleet through (or trigger combat in the hex):
   - mines: confirm damage applied via combat events; mine count decremented; `P_trigger < 1`.
   - fighters/sats: confirm they auto-join the next tactical battle on the owner's side.
6. Recover survivors via the strategic recovery action; verify HP persists.
7. Self-destruct a minefield (selective); verify removal from `mine_group`.

## Decision: `IIssuerAdapter` is the canonical issuer-polymorphism seam (QA Observation B)

The five FMS order handlers (`LayMines`, `LaunchFighters`,
`LaunchSatellites`, `RecoverFighters`, `RecoverSatellites`) were widened
to accept BOTH fleet ships AND planetary-complex facilities as the
issuer. Rather than fork each handler into parallel
`*_fleet` / `*_planet` codepaths permanently, we introduced
[`game/strategy/engine/issuer_adapter.py`](../../../game/strategy/engine/issuer_adapter.py)
as the polymorphic interface — `FleetShipIssuerAdapter` wraps
`(Fleet, ShipInstance)` against `ship.carried_items`;
`PlanetStagingYardIssuerAdapter` wraps a `Planet` against
`planet.staging_yard`. Order handlers (`*OrderHandler.execute_for_issuer`)
operate on the protocol surface (`location`, `owner_id`, `display_label`,
`pop_carried`, `count_carried`, `append_carried`, `append_recovered`)
so the same launch / recovery body runs for both issuer kinds.

Implication for future issuer types (e.g. orbital platforms, free-floating
stations): add a new `IIssuerAdapter` implementation, expose the same
surface, and route the relevant Issue*Command branch through the adapter.
Do NOT widen the handler's `_execute_fleet` / `_execute_planet` switch
further.

UI parity: both the fleet right-click menu
([`fleet_menu_items.build_menu_items`](../../../game/ui/screens/fleet_menu_items.py))
and the planet right-click menu
([`planet_menu_items.build_menu_items`](../../../game/ui/screens/planet_menu_items.py))
emit the same five FMS rows when capability gates pass; the FMS rows
carry a `callback` rather than an `InputAction` because there is no
keyboard surface for them today. Callback builders live in
[`fms_menu_callbacks.py`](../../../game/ui/screens/fms_menu_callbacks.py).

