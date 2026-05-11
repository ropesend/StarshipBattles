# PROJ-412: Reduce Strategy Turn Processing Time

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-412` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-412 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Measure (profile + characterization tests) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Cheap wins (late imports, micro-fixes) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Harvesting recompute reduction (storage + booster caches) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Orchestration overhead (snapshot, progress callback, `_run_phases`) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Secondary phase optimizations (energy / environmental / movement) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

Phases 3–5 are **conditional**. Phase 1's profiling result is authoritative — if measured cost differs from the pre-profile hypothesis, the phase ordering and content will be re-justified before any Phase 2+ work starts.

## Current State

**Last Updated:** 2026-05-10
**Active Phase:** Plan approved — ready for Phase 1
**Last Action:** Plan approved by user; aspirational target ~10× speedup recorded; UI-callback coarsening confirmed in scope; all Phase 2 short-circuits confirmed in scope
**Next Action:** Begin Phase 1 (Measure) in a new session via "Continue Project"
**Blockers:** None

## Overview

Turn processing on the user's *tiny* reference scenario (2 empires, 2 planets, a handful of ships) currently takes **~7–8 s per turn** wall-clock. Real `TURN PERF` log lines from QA session `20260510_165332` attribute ~3.9 s to the `harvesting` phase (≈50%) and leave ~2.5–3.7 s unaccounted for between named phase buckets. Combat is the largest single subsystem cost in *real* games but is explicitly out of scope here. The user's goal: make the existing Python turn pipeline as efficient as possible without changing game-mechanical behavior, without altering the 100-tick-per-turn invariant, and without making forward assumptions about resources (because mid-turn combat can destroy producing infrastructure mid-turn).

## Goals

- Reduce wall-clock turn-processing time on the tiny reference scenario.
- Preserve the 100-tick subturn loop and per-tick observable behavior (mid-turn facility destruction, build completions, fleet movement still take effect at the same tick they currently do).
- Use measurement (Scalene + the existing `_phase_times` log) to drive every optimization decision; no speculative rewrites.
- Stay inside the project's strict-TDD rule: write or identify the failing/characterization test first.
- Avoid scope creep into combat (out of scope per user direction) and into the UI panel-load issue tracked separately in [PROJ-411](../PROJ-411/plan.md).

## Scope

**In:**
- All per-tick phases listed in `DEFAULT_TICK_PHASE_LIST` *except* `combat` (phase 4).
- All end-of-turn phases (`organics_consumption` → `water_modification`).
- `TurnEngine` orchestration: `_run_phases`, `_time_phase`, `TickContext`, `TurnStateSnapshot`, `progress_callback` plumbing.
- Caching infrastructure for `_aggregate_empire_storage`, `_get_harvest_booster_mult`, and adjacent ability-source scans where the same opportunity exists.
- New `tests/performance/bench_turn_processing.py` benchmark and supporting characterization tests.
- Phase ordering / descriptor list stays unchanged (frozen by golden tests).

**Out:**
- `ConflictResolutionEngine` and any combat-sim work. Combat performance is its own separate concern; the user explicitly excluded it from this project.
- UI panel-load performance (handled by PROJ-411).
- A future port of subsystems to Rust/C++. This project optimizes the existing Python implementation only.
- Changing game-mechanical behavior. Floating-point accumulation order may change if necessary, but any observable game-state divergence must be surfaced for user approval before merging.

## Reference scenario

Per user direction: **2 empires, 2 planets, a handful of ships, no active combat**. Tests will fix a seed and reuse this exact composition.

## Target

**Aspirational:** ~10× speedup on the tiny scenario (current ~7.5 s/turn → goal ~0.75 s/turn). This is the user's stated aspiration, not a hard merge gate. Phase 1 will measure the actual ceiling; the final acceptance number is agreed at the end of Phase 4. Acceptance is stated in absolute seconds and in measured before/after deltas, not in fixed percentages.

## Key Files

| Component | File Path |
|-----------|-----------|
| Turn orchestration | `game/strategy/engine/turn_engine.py` |
| Phase descriptor list | `game/strategy/engine/turn_phase_registry.py` |
| Turn engine DI config | `game/strategy/engine/turn_engine_config.py` |
| State snapshot | `game/strategy/engine/turn_state_snapshot.py` |
| Harvesting hot path | `game/strategy/engine/harvesting_engine.py` |
| Production tick | `game/strategy/engine/production_engine.py` |
| Planet energy | `game/strategy/engine/planet_energy_engine.py` |
| Fleet movement | `game/strategy/engine/fleet_movement_engine.py` |
| Environmental hazards | `game/strategy/engine/environmental_hazard_engine.py` |
| Ability scope scan | `game/strategy/services/strategic_ability_scanner.py` |
| Ability source iteration | `game/strategy/services/ability_iterator.py` |
| Planet write service (mid-turn mutation site) | `game/strategy/services/planet_write_service.py` |
| Empire write service | `game/strategy/services/empire_write_service.py` |
| Triage source doc | [findings/turn_processing_performance.md](findings/turn_processing_performance.md) |
| Swarm: architecture / phase map | [findings/swarm_01_architecture_phase_map.md](findings/swarm_01_architecture_phase_map.md) |
| Swarm: harvesting hotspots | [findings/swarm_02_harvesting_hotspots.md](findings/swarm_02_harvesting_hotspots.md) |
| Swarm: overhead hunt | [findings/swarm_03_overhead_hunt.md](findings/swarm_03_overhead_hunt.md) |
| Swarm: cache patterns | [findings/swarm_04_cache_patterns.md](findings/swarm_04_cache_patterns.md) |
| Swarm: test impact | [findings/swarm_05_test_impact.md](findings/swarm_05_test_impact.md) |
| Swarm: invariants & risks | [findings/swarm_06_invariants_risks.md](findings/swarm_06_invariants_risks.md) |

## Related Documents

- [design.md](design.md) — architecture analysis and design rationale
- [decisions.md](decisions.md) — full decisions log with rationale
- [findings/](findings/) — six-agent swarm review reports and source triage

## Verification

- [ ] All phase checklists complete
- [ ] Final benchmark JSON (`tests/performance/bench_turn_processing.baseline.json` or equivalent) shows the agreed reduction vs. the Phase-1 baseline
- [ ] No new save-file migration, compatibility shim, or fallback path was added (root-cause rule)
- [ ] All tests passing (full sharded suite); no regression in `tests/integration/strategy/` mid-turn invariant tests
- [ ] Three new characterization tests live and green: mid-turn facility completion, harvester destruction, booster arrival
- [ ] User verified the tiny-scenario turn time on their machine
