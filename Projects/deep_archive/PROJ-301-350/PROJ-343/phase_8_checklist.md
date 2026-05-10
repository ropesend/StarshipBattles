# Phase 8: Verification + fresh OpenCode review

**Status:** Not Started
**Objective:** Confirm all five Tier-1 fixes work in concert. Dispatch a fresh OpenCode review on the PROJ-343 commits before continuing to PROJ-345 (Sprint 3).

---

## Tasks

### Task 8.1: Full unit suite [Simple]
**Tests:** `python -m pytest tests/unit/ -q`

- [ ] All pass — 15,708+ pass / 0 fail / 2 skip baseline. Small delta acceptable for added/removed pinning tests; record exact count in [decisions.md](../PROJ-343/decisions.md).
- [ ] Investigate ANY new failure — must be either a known intentional pin-rewrite (Phase 2-7 anticipated) or a real regression (BLOCKER).

**Notes:**

### Task 8.2: Lint test files [Simple]
**Tests:** `python Tools/lint_test_files.py`

- [ ] 0 violations.

**Notes:**

### Task 8.3: Manual smoke (optional, recommended) [Medium]
**Tests:** Manual

- [ ] T1.1: launch game, open TransferDialog with two fleets at same hex, transfer 1 passenger fleet→fleet. Confirm no "Planet not found." error. Order appears in queue.
- [ ] T1.4: open TransferDialog without selecting source/target, click Confirm. Dialog stays open.
- [ ] T1.5: not feasibly testable manually; rely on Phase 1 task-1.6 test.
- [ ] T1.2/T1.3: not feasibly testable manually; rely on the new Phase 1 tests.

**Notes:**

### Task 8.4: Update Projects/projects_index.md [Simple]

- [ ] Set PROJ-343 status to `Awaiting Verification`.
- [ ] `git status` first, stage only `Projects/projects_index.md`.
- [ ] Commit: `chore(PROJ-343): mark Sprint 1 awaiting verification`

**Notes:**

### Task 8.5: Dispatch fresh OpenCode review [Medium]
**Skill:** `claude-delegate-review` — read `.claude/skills/claude-delegate-review/SKILL.md` first

- [ ] Confirm review daemon is running (or start it per the SKILL.md instructions).
- [ ] Build a delegate-review request scoped to PROJ-343 commits (the 6 fix commits + Phase 1 test commit).
- [ ] Submit. Wait for the review to land in `Reviews/results/`.
- [ ] Read the review report.

**Notes:**

### Task 8.6: Triage review findings [Medium]

- [ ] If 0 CRITICAL: PROJ-343 is ready for user verification. Surface to user; note any non-CRITICAL findings as observations in [decisions.md](../PROJ-343/decisions.md) (or open a follow-up project if substantial).
- [ ] If ≥1 CRITICAL: triage with user. Add a Phase 9 to this project to address, OR open a remediation sub-project. DO NOT proceed to PROJ-345 until CRITICALs are resolved.

**Notes:**

### Task 8.7: Stop point — surface to user
- [ ] Write a concise summary: 5 defects fixed, commits landed, suite green, review dispatched. Defer the user's continuation decision to them.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] PROJ-343 marked Awaiting Verification in projects_index.md
- [ ] Fresh OpenCode review returned no CRITICAL findings (or CRITICALs resolved before close)
- [ ] User informed; awaiting decision on continuing to PROJ-345
