# Phase 4: Docs sync

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** lightweight
**Files (planned):** docs/systems/strategy_layer.md, docs/architecture/*.md (where engine interface count is cited)
**Objective:** Update any doc that describes `engines.py` as a monolithic single file. Reflect the new package layout.

---

## Tasks

### Task 4.1: Apply doc updates queued in Phase 0 [Simple]
**Files:** as identified in `findings/phase_0_doc_targets.md`
**Tests:** none — documentation change

- [ ] Re-read `findings/phase_0_doc_targets.md` for the list of files to update.
- [ ] For each doc that referenced `interfaces/engines.py` as a single file: replace with the package layout description (9 leaves + `__init__.py`) and the rationale (one-domain-per-leaf, public seam preserves consumer imports).
- [ ] If a doc cites the file's LOC ("778 LOC" or similar), remove or update the citation.
- [ ] Skip any hit under `docs/_ignore/` per AGENTS.md.

**Notes:** [Filled during implementation]

### Task 4.2: Sanity grep — no remaining stale references [Simple]
**Tests:**
```
rg -n "interfaces/engines\.py" docs/
```

- [ ] Grep returns no hits outside `docs/_ignore/`. If hits remain, update them or note why they are intentional (e.g. a changelog entry describing historical state).

**Notes:** [Filled during implementation. Per TD plan §"Per-Phase Success Criteria": Phase 4 is done only when docs no longer describe `engines.py` as a monolithic single file.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Docs accurately describe the new package layout
- [ ] No stale `interfaces/engines.py` references outside `docs/_ignore/` or intentional historical notes
- [ ] `python Projects/scripts/validate_phase.py PROJ-422 4` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
