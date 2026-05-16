# PROJ-FMS-D: Fighters/Mines/Satellites — Satellites End-to-End (2026-05-15)

> **WORKING ON THIS PROJECT:**
> - Read [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design rationale.
> - Open the phase checklist for your current phase.
> - Check off tasks as you complete them.
> - Update Current State before stopping work.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Strategic + tactical satellite launch + stationary AI | Not started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Recovery (separate ability gate from fighters) | Not started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Integration tests + E2E gameplay smoke | Not started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-15
**Active Phase:** Phase 1 (blocked on PROJ-FMS-A; PROJ-FMS-C work serves as a useful template)
**Last Action:** Project scaffolded
**Next Action:** Wait for PROJ-FMS-A complete (and ideally PROJ-FMS-C for the template), then begin Phase 1
**Blockers:** PROJ-FMS-A (hard).

## Overview
Satellites mirror fighters but stay stationary in tactical combat and use a **separate set** of bay / launch / recovery abilities so a ship with fighter capacity does not automatically pick up satellites and vice versa. After this phase, all three unit types are fully integrated.

## Goals
- `StrategicSatelliteLaunchAbility` creates a `satellite_group` in the hex.
- `TacticalSatelliteLaunchAbility` deploys satellites onto the tactical map at chosen positions.
- Tactical AI: stationary — satellites do not move, but can fire their weapons / use abilities.
- `RecoverSatellitesAbility` (separate from `RecoverFightersAbility`) moves satellites back to bays.
- Satellite bay capacity is a separate stat from fighter bay capacity (could be a different component type or a shared `VehicleBay` with type filtering — design choice in Phase 1).

## Scope
**In:** all satellite launch / combat / recovery behavior.
**Out:** mines (PROJ-FMS-B), fighters (PROJ-FMS-C).

## Dependencies
- **Hard:** PROJ-FMS-A complete (substrate).
- **Soft:** PROJ-FMS-C complete (template + verified launch path; satellites largely mirror fighters).

## Key Files

| File | Type | Action | Phase |
|------|------|--------|-------|
| `game/simulation/components/abilities/launch.py` | Production | Skeleton classes from PROJ-FMS-A; strategic execution via `OrderType.LAUNCH_SATELLITES` + handler; tactical via battle-action / firing-system | 1 |
| `game/simulation/components/abilities/recovery.py` | Production | Skeleton class from PROJ-FMS-A; strategic execution via `OrderType.RECOVER_SATELLITES` + handler | 2 |
| `game/strategy/engine/order_handlers/launch_satellites.py` (new) | Production | `LaunchSatellitesOrderHandler` | 1 |
| `game/strategy/engine/order_handlers/recover_satellites.py` (new) | Production | `RecoverSatellitesOrderHandler` | 2 |
| `game/strategy/data/fleet.py` | Production | Support `satellite_group` `group_kind` (already added in A) | 1 |
| `game/ai/controller.py` | Production | Stationary satellite AI variant ([`controller.py:361-363`](../../../game/ai/controller.py#L361) is the existing satellite ref) | 1 |
| `data/components.json` | Data | Add `satellite_bay_*` components (separate from fighter bays) | 1 |
| `game/simulation/entities/stat_contributors/launch.py` | Production | Aggregate satellite launch / bay stats separately from fighters | 1 |
| `game/ui/screens/<sector_action_menu>.py` | Production | Strategic launch + recovery UI for satellites | 1, 2 |

## Phases

### Phase 1: Strategic + tactical satellite launch + stationary AI
Implement both launch abilities (mostly mirroring PROJ-FMS-C Phase 1). Add stationary tactical AI variant. Add separate `satellite_bay_*` components if separating bay capacity by type (preferred for design clarity).

### Phase 2: Recovery (separate ability gate)
`RecoverSatellitesAbility` strategic action. End-of-battle auto-reboard for satellites launched during the battle (same overflow→sector group policy as fighters). Separate from `RecoverFightersAbility` so design space distinguishes carrier types.

### Phase 3: Integration tests + E2E gameplay smoke
Full launch → battle → recover round-trip including stationary AI behavior. Stress on separation of fighter vs satellite ability gates (a fighter-only carrier should not be able to launch satellites and vice versa).

## Related Documents
- [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md)
- Sibling projects: [PROJ-FMS-A](../PROJ-FMS-A/), [PROJ-FMS-B](../PROJ-FMS-B/), [PROJ-FMS-C](../PROJ-FMS-C/)
- Template: PROJ-FMS-C — satellites mirror fighters with three differences (stationary AI, separate ability gate, no ram-target use case usually).
