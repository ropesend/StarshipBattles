# PROJ-447 Phase 5: Simulation LOC-ceiling extractions (SPIN-OUT CANDIDATE)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-447 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started — **STRONG RECOMMENDATION TO SPIN OUT before starting**
**Depends on:** Phases 1-4 complete
**Objective:** Extract serialization / orchestration responsibilities from the 3 simulation files with clean cuts: `battle_state.py` (832 LOC), `battle_controller.py` (831 LOC), `replay_serialization.py` (634 LOC). The other 10 files in F-D-011's cluster of 13 don't have obvious clean cuts; track them as "next-touch" rule, not inline work.

**RECOMMENDATION: SPIN OUT before starting.** Per Codex consult 2026-05-18, the cluster is 13 files (not 9 as F-D-011's title originally said). 3 have clean extraction targets; the other 10 are flag-for-visibility. Recommended spin-out: 2-3 dedicated extraction projects (one per clean-cut file) under the next-available IDs.

**Cross-bucket file-ownership rule:** Only edit `game/simulation/`.

**Source-of-truth findings:** [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-011, F-D-028.

**The 13 over-ceiling simulation files (Codex-verified 2026-05-18):**
1. `game/simulation/battle_state.py` — 832 LOC ✦ clean extract target (F-D-028)
2. `game/simulation/battle_controller.py` — 831 LOC ✦ clean extract target (F-D-009 narration also lives here)
3. `game/simulation/systems/battle_engine.py` — 758 LOC
4. `game/simulation/battle_runner.py` — 734 LOC (F-D-009 lie also lives here — separately fixed in Phase 2)
5. `game/simulation/replay/replay_serialization.py` — 634 LOC ✦ clean split (capture vs replay paths)
6. `game/simulation/entities/ship.py` — 607 LOC
7. `game/simulation/systems/tactical_mine_resolver.py` — 597 LOC
8. `game/simulation/entities/stat_contributors/registry.py` — 570 LOC
9. `game/simulation/entities/ship_stats.py` — 559 LOC
10. `game/simulation/components/abilities/base.py` — 535 LOC
11. `game/simulation/systems/battle_end_conditions.py` — 532 LOC
12. `game/simulation/services/vehicle_design_service.py` — 516 LOC
13. `game/simulation/combat/fleet_aura_manager.py` — 515 LOC

---

## Tasks (if executed inline rather than spun out)

### Task 5.1: F-D-028 — Extract battle_state.py serialization [Medium]
**File:** `game/simulation/battle_state.py` (832 LOC); create `game/simulation/battle_state_serde.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state.py tests/integration/replay/ -v`

- [ ] Read battle_state.py in full to identify serialization sites. Per the finding, the file contains:
  - `BattleState` dataclass
  - `ComponentState` dataclass
  - `ShipState` dataclass
  - `BattleResults` dataclass
  - Plus `to_dict` / `from_dict` for each (~250-300 LOC of paired serialization)
- [ ] **GREEN — extract**: Create `game/simulation/battle_state_serde.py`. Move the 4 paired `to_dict` / `from_dict` methods or equivalent free functions. Mirror the `planet_serde.py` (PROJ-372) precedent.
- [ ] Keep top-level `battle_state.py` either (a) with thin delegators on each dataclass, OR (b) callers migrate to the new module's free functions. Match the planet_serde.py / fleet_serde.py convention.
- [ ] Run targeted + replay integration tests
- [ ] Verify battle_state.py drops to ~530-580 LOC. Still over but tractable; document next-pass target in decisions.md.

### Task 5.2: battle_controller.py — Extract spec-in start_from_spec flow [Medium]
**File:** `game/simulation/battle_controller.py` (831 LOC)
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py -v`

- [ ] Read battle_controller.py in full to identify the spec-in `start_from_spec` flow (the headless / direct-spec path that bypasses the legacy `BattleConfig` chain)
- [ ] **GREEN — extract**: Create `game/simulation/battle_controller_spec_in.py` (or whatever naming matches sibling conventions). Move the spec-in entry point + its private helpers.
- [ ] Top-level `battle_controller.py` retains the legacy orchestration path
- [ ] Run targeted tests; visual-mode battle screen still works (manual verification recommended since this is UI-adjacent)

### Task 5.3: replay_serialization.py — Split capture vs replay paths [Medium]
**File:** `game/simulation/replay/replay_serialization.py` (634 LOC)
**Tests:** `pytest tests/unit/simulation/replay/ tests/integration/replay/ -v`

- [ ] Read the file to confirm capture and replay paths are cleanly separable
- [ ] **GREEN — split**: `replay_capture.py` + `replay_load.py` (or equivalent naming). Each under 350 LOC. Keep the shared dataclasses in a common module if needed.
- [ ] Run targeted + replay integration tests

### Task 5.4: F-D-011 — Document the 10 remaining files as "next-touch" rule [Simple]
**File:** [decisions.md](decisions.md)

- [ ] For each of the 10 remaining over-ceiling files (files 3-4, 6-13 in the list above): add an entry to decisions.md naming the file, its current LOC, and a one-sentence note ("no clean cut identified; revisit on next touch")
- [ ] Do NOT force a split on files without a clean cut — splits-for-the-sake-of-splits hurt readability

---

## Phase Completion Checklist (if executed inline)

- [ ] Tasks 5.1-5.3 complete; 3 cleanest files extracted
- [ ] Task 5.4 documentation recorded
- [ ] battle_state.py, battle_controller.py, replay_serialization.py all under 600 LOC (battle_state.py target: under 580; others under 500 ideally)
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-447 5` — PASSED
- [ ] Update status to `Complete`; plan.md all phases Complete; Current State → "Project complete — awaiting verification"
- [ ] No behavior changes (replay capture/playback round-trips identical)

## SPIN-OUT plan (if spun out instead)

1. Create PROJ-449A / 449B / 449C via `python Projects/scripts/create_project.py "..."` (one per clean-cut file)
2. PROJ-446 Phase 5 marker reused: PROJ-447 Phase 5 marked `Spun Out` rather than `Complete`
3. Each spin-out project has 1 phase / 1 PR scope (e.g., "Extract battle_state.py serialization")
4. PROJ-447 closes with Phases 1-4 verified

## Decision

Before starting Phase 5: open [decisions.md](decisions.md), record the inline-vs-spinout decision with rationale. The default recommendation is SPIN OUT — the 3 extractions are each medium-sized PRs and benefit from focused review rather than bundling.
