# Phase 5: Final measurement + documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED on Phases 0-4)
**Objective:** Capture the final cumulative runtime delta, update `docs/known-issues.md`, and write a lessons-learned summary in this project's decisions.md so future test-quality projects can leverage which patterns yielded the biggest wins.

**Required reading:**
- All Phase 0-4 findings in `findings/`
- [`docs/known-issues.md`](docs/known-issues.md) — current state

**Parallelism:** Sequential — final phase. No other PROJ-327 phase running.

---

## Tasks

### Task 5.1: Final runtime measurement [Simple]

- [ ] Run sharded suite + median of 3 wall-clocks. Record machine spec to confirm comparability with Phase 0 baseline.
- [ ] Capture `pytest tests/ --durations=20` post-state.
- [ ] Compute total project delta vs Phase 0 baseline.

**Notes:** [Filled during implementation. Record before/after wall-clock + percent reduction.]

---

### Task 5.2: Compile runtime delta document [Simple]

**File:** `Projects/active_projects/PROJ-327/findings/runtime_delta.md` (NEW)

- [ ] Compile a per-phase breakdown:
  - Phase 0 baseline (wall-clock, slowest files)
  - Phase 1 delta (virtual_table)
  - Phase 2 delta (mutable-mock rescopes)
  - Phase 3 delta (DUP-001 / HLP-001 work)
  - Phase 4 delta (strategy_screen, if executed)
  - Cumulative project delta
- [ ] Include the post-state slowest-files list — what's NEW at the top of the leaderboard? Those are PROJ-32X candidates if runtime remains an issue.

**Notes:** [Filled during implementation]

---

### Task 5.3: Update `docs/known-issues.md` [Simple]

**File:** [`docs/known-issues.md`](docs/known-issues.md)

- [ ] Add a new section "Test runtime improvements (PROJ-327)" documenting the delta + the techniques used.
- [ ] If any deferred items in PROJ-322 are now RESOLVED (per Phase 1-4 outcomes), update those references.
- [ ] If any deferred items are RE-CONFIRMED DEFERRED (Phase 2/3 Strategy D outcomes), document the new rationale (with runtime measurement evidence).

**Notes:** [Filled during implementation]

---

### Task 5.4: Update PROJ-322 Continuation Guide (final state) [Simple]

**File:** [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide

- [ ] Confirm all 9 PROJ-327 deferral items are dispositioned in the Continuation Guide:
  - 5 (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) → Phase 2 outcome
  - 1 (Task 3.14) → Phase 1 outcome (RESOLVED)
  - 1 (Task 3.25) → Phase 4 outcome (executed or skipped+deferred)
  - 2 (Tasks 6.1 / 6.4) → Phase 3 outcome
- [ ] Note that the Continuation Guide is now historically complete — no PROJ-322 deferrals remain unaddressed.

**Notes:** [Filled during implementation]

---

### Task 5.5: Lessons-learned summary in decisions.md [Simple]

**File:** [`decisions.md`](decisions.md)

- [ ] Append a new "Lessons Learned" table or section at the bottom of decisions.md.
- [ ] Document: which technique yielded the biggest wall-clock delta per LOC touched? Which technique was lowest-risk? Which technique required the most rework?
- [ ] Future test-quality projects should reference this when prioritizing.

**Notes:** [Filled during implementation. Be specific — quantify.]

---

### Task 5.6: Cross-project final audit [Simple]

- [ ] Run `python Projects/scripts/check_project_status.py PROJ-327` — confirm all phases marked Complete (modulo Phase 4 if skipped).
- [ ] Verify all PROJ-322 deferred items have closure annotations (RESOLVED or RE-CONFIRMED DEFERRED with evidence).
- [ ] Verify no PROJ-322/323/324/325/326 cross-references are broken by PROJ-327's edits.

**Notes:** [Filled during implementation. Note any cross-project discrepancies.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Final runtime delta documented + shared with user
- [ ] `docs/known-issues.md` updated
- [ ] PROJ-322 Continuation Guide marks all 9 deferrals dispositioned
- [ ] Lessons-learned section added to decisions.md
- [ ] Sharded test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "All phases Complete"
- [ ] Update `plan.md` Verification section checkboxes
