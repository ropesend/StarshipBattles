# Phase 4: Final UI cutover — legacy DTO-path retirement + AST guard confirmation

**Status:** Complete (2026-05-18; single commit)
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_4.planned_files

**Objective:** Remove every legacy DTO row-builder consumer + their pinning tests. Confirm AST guards for the deleted constants.

> Note: the phase's original scope was narrower (just `RESOURCE_TYPES` consumer cleanup) — but PROJ-436 Phase 7 already landed those deletions, so Phase 4 expanded to absorb the legacy DTO-path retirement queued by Phase 3b's minimal cutover.

---

## Tasks (executed)

1. **View model deletions** —
   - `get_amounts(info_obj)` static method
   - `build_row_data(source_obj, target_obj)` instance method
   - `_build_pod_rows(source_obj, target_obj)` instance method
   - `all_pod_names` constructor param + field

2. **Dialog deletions** —
   - `_all_pod_names` property (read + setter)
   - `_get_amounts(info_obj)` shim method
   - `_add_pod_rows(source_obj, target_obj)` shim method
   - `self.view_model.all_pod_names = self._controller.discover_pod_designs(scene)` call in `__init__`

3. **Test retirements** —
   - `test_transfer_view_model.py::TestTransferViewModelRows::test_worker_i_transfer_vm_species_key_ordering` — the canonical 8-resource ordering pin (covered by `test_transfer_mixed_content.py` against the container path now).
   - `test_transfer_dialog_characterization.py::TestGetAmounts` (3 tests).
   - `test_transfer_dialog_characterization.py::TestAddPodRows` (1 test).
   - Total: 5 tests retired.

4. **AST guard** — `tests/static_guards/test_no_legacy_storage_fields.py:217-265` (added by PROJ-436 Phase 7) already pins absence of `transfer_view_model.RESOURCE_TYPES` / `RESOURCE_DISPLAY_NAMES` + `transfer_dialog` re-export. Planned `tests/static_guards/test_no_resource_types_constant.py` skipped as redundant.

5. **`controller.discover_pod_designs` kept** — no production caller after the dialog `__init__` cleanup, but the method is tested in isolation (`test_transfer_controller.py`) and its contract is documented public. Marginal-cost retention; no impact on PROJ-437 goals.

---

## Phase Completion Checklist
- [x] Legacy view-model DTO paths deleted
- [x] Legacy dialog shims deleted (`_get_amounts`, `_add_pod_rows`, `_all_pod_names`)
- [x] Pinning tests retired (5 tests)
- [x] AST guard for `RESOURCE_TYPES` confirmed via pre-existing pin
- [x] `grep -rn 'RESOURCE_TYPES\|RESOURCE_DISPLAY_NAMES' game/ui/ tests/` returns zero new hits
- [x] Full sharded suite green (23307 passed, -5 from 23312 matching the retired tests)
- [x] Update status to Complete; update plan.md + phase_state.json

## Deferred follow-up (not blocking)

- Dialog LOC ceiling: 523 vs 500 (down from 546). The remaining over-ceiling is the back-compat property shim cluster (`available_sources`, `available_targets`, `pending_transfers`, `_row_data`, `_filter_empty`, `_current_source`, `_current_target`) that other characterization tests (`TestPendingTransferMath`, `TestConfirmCommandEmission`) still consume. Retiring requires ~10-15 mechanical test edits but isn't blocking PROJ-437's data-model goal. Recommend a future TD ticket.
