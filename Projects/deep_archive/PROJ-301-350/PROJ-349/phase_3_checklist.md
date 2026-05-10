# Phase 3: Final closeout — full sharded suite + merge readiness

**Status:** Not Started
**Objective:** Run the full sharded suite. Ensure all PROJ-321..341 follow-on projects are marked `Awaiting Verification`. Surface a merge-readiness summary to the user.

---

## Tasks

### Task 3.1: Full unit suite [Simple]
**Tests:** `python -m pytest tests/unit/ -q`

- [ ] All pass — record exact count in [decisions.md](decisions.md).

**Notes:**

### Task 3.2: Full sharded suite from repo root [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] **MUST be run from `c:/Developer/StarshipBattles/`, NOT from a worktree** — the script has a known `\a` bug in worktree paths.
- [ ] All shards green; pre-existing failures (8 codex-discuss-skills) constant.
- [ ] Record counts + wall time in [decisions.md](decisions.md).

**Notes:**

### Task 3.3: Lint sweep [Simple]
**Tests:** `python Tools/lint_test_files.py`

- [ ] 0 violations.

**Notes:**

### Task 3.4: Final `Projects/projects_index.md` pass [Simple]
**File:** `Projects/projects_index.md`

- [ ] Confirm PROJ-343..349 all show `Awaiting Verification`.
- [ ] Update PROJ-349 → `Awaiting Verification` (this project is the last one, so its closeout commit happens here).
- [ ] Commit: `chore(PROJ-349): mark Sprint 7 awaiting verification`

**Notes:**

### Task 3.5: Merge-readiness summary [Medium]

- [ ] Compose a summary for the user covering:
  - 7 follow-on projects landed (PROJ-343..349) with commit count per project.
  - Tier-1 production bugs fixed (count: 5).
  - Test count delta from baseline 15,708 → final.
  - PROJ-342 (TestLab) coexistence — confirm no conflicts.
  - Pre-existing known failures still constant (codex-discuss-skills × 8).
  - User decision points: merge-to-main, push-to-remote.
- [ ] Surface to user. DO NOT push or merge without explicit user direction.

**Notes:**

### Task 3.6: Stop point [Simple]

- [ ] User decides:
  - "Merge" → user (or implementer with explicit go-ahead) handles `git checkout main && git merge --no-ff feat/03c-phase-aware-execution` and the push.
  - "Push only" → implementer runs `git push -u origin feat/03c-phase-aware-execution` after explicit go-ahead.
  - "Hold" → arc complete, branch stays open for further review.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Full sharded suite green
- [ ] Merge-readiness summary delivered
- [ ] User direction received and (if requested) acted on
- [ ] PROJ-349 plan.md → Complete
- [ ] All PROJ-343..349 in `Projects/projects_index.md` → `Awaiting Verification`
