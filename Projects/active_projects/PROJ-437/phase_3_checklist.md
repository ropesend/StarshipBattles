# Phase 3: Mixed content display (resources/items/population) through one screen model

**Status:** In Progress (3a complete; 3b not started)
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_3.planned_files

**Objective:** Per-kind specialized presentation under one row model. Resources display as float amounts + per-resource icons. Items display as discrete counts + design-name labels + damage indicators. Population displays as per-species integer counts + species labels. All three render through one unified row contract reading from `Container.contents()`. Drop-pod-name "always-show" handling folds into items-row presentation.

---

## Sub-phase 3a — Substrate (complete 2026-05-18)

- [x] RED — `tests/unit/ui/screens/test_transfer_mixed_content.py` confirmed `AttributeError: type object 'TransferViewModel' has no attribute 'build_row_data_from_containers'`.
- [x] GREEN — new classmethod `TransferViewModel.build_row_data_from_containers(source_containers, target_containers, *, filter_empty=False) -> list[dict]`. Row dicts shaped `{cargo_key, display_name, kind, source_amt, target_amt}` with `kind: ContainableKind` as the additive field vs the legacy builder.
- [x] GREEN — implementation extracted to `game/ui/screens/transfer_container_rows.py` (142 LOC) to keep view model under the 500-LOC ceiling. The view model's classmethod is a thin wrapper that injects `_iter_resource_definitions()`.
- [x] 9 new tests cover: resource catalog order (canonical 8 always emitted); resource aggregation across snapshots; resource display name from `ResourceDefinition.name`; population alphabetical sort; population aggregation across snapshots; item aggregation by design_id with `drop_pod:` prefix; overall row ordering (resources → population → items); `filter_empty` filters zero-zero rows; empty sides still emit canonical resources.
- [x] All existing transfer / facade / UI tests stay green.

## Sub-phase 3b — Cutover (not started)

Expected shape:
1. RED — `tests/integration/ui/test_transfer_container_e2e.py`: end-to-end mixed-content transfer flow with container-driven row builder; assert that dialog rendering matches container contents.
2. GREEN — `TransferDialog._build_grid` switches to call `view_model.build_row_data_from_containers(source_containers, target_containers, filter_empty=vm.filter_empty)` when both sides have container snapshots; legacy `build_row_data(source_obj, target_obj)` retired.
3. GREEN — `transfer_grid_renderer._add_row` accepts `kind` in row dict (renders identically for Phase 3 — per-kind icons / damage / species visuals are out-of-scope polish; the kind field unlocks them when ready).
4. Retire `TransferViewModel.all_pod_names` + `_build_pod_rows` + `get_amounts(info_obj)` + `build_row_data(source_obj, target_obj)` (legacy DTO path). Existing tests in `test_transfer_view_model.py::TestTransferViewModelRows::test_worker_i_transfer_vm_species_key_ordering` retire alongside.
5. Retire `transfer_dialog.py` back-compat property shims (`_all_pod_names`, `_row_data`, `_current_source`, `_current_target`, `_filter_empty`) — restores the dialog file under the 500-LOC ceiling. Audit external callers first.
6. Mirror in `game/ui/screens/strategy_windows/transfer_dialogs.py` only if constructor signature changes (it shouldn't).

---

## Phase Completion Checklist
- [x] Sub-phase 3a substrate complete
- [ ] Sub-phase 3b cutover complete
- [x] `tests/unit/ui/screens/test_transfer_mixed_content.py` green (9 tests)
- [ ] `tests/integration/ui/test_transfer_container_e2e.py` green
- [ ] Existing transfer UI tests green (or retired as part of legacy-path retirement)
- [ ] Manual smoke: transfer dialog with mixed-content source AND destination renders correctly
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json

## Phase-3a known limitations (resolved in 3b or beyond)

- Items always use `drop_pod:<design_id>` prefix. Vehicle (`vehicle:<design_id>`) discrimination needs `ItemRef.state` to surface in the snapshot — Container-substrate change owned by PROJ-436 Phase 9. Phase 3b will adopt the channel once it lands; until then, the legacy DTO path retains the vehicle/drop-pod split.
- Population display name falls back to `species_id`. Richer species-label registry hook is Phase 3b polish.
- Per-resource icons + damage indicators + species icons (full design.md §Per-kind row presentation) are visual polish that doesn't fit the PROJ-437 data-model-migration scope. The `kind` field in the row dict unlocks them when a future ticket picks them up.
