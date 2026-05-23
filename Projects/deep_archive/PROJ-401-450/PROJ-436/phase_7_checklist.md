# Phase 7: `TransferValidator` / resource-list deletion

**Status:** Complete
**Depends on:** phase_6
**Review Mode:** standard
**Files:** see `phase_state.json` phase_7.planned_files

**Objective:** Delete `TransferValidator.VALID_CARGO_TYPES` hardcoded whitelist at `game/strategy/validation/transfer_validator.py:16-25`. Validation through `ResourceCatalog` + categorical sentinels. Delete `transfer_view_model.RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES` hardcoded lists at `game/ui/screens/transfer_view_model.py:26-35`; UI iterates `ResourceCatalog.all_definitions()` (Core-layer single source of truth) and uses `ResourceDefinition.name` for display labels. **This phase makes PROJ-437's API stable enough to start.**

---

## Tasks (audit-driven, single cutover)

Audit collapsed the planned 7a-7f sub-phases into a single cutover commit (Phase 4f / 5f / 6b pattern). Production scope: 3 sites; test scope: 4 files. The `transfer_branches.py` order-handler branches dispatch on `cargo_type` string equality directly and never look at the whitelist — no migration needed there.

- [x] `TransferValidator`: deleted `VALID_CARGO_TYPES`; added `_CATEGORICAL_CARGO_TYPES` frozenset (`{"passengers", "drop_pod", "vehicle"}`) + `_is_known_cargo_type()` consulting `ResourceCatalog.has()`; the inline check at the old line 72 now calls `_is_known_cargo_type(cargo_type)`.
- [x] `transfer_view_model.py`: deleted `RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES`; `build_row_data` iterates `_iter_resource_definitions()` (lazy `ResourceCatalog.from_json().all_definitions()`); each row's `display_name` is `ResourceDefinition.name`.
- [x] `transfer_dialog.py`: deleted the `from game.ui.screens.transfer_view_model import RESOURCE_DISPLAY_NAMES, RESOURCE_TYPES` block + the corresponding `__all__` re-exports.
- [x] AST guards added to `tests/static_guards/test_no_legacy_storage_fields.py` for all 4 deleted surfaces (`VALID_CARGO_TYPES`, `RESOURCE_TYPES`, `RESOURCE_DISPLAY_NAMES`, dialog re-export).
- [x] Integration test `tests/integration/test_transfer_container_validation.py` created (12 tests: registry-driven cargo-type acceptance + `Container.accepts()` substrate composition).
- [x] 4 test files migrated to the new contract.
- [x] **UI label change documented for Ross**: ammo cargo row now displays as "Ammunition" (from `data/resources.json:name`) instead of the old hardcoded "Ammo". All other 7 labels unchanged.

---

## Phase Completion Checklist
- [x] All tasks complete (single cutover)
- [x] Grep gates clean (`grep -rn VALID_CARGO_TYPES game/` returns zero; `grep -rn RESOURCE_TYPES\|RESOURCE_DISPLAY_NAMES game/` returns zero)
- [x] Existing transfer UI tests green (`tests/integration/strategy/test_resource_transfer.py`)
- [x] `tests/integration/test_transfer_container_validation.py` green (12/12)
- [x] Full sharded suite green: **21233/21233** (+21 from 21212 Phase 6 baseline)
- [x] **PROJ-437 unblocked**: API stable, PROJ-437 Phase 0 may start.
- [x] Status updated; plan.md + phase_state.json updated.
