# PROJ-456: UI back-compat shim retirement sweep (9 shim clusters + transfer_dialog characterization)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-456` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-456 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main` per user standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Smallest-shim cluster: `draw_grid` + broad-catch marker + 3 single-method shims | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `build_context` legacy-kwarg sweep | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. BattleSetupState `side_0` / `side_1` cluster (2 production + 5 test files) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. `transfer_dialog` cluster + characterization sweep (drops file under 500-LOC ceiling) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Big-three shim clusters: StrategyRenderer, NewGameSetupScreen, BattleSetupScreen | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 4 (transfer_dialog cluster + characterization sweep)
**Last Action:** Phase 3 complete. F-C-001 closed: migrated 84 `.side_0`/`.side_1` references (sized up from 81 in plan; live counts: controller.py 4, test_battle_setup_state 12, test_controller 37, test_spec_compiler 22, test_spec_compiler_formation 5, test_suppressor_effects 4) to `.sides[0]`/`.sides[1]`. Deleted the property+setter block + comment header at `battle_setup_state.py:172-192`. Sharded 23362/23362 green.
**Next Action:** Phase 4 Task 4.1 — transfer_dialog shim cluster (F-C-003 + F-C-011 + F-C-029).
**Blockers:** None.

## Checkpoint Log

### 2026-05-17 — project-456-start
- **Done so far**: PROJ-454 closed and merged at `ab2da0669`. Group B series progressing on schedule.
- **Key decisions**: Phase ordering is smallest-first per Codex r4 review-burden risk.
- **Open threads**: None.
- **Next action**: Phase 1 Task 1.1.
- **Cross-group state observed**: origin/main at `ab2da0669` (post-PROJ-454 merge). origin/group-a at `f4503847a`. origin/group-c at `067b27a06`. No `_doc_consolidation/` files on origin/main yet.

## Overview
Retire 9 UI back-compat property/method shim clusters that survived prior MVVM splits (PROJ-275, PROJ-309, PROJ-329A, PROJ-374, PROJ-376, PROJ-392, PROJ-437, etc.). The same recipe applies per cluster: find test/peer reads of the shim → migrate those callers to the canonical source (controller / view-model / renderer / layer-object) → delete the shim block. Phase 4 also retires `transfer_dialog.py`'s sentinel/layout-constant class re-exports and the 6 dialog-level property shims; the file's LOC drops further from its current 448 (already under the 500-LOC ceiling at HEAD per 2026-05-19 re-measurement — DI-2026-05-18-002's original LOC-overflow framing is stale; closure is now justified by retiring the shim cluster, not by enforcing the ceiling). Also: a one-line broad-catch marker fix on `transfer_dialog._on_confirm` and a sweep of the dual-name `build_context` / `initial_yard` kwargs on `BuildQueueScreen`.

## Goals
- Eliminate the 9 owned UI back-compat shim clusters end-to-end (production block deleted; test callers migrated to canonical surface).
- Continue dropping `game/ui/screens/transfer_dialog.py` LOC by retiring the shim cluster (currently 448 at HEAD; already under the 500-LOC ceiling — DI-2026-05-18-002 closure is driven by the shim retirement, not LOC enforcement).
- Restore broad-catch convention compliance on the lone `transfer_dialog._on_confirm` violation.
- Remove the dual-name `build_context` / `initial_yard` constructor kwarg on `BuildQueueScreen` after migrating callers to the canonical `initial_yard=`.
- Keep every phase independently shippable (smallest-first ordering, big clusters last) — Codex r4 risk: "Job 8 is still the biggest review burden in the new plan. If the diff starts looking like 'every UI screen changed', cut it into two PRs by feature family."
- Land with full sharded suite green at the end of each phase.

## Scope

**In Scope:**
- F-C-001: `BattleSetupState.side_0` / `side_1` property pair retirement (2 production + 5 test files).
- F-C-002: `transfer_dialog._on_confirm` broad-catch intentional-reason marker.
- F-C-003: `transfer_dialog._extract_dropdown_value` / `_format_pending` / `_discover_pod_designs` method shims (3 methods).
- F-C-004: `StrategyRenderer._bg_image` / `_bg_scaled` / `_bg_scaled_size` / `_bg_brightness` / `_hex_outline_cache` / `_hex_outline_cache_turn` (6 property shims).
- F-C-005: Module-level `draw_grid` free function in `strategy_render/grid.py`.
- F-C-006: `BuildQueueScreen.__init__(... build_context=None ...)` legacy positional/keyword arg.
- F-C-007: `RaceSetupScreen._description_controller` property + setter.
- F-C-008: `NewGameSetupScreen` 6 view-model property shims (player_count, galaxy_type, system_count, player_races, active_race_modal, race_modal_player_index).
- F-C-009: `BattleSetupScreen` 11 view-model + controller property shims.
- F-C-010: `OrdersWindow._get_order_description` shim method.
- F-C-011: `transfer_dialog.py` sentinel re-exports (MAX_LOAD, MAX_DROP) + class-level layout constants (lines 58-86 at HEAD).
- F-C-012: `EventLogWindow.empire_name=None` back-compat default + title-fallback branch.
- F-C-029: `transfer_dialog.py` characterization tests still reach through 6 retired-style property shims (~70 refs across 3 test files).
- DI-2026-05-18-002: `transfer_dialog.py` shim residue (file currently 448 LOC at HEAD — under the 500 ceiling already; DI's original "LOC-overflow" framing is stale). Closes after F-C-003 + F-C-011 + F-C-029 + the dialog-level property shims retire because that retirement is the underlying motivation; the DI entry is updated to reflect "shim residue closed" rather than "LOC reduced under ceiling".

**Out of Scope:**
- F-C-013, F-C-014 — `IFacility.consumable_levels` / `IShipInstance.cargo_contents` protocol-layer residue (owned by PROJ-449 — strategy entity wrapper retirement).
- F-C-015 — `stat_rows_dynamic.py` `LABEL_ABBREV` (label side) — owned by **PROJ-452** (catalog-driven resource surfaces). Coordinator fix 2026-05-19: previous attribution to PROJ-453 was incorrect; PROJ-453 is engine + services polish, PROJ-452 is the catalog/resource-surfaces project.
- F-C-016 — `tests/fixtures/README.md` stale UIWindow doc — carried forward to PROJ-458 (UIWindow retrofit completion) since the README anchors to that pattern.
- F-C-017 — Deferred UIWindow retrofit (SettingsWindow + 4 PlanetTargetEditors) — owned by PROJ-458.
- F-C-018, F-C-019 — DesignLibrary / `_ACTIVATABLE_ABILITIES` static guards (landed Stages 1+2; r4 audit confirmed).
- F-C-020 — `tests/fixtures/strategy_entities.py` legacy kwargs — owned by PROJ-449.
- F-C-021..F-C-026 — test-skip wallpaper findings; out of PROJ-456 scope.
- F-C-027 — 12 UI files over 500-LOC ceiling — owned by PROJ-457.
- F-C-028 — `game/core/exceptions.py` split — owned by PROJ-457.
- F-C-030 — protocol `Dict[]` / `List[]` legacy annotations — owned by PROJ-454 (engine/service surface polish).
- DI-2026-05-18-004 — `LABEL_ABBREV` IDs side — owned by PROJ-453.

## Findings Summary

| ID | Severity | Owner phase | File |
|----|----------|-------------|------|
| F-C-001 | low | Phase 3 | `game/ui/screens/battle_setup_state.py:172-192` |
| F-C-002 | low | Phase 1 | `game/ui/screens/transfer_dialog.py:412` |
| F-C-003 | low | Phase 4 | `game/ui/screens/transfer_dialog.py:279-286` |
| F-C-004 | low | Phase 5 | `game/ui/screens/strategy_renderer.py:107-130` |
| F-C-005 | low | Phase 1 | `game/ui/screens/strategy_render/grid.py:104-110` |
| F-C-006 | low | Phase 2 | `game/ui/screens/build_queue_screen.py:84-90` |
| F-C-007 | low | Phase 1 | `game/ui/screens/race_setup/screen.py:277-285` |
| F-C-008 | low | Phase 5 | `game/ui/screens/new_game_setup_screen.py:272-321` |
| F-C-009 | low | Phase 5 | `game/ui/screens/battle_setup/screen.py:93-205` |
| F-C-010 | low | Phase 1 | `game/ui/screens/orders_window.py:464-475` |
| F-C-011 | low | Phase 4 | `game/ui/screens/transfer_dialog.py:58-86` |
| F-C-012 | low | Phase 1 | `game/ui/screens/event_log_window.py:113-116` |
| F-C-029 | medium | Phase 4 | `tests/unit/ui/screens/test_transfer_dialog_characterization.py` (61 refs) + `test_transfer_dialog.py` (5) + `test_transfer_dialog_enhanced.py` (3) = 69 total |
| DI-2026-05-18-002 | low | Phase 4 (natural close) | `game/ui/screens/transfer_dialog.py:1` (448 LOC at HEAD; already under ceiling — closure driven by shim retirement, not LOC reduction) |

Full per-finding details with status: [findings/PROJ-456_findings.md](findings/PROJ-456_findings.md).

## Key Files

| Component | File Path |
|-----------|-----------|
| BattleSetupState shim block | `game/ui/screens/battle_setup_state.py` (287 LOC at HEAD) |
| TransferDialog | `game/ui/screens/transfer_dialog.py` (448 LOC at HEAD — already under 500; Phase 4 drops further to ~390-420 post-shim-retirement) |
| StrategyRenderer | `game/ui/screens/strategy_renderer.py` (313 LOC at HEAD) |
| draw_grid free function | `game/ui/screens/strategy_render/grid.py` (183 LOC at HEAD) |
| BuildQueueScreen `build_context` kwarg | `game/ui/screens/build_queue_screen.py` (961 LOC — F-C-027 territory; this project does not retire the file's LOC overflow) |
| RaceSetupScreen `_description_controller` | `game/ui/screens/race_setup/screen.py` (522 LOC at HEAD) |
| NewGameSetupScreen VM shims | `game/ui/screens/new_game_setup_screen.py` (734 LOC at HEAD) |
| BattleSetupScreen VM+controller shims | `game/ui/screens/battle_setup/screen.py` (189 LOC at HEAD — note this contradicts the 2026-05-18 bucket-scan "559 LOC" figure) |
| OrdersWindow shim method | `game/ui/screens/orders_window.py` (473 LOC at HEAD) |
| EventLogWindow empire_name fallback | `game/ui/screens/event_log_window.py` (732 LOC — F-C-027 territory) |
| Characterization test cluster | `tests/unit/ui/screens/test_transfer_dialog_characterization.py`, `test_transfer_dialog.py`, `test_transfer_dialog_enhanced.py` |
| `side_0`/`side_1` test cluster | `tests/unit/ui/screens/test_battle_setup_state.py` (13 refs), `tests/unit/ui/screens/battle_setup/test_controller.py` (37), `test_spec_compiler.py` (22), `test_spec_compiler_formation.py` (5), `tests/integration/strategy/combat/test_suppressor_effects.py` (4) — 81 total (re-counted at HEAD 2026-05-19) |
| `BuildQueueScreen(..., build_context=)` caller blast radius | `game/ui/screens/strategy_build_queue_manager.py:128`; `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (~25 sites). NOTE: `BuildQueueController(build_context=...)` callers are NOT in scope — controller API is legitimate, see codex r5 audit. |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1: Smallest-shim cluster (5 fixes, each independently shippable)
Five tiny fixes that can land as one PR or five — operator's choice. Each touches an isolated surface and has narrow test blast radius. Smallest-first per Codex r4 review-burden risk.

- **F-C-002** — Add `# Intentional broad catch: <reason>` marker on `transfer_dialog.py:412` (one line; no test change).
- **F-C-005** — Migrate two test files (`tests/unit/ui/screens/test_strategy_renderer.py`, `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py`) from `draw_grid(r, screen)` to `GridLayer().draw(...)`; delete the module-level free function at `grid.py:104-110`.
- **F-C-007** — Migrate `_description_controller` callers in `tests/unit/ui/screens/test_race_setup_screen.py`, `tests/unit/ui/screens/race_setup/test_controller.py`, `tests/unit/ui/screens/race_setup/test_panel_factory.py` (12 refs total) to `screen._controller.description_controller`; delete property + setter at `race_setup/screen.py:277-285`.
- **F-C-010** — Migrate `_get_order_description` callers in `tests/unit/ui/screens/test_orders_window.py`, `tests/unit/ui/screens/test_fleet_orders_refresh.py`, `tests/integration/ui/test_fleet_build_button.py` to instantiate `OrderDescriber` and call `.describe(...)` directly; delete the shim at `orders_window.py:464-475`.
- **F-C-012** — Audit `EventLogWindow(...)` constructors in 8 test files; supply an explicit `empire_name` (or remove the fallback branch + parameter default).

**Checkpoint:** sharded suite green; 5 finding entries close in `findings/PROJ-456_findings.md`.

### Phase 2: `build_context` legacy-kwarg sweep
F-C-006 — Migrate every caller of `BuildQueueScreen(..., build_context=...)` to `initial_yard=...`, then remove the legacy parameter from the constructor signature and the `effective_initial_yard` resolution at `build_queue_screen.py:90`.

**Scope clarification (codex r5 audit 2026-05-19):** F-C-006 is scoped to the `BuildQueueScreen` constructor ONLY. The `BuildQueueController(build_context=...)` constructor (`game/ui/panels/build_queue_controller.py:66-85`) accepts `build_context` as a legitimate, non-legacy parameter and is OUT OF SCOPE for this phase. When sweeping `build_context=` usages, filter on the class name (`BuildQueueScreen(...)`), not the raw kwarg name.

Caller files of `BuildQueueScreen(..., build_context=...)` (verified 2026-05-19 with class-name filter):
- Production: `game/ui/screens/strategy_build_queue_manager.py:128`
- Tests: `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (25 refs)

Out-of-scope files (these are `BuildQueueController(build_context=...)` callers, controller API is legitimate):
- `tests/unit/ui/panels/test_build_queue_controller.py:57-87`
- `tests/unit/ui/panels/test_build_queue_catalog_threading.py:20-30`
- `tests/unit/strategy/engine/test_production_repro.py:150-157,201-206`
- `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py:77-116`

**Checkpoint:** Every remaining `build_context=` callsite in `game/` and `tests/` is either (a) a `BuildQueueController(build_context=...)` controller-API call (in scope of the controller surface, NOT this finding), (b) a `factory.build_context = ...` or `screen.build_context = ...` instance-attribute write, or (c) inside `game/ui/panels/build_queue_controller.py` / `game/ui/screens/build_queue_panel_factory.py` itself. PowerShell verification: `rg -n "BuildQueueScreen\([^)]*build_context\s*=" game tests` returns zero hits (use `--multiline` if calls span lines); sharded suite green.

### Phase 3: BattleSetupState `side_0` / `side_1` cluster (2 production + 5 test files)
F-C-001 — Sweep 77 references across 5 test files + 2 production files (`battle_setup_state.py`, `battle_setup/controller.py`). Replace `.side_0` / `.side_1` with the canonical `state.sides[0]` / `state.sides[1]` accessors (or `state.get_side(team_id)` where the team-id index is the natural read). Then delete the property/setter pair at `battle_setup_state.py:172-192`.

Caller files (verified 2026-05-19):
- Production: `game/ui/screens/battle_setup_state.py`, `game/ui/screens/battle_setup/controller.py`
- Tests: `tests/unit/ui/screens/test_battle_setup_state.py` (13), `tests/unit/ui/screens/battle_setup/test_controller.py` (37), `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` (22), `tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py` (5), `tests/integration/strategy/combat/test_suppressor_effects.py` (4) — 81 refs total (re-counted at HEAD 2026-05-19)

**Checkpoint (PowerShell-safe):** `rg -n "\.side_0|\.side_1" game tests` returns zero hits outside the deleted block (and the comment lines we just removed); sharded suite green.

### Phase 4: transfer_dialog cluster + characterization sweep (drops file under 500-LOC ceiling)
The four-pronged transfer_dialog cleanup. After this phase, `transfer_dialog.py` drops from its current 448 LOC (already under the 500 ceiling at HEAD per 2026-05-19 re-measurement) to ~390-420 by retiring the shim cluster. DI-2026-05-18-002 closes because the shim residue (the original motivation under the LOC-overflow framing) is gone — not because the LOC drops under the ceiling (which already happened).

- **F-C-003** — Migrate 2-3 characterization-test sites in `tests/unit/ui/screens/test_transfer_dialog_characterization.py` from `dialog._extract_dropdown_value(...)` / `dialog._format_pending(...)` / `dialog._discover_pod_designs(...)` to `TransferGridRenderer.extract_dropdown_value(...)`, `dialog.view_model.format_pending(...)`, `dialog._controller.discover_pod_designs(...)`. Delete the three method shims at `transfer_dialog.py:279-286`.
- **F-C-011** — Move sentinels (`MAX_LOAD`, `MAX_DROP`) and the 18 layout constants (`ROW_HEIGHT` through `TARGET_AMT_W`) at `transfer_dialog.py:58-86` to their owning modules (`TransferViewModel` and `TransferGridRenderer`). Update any importers; delete the class-level re-exports.
- **F-C-029** — Mechanical sweep across 3 test files (~69 refs total): `dialog._current_source` → `dialog.view_model.current_source`, `dialog._current_target` → `dialog.view_model.current_target`, `dialog._row_data` → `dialog.view_model.row_data`, `dialog._filter_empty` → `dialog.view_model.filter_empty`, `dialog.available_sources` → `dialog.view_model.available_sources`, `dialog.available_targets` → `dialog.view_model.available_targets`, `dialog.pending_transfers` → `dialog.view_model.pending_transfers`. Then delete the corresponding 6 dialog-level property shims (find them via comment block "Back-compat property shims" search).
- **DI-2026-05-18-002 natural close** — After F-C-003 + F-C-011 + F-C-029, run `(Get-Content game/ui/screens/transfer_dialog.py | Measure-Object -Line).Lines` (PowerShell); expect ~480-500 LOC. Mark the DI entry resolved in `AgentCoordination/discovered_issues/log.jsonl`.

**Checkpoint (PowerShell-safe):** `transfer_dialog.py` under 500 LOC; `rg -n "dialog\._current_source|dialog\._current_target|dialog\._row_data|dialog\._filter_empty|dialog\.available_sources|dialog\.available_targets|dialog\.pending_transfers" tests` returns zero hits; sharded suite green.

### Phase 5: Big-three shim clusters (StrategyRenderer + NewGameSetupScreen + BattleSetupScreen)
The three highest-volume shim clusters. Land in any order — write scopes are disjoint (renderer / new_game / battle_setup all in separate sibling packages).

- **F-C-004** — 6 StrategyRenderer cache-attr shims. No test reads of these names (verified 2026-05-19 — `rg "_bg_image|_bg_scaled|_bg_brightness|_hex_outline_cache" tests/` returns no files). Delete the property block at `strategy_renderer.py:107-130` directly. The findings file's "find test sites still reading the six shimmed names" task may be a no-op.
- **F-C-008** — 6 NewGameSetupScreen VM property shims. ~37 references across 3 test files + 1 fixture + 1 production file. Migrate `screen.player_count` → `screen._view_model.player_count` (etc.) across `tests/unit/ui/test_new_game_setup.py`, `tests/unit/ui/screens/test_new_game_setup_extended.py`, `tests/fixtures/new_game_setup_ui_builder.py`, and the single self-reference in `game/ui/screens/new_game_setup_screen.py`. Delete property block at lines 272-321.
- **F-C-009** — 11 BattleSetupScreen VM + controller property shims. ~37 references across `tests/unit/ui/screens/test_battle_setup_state.py` (7) + 4 production panel files (`right_panel.py:1`, `left_panel.py:11`, `center_panel.py:14`, `screen.py:2`). The panels read `screen.active_side`, `screen.active_fleet_index`, etc. extensively — those are the bulk of the migration work. Replace each `screen.<name>` read with `screen.view_model.<name>` (or `screen.controller.<name>` for the end-condition cluster). Delete property block at lines 93-205.

**Checkpoint:** sharded suite green; 3 finding entries close; PROJ-456 complete.

## Dependencies & Sibling Projects

**Group B serial order (coordinator-confirmed 2026-05-19): `PROJ-453 → PROJ-454 → PROJ-456 → PROJ-457`.** PROJ-456 is the THIRD project Group B's run agent executes; PROJ-454 (services + facade retirement) is its immediate predecessor in the series.

| Project | Status | Relationship |
|---------|--------|--------------|
| **PROJ-453** (engine + services polish) | Active — **Group B predecessor** | Already complete by the time PROJ-456 starts. No file overlap. |
| **PROJ-454** (services + facade retirement) | Active — **Group B predecessor** | Immediate predecessor in Group B series. No file overlap with PROJ-456's UI scope. PROJ-454 touches `game/ui/screens/strategy_detail_fmt.py:405` for an import migration; PROJ-456 doesn't edit that file. |
| **PROJ-457** (UI structural debt extractions) | Active — **Group B successor** | **Hard successor** in Group B series. PROJ-457 Phase 0 re-measures LOC after PROJ-456's shim retirement drops it (some F-C-027 target files may go under 500 naturally). Critical: PROJ-456 Status: Complete must be unambiguous before PROJ-457 starts. |
| PROJ-450 (typed staging-yard substrate) | Active — **Group A** | `tests/unit/ui/screens/test_transfer_dialog_characterization.py` is shared (PROJ-456 Phase 4 — F-C-029 sweep migrates 61 dialog-shim references; PROJ-450 Phase 3 rewrites fixture data on the same file). Codex Group 2 audit identified this as a HARD collision; coordinator resolution 2026-05-19: **Group A re-ordered its serial so PROJ-450 runs LAST**, which means PROJ-456 lands first and PROJ-450's Phase 3 rebases onto the new view-model attribute names. |
| PROJ-458 (UIWindow retrofit completion) | Active — **Group C** | Parallel-safe — different UI screens. PROJ-458 touches `settings_window.py`, `atmosphere_target_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`; PROJ-456 doesn't touch any of those files. |

**No worktrees** per user standing preference. Serial execution in `main` checkout.

## Related Documents

- [design.md](design.md) — design rationale for the smallest-first phasing and the per-cluster shim-retirement recipe.
- [decisions.md](decisions.md) — full decisions log; updated as the work progresses.
- [findings/PROJ-456_findings.md](findings/PROJ-456_findings.md) — 14 owned findings with verified file:line refs (2026-05-19).
- [manifest.md](manifest.md) — file-touch list grouped by phase.
- Codex r4 audit redesign: [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Job 8 row.
- Original bucket scan (2026-05-18): [`Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`](../../archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md).
- Pattern reference (UIWindow bypass-init, for tests that reach through shims): `docs/02_PATTERNS.md` §33.

## Verification

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` (§33), `docs/03_CONVENTIONS.md`.
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — all tests pass (establishes baseline).

### After Each Phase
- [ ] Targeted tests for the touched cluster pass.
- [ ] Sharded suite green (no regression).
- [ ] `plan.md` Quick Status table updated for the closed phase.
- [ ] Current State `Last Updated` / `Active Phase` / `Last Action` / `Next Action` updated.

### Final Verification (after Phase 5)
- [ ] `rg -n "back[- ]?compat" game/ui/screens/` returns zero hits in the 9 files listed above.
- [ ] `transfer_dialog.py` LOC < 500 (DI-2026-05-18-002 closed).
- [ ] All 14 owned findings flipped to `Status: resolved` in `findings/PROJ-456_findings.md`.
- [ ] Sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- [ ] Codex end-of-project consult landed; verified findings remediated.
- [ ] User applies the `verified` label.
