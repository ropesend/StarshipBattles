# PROJ-320: Strategic Combat Round Budget

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-320` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-320 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. TDD scaffolding (failing tests) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Pre-existing fleet-merge speed-recalc fix | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Multi-fleet-per-empire combat support | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Per-fleet-tick combat triggering | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Performance regression test | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Documentation update | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State

**Last Updated:** 2026-05-02 20:45
**Active Phase:** Planning — awaiting user approval
**Last Action:** Phase A deep code review + Phase B 6-agent swarm review complete; plan + decisions drafted
**Next Action:** User approves the plan → start Phase 1 in a new "Continue Project" session
**Blockers:** None — all design questions answered, baseline 16,377 / 0 / 3 is green

## Overview

Today, when two opposing fleets occupy the same sector, `ConflictResolutionEngine` fires every sub-tick of the 100-tick strategic turn — up to ~100 sequential battles per contested hex per turn. The user's intended model is one combat round per fleet per **movement-opportunity tick** (`tick % get_tick_interval(fleet.speed) == 0`), gated by whether the fleet actually leaves the hex on that tick. A speed-6 fleet vs a speed-4 fleet stalemated in one hex resolves in 6 + 4 = 10 rounds, not 100.

The change is fully internal to `ConflictResolutionEngine` — no public API, DTO, save format, or UI surface change is required. A small pre-existing bug in `OrderProcessor._execute_fleet_merge` (missing post-merge speed recalc) is fixed in scope because the new model depends on accurate per-fleet movement intervals. Expected runtime: ~10× speedup at typical contested hexes.

## Goals

- Combat at a contested hex fires only on each engaged fleet's movement-opportunity tick, not every tick.
- A fleet that successfully leaves the hex on its movement-opportunity tick does **not** trigger combat that tick.
- A fleet that has the opportunity but does not leave (no orders, action order, blocked, or destination = current hex) **does** trigger combat that tick.
- Every fleet of every empire at the contested hex contributes its own rounds independently (no per-empire batching).
- N-team encounters resolve as a single battle per round, with all fleets at the hex participating (already supported post-PROJ-275).
- Pre-existing fleet-merge speed-recalculation bug is fixed.

## Scope

**In:**
- `game/strategy/engine/conflict_resolution_engine.py` — combat triggering rewrite
- `game/strategy/engine/turn_engine.py` — Phase 4 dispatch wiring
- `game/strategy/engine/order_processor.py::_execute_fleet_merge` — bug fix (post-merge `update_fleet_speed`)
- New unit + integration tests under `tests/unit/strategy/engine/` and `tests/integration/strategy/`
- New performance regression test at `tests/performance/test_contested_hex_round_budget.py`
- Doc updates: `docs/systems/strategy_layer.md` §3 + `docs/systems/combat_simulation.md` §9

**Out:**
- Issue #8 — replay button disabled for shortcut branches (independent bug, separate work)
- Issue #7 — show current tick in Processing Turn overlay (independent feature, separate work)
- Tick-budget tunability per engagement composition beyond what the new model already gives (deferred — adequately handled by reduced round count)
- New `Fleet.remaining_moves` persistent state (rejected — model is stateless, derive from `tick % interval == 0`)
- Per-encounter scheduling registry (rejected — re-derive contested-hex membership each tick stays simpler)
- Refactoring `_resolve_conflicts` hex-map scan to event-driven (separate optimization opportunity, ~1× win)
- Changes to `IConflictEngine`, `IBattleResolver`, `BattleResult`, `ConflictResult`, `BattleSpec`, `Fleet`, save format, or any UI surface beyond test assertion adjustments
- Backward-compat shim for old per-tick path (per CLAUDE.md "Eradicate" rule, the old path is deleted)

## Key Files

| Component | File Path |
|-----------|-----------|
| Conflict resolution engine | `game/strategy/engine/conflict_resolution_engine.py` |
| Turn engine (Phase 4 dispatch) | `game/strategy/engine/turn_engine.py` |
| Order processor (merge fix) | `game/strategy/engine/order_processor.py` |
| Fleet movement engine (reference for trigger pattern) | `game/strategy/engine/fleet_movement_engine.py` |
| Fleet speed calculator (`get_tick_interval`) | `game/strategy/services/fleet_speed_calculator.py` |
| Strategy battle spec compiler | `game/strategy/combat/spec_compiler.py` |
| Post-battle hook | `game/strategy/combat/post_battle_hook.py` |
| Conflict engine tests | `tests/unit/strategy/engine/test_conflict_resolution_event_replay.py`, `tests/unit/strategy/conflict_resolution/` |
| Combat shortcut paths integration | `tests/integration/strategy/test_combat_shortcut_paths.py` |
| Triage findings (origin) | `findings/strategic_combat_round_budget.md` |
| Risk findings | `findings/risk_assessor.md` |
| Data-flow findings | `findings/data_flow.md` |
| Performance findings | `findings/performance.md` |
| Pattern findings | `findings/patterns.md` |
| UI-impact findings | `findings/ui_impact.md` |
| API-contracts findings | `findings/api_contracts.md` |

## Related Documents

- [design.md](design.md) — Initial Analysis + Swarm Findings + design rationale
- [decisions.md](decisions.md) — Locked-in user decisions with rationale
- [findings/](findings/) — Original triage doc + 6 swarm-agent reports

## Verification

- [ ] All phase checklists complete
- [ ] All affected tests passing — `python Tools/test_sharded/test_sharded.py` (baseline: 16,374 passing)
- [ ] New performance test asserts ≥5× reduction in battle invocations vs the same-scenario pre-PROJ-320 baseline
- [ ] Manual smoke: end-turn with two co-located stalemated fleets — confirm event log shows N rounds where N = sum of fleet speeds (not 100)
- [ ] `docs/systems/strategy_layer.md` §3 and `docs/systems/combat_simulation.md` §9 updated; `Last verified:` dates bumped
- [ ] Audit passed
- [ ] User verified
