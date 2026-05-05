# Phase 1: T6.8 — facade `_session` lint decision

**Status:** Complete
**Objective:** Make and document the explicit decision on facade `_session` lint enforcement. Per Codex consensus: keep convention-only unless an external-access regression appears.

---

## Tasks

### Task 1.1: Confirm current state [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py:80-90, 156-182` (read-only)

- [x] Confirm `_session` is the underscore-prefixed convention-protected name.
- [x] `git grep -nE "facade\._session|\.facade\._session" game/ tests/` — confirm there are no current external-access violations. (Only 3 test-internal refs.)
- [x] Document the current state in [decisions.md](decisions.md).

**Notes:**

### Task 1.2: Decide [Simple]

- [x] Default per Codex consensus: **convention-only, no lint rule added**. Decision logged in [decisions.md](decisions.md).
- [x] Surface to the user if you want to override this default. (Default accepted; no override needed.)

**Notes:**

### Task 1.3 (optional): Regression trap [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_session_isolation.py` (NEW)

- [ ] ~~If you want a cheap regression trap: a test that asserts `_session` is NOT in the public-surface listing per `Tools/lint_test_files.py` allowlist or per facade contract test.~~
- [ ] ~~Run.~~
- [x] Skip this sub-task if you decide convention-only is sufficient. **SKIPPED** — convention-only stands.

**Notes:**

### Task 1.4: Commit decision [Simple]

- [x] If only [decisions.md](decisions.md) changed: commit `docs(PROJ-353 T6.8): record decision to keep facade _session enforcement convention-only`.
- [ ] ~~If a regression-trap test was added: separate commit~~ N/A.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked (or sub-task 1.3 explicitly skipped per decision)
- [ ] T6.8 decision logged + commit landed
- [ ] plan.md phase table → `Complete`
- [ ] Update Current State to point to Phase 2 (Tier-7 polish bundle)
