# Phase 3: Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Record the new Python baseline in all places future contributors will look. Per CLAUDE.md Rule 2: docs are part of the deliverable.

---

## Tasks

### Task 3.1: Update CLAUDE.md "Tech Stack" entry [Simple]
**File:** [CLAUDE.md](../../../CLAUDE.md)
**Tests:** N/A — doc update

- [ ] Find the "Tech Stack" section. Currently lists "Python 3.x" (generic).
- [ ] Replace with: `- Python <TARGET>+ (upgraded from 3.10 in PROJ-295; deadline driver was Google client lib EOL on 2026-10-04)`
- [ ] Mention `.venv` activation if Phase 2 introduced one
- [ ] Save

**Notes:**

---

### Task 3.2: Update README.md [Simple]
**File:** [README.md](../../../README.md) (if exists)
**Tests:** N/A

- [ ] Check if there's a README at repo root mentioning Python version. If yes, update.
- [ ] If no README mentions Python version, skip this task.

**Notes:**

---

### Task 3.3: Update Tools/qa_observer/README.md [Simple]
**File:** [Tools/qa_observer/README.md](../../../Tools/qa_observer/README.md)
**Tests:** N/A

- [ ] If the QA observer README mentions Python version requirements, update.
- [ ] If it mentions the Google FutureWarning, remove that section.

**Notes:**

---

### Task 3.4: Add `.python-version` (pyenv) [Simple]
**File:** `.python-version` (new file at repo root)
**Tests:** N/A

- [ ] Create with one line containing the target version (e.g. `3.12.7` for 3.12)
- [ ] This file is recognized by `pyenv` users and clarifies the intended version

**Notes:** Skip if Phase 0 Q5 said no to additional environment files.

---

### Task 3.5: Update auto-memory MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** N/A

- [ ] Add an entry under "Recently Archived" or "Completed Projects" once PROJ-295 closes
- [ ] One line under ~150 chars: `- [PROJ-295 Python 3.x→<TARGET> Upgrade](file.md) — baseline bumped <date>; deadline was Google EOL 2026-10-04`
- [ ] Append a topic file at `memory/proj_295_python_upgrade.md` with details

**Notes:** Per CLAUDE.md auto-memory section, MEMORY.md is the index, individual files hold detail.

---

### Task 3.6: Verify .gitignore covers any new env files [Simple]
**File:** [.gitignore](../../../.gitignore)
**Tests:** `git status` shows clean working tree

- [ ] If Phase 2 created `.venv` at repo root, confirm `.gitignore` ignores it (likely already does)
- [ ] If Phase 2 created `pyproject.toml`, confirm it is NOT in `.gitignore` (it should be committed)
- [ ] `git status` shows only the changes from this project

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Documentation reflects the new Python baseline
- [ ] No stale references to "Python 3.10" remain in user-facing docs
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Phase 4 — closeout"
