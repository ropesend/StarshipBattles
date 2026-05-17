# Phase 2: Verification + docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-433 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** lightweight
**Files (planned):**
- `docs/architecture/*.md` or `docs/refactoring/*.md` (any doc referencing `component_inspector`)
- `Projects/active_projects/PROJ-425/decisions.md` + `findings_ledger.md` (back-link)

**Objective:** Run the sharded suite to catch any caller missed by Phase 1, update any docs that referenced `component_inspector.py` by name, and back-link the split into PROJ-425's findings so the deferred-split note there points at this project's outcome.

---

## Tasks

### Task 2.1: Sharded suite run [Standard]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite. Expected: green.
- [x] If any test fails because of a stale `from game.strategy.services.component_inspector import ...` line that Phase 1's grep missed, update the import and rerun.

### Task 2.2: Grep for doc references [Simple]
**Tests:** none (analysis task)

- [x] `rg -n "component_inspector" docs Reviews Projects`.
- [x] For each reference, decide whether it still applies (likely yes — most are architectural mentions) or needs updating to point at `component_abilities` / `component_layers`.

### Task 2.3: Update PROJ-425 back-link [Simple]
**File:** `Projects/active_projects/PROJ-425/findings_ledger.md`

- [x] Add a line to PROJ-425's Phase 2 entry noting "Split landed in [PROJ-433](../PROJ-433/plan.md) on YYYY-MM-DD." This closes the loop from the deferred-split note recorded in PROJ-425.
- [x] Optionally also add a row to PROJ-425's `decisions.md` linking to PROJ-433's completion.

### Task 2.4: Final LOC check [Simple]
**Tests:** none

- [x] Record final LOC for `component_abilities.py` and `component_layers.py` in `findings_ledger.md`. Both must be materially under 500.
- [x] If `component_inspector.py` survived as Option A's re-export shim, record its final LOC too.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Sharded suite green
- [x] PROJ-425 findings_ledger back-link added
- [x] Doc references updated where needed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project execution complete"
