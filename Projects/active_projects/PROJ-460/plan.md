# PROJ-460: Simulation clean-cut LOC extractions (battle_state_serde + battle_controller spec-in + replay_serialization split)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-460` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-460 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on main; user's standing preference — no worktrees)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. F-D-028 — extract `battle_state.py` serde into `battle_state_serde.py` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. F-D-011 partial — extract `battle_controller.py` `start_from_spec` headless / spec-in flow | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. F-D-011 partial — split `replay_serialization.py` into `replay_capture_serde.py` + `replay_outcome_serde.py` (+ shared helpers) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Document the 10 remaining over-ceiling simulation files as next-touch | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Planning
**Last Action:** Group 3 pre-execution review fixes applied (codex + subagent reviews; see consult artifacts at `AgentCoordination/Scratchpad/Consult/20260519T024637Z_group3-pre-execution-review/` and `.agent_reports/group3_pre_execution_review/`). Three fixes: (a) **`__init__.py` docstring refresh added to Phase 3** as new Task 3.7b — the current package docstring at `game/simulation/replay/__init__.py:12-21` references the soon-deleted `replay_serialization` module and incorrectly claims "Phase 3 adds `replay_capture.py`" (which already existed pre-PROJ-460). Phase 3 already edits this file for re-exports; the docstring touch is bundled into the same edit. (b) **LOC drift refreshed across plan.md + findings file** — the three target files have shrunk since the original 2026-05-18 scan: `battle_state.py` 832 → 715, `battle_controller.py` 831 → 682, `replay_serialization.py` 634 → 516. Cited symbol lines still resolve correctly; the practical consequence is Phase 3's "split at line 407" guidance is stale (actual `def battle_outcome_to_dict(…)` boundary is now near line 540-542). Phase 1's "drop to ~530-580 LOC" target is re-derived from the new baseline to ~430-470 LOC. (c) **Phase 3 Task 3.0 pre-flight added** — re-measure LOC and re-derive the spec/outcome boundary before Task 3.1, recording the result in `decisions.md`. Earlier 2026-05-19 codex Bucket-D fix retained: project respun from Codex r4 redesign (`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`) as Job 12; PROJ-444..447 archived; F-D-028 and the actionable slice of F-D-011 carried forward from `Projects/archived_projects/PROJ-447/findings/bucket_d_simulation_ai_research_engine_docs_scan.md`.
**Next Action:** Run agent picks up PROJ-460 Phase 1 after PROJ-452 + PROJ-455 + PROJ-458 all complete (PROJ-460 is **position 4 of 4 — FINAL** in Group C's serial order `452 → 455 → 458 → 460` — see Group C execution context in the Dependencies & Sibling Projects section and `Projects/active_projects/GroupC_execution_prompt.txt`). PROJ-460 has no Phase 0; first phase is Phase 1 (battle_state serde extraction). However, Phase 3 now starts with a Task 3.0 pre-flight (re-measure LOC and re-derive the spec/outcome boundary).
**Blockers:** Serial gate: PROJ-452 + PROJ-455 + PROJ-458 must complete first within Group C. No external blockers.
**2026-05-19 cross-group resolution (final):** Doc-consolidation rule added (see new "Doc consolidation rule (cross-group)" section above) — PROJ-460's doc additions for `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md` accumulate as a `Pending doc consolidation` block in `decisions.md` rather than landing inline. Same rule lives in PROJ-457 (Group B) and PROJ-459 (Group A). Whichever of the three finishes LAST is responsible for the single consolidated edit. Run agent checks PROJ-457 + PROJ-459 status when this project completes; if both are closed, PROJ-460 is the LAST runner and owns the consolidated doc edit. Group C execution-context block added to Dependencies.

## Overview
Three clean LOC extractions in the simulation layer, each modeled on the planet_serde.py / fleet_serde.py (PROJ-372 / PROJ-459) precedent. Plus Phase 4 documents the OTHER 10 over-ceiling simulation files as "next-touch" rule entries — explicitly not touched in this project.

1. `game/simulation/battle_state.py` is 715 LOC as of 2026-05-19 (was 832 LOC at original drafting). The `BattleState` / `ShipState` / `ComponentState` / `ProjectileState` / `BattleResults` to_dict/from_dict cluster is ~250-300 LOC of clean extraction. Target: drop battle_state.py to ~430-470 LOC (re-derived from the new 715 baseline; the original "~530-580" target was derived from the now-stale 832 baseline). Cited symbol lines still resolve correctly.
2. `game/simulation/battle_controller.py` is 682 LOC as of 2026-05-19 (was 831 LOC at original drafting). The `start_from_spec` headless / spec-in flow (controller.py:242 — still resolves correctly) is a self-contained orchestration responsibility that doesn't belong in the visual-mode controller proper. Extract to a sibling module. UI-adjacent, so manual smoke verification is required.
3. `game/simulation/replay/replay_serialization.py` is 516 LOC as of 2026-05-19 (was 634 LOC at original drafting). The file already splits naturally into two halves: BattleSpec capture/preparation paths (boundary, modifier stack, spec serialization) and BattleOutcome / replay-load paths (outcome, hit records, ship stats). The spec/outcome boundary is at `def battle_outcome_to_dict(...)` — now at line ~540-542 (was ~407 at original drafting); Phase 3 Task 3.0 re-measures and records the exact line. Split into **`replay_capture_serde.py`** (spec-side serialization) + **`replay_outcome_serde.py`** (outcome-side serialization), with shared helpers extracted into **`replay_serde_helpers.py`** (`_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`). Both serde halves end up under 350 LOC. **Note:** `replay_capture.py` already exists in the package (it owns the `IReplayCaptureSink` / `ReplayCaptureContext` runtime hook — see `game/simulation/replay/__init__.py:25-32`); the new serde modules use distinct `_serde` suffixed names to avoid collision.

Phase 4 is the discipline phase: document the 10 OTHER over-ceiling simulation files (battle_engine.py 758, battle_runner.py 735, ship.py 607, tactical_mine_resolver.py 597, stat_contributors/registry.py 570, ship_stats.py 559, components/abilities/base.py 535, battle_end_conditions.py 532, vehicle_design_service.py 516, fleet_aura_manager.py 515) as "next-touch" rule entries — one line each in `decisions.md`. **Do NOT attempt to split them.**

Per Codex r4 risk callout: "If Job 12 absorbs the other 10 F-D-011 files, you are back to a jumbled structural omnibus." The discipline rule is what keeps this project from becoming a structural omnibus.

## Goals
- Close F-D-028 (battle_state.py serde extraction) — clean, well-shaped target.
- Close the actionable slice of F-D-011: battle_controller.py spec-in extraction + replay_serialization.py split.
- Maintain save-load round-trip byte-identity. This is the regression gate.
- Maintain replay regression integrity (capture / load round-trip).
- Document the 10 non-clean simulation overflows as next-touch entries with no attempt to force splits.
- Zero behavior change.

## Scope
**In Scope (3 files):**
- Phase 1: `game/simulation/battle_state.py` — extract serde into `game/simulation/battle_state_serde.py`. Drop battle_state.py to ~430-470 LOC (re-derived from the 2026-05-19 715-LOC baseline; the original "~530-580" target was derived from the now-stale 832 baseline).
- Phase 2: `game/simulation/battle_controller.py` — extract `start_from_spec` flow into a sibling module (proposed: `game/simulation/battle_controller_spec.py` or `game/simulation/battle_spec_loader.py` — name decided in-phase per the cleanest mental model).
- Phase 3: `game/simulation/replay/replay_serialization.py` — split into `replay_capture_serde.py` (spec/boundary/modifier-stack capture-side serialization) + `replay_outcome_serde.py` (outcome/hit/stats load-side serialization), with shared helpers in `replay_serde_helpers.py` (`_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`). Both serde halves under 350 LOC. The `_serde` suffix is used because `replay_capture.py` already exists in the package as the runtime capture-sink hook (`game/simulation/replay/__init__.py:25-32`) — the new names avoid collision and make the "serialization helpers vs runtime hook" distinction clear.
- Phase 4 (documentation only): `decisions.md` carries 10 lines, one per non-cut simulation file.

**Out of Scope (10 files explicitly listed and NOT touched):**
Per Codex r4 risk callout — these files exceed the ceiling but do NOT have a clean cut available, so they stay as next-touch:

| File | Current LOC (2026-05-19) | Reason out of scope |
|------|--------------------------|---------------------|
| `game/simulation/systems/battle_engine.py` | 758 | Core tick-loop orchestrator; no clean split axis identified |
| `game/simulation/battle_runner.py` | 735 | Headless run entry point; tight coupling to engine + outcome extraction |
| `game/simulation/entities/ship.py` | 607 | Facade over many delegates; structural split needs separate analysis |
| `game/simulation/systems/tactical_mine_resolver.py` | 597 | Single-responsibility mine resolution; would need finer-grained resolver split |
| `game/simulation/entities/stat_contributors/registry.py` | 570 | Registry pattern with many contributors inline; potential per-contributor split is a separate project |
| `game/simulation/entities/ship_stats.py` | 559 | Tight to Ship facade; no obvious internal split |
| `game/simulation/components/abilities/base.py` | 535 | Base classes for the ability hierarchy; structural sensitivity |
| `game/simulation/systems/battle_end_conditions.py` | 532 | Multiple end-condition classes in one file; per-class split is a separate decision |
| `game/simulation/services/vehicle_design_service.py` | 516 | Service-level; modest ceiling overage |
| `game/simulation/combat/fleet_aura_manager.py` | 515 | Aura manager with mixed responsibilities; needs separate scope analysis |

**Also Out:**
- Behavior changes. Save-format changes. Public API changes. Replay schema changes.
- The other simulation files NOT named (those under 500 LOC; nothing to do).
- Any non-LOC residue (e.g., F-D-009 battle_runner docstring lie, F-D-005 design_library.py stale docs). Those belong to other projects.

## Dependencies
**No hard predecessors.** Per Codex r4: "Parallel-safe. Depends on: none." Can run independently of the rest of the 12-job set.

**Soft adjacency:** If PROJ-459 lands fleet_serde.py first, that gives the team an additional concrete instance of the serde pattern (alongside planet_serde.py) to model battle_state_serde.py on. Not blocking, just convenient.

**No worktrees** per user standing preference. Serial execution in main checkout.

## Findings Summary
Source: `Projects/archived_projects/PROJ-447/findings/bucket_d_simulation_ai_research_engine_docs_scan.md`. Per-finding entries with current-state verification live in [findings/PROJ-460_findings.md](findings/PROJ-460_findings.md).

| Finding | Severity | File:line | Status | Closure phase |
|---------|----------|-----------|--------|---------------|
| F-D-028 | medium | `game/simulation/battle_state.py:1` (715 LOC as of 2026-05-19; was 832 at original drafting); 10 paired serde methods at :48/:59/:149/:179/:460/:482/:628/:647/:787/:805 (symbol lines still resolve correctly) | open | Phase 1 — extract `battle_state_serde.py` |
| F-D-011 (actionable slice) | medium | `game/simulation/battle_controller.py:242` (`start_from_spec` — start line confirmed 2026-05-19; file now 682 LOC, was 831) + `game/simulation/replay/replay_serialization.py:1` (516 LOC as of 2026-05-19; was 634; spec/outcome split boundary now ~540-542, was ~407) | open | Phase 2 (`battle_controller` spec-in extraction) + Phase 3 (replay split) |
| F-D-011 (next-touch residue) | medium | 10 other simulation files over 500 LOC (battle_engine.py 758, battle_runner.py 735, ship.py 607, etc. — see Out of Scope table) | open (deferred next-touch) | Phase 4 — document as 10 next-touch entries; NOT addressed in this project |

## Dependencies & Sibling Projects

### Group C execution context (coordinator-assigned 2026-05-19)

**Group C serial order: PROJ-452 → PROJ-455 → PROJ-458 → PROJ-460.**

This is **PROJ-460 — position 4 of 4 (FINAL)** in Group C. The run agent reaches this project only after PROJ-452, PROJ-455, and PROJ-458 all complete (all phases + codex audits + any audit-driven extra phases). When this project is complete, Group C is done.

Groups A (PROJ-449/451/450/459) and B (PROJ-456/454/457) run in parallel branches. Coordinator confirmed no hard cross-group blockers. See `Projects/active_projects/GroupC_execution_prompt.txt` for the run agent's full execution contract. PROJ-460 may also be the LAST runner across all 3 groups for doc consolidation — see the "Doc consolidation rule" section above for the responsibility check.

### Other-project relationships

| This project depends on | What | Why | Phase(s) gated |
|-------------------------|------|-----|----------------|
| (none) | none | Per Codex r4: "Parallel-safe. Depends on: none." | n/a |

| Sibling / soft adjacency | Relationship to PROJ-460 |
|--------------------------|--------------------------|
| PROJ-459 (Strategy data LOC extractions) | Soft adjacency. If PROJ-459 lands first, `fleet_serde.py` gives a second concrete serde-pattern instance to model `battle_state_serde.py` on; if not, `planet_serde.py` alone is sufficient. Not blocking. |

| Downstream projects | Their dependency on PROJ-460 |
|---------------------|-------------------------------|
| (10 next-touch simulation files — `battle_engine.py`, `battle_runner.py`, `ship.py`, `tactical_mine_resolver.py`, `stat_contributors/registry.py`, `ship_stats.py`, `components/abilities/base.py`, `battle_end_conditions.py`, `vehicle_design_service.py`, `fleet_aura_manager.py`) | Each may be picked up as a separate "next-touch" project when that file is next touched for a behavior change. PROJ-460 Phase 4 records the ledger so the touching agent sees the LOC residue; no scheduled successor. |

Per Codex r4 redesign DAG: PROJ-460 is Job 12 — parallel-safe, no upstream gate.

## Doc consolidation rule (cross-group)

PROJ-457 (Group B), PROJ-459 (Group A), and PROJ-460 (this) all update `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` to describe their respective LOC extractions. To avoid 3-way merge conflicts:

- **PROJ-460's plan.md and decisions.md describe doc changes WITHOUT applying them inline.** Every phase that would normally append entries to `docs/01_ARCHITECTURE.md` / `docs/02_PATTERNS.md` instead records the intended addition in `decisions.md` under a "Pending doc consolidation" block.
- **Required block at end of PROJ-460 (when all phases complete):** a structured `Pending doc consolidation` block in `decisions.md` listing every doc edit this project would have made — at minimum: `battle_state_serde.py` + `battle_controller` spec-in extract + `replay_capture_serde.py` + `replay_outcome_serde.py` + `replay_serde_helpers.py` entries for the architecture package-map and the patterns serde-extraction table. Format the block as a copy-paste-ready diff or unified-list so whoever applies the consolidated edit can do it mechanically.
- **Last-runner rule:** whichever of PROJ-457 / PROJ-459 / PROJ-460 finishes LAST is responsible for applying ALL three projects' `Pending doc consolidation` blocks as a single consolidated edit to `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md`. Check the other two projects' decisions.md files before declaring the project done; if both are closed, this project's run agent is the LAST and owns the consolidated edit.

This rule is consistent across Group A / B / C — the same wording appears in PROJ-457 (Group B) and PROJ-459 (Group A) per the coordinator's resolution.

## Key Files
| Component | File Path | Current LOC (2026-05-19) |
|-----------|-----------|--------------------------|
| BattleState (simulation) | `game/simulation/battle_state.py` | 715 (was 832 at original drafting) |
| BattleState serde (new) | `game/simulation/battle_state_serde.py` | 0 (to be created) |
| BattleController (simulation, visual-mode) | `game/simulation/battle_controller.py` | 682 (was 831 at original drafting) |
| BattleController spec extraction (new) | `game/simulation/battle_controller_spec.py` (proposed) | 0 (to be created) |
| Replay serialization | `game/simulation/replay/replay_serialization.py` | 516 (was 634 at original drafting; to be deleted in Phase 3; spec/outcome boundary now ~540-542, was ~407) |
| Replay capture serde (new) | `game/simulation/replay/replay_capture_serde.py` | 0 (to be created) |
| Replay outcome serde (new) | `game/simulation/replay/replay_outcome_serde.py` | 0 (to be created) |
| Replay serde shared helpers (new) | `game/simulation/replay/replay_serde_helpers.py` | 0 (to be created; `_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`) |
| Replay capture (existing — runtime hook, NOT touched) | `game/simulation/replay/replay_capture.py` | ~5 KB (existing; owns `IReplayCaptureSink`, `ReplayCaptureContext`) |
| Planet serde (template) | `game/strategy/data/planet_serde.py` | 219 (read-only reference) |
| Fleet serde (template, post-PROJ-459) | `game/strategy/data/fleet_serde.py` | TBD (read-only reference once PROJ-459 lands) |

Full enumeration in [manifest.md](manifest.md). Consolidated findings live at [findings/PROJ-460_findings.md](findings/PROJ-460_findings.md).

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale
- [decisions.md](decisions.md) — Full decisions log (includes the 10 next-touch entries from Phase 4)
- [findings/PROJ-460_findings.md](findings/PROJ-460_findings.md) — F-D-011 (partial) + F-D-028 carried verbatim from archived PROJ-447 with current status
- Codex r4 redesign source: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (Job 12)

## Phases

### Phase 1: F-D-028 — extract `battle_state.py` serde into `battle_state_serde.py` [Medium]
**Closes F-D-028.** Apply the planet_serde.py / fleet_serde.py precedent to the simulation layer.

**Characterization-first refactor.** This is a pure no-behavior-change extraction; the standard RED-then-GREEN cycle does not apply because no new behavior is introduced. Per CLAUDE.md's allowance for pure-refactor work, the discipline is characterization-first: write comprehensive round-trip tests for each of the 5 dataclasses that PASS against current code (capture the current dict shape verbatim), freeze the dicts as comparison constants, THEN extract. Any drift between pre- and post-extraction dict output is a real failure. Save-load tests + replay capture/playback round-trips are the critical regression gate; run them after every commit in this phase.

- Read `planet_serde.py` (and `fleet_serde.py` if PROJ-459 has landed) as templates.
- Create `game/simulation/battle_state_serde.py` with free-function `*_to_dict` / `*_from_dict_kwargs` pairs for the 5 serialization-heavy dataclasses: `ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults`.
- Replace the methods on the dataclasses with 1-line facades calling into the serde module.
- Note: this is different from planet_serde because each dataclass has its own `to_dict` / `from_dict` (not just one entity); the serde module ends up with ~5 paired functions. Decide whether to keep them as classmethods on the dataclasses or migrate fully to module-level functions. Document the choice in decisions.md.
- Verify: byte-identical save output before and after extraction.

**Targeted gate:**
```powershell
pytest tests/integration/replay/ tests/integration/save_load/ tests/unit/simulation/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

**Checkpoint:** battle_state.py drops to ~430-470 LOC (re-derived from the 2026-05-19 715-LOC baseline; the original "~530-580" target was based on the now-stale 832-LOC baseline). battle_state_serde.py ~280 LOC. Save-format byte-identical. Replay capture/playback round-trips green. Sharded suite green.

### Phase 2: F-D-011 partial — extract `battle_controller.py` `start_from_spec` headless / spec-in flow [Medium]
**Closes the battle_controller.py portion of F-D-011.**

`BattleController.start_from_spec` (battle_controller.py:242-368, ~125 LOC) is the spec-in path that constructs the engine from a `BattleSpec`. It's self-contained orchestration that doesn't share state with the visual-mode controller's per-frame update logic. Clean extraction target.

**Manual UI smoke test required.** This is battle-screen-adjacent code; the visual-mode start path goes through `BattleController.start_from_spec(...)`. Even with full test-suite coverage, a manual run of "start a battle in BattleSetupScreen, watch ticks happen" is the gate that catches subtle pre-tick-callback wiring drift.

- Identify the natural extraction. Options:
  - **Option A:** Create `game/simulation/battle_controller_spec.py` with a free function `build_controller_from_spec(controller, spec, ai_factory, ship_builder=None, registry_provider=None) -> BattleServiceResult` that holds the body of `start_from_spec`. `BattleController.start_from_spec` becomes a 1-line facade.
  - **Option B:** Move `start_from_spec` entirely off `BattleController` into a free function `start_from_spec(controller, spec, ...)`. Callers would change from `controller.start_from_spec(spec, ...)` to `start_from_spec(controller, spec, ...)`. More disruption, less LOC win.
  - Pick Option A by default. Option B only if Option A doesn't actually drop battle_controller.py below 700 LOC.
- Verify spec-in flow still works headlessly via existing tests (`tests/unit/simulation/battle_controller/test_start_from_spec.py`).
- Manual smoke: run the game, start a battle, confirm no regression in the visual-mode startup path.

**Targeted gate:**
```powershell
pytest tests/unit/simulation/test_battle_runner_di.py tests/unit/simulation/battle_controller/test_start_from_spec.py tests/integration/replay/test_headless_visual_equivalence.py tests/unit/simulation/battle_controller/ tests/integration/replay/ -q -n 4
python Tools/test_sharded/test_sharded.py
# Manual: start the game, start a battle via BattleSetupScreen, confirm no regression
```

Per audit feedback (Bucket D, response.md): the manual UI smoke gate should NOT stand alone for Phase 2. The targeted pytest run above explicitly includes the three strongest automated guards for the spec-in path (`test_battle_runner_di.py`, `test_start_from_spec.py`, `test_headless_visual_equivalence.py`) so the manual smoke check is supplementary, not solo.

**Checkpoint:** battle_controller.py drops by ~125 LOC from the 2026-05-19 baseline of 682 LOC to ~555 LOC (the original "~700 LOC" target was derived from the now-stale 831-LOC baseline). New sibling module at ~150 LOC. Visual-mode start path manually verified. Automated spec-in guards green. Sharded suite green.

### Phase 3: F-D-011 partial — split `replay_serialization.py` into `replay_capture_serde.py` + `replay_outcome_serde.py` + shared helpers [Medium]
**Closes the replay_serialization.py portion of F-D-011.**

`replay_serialization.py` is 516 LOC as of 2026-05-19 (was 634 LOC at original drafting) and splits naturally at the spec/outcome boundary (`def battle_outcome_to_dict(...)` — now at line ~540-542; was ~407 at original drafting; Phase 3 Task 3.0 re-measures and records the exact line):
- Spec-side (above the boundary): BattleSpec capture path — Vector2 helpers, Boundary, ModifierStack, ComponentStateSpec, ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec, BattleSpec serialization.
- Outcome-side (below the boundary): BattleOutcome / replay-load path — ModifierApplication, HitRecord, WeaponSummary, ShipStats, ShipOutcome, TeamOutcome, BattleOutcome serialization, plus `compute_components_registry_hash`.

**Important — file naming.** The package already contains `game/simulation/replay/replay_capture.py` (the runtime capture-sink hook owning `IReplayCaptureSink` / `NullCaptureSink` / `ReplayCaptureContext` — see `game/simulation/replay/__init__.py:25-32`). The new modules MUST use distinct names. The chosen naming is:
- **`replay_capture_serde.py`** — spec-side serialization (lines 78-407 of the old file).
- **`replay_outcome_serde.py`** — outcome-side serialization (lines 407-634 of the old file).
- **`replay_serde_helpers.py`** — shared helpers (extracted from the split-boundary code).

**Shared-helper plan (Option A — shared module).** The proposed line-407 split is not clean as-is: outcome-side code (`replay_serialization.py:481-518`, ship_outcome serde) depends on `_vec_to_list` / `_list_to_vec` (defined at :78-85) and `_component_state_to_dict` / `_component_state_from_dict` (defined at :222-240), which are first used by spec-side code. Three options were considered:
- **Option A (chosen):** Extract shared helpers (`_vec_to_list`, `_list_to_vec`, `_component_state_to_dict`, `_component_state_from_dict`) into a third module `replay_serde_helpers.py` that both halves import. Cleanest separation; no circular risk; both serde modules have a single, well-defined import direction.
- **Option B:** Duplicate the shared helpers in each module. Rejected — the helpers are non-trivial (especially `_component_state_to_dict` at 7+ fields), and duplication invites drift.
- **Option C:** Keep one half as a "leader" exporting helpers; the other imports from it. Rejected — creates a non-obvious dependency direction between two peer modules.

Both serde halves end up under 350 LOC; the helpers module is ~20-30 LOC. All three are well below the ceiling.

**Save-load tests + replay tests are the critical regression gate.** A subtle import drift here could break replay capture or playback.

- Create `game/simulation/replay/replay_serde_helpers.py` first (the shared helpers — both new modules will import from it).
- Create `game/simulation/replay/replay_capture_serde.py` for the spec-side (lines 78-407 minus extracted helpers, plus REPLAY_SCHEMA_VERSION constant).
- Create `game/simulation/replay/replay_outcome_serde.py` for the outcome-side (lines 407-634 minus extracted helpers; imports `REPLAY_SCHEMA_VERSION` from `replay_capture_serde` only if needed, otherwise leave it in `replay_capture_serde`).
- Update `game/simulation/replay/__init__.py` re-exports (lines 33-45) to point to the new modules. All package-root callers (`from game.simulation.replay import ...`) keep working with one update to `__init__.py`.
- Delete `replay_serialization.py` (don't keep as a re-export shim per CLAUDE.md "no compat shims" rule). Update all DIRECT imports (`from game.simulation.replay.replay_serialization import ...`) AND verify package-root callers (`from game.simulation.replay import ...`) still resolve via the updated `__init__.py`.
- Run the full test suite. Replay capture / playback / verification round-trips MUST round-trip byte-identical.

**Targeted gate:**
```powershell
pytest tests/integration/replay/ tests/unit/simulation/replay/ -q -n 4
python Tools/test_sharded/test_sharded.py
```

**Checkpoint:** replay_serialization.py replaced by replay_capture_serde.py (~310 LOC) + replay_outcome_serde.py (~210 LOC) + replay_serde_helpers.py (~30 LOC). Replay round-trips byte-identical. Sharded suite green. All `from game.simulation.replay.replay_serialization import ...` direct callers migrated; all `from game.simulation.replay import ...` package-root callers continue to resolve via updated `__init__.py`.

### Phase 4: Document the 10 remaining over-ceiling simulation files as next-touch [Simple]
**Discipline phase.** No code touched. Document only.

Per Codex r4 risk callout: "Keep the other 10 over-ceiling simulation files as 'next-touch', not inline scope." This phase makes the discipline explicit in writing.

- Add to `decisions.md` one entry per file (10 total), each with: file path, current LOC, "no clean cut identified in PROJ-460 scope; revisit on next touch".
- Optionally add a single consolidated "next-touch ledger" entry in `findings/PROJ-460_findings.md` linking back to the F-D-011 original finding and Codex r4 Job 12 framing.
- NO code changes. NO file splits attempted. NO charters scaffolded for these.
- A future project may scaffold one of these (e.g., "battle_engine.py LOC reduction"), but that's a separate decision driven by the next touch on that file, not by this project's scope.

**Targeted gate:** none (no code changes). Sharded suite green from Phase 3 is sufficient.

**Checkpoint:** `decisions.md` carries 10 next-touch entries. PROJ-460 scope explicitly held to 3 files; the 10 others remain as next-touch.

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (`01_ARCHITECTURE.md`, `02_PATTERNS.md`, `03_CONVENTIONS.md`)
- [ ] Read `game/strategy/data/planet_serde.py` (template)
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — all green (establishes baseline)

### After Each Phase
- [ ] Run targeted gate listed in the phase
- [ ] Run sharded suite — no regression vs baseline
- [ ] Save-load round-trip byte-identical (Phase 1 specifically)
- [ ] Replay round-trip byte-identical (Phase 1 + Phase 3 specifically)
- [ ] Update `plan.md` Current State

### Final Verification
- [ ] All 4 phases checked off
- [ ] battle_state.py, battle_controller.py, replay_serialization.py — three Phase 1/2/3 cuts landed
- [ ] 10 next-touch entries in `decisions.md`
- [ ] `findings/PROJ-460_findings.md` updated with final status per finding (F-D-028 closed; F-D-011 actionable slice closed; F-D-011 next-touch ledger documented)
- [ ] Save-load tests green (`pytest tests/integration/save_load/`)
- [ ] Replay tests green (`pytest tests/integration/replay/`)
- [ ] Sharded suite green
- [ ] Manual smoke test: start a battle via BattleSetupScreen, confirm no visual-mode regression
- [ ] Docs updated if architecture/patterns changed
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 battle_state_serde extraction landed (F-D-028 closed)
- [ ] Phase 2 battle_controller spec-in extraction landed (F-D-011 partial closed)
- [ ] Phase 3 replay_serialization split landed (F-D-011 partial closed)
- [ ] Phase 4 next-touch documentation written (10 files in decisions.md)
- [ ] All tests passing
- [ ] Manual UI smoke test passed
- [ ] Audit passed (no significant issues; in particular: no "structural omnibus" scope creep into the 10 next-touch files)
- [ ] User verified
