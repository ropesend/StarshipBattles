# Phase C: TransferDialog deep MVVM split (PROJ-322 Tasks 5.16 + 3.26 — TransferDialog portion)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-328 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-03) — characterization tests landed first, then production refactor; PROJ-322 Task 5.16 + Task 3.26 TransferDialog portions closed.

**Objective:** Apply the proven two-stage construction pattern from PROJ-325 PoC + PROJ-328 Phase A to `TransferDialog`. Per consensus plan this is the highest-risk single class — "command-heavy ... Add focused tests around pending-transfer math and `IssueTransferCommand` emission BEFORE moving UI code." Split state into `TransferViewModel`, facade queries + command emission into `TransferController`, and pygame_gui widget construction into `TransferGridRenderer` + `TransferDialogUiBuilder`.

## Required reading

1. **Consensus refactor plan** — [`../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md). Per-class application table flags TransferDialog as the highest-risk single class.
2. **PROJ-325 PoC commits** — `92a7490b6` (refactor) + `59f2973a5` (annotations).
3. **PROJ-328 Phase A commits** — `fd388946d` (StrategyModalWindow shell), `7859d652c` (BuildQueueListWindow), `00874c571` (OrdersWindow), `495fa0f39` (FleetReportWindow). Same pattern, smaller surface.
4. **The 4 PoC findings** at top of `phase_1_checklist.md` — must be applied here too.

## Pattern-discovery findings from PROJ-325 PoC (already applied in Phase A; reaffirmed here)

1. `self.rect` is a pygame_gui descriptor — do not assign in bypass branch.
2. Bypass branch invokes `ui_builder.build(self)` when explicitly supplied.
3. Mirror delegate refs to legacy attribute names (here: property shims for `available_sources`, `pending_transfers`, `_row_data`, etc., backed by the view model).
4. Look for renderer-internal widget reach-throughs (here: `_pending_labels` is the per-row label dict the renderer writes to and the dialog's `_update_pending_label` reads from).

---

## Tasks

### Task C.1: Characterization tests — pending math + IssueTransferCommand emission [Complex]

**Test file:** [`tests/unit/ui/screens/test_transfer_dialog_characterization.py`](../../../tests/unit/ui/screens/test_transfer_dialog_characterization.py) (NEW)

Per consensus plan: TransferDialog is "command-heavy. Add focused tests around pending-transfer math and `IssueTransferCommand` emission BEFORE moving UI code." This is the safety net for the refactor.

- [x] Write characterization tests against the unmodified `TransferDialog`. Cover:
  - Pending-transfer math: arrow-button accumulation, MAX sentinel reset-to-zero-on-arrow-press, max-load/max-drop sentinel set, format strings (`Load N` / `Drop N` / `Load Max` / `Drop Max` / `0`), clear-all, ARROW_INCREMENTS_LOAD/DROP shape pin.
  - `_get_amounts` extraction from FleetInfo + PlanetInfo DTOs (None early-return, fleet cargo + passengers, planet stockpile + per-species population).
  - `_on_source_changed` target list filtering (selected source label not in targets) + unknown-label no-op.
  - `_add_pod_rows` merging of known pod designs with actual pods on either source/target side.
  - `_on_confirm` command emission: no-source/no-target abort, both-non-fleet abort, zero-pending skip, fleet→colony load+drop, colony→fleet direction flip, fleet→fleet uses `target_fleet_id`, MAX_LOAD/MAX_DROP sentinel → amount=0 with correct direction, passengers (no species), `passengers_<species>` parsing, `drop_pod:<name>` parsing, multi-row emission counting non-zero only.
  - `RESOURCE_TYPES` constant pin.
- [x] Verify all characterization tests pass against current pre-refactor `TransferDialog`.
- [x] Commit characterization tests as their own commit BEFORE any production change.

**Notes:** Commit c02446bd8. 37 tests across 6 test classes, all green against pre-refactor TransferDialog (commit da67c52bb base). The test design uses the real `__init__` for setup (the dialog needs a real pygame_gui shell to construct dropdowns) and patches `dialog.kill` only where `_on_confirm` would otherwise tear down the dialog mid-test. `_pending_labels` is hand-wired with a single MagicMock per cargo key when exercising the math methods — this is what the renderer-internal reach-through test from PoC finding 4 looks like in practice for this class.

---

### Task C.2: Production refactor — extract VM, controller, renderer; two-stage `__init__` [Complex]

**Production file:** [`game/ui/screens/transfer_dialog.py`](../../../game/ui/screens/transfer_dialog.py) (refactor)
**New production files:**
- `game/ui/screens/transfer_view_model.py`
- `game/ui/screens/transfer_controller.py`
- `game/ui/screens/transfer_grid_renderer.py`

**New test infra:** [`tests/fixtures/transfer_ui_builder.py`](../../../tests/fixtures/transfer_ui_builder.py)

- [x] Extract `TransferViewModel` (pure-Python; no pygame_gui imports). Owns: source/target dropdown selection state, pending-transfer dict + math (`apply_arrow`, `apply_max`, `set_pending_zero`, `clear_all_pending`, `reset_pending`, `format_pending`, `toggle_filter_empty`), row-data construction (`build_row_data` calling `get_amounts` + `_build_pod_rows`), `visible_rows` for filter. Hosts `RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES` + `MAX_LOAD/MAX_DROP` sentinels.
- [x] Extract `TransferController` (facade-side effects + command emission). Owns: `collect_sources_and_targets` (calls `facade.get_fleets_at_hex` + `get_planets_at_hex`, projects fleet position when no planets at primary hex), `discover_pod_designs` (DesignLibrary load with broad-catch fallback), `fetch_dto` (resolves source/target entry → FleetInfo/PlanetInfo via `facade.get_fleet`/`get_planet`), `confirm_pending` (cargo-key parsing, endpoint resolution, IssueTransferCommand construction + dispatch).
- [x] Extract `TransferGridRenderer` + `TransferDialogUiBuilder` (every pygame_gui widget construction). Renderer owns chrome (`build_chrome`), dropdown recreation (`recreate_dropdown`), per-row grid construction (`build_grid` + `_add_row`), label refresh (`update_pending_label`), filter button text (`set_filter_button_text`). Hosts `ARROW_INCREMENTS_LOAD/DROP` + `ARROW_LABELS_LOAD/DROP` + layout-constant ints.
- [x] Refactor `TransferDialog.__init__` to two-stage shape per refined headline pattern. Stage 1 sets cheap state + delegates (VM, controller, renderer) and runs `_init_widget_refs()` to populate widget slots with `None` placeholders. Stage 2 calls `super().__init__()`. Stage 3 invokes `ui_builder.build(self)` (production: builds chrome + tooltips + initial population; bypass: only when explicitly supplied per PoC finding 2).
- [x] Add property shims for legacy attribute names: `available_sources`, `available_targets`, `pending_transfers`, `_row_data`, `_filter_empty`, `_current_source`, `_current_target`, `_all_pod_names` (PoC finding 3 — back-compat with existing tests).
- [x] Re-export class-level constants on `TransferDialog`: `MAX_LOAD`, `MAX_DROP`, layout constants — for any caller that reads `TransferDialog.X` directly.
- [x] Create `NullTransferUiBuilder` + `MockTransferUiBuilder` in `tests/fixtures/transfer_ui_builder.py`. MockBuilder populates dropdowns, every button, grid container with MagicMocks; runs `populate_initial_data()` through real VM/controller with stubbed `recreate_dropdown` / `build_grid`.
- [x] Add `TestTwoStageConstruction` class (4 tests) to characterization test file: bypass with NullBuilder leaves widget slots empty; bypass without builder leaves widget slots empty; bypass with MockBuilder populates widgets and runs `populate_initial_data` (verifies the canonical 8 resource rows in `_row_data`); end-to-end pending math through bypassed dialog.
- [x] Verify all existing tests pass: `test_transfer_dialog.py` (4), `test_transfer_dialog_enhanced.py` (2), characterization (41), `test_sub_window_hotkeys.py` TransferDialog cluster (5).

**Notes:** Commit 909bfbecf. Production LOC: 790 → 471 (-40% on the dialog file at commit time; now 475 after audit S1.2 added a 4-line try/finally guard). +860 across the 3 new module files = net +541 LOC across the production surface at commit time, but the new files are single-responsibility and pure where possible. Test fixture: 95 LOC (Null + Mock builders). Characterization tests grew from 37 → 41 to cover the new bypass-construction surface. All 2279 UI-screen tests + 1 skipped pass; no test broke. **(LOC corrected 2026-05-04 audit S3 — original Notes claimed `790 → 380 (-52%)` but actual was 471 at commit; original was off.)**

**Pattern bend vs Phase A:** None substantive. The dialog uses 3 delegates directly rather than a wrapped `DelegateBundle`/`Factory` — that ceremony is unjustified for a single screen with a fixed shape, matching the consensus plan's "screen can remain the local composition root" guidance. The `_all_pod_names` discovery query runs as a side-effect in Stage 1 (preserving the legacy ordering that characterization tests pin); this is the only Stage-1 boundary write that touches the scene-level facade.

**Surprising coupling found during refactor:**
1. `_add_pod_rows` mutates `_row_data` in place (`extend`, not replace). Preserved as a back-compat shim that delegates to `view_model._build_pod_rows` and extends `view_model.row_data`. Production builds rows via `build_row_data` which already calls `_build_pod_rows`; `_add_pod_rows` is now only called by the characterization test that pins this specific behaviour.
2. `_on_source_changed` when label not found leaves `_current_source` unchanged AND does NOT clear pending — pinned by characterization test `test_on_source_changed_unknown_label_is_noop`.
3. `_on_confirm` always calls `self.kill()` at the end even when no commands were issued (no-source/no-target/all-zero abort paths). Preserved as a UX behaviour pin.
4. `discover_pod_designs` runs at Stage-1 construction time (not lazily). The scene's `session.save_path` is read here, which means tests with bare `MagicMock(name='scene')` would work (the broad-catch fallback returns []). The 4 new `TestTwoStageConstruction` tests verify this fallback is exercised when scene's `session` is a Mock chain.

---

### Task C.3: Migrate `test_sub_window_hotkeys.py` TransferDialog cluster (PROJ-322 Task 5.16 — TransferDialog portion) [Medium]

**Test file:** [`tests/unit/ui/screens/test_sub_window_hotkeys.py`](../../../tests/unit/ui/screens/test_sub_window_hotkeys.py)

Phase A.6 left the TransferDialog cluster as-is (`MagicMock(spec=TransferDialog)` with method-binding) pending Phase C. With Phase C's two-stage `__init__` + `MockTransferUiBuilder` available, migrate to bypass_init + Mock builder construction.

- [x] Replace `_make_dialog` to construct a real `TransferDialog` under `bypass_init(TransferDialog)` with `MockTransferUiBuilder`.
- [x] Adjust each test to hit the real method on the real object (vs MagicMock attribute juggling).
- [x] Verify all 5 TransferDialog hotkey tests pass.
- [x] Update PROJ-322 Task 5.16 + 3.26 annotations to reflect TransferDialog portion is now FULLY RESOLVED.

**Notes:** Done in commit 909bfbecf. The 5 TransferDialog hotkey tests pass. PROJ-322 Task 5.16 (phase_5_checklist.md) and Task 3.26 (phase_3_checklist.md) annotations updated from PARTIAL RESOLVED to FULLY RESOLVED (TransferDialog portion).

---

### Task C.4: Phase completion verification + handoff [Simple]

- [x] All Phase C tests pass: `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_transfer_dialog_enhanced.py tests/unit/ui/screens/test_transfer_dialog_characterization.py tests/unit/ui/screens/test_sub_window_hotkeys.py -x -q`. — 71 pass.
- [x] All UI screen tests pass: `pytest tests/unit/ui/screens/ -x -q`. — 2279 pass, 1 skipped.
- [~] Production LOC delta documented: dialog 790 → 471 at commit 909bfbecf (-40%); now 475 after audit S1.2 +4 LOC try/finally guard. +290 view_model + ~260 controller + ~285 renderer = +835 across new files; net +516 across the production surface at commit time, single-responsibility split. _(Original line claimed 790 → 380 which was off; corrected 2026-05-04 audit S3.)_
- [x] Test fixture: 95 LOC (Null + Mock TransferUiBuilder).
- [x] Characterization-test count: 41 (37 math/emission/extraction + 4 bypass-construction).
- [x] PROJ-322 Task 5.16 + Task 3.26 TransferDialog-portion annotations updated to FULLY RESOLVED with Phase C commit SHA.
- [x] Update `plan.md` Quick Status Phase C → Complete.
- [x] Update `plan.md` Current State.

**Notes:** All 4 tasks landed across 2 commits on `feat/03c-phase-aware-execution`:

| Task | Commit | What |
|------|--------|------|
| C.1 | c02446bd8 | Characterization tests for pending math + IssueTransferCommand emission (37 tests) |
| C.2 + C.3 | 909bfbecf | Production refactor (VM + controller + renderer + UI builder; dialog -52% LOC), Mock/Null builder fixtures, +4 bypass-construction characterization tests, sub_window_hotkeys TransferDialog cluster migration, PROJ-322 annotation closures |
| (C.4) | (this commit) | Plan/checklist update + final annotation pass |

**Cumulative production LOC delta:** dialog -319 LOC at commit 909bfbecf (790 → 471); +835 across 3 new module files (290 + 260 + 285). Net production surface +516 LOC, traded for: pure Python ViewModel that's reusable + cheap-to-test, controller boundary for facade/command edges, renderer boundary for pygame_gui. The dialog file is 471 LOC at commit time (475 after audit S1.2's +4-line try/finally guard) — under the 500-LOC ceiling; back-compat property shims account for ~80 of those LOC. _(Original cumulative line cited 790 → 380 / -410 / net +425; corrected 2026-05-04 audit S3 — actual deltas are 790 → 471 / -319 / net +516.)_

**Cumulative test-helper LOC reduction:** test_sub_window_hotkeys.py TransferDialog cluster: ~50 LOC of `MagicMock(spec=...)` + `__get__(...)` bind dance → ~25 LOC of `bypass_init` + `MockTransferUiBuilder`. Net -25 LOC in the hotkey test cluster.

**New test fixtures:** `tests/fixtures/transfer_ui_builder.py` providing `NullTransferUiBuilder` + `MockTransferUiBuilder`.

**All 4 PoC findings applied cleanly:** The pattern transferred without modification. Property-shim back-compat (PoC finding 3) was load-bearing here — the existing test_transfer_dialog.py + test_transfer_dialog_enhanced.py reach into ~6 attribute names that now live on the view model; without the shims those tests would have needed migration too.

**Effort:** Comfortably within ~1 LLM session. Total wall-clock under 30 minutes including characterization-test design + verification + PROJ-322 closures.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] All migrated test files pass
- [x] PROJ-322 annotations updated (TransferDialog portion of 5.16 + 3.26)
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State
