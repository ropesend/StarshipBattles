# Phase 4: Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Record the new Python baseline in all places future contributors will look. Per CLAUDE.md Rule 2: docs are part of the deliverable.

---

## Tasks

### Task 4.1: Update CLAUDE.md "Tech Stack" entry [Simple]
**File:** [CLAUDE.md](../../../CLAUDE.md)
**Tests:** N/A — doc update

- [x] Found the "Tech Stack" section (line 142). Was "Python 3.x".
- [x] Replaced with explicit "Python 3.13+" + venv activation instructions + the PROJ-295 trigger comment.
- [x] Bumped pytest baseline mention from 14420 → 15112 tests; named the sharded runner location.

**Notes:**

---

### Task 4.2: Check root README.md [Simple]
**File:** N/A
**Tests:** N/A

- [x] No root `README.md` exists. Skipped.

**Notes:**

---

### Task 4.3: Update Tools/qa_observer/README.md [Simple]
**File:** [Tools/qa_observer/README.md](../../../Tools/qa_observer/README.md)
**Tests:** N/A

- [x] Grepped for `pyaudio`, `Python 3.10`, `FutureWarning` — no matches. The README doesn't mention Python version or the Google warning. Nothing to update.

**Notes:**

---

### Task 4.4: Add `.python-version` (pyenv) [Simple]
**File:** [.python-version](../../../.python-version)
**Tests:** N/A

- [x] Created with `3.13.13` (the actually-installed version).

**Notes:**

---

### Task 4.5: Update combat_lab/README.md System Requirements [Simple]
**File:** [combat_lab/README.md](../../../combat_lab/README.md)
**Tests:** N/A

- [x] Found "Python 3.10+" at line 641. Updated to "Python 3.13+ (PROJ-295: project baseline bumped from 3.10 on 2026-04-26)".

**Notes:** This task wasn't in the original Phase 4 plan but was discovered during the broader grep for `Python 3.10` references.

---

### Task 4.6: Update auto-memory [Simple]
**File:** Memory files at `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\`
**Tests:** N/A

- [x] Wrote topic file `proj_295_python_upgrade.md` with full upgrade detail (decisions, code changes, test fix rationale, verification, future cleanup opportunity).
- [x] Added one-line index entry to MEMORY.md under "In-Progress Projects" pointing to the topic file.

**Notes:** Followed the topic-file pattern established by PROJ-293 to keep MEMORY.md within size budget.

---

### Task 4.7: Verify .gitignore [Simple]
**File:** [.gitignore](../../../.gitignore)
**Tests:** `git status`

- [x] `.venv` already in .gitignore.
- [x] `pyproject.toml` is NOT ignored (correct — should be committed).
- [x] `.python-version` is NOT ignored (correct — should be committed for pyenv users).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Documentation reflects the new Python baseline (Python 3.13+ in CLAUDE.md, combat_lab/README.md; `.python-version` and `pyproject.toml` declare the requirement)
- [x] No stale references to "Python 3.10" remain in user-facing docs (Reviews/, archived projects, Tracking/ historical artifacts left as-is — those are frozen records)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phase 5 — closeout"
