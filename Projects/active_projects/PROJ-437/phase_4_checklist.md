# Phase 4: Delete `transfer_view_model.RESOURCE_TYPES` consumers; final UI cutover

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_4.planned_files

**Objective:** PROJ-436 Phase 7 deleted the data-side `RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES` constants. This phase audits and removes any UI-side consumers that still reference them (`transfer_dialog.py:39-43` re-export if it survives PROJ-436 Phase 7's sweep; other UI files). UI iterates `ResourceCatalog.all_ids()` (Core-layer single source of truth) end-to-end. Final grep gate.

---

## Tasks

To be authored at phase start.

Expected shape:
1. Audit: `grep -rn 'RESOURCE_TYPES\|RESOURCE_DISPLAY_NAMES' game/ui/ tests/` — enumerate remaining consumers.
2. Migrate each to `ResourceCatalog.all_ids()` + `ResourceDefinition.name` for display names (Core-layer single source of truth).
3. RED — `test_no_resource_types_constant.py` AST guard fails because constants still exist somewhere.
4. GREEN — delete final consumers.
5. AST guard green.
6. Final UI smoke pass.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/static_guards/test_no_resource_types_constant.py` green
- [ ] `grep -rn 'RESOURCE_TYPES\|RESOURCE_DISPLAY_NAMES' game/ui/ tests/` returns zero hits
- [ ] UI smoke tests green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
