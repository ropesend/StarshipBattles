# Phase 3: Mixed content display (resources/items/population) through one screen model

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_3.planned_files

**Objective:** Per-kind specialized presentation under one row model. Resources display as float amounts + per-resource icons (`display_precision` from resource registry). Items display as discrete counts + design-name labels + damage indicators for non-healthy items. Population displays as per-species integer counts + species labels. All three render through one unified row contract reading from `Container.contents()`. Drop-pod-name "always-show" handling folds into items-row presentation via a per-design display flag.

---

## Tasks

To be authored at phase start.

Expected shape:
1. RED — `test_transfer_mixed_content.py`: mixed-content source/destination render correctly; per-kind formatting applied; transfer math composes across kinds.
2. GREEN — view-model row construction reads `Container.contents()` and applies per-kind formatting hooks.
3. `transfer_grid_renderer.py` per-kind row rendering specialization.
4. Mirror Phase 3 changes in `strategy_windows/transfer_dialogs.py`.
5. `all_pod_names` field retired in favor of per-design display flag.
6. RED + GREEN — `test_transfer_container_e2e.py` integration test for mixed-content transfer flow.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/unit/ui/screens/test_transfer_mixed_content.py` green
- [ ] `tests/integration/ui/test_transfer_container_e2e.py` green
- [ ] Existing transfer UI tests green
- [ ] Manual smoke: transfer dialog with mixed-content source AND destination renders correctly
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
