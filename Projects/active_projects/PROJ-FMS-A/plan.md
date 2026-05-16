# PROJ-FMS-A: Fighters/Mines/Satellites — Foundation (2026-05-15)

> **WORKING ON THIS PROJECT:**
> - Read [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the full design rationale
> - Open the phase checklist for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data: mine vehicle classes, layer, components | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Abilities: Warhead / Laserhead / Sensor / Ram | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. VehicleBay substrate + carried_items generalisation | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fleet `group_kind` + signature_bonus + production normalisation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Launch/recover ability skeletons + tests | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-15
**Active Phase:** All 5 phases complete; ready for PROJ-FMS-B handoff
**Last Action:** Phase 5 — launch/recovery skeletons + OrderType reservations + integration tests + ability_reference.md docs update
**Next Action:** Hand off to PROJ-FMS-B (mine end-to-end). All foundation plumbing in place.
**Blockers:** None. Pre-existing test failures on main (6 errors + 1 ship_instance_damage flake + 5 quickstart metadata + 3 ship_stats_golden) are unchanged by FMS-A.

## Overview
Foundation phase for the four-project Fighters/Mines/Satellites sequence. Establishes the data, components, abilities, and storage substrate that PROJ-FMS-B/C/D all build on. **No user-facing behavior in this project** — everything is plumbing.

## Goals
- Define mine vehicle classes + `Mine_Standard` layer with strict component whitelist.
- Add `Warhead`, `Laserhead`, `SmallTargetingSensor`, `RamTarget` components and ability classes (`LaserheadAbility` subclasses `BeamWeaponAbility`).
- Wire `signature_bonus` from vehicle-class data into `total_defense_score`.
- Add `VehicleBayAbility` + per-instance `CarriedVehicle` dataclass; generalise existing `carried_items` to hold design-backed vehicles.
- Add `group_kind` discriminator to `Fleet` + order-validation rejection of strategic moves for non-fleet kinds.
- Normalise production output: planet → `Planet.staging_yard`; fleet-yard → bay if capacity.
- Register empty skeletons for the six strategic/tactical launch abilities + two recovery abilities — behavior fills in PROJ-FMS-B/C/D.

## Scope
**In:** data + components + abilities + storage substrate + Fleet discriminator + production normalisation. Empty-skeleton launch/recover abilities (registration only).
**Out:** any user-facing behavior — mine detonation, fighter launch, satellite recovery. Those land in PROJ-FMS-B/C/D respectively.

## Key Files
See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md#proj-fms-a-foundation) "Critical files to modify (PROJ-FMS-A)" section. Summary:

| File | Type | Action |
|------|------|--------|
| `data/vehicleclasses.json` | Data | Add 3–4 mine size tiers |
| `data/vehiclelayers.json` | Data | Add `Mine_Standard` layer + extend `Fighter_Standard` allow-list |
| `data/components.json` | Data | Add `Warhead`, `Laserhead`, `SmallTargetingSensor`, `RamTarget` |
| `game/simulation/components/abilities/__init__.py` | Production | Register new ability classes |
| `game/simulation/components/abilities/markers.py` | Production | Refactor `VehicleLaunchAbility`; add launch ability skeletons |
| `game/simulation/components/abilities/cargo.py` or new file | Production | `VehicleBayAbility` |
| `game/strategy/data/ship_instance.py:135-136` | Production | Typed `carried_items` for vehicles |
| `game/strategy/data/ship_cargo_manager.py` | Production | `load_vehicle()`, `unload_vehicle()` |
| `game/strategy/data/fleet.py:39-93` | Production | `group_kind` field + order-validation hook |
| `game/simulation/entities/ship_stats.py:424-444` | Production | Wire `signature_bonus` into `total_defense_score` |
| `game/strategy/engine/production_spawner.py:107-117` | Production | Output normalisation |
| `game/strategy/engine/order_handlers/transfer_branches.py:128-281` | Production | Generalise staging transfer |
| `game/ui/screens/transfer_view_model.py:264-303` | Production | Generic carried-vehicle DTO rows |
| `game/strategy/facade/dto/fleet_dto.py:96-100,187-218` | Production | DTO surface for `group_kind` + vehicles |

## Phases

### Phase 1: Data — mine vehicle classes + layer + components
Add the data definitions that the workshop validates against. No code yet.

### Phase 2: Abilities — Warhead / Laserhead / SmallTargetingSensor / RamTarget
Define the ability classes (`WarheadAbility`, `LaserheadAbility(BeamWeaponAbility)`, `RamTargetAbility`; `SmallTargetingSensor` reuses existing `ToHitAttackModifier`). Register. Implement no behavior — that's PROJ-FMS-B.

### Phase 3: VehicleBay substrate
`VehicleBayAbility` + `CarriedVehicle` dataclass. Generalise `ShipInstance.carried_items` and `ShipCargoManager` load/unload to handle design-backed vehicles. DTO updates for UI surface.

### Phase 4: Fleet `group_kind` + signature_bonus + production normalisation
Add `group_kind` to `Fleet` with order-validation invariant. Wire vehicle-class `signature_bonus` into defense score aggregation. Normalise production output across planet vs fleet-yard paths.

### Phase 5: Launch/recover ability skeletons + tests
Register empty `Strategic*LaunchAbility` / `Tactical*LaunchAbility` / `Recover*Ability` classes (six launch + two recovery). Skeleton must validate as a component but raise on `apply()`. Full test coverage on Phases 1–4.

## Related Documents
- [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) — canonical design
- Discussion: `AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`
- Sibling projects: [PROJ-FMS-B](../PROJ-FMS-B/), [PROJ-FMS-C](../PROJ-FMS-C/), [PROJ-FMS-D](../PROJ-FMS-D/)
