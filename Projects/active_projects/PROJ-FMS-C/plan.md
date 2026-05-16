# PROJ-FMS-C: Fighters/Mines/Satellites — Fighters End-to-End (2026-05-15)

> **WORKING ON THIS PROJECT:**
> - Read [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design rationale.
> - Open the phase checklist for your current phase.
> - Check off tasks as you complete them.
> - Update Current State before stopping work.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Strategic + tactical fighter launch (design-instance based) | Not started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Deployed wing combat join + fighter AI | Not started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Recovery + end-of-battle reboard | Not started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration tests + E2E gameplay smoke | Not started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-15
**Active Phase:** Phase 1 (blocked on PROJ-FMS-A)
**Last Action:** Project scaffolded
**Next Action:** Wait for PROJ-FMS-A complete (and ideally PROJ-FMS-B, though only A is hard-blocking), then begin Phase 1
**Blockers:** PROJ-FMS-A (hard); ramming from PROJ-FMS-B can land before or after fighters (soft).

## Overview
End-to-end fighters: ships carry fighters as bay cargo, launch them strategically into a hex (forming a `fighter_group`) or tactically into a battle (deploying actual carried design instances). Fighters fight via minimal AI. Survivors recover — strategically via an explicit empire action, tactically via end-of-battle reboard with overflow → sector group.

## Goals
- `StrategicFighterLaunchAbility` creates a `fighter_group` in the launching ship's hex.
- `TacticalFighterLaunchAbility` replaces the existing `VehicleLaunchAbility` auto-launch path; deploys carried design instances onto the tactical map.
- Deployed wings auto-join combat in their hex on their owner's side (free via PROJ-FMS-A `group_kind`).
- Minimal fighter AI: target nearest enemy.
- `RecoverFightersAbility` (strategic empire action) moves fighters back to ship bays with HP preserved.
- End-of-battle: fighters launched **during that battle** auto-reboard; overflow → new sector `fighter_group`; pre-existing groups stay until explicit recovery.

## Scope
**In:** all fighter launch / combat / recovery behavior.
**Out:** mines (PROJ-FMS-B), satellites (PROJ-FMS-D), workshop-side fighter design (existed pre-PROJ-FMS-A, just adjusts in A).

## Dependencies
- **Hard:** PROJ-FMS-A complete (substrate).
- **Soft:** PROJ-FMS-B for ramming (kamikaze fighters use `RamTargetAbility`); fighter behavior works without it.

## Key Files
See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md#proj-fms-c-fighters) "Critical files to modify (PROJ-FMS-C)" section.

| File | Type | Action | Phase |
|------|------|--------|-------|
| `game/simulation/components/abilities/launch.py` | Production | Skeleton classes from PROJ-FMS-A; strategic execution via `OrderType.LAUNCH_FIGHTERS` + handler (no `apply()` method exists on `Ability`); tactical execution via firing-system rewrite | 1 |
| `game/simulation/components/abilities/recovery.py` | Production | Skeleton class from PROJ-FMS-A; strategic execution via `OrderType.RECOVER_FIGHTERS` + handler | 3 |
| `game/strategy/engine/order_handlers/launch_fighters.py` (new) | Production | Strategic fighter-launch handler (mirrors [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py)) | 1 |
| `game/strategy/engine/order_handlers/recover_fighters.py` (new) | Production | Strategic fighter-recovery handler | 3 |
| `game/simulation/combat/weapon_firing_system.py:115-141` | Production | Replace auto-launch with design-instance deploy | 1 |
| `game/simulation/systems/attack_processor.py:68-97` | Production | Accept design-instance payload, not class string | 1 |
| `game/simulation/systems/battle_engine.py` | Production | End-of-battle reboard + overflow-to-sector-group | 3 |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Verify `fighter_group` inclusion in combat manifest | 2 |
| `game/simulation/entities/stat_contributors/launch.py:29-61` | Production | Update for new launch ability shape | 1 |
| `game/ai/controller.py` | Production | Minimal "target nearest enemy" fighter AI | 2 |

## Phases

### Phase 1: Strategic + tactical fighter launch (design-instance based)
Implement both launch abilities. Strategic creates `fighter_group` in hex; tactical deploys actual `CarriedVehicle` instances onto the tactical map. Replace [`weapon_firing_system.py:130-140`](../../../game/simulation/combat/weapon_firing_system.py#L130) class-string path with design-instance payload.

### Phase 2: Deployed wing combat join + fighter AI
Confirm `fighter_group` Fleets join contested-hex combat through existing conflict resolution. Implement minimal fighter AI in [`game/ai/controller.py`](../../../game/ai/controller.py).

### Phase 3: Recovery + end-of-battle reboard
`RecoverFightersAbility` strategic action. End-of-battle reboard hook in `battle_engine`: fighters launched *during that battle* auto-dock onto friendly ships with bay space; overflow becomes a new `fighter_group` in the sector; pre-existing groups stay.

### Phase 4: Integration tests + E2E gameplay smoke
Full launch → combat → recover round-trip tests including HP persistence. Stress tests around overflow scenarios.

## Related Documents
- [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md)
- Sibling projects: [PROJ-FMS-A](../PROJ-FMS-A/), [PROJ-FMS-B](../PROJ-FMS-B/), [PROJ-FMS-D](../PROJ-FMS-D/)
