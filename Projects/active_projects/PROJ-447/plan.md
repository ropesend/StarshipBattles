# PROJ-447: Post-refactor residue — Simulation + AI + Research + LowLevelEngine + Docs (Bucket D supplemental)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-447` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-447 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Docs drift cleanup (deleted-class references in docs/) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Stale-comment cleanup (simulation/ai narrating retired surfaces) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Pre-PEP-604 annotation sweep (research/assets/engine/simulation loaders) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test-wallpaper + static-guard backfill | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation LOC-ceiling extractions (battle_state, battle_controller, etc.) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning
**Last Action:** Charter created from supplemental Bucket D scan ([findings/bucket_d_simulation_ai_research_engine_docs_scan.md](findings/bucket_d_simulation_ai_research_engine_docs_scan.md), 28 findings)
**Next Action:** User review of phasing. Phase 1 (docs drift) is the natural starting point — 7 small text-only fixes, no code risk.
**Blockers:** None

## Overview

Supplemental residue cleanup for layers the original 3-bucket scan (PROJ-444/445/446) SILENTLY OMITTED: `game/simulation/`, `game/ai/`, `game/research/`, `game/engine/` (the low-level combat engine, distinct from `game/strategy/engine/`), `game/assets/`, and `docs/`.

**Origin:** Codex independent verification of the original review on 2026-05-18 surfaced 4 concrete residue sites in these layers and flagged the scope gap. A 4th supplemental scan (Bucket D) confirmed all 4 codex seeds (F-D-001..F-D-004) and identified 24 additional findings. The seeds:

- `game/simulation/services/design_loader.py:39` — class docstring still tells callers to use deleted `DesignLibrary.load_design_data()` (PROJ-427/PROJ-434 retirement)
- `game/simulation/entities/ship_stats.py:209-210` — inline comment references retired `ShipInstance.carried_items` surface (PROJ-431/PROJ-436 retirement)
- `tests/unit/strategy/engine/test_command_specs_contract.py:85-87` — assertion message tells maintainers to add entries in deleted `commands/specs.py` (PROJ-371 retirement)
- `docs/systems/ability_reference.md:554` — maintainer recipe instructs updating deleted `_ACTIVATABLE_ABILITIES` (PROJ-429 retirement)

Each was independently re-verified by Bucket D against the current code.

## Goals

- Stop docs/ from lying about current behavior. Docs name 4+ deleted classes (`DesignLibrary`, `_ACTIVATABLE_ABILITIES`, `AreaEffectManager`, `EnvironmentalEffects`) as if they were current production surfaces. Maintainers following these recipes will hit `ImportError` or re-introduce regression.
- Sweep simulation + AI inline comments and docstrings narrating retired substrates (`carried_items` direct field access, `cargo_contents` pre-PROJ-436 references, the pre-PROJ-228 plain-string CLOSE_WARP_POINT target shape, the pre-PROJ-269 `BattleController`-slated-for-deletion narration).
- Modernize the remaining pre-PEP-604 annotations across the lower-layer loaders (`research/`, `assets/`, `engine/`, `simulation/` loaders) — the sibling sweep to PROJ-446's F-C-030 for protocol modules.
- Close the test-wallpaper + missing-guard gaps the original scan missed: `test_workflow.py:188-192` tech_tree skip wallpaper (corrects PROJ-446's F-C-021 filename), missing static guard against `commands/specs.py` re-emergence (sibling to PROJ-446 F-C-018/F-C-019).
- Extract the simulation-layer LOC-ceiling violators where the split target is clean (battle_state.py serialization extraction; battle_controller.py orchestration extraction). 9 simulation files >500 LOC; the worst two are 832 and 831.

## Scope

**In (this project owns these layers — explicitly NOT owned by PROJ-444/445/446):**
- `game/simulation/` — all entities, services, components, systems, abilities, managers, replay
- `game/ai/` — controllers and behaviors
- `game/research/` — tech tree, research progression
- `game/engine/` — the low-level combat engine (`collision.py`, `physics.py`, `__init__.py`). DISTINCT from `game/strategy/engine/` which belongs to PROJ-445.
- `game/assets/` — asset manager, manifest loaders
- `docs/` — all documentation files (architecture, patterns, conventions, systems guides, error handling docs)
- `game/strategy/interfaces/` — Codex flagged that the original 3-bucket cut also missed this protocol/interface boundary directory; F-D-010 lives here

**Out (already owned by other projects):**
- PROJ-444: `game/strategy/data/`, `game/strategy/facade/`
- PROJ-445: `game/strategy/engine/`, `game/strategy/services/`
- PROJ-446: `game/ui/`, `game/core/`, `tests/static_guards/`, `tests/regression/`, fixture/conftest tests
- PROJ-443: Hidden-test triage broad sweep

**Tests:**
- Test files whose primary subject is a `game/simulation/` / `game/ai/` / `game/research/` / `game/engine/` / `game/assets/` class belong here
- Test files where the subject sits in another bucket but a Bucket D residue site is named in the test (e.g., the `test_command_specs_contract.py` assertion-message fix) belong here when the fix is purely the test-side message
- Static guards backfilling Bucket D retirements (e.g., F-D-025 `commands/specs.py` re-emergence guard) belong here even though `tests/static_guards/` is nominally PROJ-446's home — coordinate via decisions.md if conflict

## Findings Summary

Full report: [findings/bucket_d_simulation_ai_research_engine_docs_scan.md](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) (28 findings)

| Severity | Count | Notes |
|----------|-------|-------|
| High     | 0     | (no high-severity items in this bucket) |
| Medium   | 11    | Docs drift naming deleted classes (F-D-001/D-003/D-005), simulation LOC overflows (F-D-011/D-028), asset manager untyped public surface (F-D-015) |
| Low      | 17    | Stale comments, pre-PEP-604 annotation drift, test wallpaper, missing guard |

| Category | Count |
|----------|-------|
| Obsolete-code | 14 |
| Test-inconsistency | 3 |
| Missing-functionality | 4 |
| Polish | 7 |

### Cross-bucket couplings

- **F-D-003 + F-D-025** — Test assertion message points at deleted `commands/specs.py`; no static guard against file re-emergence. F-D-025 lives in `tests/static_guards/` which is nominally PROJ-446's home. Two options: (a) PROJ-446 absorbs F-D-025 since they own static_guards/, (b) PROJ-447 ships both as paired companion fixes. Recommend (b) since the missing-guard rationale comes from the same retirement (PROJ-371) as the assertion-message fix.
- **F-D-013 + F-D-016 + F-D-017 + F-D-018 + F-D-019 + PROJ-446 F-C-030** — Pre-PEP-604 annotation drift. PROJ-446 F-C-030 covers the 7 `game/core/protocols/*.py` files; PROJ-447 covers the parallel surface across research/assets/engine/simulation loaders. Coordinate by sequence; same mechanical recipe (`Dict` → `dict`, `Optional[X]` → `X | None`, etc.).
- **F-D-020 + PROJ-446 F-C-021** — `tests/integration/research_workflow/test_workflow.py` tech-tree skip. PROJ-446 F-C-021 named the file but cited the wrong path (`tech_tree.json` doesn't exist; real filename is `data/techtree.json`). PROJ-447 closes the actual finding with the corrected filename. PROJ-446 should mark F-C-021 as superseded.
- **F-D-024 + PROJ-445 F-B-016** — `game/strategy/services/fleet_speed_calculator.py:175` `EnvironmentalEffects` docstring reference. Bucket B's scan explicitly noted this as a sibling site of F-B-016 but did not file an entry. PROJ-445 should fold this fix into F-B-016's edit.

## Key Files

### Docs drift (the loud ones)
| File | Findings | Issue |
|------|----------|-------|
| `docs/05_ERROR_HANDLING.md:17,335` | F-D-005 | Names deleted `design_library.py` + dead pytest path |
| `docs/systems/production_system.md:553,50-61` | F-D-006, F-D-008 | Deleted `design_library.py` row; mutable-default `={}` in example |
| `docs/systems/strategy_layer.md:32` | F-D-007 | Names `DesignLibrary` as current UI collaborator |
| `docs/systems/ability_reference.md:554` | F-D-004 (codex seed) | Recipe instructs editing deleted `_ACTIVATABLE_ABILITIES` |

### Simulation comment rot
| File | Findings | Issue |
|------|----------|-------|
| `game/simulation/services/design_loader.py:39, 1-13` | F-D-001 (codex seed), F-D-026 | Docstring names deleted `DesignLibrary.load_design_data()` + PROJ-30 era provenance |
| `game/simulation/entities/ship_stats.py:208-211` | F-D-002 (codex seed) | Comment narrates retired `ShipInstance.carried_items` |
| `game/simulation/entities/stat_contributors/launch.py:111` | F-D-022 | Same as F-D-002 |
| `game/simulation/components/abilities/vehicle_bay.py:5` | F-D-023 | "Generalises the previous..." migration-in-progress framing |
| `game/simulation/battle_runner.py:8-12` | F-D-009 | "Slated for deletion" lie about BattleController/Config/Mode |
| `game/strategy/interfaces/engines/combat.py:82,87` | F-D-010 | `IEnvironmentalHazardEngine` docstring references deleted `AreaEffectManager` |
| `game/ai/carrier_controller.py:275-279` | F-D-021 | `_pop_carried_vehicles_legacy` name + stale narration |

### Tests
| File | Findings | Issue |
|------|----------|-------|
| `tests/unit/strategy/engine/test_command_specs_contract.py:85-87` | F-D-003 (codex seed) | Assertion message names deleted `commands/specs.py` |
| `tests/integration/research_workflow/test_workflow.py:188-192` | F-D-020 | Skip-on-FileNotFoundError wallpaper for `data/techtree.json` |
| `tests/static_guards/` (new file) | F-D-025 | Missing AST guard against `commands/specs.py` re-emergence |

### Pre-PEP-604 annotation drift
| File | Findings |
|------|----------|
| `game/research/data/tech_tree.py:26,31` | F-D-013, F-D-014 |
| `game/assets/asset_manager.py:5,15,31,54,70,95,121` | F-D-015, F-D-016 |
| `game/engine/collision.py:68`, `physics.py:53` | F-D-017 |
| `game/simulation/components/component_loader.py:78,186` | F-D-018 |
| `game/simulation/entities/ship_loader.py:51,118` | F-D-019 |

### Simulation LOC ceiling
| File | LOC | Findings |
|------|-----|----------|
| `game/simulation/battle_state.py` | 832 | F-D-011, F-D-028 (clean serde extract target) |
| `game/simulation/battle_controller.py` | 831 | F-D-011 |
| `game/simulation/systems/battle_engine.py` | 758 | F-D-011 |
| `game/simulation/battle_runner.py` | 734 | F-D-011 (also has F-D-009 lie) |
| `game/simulation/replay/replay_serialization.py` | 634 | F-D-011 |
| `game/simulation/entities/ship.py` | 607 | F-D-011 |
| `game/simulation/systems/tactical_mine_resolver.py` | 597 | F-D-011 |
| `game/simulation/entities/stat_contributors/registry.py` | 570 | F-D-011 |
| `game/simulation/entities/ship_stats.py` | 559 | F-D-011 (also has F-D-002 stale comment) |
| `game/simulation/components/abilities/base.py` | 535 | F-D-011 |
| `game/simulation/systems/battle_end_conditions.py` | 532 | F-D-011 |
| `game/simulation/services/vehicle_design_service.py` | 516 | F-D-011 |
| `game/simulation/combat/fleet_aura_manager.py` | 515 | F-D-011 |

## Phase Breakdown

### Phase 1 — Docs drift cleanup (start here — text-only, no code risk)

7 findings, all `tiny` effort, all isolated text edits in `docs/`:

- F-D-004 (codex seed): Rewrite the `_ACTIVATABLE_ABILITIES` recipe step in `docs/systems/ability_reference.md:554` to point at `ability_metadata.py` + `EnergyFacet`
- F-D-005: Replace both `design_library.py` citations in `docs/05_ERROR_HANDLING.md` (cross-ref + pytest path)
- F-D-006: Replace `design_library.py` row in `docs/systems/production_system.md:553` with the `design_repository.py` + `design_catalog.py` split
- F-D-007: Replace `DesignLibrary` with `DesignCatalog` in `docs/systems/strategy_layer.md:32`
- F-D-008: Fix mutable-default `={}` in `docs/systems/production_system.md:50-61` PlanetaryFacility example

### Phase 2 — Stale-comment cleanup (simulation + AI + interfaces)

8 findings, mostly `tiny` effort, isolated docstring/comment edits:

- F-D-001 (codex seed): Rewrite `SimulationDesignLoader` class docstring → `DesignRepository.load_design_data` + `DesignCatalog.load_design_data`
- F-D-002 (codex seed): One-word swap on `ship_stats.py:208-211` comment
- F-D-009: Replace "slated for deletion" framing in `battle_runner.py:8-12`
- F-D-010: Rewrite `IEnvironmentalHazardEngine` docstring + uncompileable example at `game/strategy/interfaces/engines/combat.py:82,87`
- F-D-021: Rename `_pop_carried_vehicles_legacy` → `_pop_carried_vehicles_count_based`; drop stale PROJ-431 narration half
- F-D-022: One-word swap on `launch.py:111`
- F-D-023: Drop "Generalises the previous" migration narration in `vehicle_bay.py:5`
- F-D-024 (coordinated with PROJ-445 F-B-016): Fix `EnvironmentalEffects` reference in `fleet_speed_calculator.py:175` — fold into F-B-016's same-PR fix
- F-D-026: Trim `SimulationDesignLoader` module docstring; drop PROJ-30/PROJ-45/PROJ-50 archaeology

### Phase 3 — Pre-PEP-604 annotation sweep (mechanical)

6 findings, all `tiny`, mechanical search-and-replace:

- F-D-013, F-D-014: `game/research/data/tech_tree.py` — 2 sigs
- F-D-015, F-D-016: `game/assets/asset_manager.py` — 5 public methods + module singleton annotation
- F-D-017: `game/engine/collision.py`, `physics.py` — constructor annotations
- F-D-018: `game/simulation/components/component_loader.py` — 2 loaders
- F-D-019: `game/simulation/entities/ship_loader.py` — 2 loaders

Same recipe as PROJ-446 F-C-030 (protocols sweep); sequence with that one to avoid `from __future__ import annotations` churn.

### Phase 4 — Test-wallpaper + static-guard backfill

3 findings:

- F-D-003 (codex seed): Rewrite assertion message in `test_command_specs_contract.py:85-87` to point at `@command_spec(...)` decorator + `register(registry)` (per `docs/systems/orders_system.md`)
- F-D-020: Drop the try/except in `test_workflow.py:188-192` — let `FileNotFoundError` fail loudly. **Note:** PROJ-446 F-C-021 named the wrong filename (`tech_tree.json` doesn't exist; the file is `data/techtree.json`) — supersede F-C-021 when this fix lands.
- F-D-025: Create `tests/static_guards/test_no_commands_specs_module.py` asserting `game/strategy/engine/commands/specs.py` does not exist

### Phase 5 — Simulation LOC-ceiling extractions (CONSIDER SPIN-OUT)

13 files over the 500-LOC ceiling. Two have clean extraction targets:

- F-D-028: `battle_state.py` (832) — extract `to_dict`/`from_dict` for `BattleState` / `ComponentState` / `ShipState` / `BattleResults` into `battle_state_serde.py` (PROJ-372-style). Drops file by ~250-300 LOC.
- F-D-011 (battle_controller.py, 831): Extract spec-in `start_from_spec` flow into a sibling module.
- F-D-011 (replay_serialization.py, 634): Split capture vs replay paths.

The remaining 10 files don't have obvious clean cuts and are flagged-for-visibility. Recommendation: spin Phase 5 out as 2-3 dedicated extraction projects (one per file with clean cut) and track the rest as a "next-touch" rule rather than shipping inline.

## Related Documents

- [design.md](design.md) — Architecture analysis
- [decisions.md](decisions.md) — Full decisions log including cross-project coordination
- [findings/bucket_d_simulation_ai_research_engine_docs_scan.md](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — Source scan, 28 findings with file:line citations
- [`AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md`](../../../AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md) — Top-level review report
- [Codex consult response](../../../AgentCoordination/Scratchpad/Consult/20260518T174511Z_post-refactor-residue-review-verification/response.md) — Independent verification that surfaced this scope gap and seeded the 4 codex findings

## Sibling Projects

| Project | Layer | Findings | High-severity items |
|---------|-------|----------|---------------------|
| [PROJ-444](../PROJ-444/plan.md) | data + facade | 32 | 0 |
| [PROJ-445](../PROJ-445/plan.md) | engine + services | 22 | 1 (LayMines TypeError) |
| [PROJ-446](../PROJ-446/plan.md) | ui + core + tests | 30 | 0 |
| PROJ-447 (this) | simulation + ai + research + lowlevelengine + docs | 28 | 0 |
| **Total** | — | **112** | **1** |

## Verification

- [ ] All phase checklists complete
- [ ] All 28 findings either fixed, deferred-with-rationale (Phase 5 expected to spin out), or recategorized
- [ ] No `docs/` reference remains to deleted classes (`DesignLibrary`, `_ACTIVATABLE_ABILITIES`, `AreaEffectManager`, `EnvironmentalEffects`)
- [ ] PROJ-446 F-C-021 marked superseded by F-D-020 with corrected filename
- [ ] PROJ-445 F-B-016 fix includes the F-D-024 sibling site (`fleet_speed_calculator.py:175`)
- [ ] Static guard for `commands/specs.py` re-emergence in place and green
- [ ] Full sharded test suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Audit passed
- [ ] User verified
