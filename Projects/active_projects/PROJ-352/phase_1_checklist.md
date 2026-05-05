# Phase 1: T4.7 — NewGameSetup builder docstring fix

**Status:** Not Started
**Objective:** Correct the misleading docstring at `new_game_setup_screen.py:20-28` that claims the builder owns the widget tree (currently false; `build()` is a one-line passthrough). Per Codex r003: KEEP the builder seam (Pattern §33-compliant test substitution surface); just fix the doc.

---

## Tasks

### Task 1.1: Read current docstring + builder shape [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py:20-28`, `game/ui/screens/new_game_setup_ui_builder.py:37-38`

- [ ] Read both files to confirm the divergence between docstring claim and code reality.
- [ ] Document the actual current relationship in [decisions.md](decisions.md) for future maintainers.

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
- [ ] Commit: `docs(new-game-setup-screen): fix misleading builder docstring per PROJ-352 T4.7`

**Notes:**

### Task 1.4: Update plan.md to point to Phase 2

- [ ] Mark Phase 1 complete; Active Phase → Phase 2 (T6.6).

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] T4.7 commit landed
- [ ] plan.md phase table → `Complete`
