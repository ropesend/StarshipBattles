# Phase 1: TBD

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-352 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** [What this phase accomplishes]

---

## Tasks

### Task 1.1: [Task Name] [Simple/Medium/Complex]
**File:** `path/to/file.py`
**Tests:** `pytest tests/path/`

- [ ] Subtask with specific action
- [ ] Another subtask
- [ ] Verify: [what to check]

**Notes:**

### Task 1.2: Rewrite docstring [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:20-28`
**Tests:** none (doc only)

- [ ] Remove or rewrite any claim that the builder "owns the widget tree".
- [ ] State the actual relationship: builder is a Pattern §33 test-substitution seam; `build()` currently delegates to `screen._create_ui()` (low-priority follow-up could move widget construction into the builder, but that is NOT this project's scope).
- [ ] Cross-reference Pattern §33 in `docs/02_PATTERNS.md` if useful.

**Notes:**

### Task 1.3: Commit [Simple]

- [ ] `git status` — verify only `new_game_setup_screen.py` staged.
- [ ] Commit: `docs(new-game-setup-screen): fix misleading builder docstring per PROJ-352A T4.7`

**Notes:**

### Task 1.4: Update plan.md to point to Phase 2

- [ ] Mark Phase 1 complete; Active Phase → Phase 2 (T6.6).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
