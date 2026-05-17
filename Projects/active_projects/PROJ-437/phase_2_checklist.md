# Phase 2: Slider quantity + mass-remaining preview against `Container.add()` validation

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_2.planned_files

**Objective:** Wire existing slider/arrow/Max controls to `Container.add()` validation. Show mass-remaining preview as transfers stage. Validation rejections (capacity / policy) surface as inline UI messages, not silent ignores. Preserve `MAX_LOAD` / `MAX_DROP` sentinels.

---

## Tasks

To be authored at phase start.

Expected shape:
1. RED — `test_transfer_mass_preview.py`: pending-transfer math computes mass-remaining-after correctly; policy rejections surface as `PendingTransferStatus.REJECTED_POLICY` etc.
2. GREEN — view-model `apply_arrow` / `apply_max` call `Container.add()` in dry-run mode (validation only, no mutation) to compute preview.
3. `transfer_grid_renderer.py` renders mass-remaining indicator + per-row rejection message styling.
4. `transfer_dialog.py` surfaces validation messages in dialog status area.
5. Existing `MAX_LOAD` / `MAX_DROP` sentinel tests stay green.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] Existing pending-transfer math tests green
- [ ] `tests/unit/ui/screens/test_transfer_mass_preview.py` green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
