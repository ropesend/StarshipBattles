# Phase 7: `TransferValidator` / resource-list deletion

**Status:** Not Started
**Depends on:** phase_6
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_7.planned_files

**Objective:** Delete `TransferValidator.VALID_CARGO_TYPES` hardcoded whitelist at `game/strategy/validation/transfer_validator.py:16-25`. Validation through `Container.accepts()` + `ResourceCatalog` (resources) + species registry + design registry. The `_validate_cargo_type` check at lines 72-76 collapses to `source.accepts(containable) and dest.accepts(containable)`. Delete `transfer_view_model.RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES` hardcoded lists at `game/ui/screens/transfer_view_model.py:26-35`; UI iterates `ResourceCatalog.all_ids()` (Core-layer single source of truth) and uses `ResourceDefinition.name` for display labels. **This phase makes PROJ-437's API stable enough to start.**

---

## Tasks

To be authored at phase start. Expected sub-phase shape:
- 7a — `TransferValidator` rewrite: `_validate_cargo_type` delegates to `Container.accepts()`.
- 7b — sweep callers of `VALID_CARGO_TYPES` (tests in `tests/integration/strategy/test_resource_transfer.py` reference it).
- 7c — delete `VALID_CARGO_TYPES`; grep gate returns zero hits in `game/`.
- 7d — `transfer_view_model.py` reads via `ResourceCatalog.all_ids()` (Core-layer single source of truth); `RESOURCE_DISPLAY_NAMES` collapses to `ResourceDefinition.name` lookup through the same catalog.
- 7e — sweep `transfer_dialog.py:39-43` and other UI re-exports.
- 7f — final cutover: delete `RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES`; grep gate.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] Grep gates clean (no `VALID_CARGO_TYPES`, no `RESOURCE_TYPES` constant)
- [ ] Existing transfer UI tests green (`tests/integration/strategy/test_resource_transfer.py`)
- [ ] `tests/integration/test_transfer_container_validation.py` green
- [ ] Full sharded suite green
- [ ] **Notify PROJ-437 owner: API stable, PROJ-437 Phase 0 may start.**
- [ ] Update status to Complete; update plan.md + phase_state.json
