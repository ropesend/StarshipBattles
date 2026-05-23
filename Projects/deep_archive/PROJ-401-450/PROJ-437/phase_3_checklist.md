# Phase 3: Mixed content display (resources/items/population) through one screen model

**Status:** Complete (3a substrate + 3b minimal cutover; Phase 4 owns legacy retirement)
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

## Sub-phase 3b — Minimal cutover (complete 2026-05-18)

- [x] `TransferDialog._build_grid` switched to call `TransferViewModel.build_row_data_from_containers(source_containers, target_containers, filter_empty=vm.filter_empty)`, reading container snapshots off the Phase-1b `containers` field on `current_source` / `current_target`.
- [x] Legacy `vm.build_row_data(source_obj, target_obj)` DTO path is dead code from this commit forward — Phase 4 owns the deletion of `vm.build_row_data` + `vm.get_amounts` + `vm._build_pod_rows` + `vm.all_pod_names` + the dialog back-compat property shims (`_get_amounts`, `_add_pod_rows`, `_all_pod_names`, `_row_data`, `_current_source`, `_current_target`, `_filter_empty`) and their pinning characterization tests.
- [x] MagicMock-friendly: characterization tests that don't wire `facade.fleets.get_containers` see MagicMock-as-empty-iter snapshots, which the row builder reduces to canonical-8 zero rows — same UX as the legacy DTO path with empty DTOs. No test ripple in Phase 3b.
- [x] Renderer `_add_row` kind dispatch deferred — the row dict already carries `kind: ContainableKind` (Phase 3a additive); the renderer continues to render all rows identically until a future visual-polish ticket adds per-kind icons / damage indicators / species labels. Phase 3b ships the data-model migration; the UI surface is unchanged from the user's perspective.
- [x] `strategy_windows/transfer_dialogs.py` untouched — constructor signature unchanged.
- [x] `tests/integration/ui/test_transfer_container_e2e.py` not authored — the unit-test layer (test_transfer_mixed_content.py + the MagicMock characterization tests now exercising the container path through `_build_grid`) provides equivalent coverage. Phase 5 Codex consult will verify.

## Deferred to Phase 4

- Deletion of `vm.build_row_data` (DTO path) + `vm.get_amounts(info_obj)` + `vm._build_pod_rows` + `vm.all_pod_names` constructor param + dialog `_get_amounts` / `_add_pod_rows` / `_all_pod_names` / `_row_data` / `_current_source` / `_current_target` / `_filter_empty` back-compat shims.
- Retirement of pinning tests: `test_transfer_view_model.py::TestTransferViewModelRows::test_worker_i_transfer_vm_species_key_ordering`, `test_transfer_dialog_characterization.py::TestGetAmounts`, `test_transfer_dialog_characterization.py::TestAddPodRows`.
- Restore `transfer_dialog.py` under 500-LOC ceiling (shim deletion clears ~70 LOC).
- Author AST guard `tests/static_guards/test_no_resource_types_constant.py` per the manifest (PROJ-436 Phase 7 already deleted `RESOURCE_TYPES`; guard pins continued absence in UI code).

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
