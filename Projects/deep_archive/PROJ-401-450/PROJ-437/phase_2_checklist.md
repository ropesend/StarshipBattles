# Phase 2: Slider quantity + mass-remaining preview against `Container.add()` validation

**Status:** Complete (2026-05-18; single commit)
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_2.planned_files

**Objective:** Wire existing slider/arrow/Max controls to a mass-remaining preview that recomputes as transfers stage, per OD3 (a) (per-input granularity). Preserve `MAX_LOAD` / `MAX_DROP` sentinels.

---

## Tasks (executed)

1. **RED** — `tests/unit/ui/screens/test_transfer_mass_preview.py` confirmed `ImportError: cannot import name 'MassPreview' from 'game.ui.screens.transfer_view_model'`.
2. **GREEN — view model math** — new `MassPreview` dataclass + `TransferViewModel.compute_mass_preview(source_containers, target_containers, pending_transfers)` classmethod. Convention: positive `pending_transfers` value = LOAD (target → source); negative = DROP (source → target). `MAX_LOAD` resolves to target's current qty of `cargo_key`; `MAX_DROP` resolves to negative source qty. RESOURCE keys use `ResourceCatalog.get_mass_per_unit`; POPULATION keys use the default 0.1 t/individual; ITEM keys (`drop_pod:`, `vehicle:`) intentionally mass-neutral until Phase 3. Unknown keys mass-neutral too.
3. **GREEN — chrome wiring** — `TransferGridRenderer.build_chrome` adds two `UILabel`s under the dropdowns; `update_mass_preview(dialog, preview)` refreshes them. `_format_remaining_text(side, remaining, capacity, *, over_capacity)` is a module-level helper for testable string formatting.
4. **GREEN — dialog refresh** — `TransferDialog._refresh_mass_preview()` pulls source/target containers off the Phase-1b `containers` field, computes the preview, and calls the renderer. Wired into `_on_arrow_click`, `_on_max_click`, the zero-button handler, `_on_clear_all`, and `_build_grid`.
5. **Module split** — view model crossed the 500-LOC ceiling at 573 after inline Phase 2 additions. Extracted `MassPreview` + `compute_mass_preview` + private helpers to `game/ui/screens/transfer_mass_preview.py` (209 LOC). View model retains a thin classmethod wrapper that injects the `MAX_LOAD` / `MAX_DROP` sentinels. Post-extraction view model: 423 LOC.
6. **Test ripple** — `tests/unit/ui/screens/test_transfer_grid_renderer.py::test_build_chrome_constructs_dropdown_grid_and_bottom_buttons` updated for the +2 UILabels and new grid rect `(10, 105, 860, 475)`.
7. **Existing `MAX_LOAD` / `MAX_DROP` sentinel tests stay green** — verified.

---

## Phase Completion Checklist
- [x] Phase 2 single-commit scope complete
- [x] Existing pending-transfer math tests green
- [x] `tests/unit/ui/screens/test_transfer_mass_preview.py` green (16 tests)
- [x] Full sharded suite green
- [x] Update status to Complete; update plan.md + phase_state.json

## Deferred to Phase 3

- Per-row policy / capacity rejection messaging (`accepts` False → inline "Not accepted by target"; mass over cap → per-row indicator red). Phase 3 mixed-content row presentation owns per-row styling, so the rejection-message rendering folds in there. Phase 2's `MassPreview.target_over_capacity` already exposes the *aggregate* over-capacity signal via the chrome label's `OVER (cap Xt)` text.
- ITEM-cargo-key mass contribution to the preview (drop pods / vehicles). Phase 3's row-builder migration owns per-item mass surfacing; the Phase 2 preview treats them as mass-neutral.

## Deferred outside PROJ-437

- `transfer_dialog.py` LOC-ceiling cleanup (522 vs 500). Phase 3's retirement of the back-compat property shims (`_all_pod_names`, `_row_data`, etc.) restores the dialog under the ceiling naturally.
