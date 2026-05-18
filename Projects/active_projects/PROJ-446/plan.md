# PROJ-446: Post-refactor residue — UI + Core + Tests layer (Bucket C)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-446` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-446 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test wallpaper removal (skipped-but-vacuous, stale skips) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Static-guard backfill + protocol read-only narrowing | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI back-compat shim retirement (transfer_dialog, battle_setup, new_game_setup, etc.) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI LOC-ceiling extraction (build_queue_screen, planet_list_window) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Deferred UIWindow retrofit closure (SettingsWindow + 4 planet target editors) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Phase 3 (UI back-compat shim cluster retirement) — NOT YET STARTED
**Last Action:** Stage 1 complete (Phases 1 + 2). Phase 1 closed 7 wallpaper-skip findings (F-C-016, F-C-022, F-C-023, F-C-024, F-C-025, F-C-026, F-C-021-superseded); Phase 2 closed 5 surface-cracks findings (F-C-013, F-C-014, F-C-018, F-C-019, F-C-030). Phase 1 sharded suite: 23,317 passed / 0 failed. Phase 2 targeted suites: 1,841 passed (static_guards + unit/core). Phase 2 full sharded run still recommended before Phase 3 starts.
**Next Action:** STOP — Phase 3 (UI shim cluster retirement) is materially bigger than Phases 1+2 together and starts only under separate explicit direction from the user. The 9 UI shim clusters (F-C-001..F-C-012 minus already-noted exclusions, plus F-C-015 + F-C-029 paired-DI sweeps, plus F-C-020 STRUCTURAL JOINT-PHASE with PROJ-444) should be scoped and sequenced afresh. Cross-bucket coordination note dropped into decisions.md: `docs/known-issues.md` still carries the obsolete "Stale-doc warning" pointing at the (now-fixed) `tests/fixtures/README.md`; PROJ-447 owns `docs/**` in this stage's file partition and should drop that paragraph.
**Blockers:** Phase 5 (UIWindow retrofits) is genuinely 5 mini-projects in a trench coat — likely needs to spin off rather than ship under PROJ-446

## Overview

Residue cleanup for the **`game/ui/` + `game/core/` + broader `tests/`** layer accumulated across ~22 archived refactors. Companion project to PROJ-444 (data + facade) and PROJ-445 (engine + services) — by design the three projects touch **disjoint file sets** so they can run in parallel without merge conflicts.

This is the largest bucket by raw count (30 findings) **and** by spread (UI is the most-touched layer in the refactor history — PROJ-275, PROJ-309, PROJ-322-328, PROJ-329A, PROJ-343, PROJ-374, PROJ-376, PROJ-392, PROJ-435, PROJ-437 all left UI residue). It also owns the bulk of test-inconsistency findings (8) because test infrastructure crosses layers but most of the wallpapered skips and stale fixtures live in UI/builder/regression suites.

The single largest cluster: **back-compat property shims on UI screens.** Nine distinct shim clusters survive across battle_setup, new_game_setup, transfer_dialog, strategy_renderer, orders_window, race_setup, event_log_window, build_queue_screen. Each was created by a controller/view-model MVVM split, kept "until tests migrate," and never migrated.

## Goals

- **(Phase 1)** Stop CI's silent passes. 30+ `pytest.skip(...)` paths across the test tree currently fire when fixtures aren't there, baselines don't exist, or data files were deleted — each one is a test slot that asserts nothing.
- Backfill the two missing static guards (`DesignLibrary`, `_ACTIVATABLE_ABILITIES`) so the retirement projects PROJ-434 and PROJ-435 land their full surface contract — the existing guards (`test_no_resource_types_constant`, `test_no_legacy_storage_fields`, `test_no_carried_items_proxy`, `test_no_legacy_protocol_names`) are the established pattern; these two are the gaps.
- Narrow `IShipInstance.cargo_contents` and `IFacility.consumable_levels` protocol surfaces from writable `Dict` to read-only `Mapping` so callers using the protocol can't quietly bypass the manager APIs PROJ-436 introduced.
- Retire the 9 back-compat property shim clusters by migrating the test sites first, then deleting the screen-level `@property` blocks. Same recipe PROJ-437 Phase 4 used for transfer_dialog's dialog-level shims.
- Backfill the deferred companion fixes that the existing `discovered_issues/log.jsonl` entries already named: `LABEL_ABBREV` label-side companion (F-C-015 → DI-2026-05-18-004) and the transfer_dialog characterization-test sweep (F-C-029 → DI-2026-05-18-002).
- Close out the protocol-surface modernization (legacy `Dict`/`List`/`Optional` → modern syntax) across the 7 of 9 `game/core/protocols/*.py` files that still use the legacy form.

## Scope

**In (this project owns these files):**
- All files under `game/ui/` (screens, panels, widgets, dialogs — every subdir)
- `game/core/protocols/` (the entire protocol surface)
- `game/core/exceptions.py`
- `tests/static_guards/` (existing guards + 2 new)
- `tests/regression/modifier_ability_snapshots/`
- `tests/fixtures/` (shared fixture modules + README)
- All `tests/` files whose primary subject is a UI screen, a protocol member, or a core module

**Out (PROJ-444 owns these — do NOT touch in this project):**
- `game/strategy/data/`, `game/strategy/facade/`
- `tests/unit/strategy/data/`, `tests/unit/strategy/facade/`
- Save/load integration tests

**Out (PROJ-445 owns these — do NOT touch in this project):**
- `game/strategy/engine/`, `game/strategy/services/`
- Engine/services tests

**Out (deferred to future projects regardless of layer):**
- PROJ-443 (pytest norecursedirs fix and hidden-test triage) — already chartered, partially overlapping with this project's Phase 1
- Phase 5 (UIWindow retrofits) may need to spin out as 5 mini-projects rather than ship inline — see Phase 5 notes

## Findings Summary

Full report: [findings/bucket_c_ui_core_tests_scan.md](findings/bucket_c_ui_core_tests_scan.md) (30 findings)

| Severity | Count | Notes |
|----------|-------|-------|
| High     | 0     | (no high-severity items in this layer — the load-bearing scary findings are all engine-side in PROJ-445) |
| Medium   | 12    | Static-guard gaps, protocol surface cracks, large LOC overflows, wallpapered regression-snapshot skips |
| Low      | 18    | Polish, individual shim clusters, stale comments |

| Category | Count |
|----------|-------|
| Obsolete-code | 14 |
| Test-inconsistency | 8 |
| Missing-functionality | 3 |
| Polish | 5 |

### Cross-bucket couplings — coordination points and structural joint-phase seams
- **(Coordination)** **F-C-014** — `IShipInstance.cargo_contents` writable-dict-view protocol crack. The concrete-class setter is on PROJ-444's `ship_instance.py` (`_ship_instance_init_with_legacy_kwargs` wrapper, F-A-003/F-A-005). PROJ-446 narrows the protocol annotation (`Dict` → `Mapping`) now; the wrapper retirement that completes the fix lives in PROJ-444 Phase 3.
- **(STRUCTURAL JOINT-PHASE)** **F-C-020 + PROJ-444 F-A-003 / F-A-005** — Codex consult 2026-05-18 verified this is NOT mere coordination. The shared fixture `tests/fixtures/strategy_entities.py` legacy-kwarg sites are the structural unblock for PROJ-444's wrapper retirement (Phase 3). The wrapper retirement cannot land cleanly without first editing this fixture file, which PROJ-446 owns. **Either rebucket F-C-020 into PROJ-444's wrapper-retirement phase, or commit to a stacked PR / joint phase across PROJ-444 + PROJ-446.** The legacy-kwarg test footprint is materially larger than PROJ-443's earlier 18-file estimate; size with a fresh `rg` count before committing.
- **(Coordination)** **F-C-015** — `stat_rows_dynamic.py` `LABEL_ABBREV` label-side. The IDs-side fix is captured in `discovered_issues/log.jsonl` as DI-2026-05-18-004. F-C-015 is its label-side companion. This project closes both as a paired fix.
- **(Coordination)** **F-C-029** — 70+ `dialog._row_data` / `dialog._current_source` references in transfer_dialog characterization tests. Pinned in `discovered_issues/log.jsonl` as DI-2026-05-18-002 (the 23-LOC-over-ceiling finding). This project closes both as a paired fix (drops the file under the ceiling).
- **(Coordination)** **F-C-016 + F-C-022 + PROJ-443** — Hidden-test triage scope overlap. PROJ-443 owns the broader hidden-test surface; this project's scope is just the documented-skip cases. Avoid double-fixing.

## Key Files

### UI screens with back-compat shim clusters
| Component | File Path | LOC | Findings |
|-----------|-----------|-----|----------|
| BattleSetupState | `game/ui/screens/battle_setup_state.py` | <500 | F-C-001 (side_0/side_1) |
| BattleSetupScreen | `game/ui/screens/battle_setup/screen.py` | **559** | F-C-009 (~11 VM/controller shims) |
| TransferDialog | `game/ui/screens/transfer_dialog.py` | 523 (DI log) | F-C-002, F-C-003, F-C-011, F-C-029 |
| StrategyRenderer | `game/ui/screens/strategy_renderer.py` | <500 | F-C-004 (6 cache-attr shims) |
| draw_grid free fn | `game/ui/screens/strategy_render/grid.py` | <500 | F-C-005 |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` | **961** | F-C-006, F-C-027 |
| RaceSetupScreen | `game/ui/screens/race_setup/screen.py` | <500 | F-C-007 |
| NewGameSetupScreen | `game/ui/screens/new_game_setup_screen.py` | **734** | F-C-008 (6 VM shims), F-C-027 |
| OrdersWindow | `game/ui/screens/orders_window.py` | <500 | F-C-010 |
| EventLogWindow | `game/ui/screens/event_log_window.py` | **732** | F-C-012, F-C-027 |
| stat_rows_dynamic | `game/ui/screens/builder/stat_rows_dynamic.py` | <500 | F-C-015 (+ DI-004 companion) |

### Core protocol surface
| Component | File Path | Findings |
|-----------|-----------|----------|
| Strategy domain protocols | `game/core/protocols/strategy_domain.py` | F-C-013, F-C-014, F-C-030 |
| Other protocol modules | `game/core/protocols/{strategy_entities,boundary,combat,persistence,common,registry}.py` | F-C-030 |
| Core exceptions | `game/core/exceptions.py` | **544** LOC; F-C-028 |

### Static guards
| Component | File Path | Findings |
|-----------|-----------|----------|
| Missing: DesignLibrary guard | `tests/static_guards/test_no_design_library_class.py` (to create) | F-C-018 |
| Missing: ACTIVATABLE_ABILITIES guard | `tests/static_guards/test_no_activatable_abilities_constant.py` (to create) | F-C-019 |

### Tests with wallpapered skips
| File | Skips | Findings |
|------|-------|----------|
| `tests/integration/research_workflow/test_workflow.py` | 1 stale | F-C-021 |
| `tests/unit/builder/test_builder_ui_sync.py` | 1 wallpapered | F-C-022 |
| `tests/unit/quickstart/test_quickstart_designs.py` | 1 contract-violating | F-C-023 |
| `tests/unit/modifiers/test_pipeline_unification.py` | 5-6 wallpapered | F-C-024 |
| `tests/regression/modifier_ability_snapshots/test_*.py` | 16+ baseline-missing | F-C-025 |
| `tests/unit/data/test_data_validation.py` | 2 vacuous (PROJ-40) | F-C-026 |
| `tests/fixtures/strategy_entities.py` | (legacy kwargs) | F-C-020 |
| `tests/fixtures/README.md` | (stale doc) | F-C-016 |
| `tests/unit/ui/screens/test_transfer_dialog*.py` | (70+ shim writes) | F-C-029 |

### UIWindow retrofits deferred since PROJ-329A (no DEDICATED behavior-locking retrofit tests; incidental coverage exists)
| Component | File Path | LOC | Findings | Existing incidental coverage |
|-----------|-----------|-----|----------|------------------------------|
| SettingsWindow | `game/ui/screens/settings_window.py` | 109 | F-C-017 | `test_empire_panel_ctrl.py:100-127` via SettingsRegistrar |
| AtmosphereTargetEditor | `game/ui/screens/atmosphere_target_editor.py` | 273 | F-C-017 | `test_strategy_modal_window.py:367-398` (window-manager contract) |
| GravityTargetEditor | `game/ui/screens/gravity_target_editor.py` | 220 | F-C-017 | `test_strategy_modal_window.py:367-398` |
| WaterTargetEditor | `game/ui/screens/water_target_editor.py` | 227 | F-C-017 | `test_strategy_modal_window.py:367-398` |
| RadiationShieldEditor | `game/ui/screens/radiation_shield_editor.py` | 231 | F-C-017 | `test_strategy_modal_window.py:367-398` |

## Phase Breakdown

### Phase 1 — Test wallpaper removal (clear CI noise first)

These are independent fixes; pick them off in any order. Each removes a `pytest.skip` that quietly hides regressions:

- F-C-021: Delete or harden the `Tech tree JSON not found` skip in `tests/integration/research_workflow/test_workflow.py:192`
- F-C-022: Replace `No vehicle classes found` skip in `tests/unit/builder/test_builder_ui_sync.py:163` with explicit non-empty assertion
- F-C-023: Make missing `expected_stats` a failure in `tests/unit/quickstart/test_quickstart_designs.py:133`, per the documented convention
- F-C-024: Re-tool the 5-6 hardcoded-component skips in `tests/unit/modifiers/test_pipeline_unification.py` to dynamic component lookup
- F-C-025: Commit the regression-snapshot baselines (or change skip-on-missing to fail-on-missing) for the 16+ `tests/regression/modifier_ability_snapshots/` skips
- F-C-026: Delete the two PROJ-40 vacuous test functions in `tests/unit/data/test_data_validation.py`
- F-C-016: Rewrite `tests/fixtures/README.md` UIWindow factory section to point at Pattern #33 (docs/known-issues.md already flags it)

### Phase 2 — Static-guard backfill + protocol surface narrowing

- F-C-018: Create `tests/static_guards/test_no_design_library_class.py` mirroring `test_no_carried_items_proxy.py` pattern
- F-C-019: Create `tests/static_guards/test_no_activatable_abilities_constant.py` mirroring `test_no_resource_types_constant.py` pattern
- F-C-013: Document `IFacility.consumable_levels` as intentional-inconsistency in the protocol docstring (preserves the existing ratchet test's "stay-as-is" decision)
- F-C-014: Narrow `IShipInstance.cargo_contents` annotation from `Dict[str, int]` to `Mapping[str, int]` (coordinated with PROJ-444 Phase 3)
- F-C-030: Mechanical sweep of 7 protocol modules: `Dict[K,V]` → `dict[K,V]`, `List[X]` → `list[X]`, `Optional[X]` → `X | None`, add `from __future__ import annotations` as needed

### Phase 3 — UI back-compat shim cluster retirement

Nine clusters; same recipe per cluster (find test/peer reads → migrate to canonical source → delete property block). Order by smallest-first:

- F-C-005: `draw_grid` free function deletion (2 test-file edits)
- F-C-006: `build_context=` legacy kwarg sweep + delete
- F-C-007: `RaceSetupScreen._description_controller` shim retire
- F-C-010: `OrdersWindow._get_order_description` shim retire
- F-C-012: `EventLogWindow.empire_name=None` fallback delete
- F-C-001: `BattleSetupState.side_0` / `side_1` (~30 mechanical edits across 2 production + 5 test files)
- F-C-002: Add `# Intentional broad catch: <reason>` marker on `transfer_dialog.py:412`
- F-C-003 + F-C-011 + F-C-029 (+ DI-2026-05-18-002): Joint sweep of all transfer_dialog test reaches off shim surface; delete the three method shims + sentinels/layout constant re-exports. **This closes DI-2026-05-18-002 and drops transfer_dialog.py under the 500-LOC ceiling.**
- F-C-004: `StrategyRenderer` 6 cache-attr shims
- F-C-008: `NewGameSetupScreen` 6 VM property shims (largest cluster; ~734 LOC file likely drops under ceiling after)
- F-C-009: `BattleSetupScreen` ~11 VM+controller shims (~559 LOC file likely drops under ceiling after)
- F-C-015 (+ DI-2026-05-18-004): `stat_rows_dynamic.py` LABEL_ABBREV label-side closure (paired with the existing log entry IDs-side fix). Single PR closes both halves.
- F-C-020: `tests/fixtures/strategy_entities.py` migrate 3 fixture sites off legacy kwargs (unlocks PROJ-444's F-A-003 retirement)

### Phase 4 — UI LOC-ceiling extraction

After Phase 3 several files naturally drop. The remaining hard cases:

- F-C-027: Extract one responsibility from `build_queue_screen.py` (961 LOC; pick yard population or queue selection) into a sibling module
- F-C-027: Same recipe for `planet_list_window.py` (862), `test_lab/screen.py` (744), `empire_build_queue_window.py` (734), `panels/race_summary_panel.py` (732), `empire_panel_window.py` (724), `panels/build_queue_controller.py` (723), `panels/system_tree_panel.py` (711), `design_selector_window.py` (708), `strategy_detail_fmt.py` (707) — at least the top 3 in scope; the rest tracked for future visibility
- F-C-028: Split `game/core/exceptions.py` (544) by domain — `exceptions_persistence.py`, `exceptions_validation.py`, etc. — with the top-level `exceptions.py` re-exporting for back-compat (allowed per the convention since the class has many callers)

### Phase 5 — Deferred UIWindow retrofit closure (CONSIDER SPIN-OUT)

F-C-017 captures 5 UI windows lacking DEDICATED behavior-locking retrofit tests (Codex 2026-05-18 verified incidental coverage exists via window-manager and registrar contract suites; the gap is dedicated characterization passes, not "zero coverage" as the original framing claimed). PROJ-329A explicitly deferred them until they gained dedicated coverage. This phase is genuinely 5 sub-projects in a trench coat — each window needs characterization tests + a two-stage retrofit. Recommendation: extract this as **PROJ-448 / PROJ-448A-E** (or whatever the next available IDs are at the time — PROJ-447 was consumed by the r2 supplemental scan) when PROJ-446 reaches it. Track here for visibility only.

- SettingsWindow (109 LOC, smallest, best starter)
- AtmosphereTargetEditor (273 LOC)
- GravityTargetEditor (220 LOC)
- WaterTargetEditor (227 LOC)
- RadiationShieldEditor (231 LOC)

## Related Documents

- [design.md](design.md) — Architecture analysis and parallelism contract with PROJ-444/445
- [decisions.md](decisions.md) — Full decisions log including PROJ-443 coordination
- [findings/bucket_c_ui_core_tests_scan.md](findings/bucket_c_ui_core_tests_scan.md) — Source scan, 30 findings with file:line citations
- [`AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md`](../../../AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md) — Top-level review report (covers all 3 buckets)
- [`AgentCoordination/discovered_issues/log.jsonl`](../../../AgentCoordination/discovered_issues/log.jsonl) — 9 prior entries; 2 of them (DI-002 transfer_dialog, DI-004 LABEL_ABBREV) have their companion fix sites in this project

## Sibling Projects

| Project | Layer | Findings | High-severity items |
|---------|-------|----------|---------------------|
| [PROJ-444](../PROJ-444/plan.md) | data + facade | 32 | 0 |
| [PROJ-445](../PROJ-445/plan.md) | engine + services | 22 | 1 (LayMines TypeError) |
| PROJ-446 (this) | ui + core + tests | 30 | 0 |

## Verification

- [ ] All phase checklists complete
- [ ] All 30 findings either fixed, deferred-with-rationale (UIWindow retrofits expected to spin out), or recategorized
- [ ] No `pytest.skip` paths remaining that silently mask real failures
- [ ] DesignLibrary + ACTIVATABLE_ABILITIES static guards in place and green
- [ ] DI-2026-05-18-002 (transfer_dialog 523 LOC) + DI-2026-05-18-004 (LABEL_ABBREV) closed in log.jsonl
- [ ] Full sharded test suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] No new entries in `discovered_issues/log.jsonl` during this project (or new entries are real out-of-scope discoveries)
- [ ] Audit passed
- [ ] User verified
