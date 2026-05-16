# PROJ-FMS-B: Fighters/Mines/Satellites — Mines End-to-End (2026-05-15)

> **WORKING ON THIS PROJECT:**
> - Read [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the full design rationale.
> - Open the phase checklist for your current phase.
> - Check off tasks as you complete them.
> - Update Current State before stopping work.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Strategic mine layer + minefield_resolver + warhead trigger math | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Warhead detonation + Laserhead beam behavior with threshold | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Tactical mine resolver + sector scatter | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Sensitivity UI + selective self-destruct + ramming | Complete (service layer) | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Integration tests + E2E gameplay smoke | Complete (automated) | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-16
**Active Phase:** All 5 phases complete
**Last Action:** Phase 5 integration tests + statistical balance + docs landed
**Next Action:** Codex consult / audit pass
**Blockers:** None
**Known follow-ups:** ~~Strategy-side battle-spec compiler does not yet
wire `BattleEngine.mine_resolver` automatically.~~ **Resolved 2026-05-16
in audit Fix 2** — wiring is now automatic via `build_mine_resolver_setup`
+ `_mine_groups` side-channel on the frozen `BattleSpec`; see
`findings/audit_fix_report.md` Fix 2 for the full mechanism.

## Overview
End-to-end mines: lay them strategically, hit fleets entering the hex, deal damage; tactical participation; ramming for fighters/ships with warheads; selective self-destruct; mine field sensitivity and laserhead threshold UI.

## Goals
- `StrategicMineLayerAbility` and `TacticalMineLayerAbility` fully functional.
- Strategic detonation math hooks into `turn_engine` movement phase before conflict detection.
- Tactical resolver participates in per-tick movement loop.
- `WarheadAbility` detonation via the existing damage pipeline; always-hits semantics.
- `LaserheadAbility` fires as one-shot beam gated by continuous expected-hit-chance threshold.
- Sensitivity (LOW/MED/HIGH) per minefield + laserhead threshold slider — owner-adjustable.
- Selective self-destruct UI action on a `mine_group`.
- Ramming behavior for fighters/ships with warheads.
- Sector scatter (battle-boundary or fixed-radius fallback), deterministic per minefield.

## Scope
**In:** all mine behavior end-to-end + ramming (which uses warheads).
**Out:** fighter combat AI (PROJ-FMS-C), satellites (PROJ-FMS-D), workshop-side mine design (already done in PROJ-FMS-A).

## Dependencies
- **Hard:** PROJ-FMS-A complete.
- **Soft:** none.

## Key Files
See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md#proj-fms-b-mines) "Critical files to modify (PROJ-FMS-B)" section.

| File | Type | Action | Phase |
|------|------|--------|-------|
| `game/simulation/components/abilities/warhead.py` | Production | Implement | 2 |
| `game/simulation/components/abilities/laserhead.py` | Production | Implement | 2 |
| `game/simulation/components/abilities/ram_target.py` | Production | Implement | 4 |
| `game/simulation/components/abilities/launch.py` | Production | Skeleton classes from PROJ-FMS-A (data-only; no `apply()` — that's not a method on `Ability`). Strategic mine-laying wires through `OrderType.LAY_MINES` + a new `LayMinesOrderHandler` in `order_handlers/`. Tactical mine-laying wires through battle-action / firing-system. | 1, 3 |
| `game/strategy/engine/minefield_resolver.py` | Production | New file | 1 |
| `game/strategy/engine/turn_engine.py` | Production | Wire mine resolver into movement phase pre-conflict | 1 |
| `game/simulation/systems/battle_engine.py` | Production | Per-tick mine proximity + laserhead range trigger | 3 |
| `data/balance/mines.json` | Data | New file with constants | 1 |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Confirm `mine_group` inclusion in combat manifest | 3 |
| `game/ui/...` (TBD) | Production | Sensitivity slider, threshold slider, self-destruct action, ram target UI | 4 |

## Phases

### Phase 1: Strategic mine layer + minefield_resolver + warhead trigger math
Wire strategic mine-laying through the existing order-handler pattern: new `OrderType.LAY_MINES` (enum value reserved in PROJ-FMS-A Phase 5), new `IssueLayMinesCommand` + `LayMinesOrderHandler(BaseOrderHandler)`. The handler consumes mines from the issuing ship's bay and creates / extends a `mine_group` Fleet in the hex. Implement `minefield_resolver.py` with the per-ship warhead-pass math. Wire into `turn_engine` before conflict detection. Balance constants in `data/balance/mines.json`.

### Phase 2: Warhead detonation + Laserhead beam behavior
`WarheadAbility` detonation routes through the damage pipeline. `LaserheadAbility` fires as one-shot beam reusing `BeamWeaponAbility.calculate_hit_chance()`, gated by minefield's `expected_hit_chance_threshold`. Consumed-on-fire.

### Phase 3: Tactical mine resolver + sector scatter
Wire `TacticalMineLayerAbility` execution into the battle-action / weapon-firing-system path (no `apply()` method — abilities are data-only). Per-tick mine behavior in `battle_engine`. Scatter algorithm: tactical-battle-boundary when present, fixed deployment-circle fallback (radius from `data/balance/mines.json`). Scatter coords stored on the `mine_group` Fleet, PRNG-seeded for re-entry determinism. Mid-battle-laid mines **persist to the laying empire's `mine_group`** (sector assets, uniform with strategic-laid mines).

### Phase 4: Sensitivity UI + selective self-destruct + ramming
LOW/MED/HIGH sensitivity selector + continuous laserhead threshold slider on `mine_group` UI. Selective self-destruct UI (pick designs / subsets to destroy). `RamTargetAbility` behavior for fighters/ships: explicit set-target action, AI flies into the target, on collision all `Warhead` components detonate against the target, rammer destroyed.

### Phase 5: Integration tests + E2E gameplay smoke
Full E2E coverage: design → build → load into bay → strategic lay → enemy fleet enters → damage applied; tactical battle → mines fire each tick → consumed; self-destruct; ramming round-trip; threshold gating verified.

## Related Documents
- [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md)
- Sibling projects: [PROJ-FMS-A](../PROJ-FMS-A/), [PROJ-FMS-C](../PROJ-FMS-C/), [PROJ-FMS-D](../PROJ-FMS-D/)
