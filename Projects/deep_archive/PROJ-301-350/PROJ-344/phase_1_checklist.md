# Phase 1: Doc + test misalignment cleanup (T2.1 .. T2.6)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-344 1`
> 2. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Land six small fixes for cross-validated doc/test misalignments. Commit per concern.

---

## Tasks

### Task 1.1: T2.1 — PROJ-336 D-008 rewrite [Simple]
**File:** `Projects/active_projects/PROJ-336/decisions.md`
**Tests:** none (doc only)

- [ ] Read line 15 (currently "negative load reduces projected cargo").
- [ ] Read `game/strategy/services/fleet_cargo_projector.py:54-61` and the test pin at `tests/unit/strategy/services/test_fleet_cargo_projector.py:123-146` to confirm the actual semantics: any non-positive load fills to capacity (auto-fill sentinel); any non-positive unload drains to zero.
- [ ] Rewrite D-008 to match production. Mark the old wording as superseded (date-stamped).

**Notes:**

### Task 1.2: T2.3 — PROJ-332 `harvest` → `harvesting` [Simple]
**File:** `Projects/active_projects/PROJ-332/{design.md, phase_1_checklist.md}`
**Tests:** none (doc only)

- [ ] In `design.md:69-72`, replace `harvest` with `harvesting` (the actual phase key).
- [ ] In `phase_1_checklist.md:31`, same.

**Notes:**

### Task 1.3: T2.1 + T2.3 commit
- [ ] `git status` — verify no unrelated files staged.
- [ ] Stage only PROJ-336 + PROJ-332 doc changes.
- [ ] Commit: `docs: align PROJ-336 D-008 + PROJ-332 phase key with production (PROJ-344 T2.1 T2.3)`

**Notes:**

### Task 1.4: T2.2 — PROJ-327 `-3.9s` retraction across docs [Medium]
**Files:** `Projects/active_projects/PROJ-327/{decisions.md:31, runtime_delta.md:37,41, phase_5_checklist.md:27,44,56,83, phase_1_checklist.md:92, virtual_table_runtime.md:25,38}`, `docs/known-issues.md:128,132`
**Tests:** none (doc only)

- [ ] For each cell listed, append `(retracted per audit S2.7)` OR strikethrough.
- [ ] If a cell asserts "best-ROI win" on the basis of `-3.9s`, rewrite to remove the misleading framing entirely (the actual measured delta is within noise).
- [ ] `docs/known-issues.md:128,132` are USER-FACING — prioritize clarity over minimal-edit.

**Notes:**

### Task 1.5: T2.2 commit
- [ ] Stage only the PROJ-327 docs + `docs/known-issues.md`.
- [ ] Commit: `docs(PROJ-327): mark -3.9s retraction across all in-repo cites (PROJ-344 T2.2)`

**Notes:**

### Task 1.6: T2.5 — concurrent_commit_audit update [Medium]
**File:** `Projects/active_projects/PROJ-329A/findings/concurrent_commit_audit.md`
**Tests:** none (doc only)

- [ ] `git show --stat ddfec64e0` — confirm `empire_panel_window.py` (PROJ-329B work) appears alongside the labeled PROJ-333 changes.
- [ ] `git show --stat 9d16524f1` — confirm `planet_abilities_window.py` + `planet_abilities_controller.py` (PROJ-329C work) appear alongside the labeled PROJ-333 changes.
- [ ] Append both commits to the audit file in the same shape as the existing two entries (commit SHA, labeled message, actually-contains list, bisect/revert impact).
- [ ] Update the disposition section's commit count.

**Notes:**

### Task 1.7: T2.5 commit
- [ ] Stage only the audit doc.
- [ ] Commit: `docs(PROJ-329A): record 2 additional concurrent-commit contaminations (PROJ-344 T2.5)`

**Notes:**

### Task 1.8: T2.4 — MockStrategyScreenComposition guard [Medium]
**File:** locate `MockStrategyScreenComposition` via `git grep -n "MockStrategyScreenComposition"`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen_composition.py -x` (or whichever file)

- [ ] Read the existing class. Audit S4.4 added a guard; current docstring claims "same screen, different composition" but code actually catches "same composition, different screens".
- [ ] Fix docstring to match code.
- [ ] Add test: same-screen reuse passes (no exception).
- [ ] Add test: different-screen reuse raises (exact exception type and message asserted).
- [ ] Run.

**Notes:**

### Task 1.9: T2.4 commit
- [ ] Stage MockStrategyScreenComposition file + new tests.
- [ ] Commit: `test: cover MockStrategyScreenComposition guard + fix docstring (PROJ-344 T2.4)`

**Notes:**

### Task 1.10: T2.6 — Facade method-surface invariant verification [Medium]
**File:** `tests/unit/strategy/services/test_strategy_session_facade_contract.py`
**Tests:** `pytest tests/unit/strategy/services/test_strategy_session_facade_contract.py -x`

- [ ] Read the file (114 LOC).
- [ ] `git log --diff-filter=D --all -- 'tests/unit/**/test_strategy_session_facade_public_api.py'` — find the deletion commit.
- [ ] `git show <commit>` — extract the deleted `TestPublicMethodSurface` class to see what invariant it asserted (likely a `PUBLIC_METHODS` set diff).
- [ ] Diff against current `test_strategy_session_facade_contract.py` — does the new file cover the public-method-surface invariant? If yes: document in [decisions.md](decisions.md) and skip restoration. If no: add a `TestPublicMethodSurface`-style class.

**Notes:**

### Task 1.11: T2.6 commit (if change made)
- [ ] If facade contract was extended: commit `test: restore facade public-method-surface invariant (PROJ-344 T2.6)`.
- [ ] If verified-only: add note to [decisions.md](decisions.md), no commit.

**Notes:**

### Task 1.12: Verification + index update
- [ ] `pytest tests/unit/strategy/services/ tests/unit/ui/screens/test_strategy_screen_composition.py -x -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-344 → `Awaiting Verification`. Single commit: `chore(PROJ-344): mark Sprint 2 awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] Commits per concern landed
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State; surface to user
