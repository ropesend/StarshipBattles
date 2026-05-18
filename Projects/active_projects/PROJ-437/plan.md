# PROJ-437: Container-Aware Transfer UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-437` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-437 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Read PROJ-436 Container API; survey current transfer UI | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Source/destination container browsing against unified API | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Slider quantity + mass-remaining preview against `Container.add()` validation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Mixed content display (resources/items/population) through one screen model | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete `transfer_view_model.RESOURCE_TYPES` consumers; final UI cutover | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Codex consult + verified-finding remediation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Phase 0 complete — handing off to Phase 1.
**Last Action:** Phase 0 migration map written at [findings/transfer_ui_migration_map.md](findings/transfer_ui_migration_map.md). OD1/OD2/OD3 resolved at defaults (a/a/a). Surfaced manifest correction (`fleet_data_source.py` is the wrong Phase 1 target — actual target is `transfer_controller.py::collect_sources_and_targets` + a new DTO/facade `get_containers(id)` accessor). Two tangential hardcoded-resource-tuple leaks flagged (`fleet_dto.py:217-226`, `builder/stat_rows_dynamic.py:179,252`) for a future TD ticket — out of PROJ-437 scope.
**Next Action:** Phase 1 start — recommended split: 1a substrate (additive `ContainerRef` + `ContainerSnapshotInfo` + parallel `facade.*.get_containers(id)` accessor) → 1b cutover (`transfer_view_model.get_amounts` / `build_row_data` + `transfer_controller.fetch_dto` / `collect_sources_and_targets`). Phase 1 entrypoint must advance `phase_state.json.project_baseline_sha` from `4177fef36…` to the current `main` HEAD and re-record the sharded baseline (PROJ-443 Phase 4 made 1953 additional `tests/unit/strategy/data/` tests visible).
**Blockers:** None. PROJ-436 Phase 7 stable; AST guards green. Ross to review the Phase 0 finding about the **"Ammo" → "Ammunition"** UI label change ([findings/transfer_ui_migration_map.md §7](findings/transfer_ui_migration_map.md#7-heads-up-to-user-ross--ui-label-change-pending-review)) before Phase 5 ship — a one-line `data/resources.json` edit reverts it.

## Overview
Rebuild the current transfer / loading / unloading UX on top of the unified `Container` API that PROJ-436 lands. The existing dialog ([game/ui/screens/transfer_dialog.py](../../../game/ui/screens/transfer_dialog.py) + `transfer_controller.py` + `transfer_view_model.py` + `transfer_grid_renderer.py`) works adequately today against the legacy `cargo_contents` / `stockpile` / `bay_inventory` / `_fleet_resource_pool` patchwork. After PROJ-436, that patchwork is replaced by one `Container` abstraction. This project rebuilds the UI to source/destination browse, validate, and execute transfers through the unified API while preserving the user's existing slider-driven UX shape.

## Goals
- Source/destination dropdowns enumerate `Container` instances on the selected entity (planet / fleet / ship); not hardcoded source-vs-destination type pairs.
- Per-row UI specialization for resources (continuous float) vs items (discrete with identity) vs population (per-species integer), reading from the unified three-slice `Container.contents()`.
- Slider + arrow + Max controls preserve existing UX (per user: "we already have a transfer UI that works OK, it is somewhat similar to a slider system").
- Mass-remaining preview as transfers stage in the pending state.
- Validation through `Container.accepts()` — no hardcoded type whitelists in UI code.
- Resource iteration through `ResourceCatalog.all_ids()` (Core-layer single source of truth) — no `RESOURCE_TYPES` hardcoded list, no parallel strategy/UI registry.
- All existing transfer integration tests stay green throughout migration.

## Scope
**In:** rebuild of `transfer_dialog.py` + `transfer_controller.py` + `transfer_view_model.py` + `transfer_grid_renderer.py` around the unified `Container` API; per-kind specialized presentation; mass-remaining preview integrated with `Container.add()` validation; final deletion of `RESOURCE_TYPES` hardcoded list (PROJ-436 Phase 7 makes the data-side deletion; this project completes any UI-side consumers that still reference it); end-of-project Codex consult.

**Out:** changes to the underlying `Container` data model (PROJ-436 owns that); broader transfer-flow UX redesigns beyond the three-slice unification; non-transfer UI cleanup; documentation updates that aren't directly about the transfer dialog (PROJ-436 Phase 10 owns the broader doc refresh); accessibility / theming changes not driven by the data-model change.

## Dependencies
**Soft dependency: PROJ-436 Phase 7.** PROJ-437 Phase 1 (browsing) cannot ship until `Container.accepts()` is the validation surface and `VALID_CARGO_TYPES` is gone. **PROJ-437 Phase 0** (read-the-API + survey current UI) MAY start during PROJ-436 Phase 6-8 if the API has stabilized — the Phase 0 task list is research, not implementation.

**No hard predecessor outside PROJ-436.** PROJ-422..PROJ-435 prerequisite tranche complete.

**No worktrees** per user standing preference.

## Key Files
| Component | File Path |
|-----------|-----------|
| Transfer dialog (UI) | `game/ui/screens/transfer_dialog.py` |
| Transfer controller (event handling) | `game/ui/screens/transfer_controller.py` |
| Transfer view model (state) | `game/ui/screens/transfer_view_model.py` |
| Transfer grid renderer | `game/ui/screens/transfer_grid_renderer.py` |
| Strategy-window transfer dialogs (other entry) | `game/ui/screens/strategy_windows/transfer_dialogs.py` |
| Fleet data source (provides source/dest options) | `game/ui/screens/fleet_data_source.py` |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Read PROJ-436 Container API; survey current transfer UI
Research-only phase. Read the final `Container`, `Containable`, `ContainerPolicy` API after PROJ-436 Phase 6-7 lands. Audit current transfer UI: which view model fields, which controller events, which grid renderer paths consume the legacy storage shapes. Produce a per-file migration map under `findings/`. **Checkpoint:** migration map document committed; no production-code changes yet.

### Phase 1: Source/destination container browsing against unified API
Replace the source/destination dropdown enumeration with a query over the selected entity's container list. A planet exposes its facility-component containers; a fleet exposes per-ship containers (filtered by accessibility); a docked ship exposes its bay + per-component-storage containers. Browse-only — no transfer logic changes yet. **Checkpoint:** existing transfer integration tests green; manual smoke: open transfer dialog from various contexts, see container options listed.

### Phase 2: Slider quantity + mass-remaining preview against `Container.add()` validation
Wire the existing slider/arrow/Max controls to `Container.add()` validation. Show mass-remaining preview as transfers stage. Validation rejections (capacity / policy) surface to UI as inline messages, not silent ignores. Preserve `MAX_LOAD` / `MAX_DROP` sentinels. **Checkpoint:** existing pending-transfer math tests green; new tests for mass-remaining preview and policy-rejection messaging.

### Phase 3: Mixed content display (resources/items/population) through one screen model
Per-kind specialized presentation: resources show float amounts + per-resource icons; items show discrete counts + design-name labels + damage indicators for non-healthy items; population shows per-species integer counts + species labels. All three render through one unified row model under the unified `Container.contents()` API. Drop-pod-name handling (currently special-cased via `all_pod_names`) folds into the items-row presentation. **Checkpoint:** mixed-content scenarios render correctly; existing UI tests green; new tests for cross-kind transfer scenarios.

### Phase 4: Delete `transfer_view_model.RESOURCE_TYPES` consumers; final UI cutover
By PROJ-436 Phase 7 close, `transfer_view_model.RESOURCE_TYPES` is deleted at the data side. This phase audits and removes any remaining UI-side consumers (`transfer_dialog.py:39-43` re-export, etc.). UI iterates `ResourceCatalog.all_ids()` end-to-end. Final grep gate. **Checkpoint:** grep returns zero hits for the constant; UI smoke tests green; full sharded suite green.

### Phase 5: Codex consult + verified-finding remediation
Per the standing end-of-project workflow: run a Codex consult on the landed PROJ-437 UI work. Verify each finding against current code. Verified findings become added phases. **Checkpoint:** consult complete; remediation phases (if any) RED→GREEN tested.

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (sharded suite green at each phase boundary)
- [ ] Manual smoke: transfer dialog opens, browses, validates, executes across at least 5 source/dest combinations (planet→fleet, fleet→planet, ship→ship, fleet→fleet, with mixed content)
- [ ] Audit passed
- [ ] User verified
