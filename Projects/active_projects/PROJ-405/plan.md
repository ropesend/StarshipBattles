# PROJ-405: Tier 1 B-06 — Wire EventBus through Projectile/Seeker construction

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Thread EventBus through production constructors | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1
**Last Action:** Project skeleton created from REMEDIATION_PLAN B-06
**Next Action:** Thread EventBus from `BattleState` through the projectile/seeker construction chain so `SEEKER_EXPIRE` actually records.
**Blockers:** None

## Overview
PROJ-382 added an `event_logger` kwarg to `Projectile`, but production callers don't pass it; the default is a no-op, so `SEEKER_EXPIRE` telemetry is silently dropped in normal play. EventBus must be threaded through the actual construction chain — likely `BattleState` → `WeaponFiringSystem` (or whatever creates projectiles in production) → `Projectile`/`Seeker`.

## Goals
- Production construction of `Projectile` and `Seeker` injects the session EventBus, not the no-op default.
- `SEEKER_EXPIRE` events are observed by EventBus subscribers in a normal battle tick.
- Add a regression test that subscribes to the bus and asserts `SEEKER_EXPIRE` is emitted on seeker expiration through the production path (not via direct projectile construction).

## Scope
**In:**
- The construction chain: `game/simulation/battle_state.py`, `game/simulation/combat/families/seeker.py`, `game/simulation/combat/families/projectile.py`, plus whichever weapon-firing/spawning service constructs projectiles.
- A test that uses a real (or close-to-real) battle path and asserts the event is emitted.

**Out:**
- The other PROJ-382 audit-readiness drift (Tier 2 PROJ-406).
- PROJ-382's `StrategyScreen.session` chain residue (deferred U1/U2/U3 in PROJ-382's own plan).

## Key Files
| Component | File Path |
|-----------|-----------|
| `Projectile` (kwarg target) | `game/simulation/entities/projectile.py` |
| `Seeker` family | `game/simulation/combat/families/seeker.py` |
| Projectile family | `game/simulation/combat/families/projectile.py` |
| `BattleState` (top of chain) | `game/simulation/battle_state.py` |
| Probable middle of chain | `game/simulation/combat/weapon_firing_system.py` (or similar — confirm) |
| EventBus (read-only) | `game/services/events/event_bus.py` (confirm path) |

## Source Evidence (REMEDIATION_PLAN B-06)
- `game/simulation/entities/projectile.py:8-20`, `:40-42`, `:119-122`, `:138-141` — `event_logger` kwarg added with no-op default.
- `game/simulation/combat/families/seeker.py:55-65` — `Seeker` constructor.
- `game/simulation/combat/families/projectile.py:33-43` — projectile family.
- `game/simulation/battle_state.py:564-575` — top of the construction chain.
- Reviewer: `rg event_logger` under `game/simulation` finds only `projectile.py`.
- PROJ-382 review (`Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-382_report.md`).

## Verification
- [ ] Phase 1 checklist complete
- [ ] `pytest tests/unit/simulation/entities/test_projectile.py -v` passes
- [ ] New regression test asserting `SEEKER_EXPIRE` is observed by an EventBus subscriber via the production construction path passes
- [ ] `rg -n "event_logger|event_bus" game/simulation/` shows the kwarg threaded through every constructor in the chain
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-405` passes
- [ ] User verified
