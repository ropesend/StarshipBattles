# Phase 1: PROJ-323 documentation corrections

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-325 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the OpenCode 323-review findings: 1 CRIT (false-positive `[x]` checkmarks on tasks targeting deleted files) + the doc/test MIN findings (terminology mismatch, LOC delta annotation, design.md references, manifest cleanup, Task 5.19 precision mismatch).

**Required reading:**
- [`Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md`](Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md) — full finding list
- Each PROJ-323 file before editing

**Parallelism:** Fully parallel-safe with PROJ-324 (file-disjoint) and PROJ-326 (file-disjoint). Can also run in parallel with Phase 2 of this same project. Do NOT run in parallel with Phase 3 of this same project (Phase 3 is conditional and starts after PROJ-324 Phase 3 Task 3.4).

---

## Tasks

### Task 1.1: Fix Tasks 3.3 + 3.6 false-positive checkmarks (FND-CC-001) [Simple]

**File:** [`Projects/active_projects/PROJ-323/phase_3_checklist.md`](Projects/active_projects/PROJ-323/phase_3_checklist.md)

- [ ] Locate Task 3.3 (S11-CAT10-005, target file `tests/unit/strategy/data/test_colonization_facade.py`). The file was deleted by PROJ-321.
- [ ] Replace the `[x]` checkmarks for the deleted-file work items with `[-]` (or remove the checkmark) and add the standard skip annotation: `_(skipped — upstream project already deleted target file)_`.
- [ ] Same treatment for Task 3.6 (S11-CAT10-007, target file `tests/unit/ui/test_color_helpers.py`).
- [ ] Document the ~314 LOC fictitious delta — note it in this task's Notes so any cross-project audit reconciles correctly.
- [ ] Verify: `python Projects/scripts/check_project_status.py PROJ-323` still parses cleanly.

**Notes:** [Filled during implementation]

---

### Task 1.2: Resolve Task 3.10 ambiguity (FND-CC-005) [Simple]

**File:** [`Projects/active_projects/PROJ-323/phase_3_checklist.md`](Projects/active_projects/PROJ-323/phase_3_checklist.md)

- [ ] Locate Task 3.10 — currently marked `[x]` (complete) but annotated "deferred". This is internally inconsistent.
- [ ] Investigate the actual state: read the cited test file, check git blame, determine whether the task was actually done or deferred.
- [ ] Pick one: if done, remove the deferral annotation. If deferred, un-check `[x]` and keep the deferral annotation.
- [ ] Document the determination in Notes.

**Notes:** [Filled during implementation]

---

### Task 1.3: Reconcile "items" vs "tasks" terminology + LOC delta annotation (FND-CC-002, FND-CC-003) [Simple]

**File:** [`Projects/active_projects/PROJ-323/plan.md`](Projects/active_projects/PROJ-323/plan.md)

- [ ] In the header table: 32+32+53+15+27 = 159 "items" but Current State says 149/149 "tasks". Add a footnote explaining: "items" = source-review CAT-finding count; "tasks" = checklist Task N.M count; gap = items absorbed into multi-finding tasks (e.g., Phase 2 has 30 tasks for 32 items).
- [ ] Per-task LOC delta numbers in verify lines are pre-work estimates from the source review. Annotate them as such, OR replace with actual git-stat deltas from the merge commits. The naive sum shows ~7,700+ when actual is ~-1,418, so an unannotated reader is misled.
- [ ] Verify: plan.md is internally consistent.

**Notes:** [Filled during implementation]

---

### Task 1.4: Clean stale manifest entries (FND-CC-004) [Medium]

**File:** [`Projects/active_projects/PROJ-323/manifest.md`](Projects/active_projects/PROJ-323/manifest.md)

- [ ] Walk the manifest. For each entry, check whether the file still exists at the listed path. Remove entries for files PROJ-321 deleted (~42 of ~147 per the OpenCode review).
- [ ] Add a header comment documenting the cleanup date + reason: `<!-- Cleaned 2026-05-04 (PROJ-325 Phase 1 Task 1.4): removed entries for files deleted by upstream PROJ-321. See FND-CC-004 in OpenCode 323-review. -->`
- [ ] Verify: `python Projects/scripts/check_project_status.py PROJ-323` still parses.

**Notes:** [Filled during implementation. Record exact count of removed entries.]

---

### Task 1.5: Fix design.md line 41 + line 42 (FND-P2-003, FND-P2-005) [Simple]

**File:** [`Projects/active_projects/PROJ-323/design.md`](Projects/active_projects/PROJ-323/design.md)

- [ ] Line 41 references `test_projectile_manager.py` as canonical CAT-12 example, but the file was deleted by upstream work. Replace with a surviving example (e.g., the Task 5.18/5.23 implementations cited in the OpenCode review as fundamentally sound).
- [ ] Line 42 mischaracterizes Task 4.2 pattern as "advisory soft assertions" — the actual implementation is hard assertions with adjustable thresholds (`assert total <= EXPECTED_X_COUNT`). Reword.

**Notes:** [Filled during implementation]

---

### Task 1.6: Fix Task 5.19 precision mismatch (FND-P2-001) [Simple]

**File:** [`tests/unit/simulation/projectile/test_projectile_manager.py`](tests/unit/simulation/projectile/test_projectile_manager.py) (verify path — Task 1.5 may have updated design.md to point at a different file)
**Tests:** `pytest tests/unit/simulation/projectile/test_projectile_manager.py`

- [ ] Locate the test/assertion using docstring approximations like `~0.94`, `~0.9787` paired with `pytest.approx(rel=1e-9)` on `-0.005596103475344202`.
- [ ] Pick ONE of:
  - Add intermediate values to the docstring at assertion precision (e.g., `vector decomposition: 0.94247... × 0.97872... × 0.00606... = -0.005596...`), so a maintainer can re-derive the expected value.
  - Relax the tolerance to `rel=1e-5` if the precision claim is overly tight.
- [ ] Verify: tests still pass.

**Notes:** [Filled during implementation. Record which option chosen.]

---

### Task 1.7: Fix Task 4.9 mis-categorization (FND-P2-004) [Simple]

**File:** [`Projects/active_projects/PROJ-323/phase_4_checklist.md`](Projects/active_projects/PROJ-323/phase_4_checklist.md)

- [ ] Locate Task 4.9. It's annotated as fragile-assertion replacement (CAT-11) but is actually data cleanup. Re-categorize the task header / annotation accordingly.

**Notes:** [Filled during implementation]

---

### Task 1.8: Re-derive Tasks 2.8 + 2.9 LOC deltas (FND-CC-006) [Simple]

**File:** [`Projects/active_projects/PROJ-323/phase_2_checklist.md`](Projects/active_projects/PROJ-323/phase_2_checklist.md)

- [ ] Tasks 2.8 (~307 LOC) and 2.9 (~250 LOC) double-count work done in Phase 1. Re-derive from `git log --stat` of the relevant commits.
- [ ] Update verify lines with actual deltas.

**Notes:** [Filled during implementation. Record actual deltas.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] No stale `[x]` for deleted files in PROJ-323 phase checklists
- [ ] Tests still pass: `pytest tests/unit/simulation/projectile/test_projectile_manager.py`
- [ ] PROJ-323 plan.md / design.md / manifest.md are internally consistent
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 2 (if not already done in parallel)
