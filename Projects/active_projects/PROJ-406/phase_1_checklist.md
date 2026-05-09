# Phase 1: Reconcile audit-readiness records + projects_index status

**Status:** Complete
**Objective:** Get `validate_audit_ready.py` PASSED for all of PROJ-380..399 and update the index. **No code changes.** If a project genuinely cannot honestly be marked complete, raise a blocker.

---

## Tasks

### Task 1.1: Initial pass — confirm current state of all 20 projects [Simple]
**Tests:** `for p in 380..399: python Projects/scripts/validate_audit_ready.py PROJ-$p`

- [x] Run `validate_audit_ready.py` for each of PROJ-380..PROJ-399 and capture the result (PASSED / FAILED + summary).
- [x] Record the matrix in `findings/audit_baseline.md` so the after-state is comparable.
- [x] Note: PROJ-381, PROJ-386, PROJ-388, PROJ-389 (per the reviews) likely already PASS audit-readiness with only index `Planning` warnings — those are A-10 sweep items and don't need per-project reconciliation work.

**Notes:**

### Task 1.2: PROJ-382 reconciliation (A-01) [Medium]
**File:** `Projects/active_projects/PROJ-382/{plan,phase_1..5_checklist,manifest,design,decisions}.md`

- [x] Read current `plan.md` Quick Status (claims all phases complete) vs the 5 phase checklists (all say Not Started).
- [x] Cross-reference with `Projects/active_projects/PROJ-382/findings/verification_report.md` for actually-shipped state.
- [x] For each phase: if work shipped, set Status to `Complete`, check off all task subboxes, populate brief Notes summarizing what was done (1-2 sentences pulled from verification_report).
- [x] Phase 5 Task 5.4: the file is now under 500 LOC per the review (closed by PROJ-396 phase 3). Update task to `Complete` with a Note pointing to PROJ-396.
- [x] Plan.md verification checklist: tick the now-true rows, leave any genuinely-still-pending items (e.g. user smoke).
- [x] Run `python Projects/scripts/validate_audit_ready.py PROJ-382` — should PASS.

**Notes:**

### Task 1.3: PROJ-393 reconciliation (A-02) [Medium]
**File:** `Projects/active_projects/PROJ-393/...`

- [x] Tick the unchecked phase-completion sub-checkboxes in phase_1, phase_2, phase_3.
- [x] For Tasks 3.2, 3.3, 3.5: cross-reference with PROJ-397 closeout. Add a Note to each that says "Closed via PROJ-397: <task>" where applicable; mark the originating task `Complete` with that note.
- [x] Update `plan.md` accordingly.
- [x] Validators PASS.

**Notes:**

### Task 1.4: PROJ-395 reconciliation (A-03) [Medium]
**File:** `Projects/active_projects/PROJ-395/...`

- [x] MAJ-013 + MAJ-014 are deferred — these are picked up by Wave 5 (PROJ-409). Don't try to close them here.
- [x] Update `plan.md` so the Phase 2 status honestly says "11/14 MAJORs closed; 2 deferred → PROJ-409." Don't claim Phase 2 is "Complete" if its stated goal was "all 14 closed."
- [x] Acceptable closure: mark Phase 2 `Complete with deferrals` (or whatever your validator allows). If validator rejects partial completion, change the phase goal to "11/14 + 2 deferred" so records and reality agree.
- [x] Validator PASSES (after reconciliation, possibly with a documented warning).

**Notes:**

### Task 1.5: PROJ-397 reconciliation (A-04) [Medium]
**File:** `Projects/active_projects/PROJ-397/...`

- [x] All phase checklists say `Not Started`. Cross-reference with the project's verification_report and recent commits (`git log --oneline -- Projects/active_projects/PROJ-397/`).
- [x] Tick all subtasks for shipped work; populate Notes.
- [x] Phase 3 `fleet_id` deferral text contradicts the implemented Path B — update the text to reflect the actual decision.
- [x] Update `plan.md` Quick Status + Current State.
- [x] F-05 introspection-only test is a Tier 4 item (PROJ-408 C-01) — leave a clear deferral note here.
- [x] Validators PASS.

**Notes:**

### Task 1.6: PROJ-398 reconciliation (A-05) [Simple]
**File:** `Projects/active_projects/PROJ-398/...`

- [x] Tick Phase 1 task subboxes.
- [x] Populate manifest + decisions with shipped state.
- [x] Validators PASS.

**Notes:**

### Task 1.7: PROJ-399 reconciliation (A-06) [Simple]
**File:** `Projects/active_projects/PROJ-399/...`

- [x] Tick Phase 1 task subboxes (every Task 1.1..1.5 should be checked off — work is done per `fd4a23068`).
- [x] Update `plan.md` Verification: row "User verified" can stay unchecked.
- [x] Validators PASS.

**Notes:**

### Task 1.8: PROJ-396 reconciliation (A-07) [Medium]
**File:** `Projects/active_projects/PROJ-396/...`

- [x] Tick all phase checklists.
- [x] Populate manifest + design with shipped state.
- [x] If the "19735/19745 sharded pass" claim is unsupported by checked evidence, replace with the current sharded pass state (the post-Wave-1 result from this remediation run is the most authoritative).
- [x] Validators PASS.

**Notes:**

### Task 1.9: PROJ-389 reconciliation (A-08) [Simple]
**File:** `Projects/active_projects/PROJ-389/...`

- [x] Tick Task 1.6 + verification rows.
- [x] Update manifest to include the 4 test files + 3 doc files actually migrated beyond the original 6-caller estimate.
- [x] Validators PASS.

**Notes:**

### Task 1.10: PROJ-384 reconciliation (A-09) [Simple]
**File:** `Projects/active_projects/PROJ-384/...`

- [x] Remove stale blocker text from `plan.md` (or update it to reflect resolution).
- [x] Tick the final regression task.
- [x] Validators PASS.

**Notes:**

### Task 1.11: Final index sweep (A-10) [Simple]
**File:** `Projects/projects_index.md`

- [x] Flip every PROJ-380..PROJ-399 row from `Planning` (or `Active`) to `Complete`.
- [x] Sanity-check there are no other surprise stale entries.

**Notes:**

### Task 1.12: Final validator pass [Simple]
**Tests:** validators for all 20 projects

- [x] Re-run `validate_audit_ready.py` for each of PROJ-380..PROJ-399. **All 20 must PASS.**
- [x] Record the after-matrix in `findings/audit_baseline.md` next to the before-matrix.
- [x] If any still fails, triage. If it's a real-work gap, raise a blocker and stop — surface to the orchestrator.

**Notes:**

### Task 1.13: Closeout
- [x] Phase 1 status `Complete`
- [x] Plan.md updated
- [x] `Projects/projects_index.md` row for PROJ-406 set to `Complete`
- [x] `validate_audit_ready.py PROJ-406` PASSED
- [x] Commit with message `PROJ-406 phase 1: reconcile audit-readiness records across PROJ-380..399`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] All 20 PROJ-380..399 audits PASS
- [x] `python Projects/scripts/validate_phase.py PROJ-406 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-406` PASSED
