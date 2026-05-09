# Phase 2: MAJOR — 14 follow-up findings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-395 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (12 closed in commit 793f592e0; MAJ-013 + MAJ-014 deferred — see commit message)
**Objective:** Close the 14 MAJOR findings from the PROJ-381 review. Each is a focused, well-scoped follow-up; many are doc/test/comment polish.

---

## Tasks

### Task 2.1: Read the source review
**File:** `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/report.md`
**Tests:** —

- [ ] Read the full MAJOR section. The 14 items map roughly to:
  - MAJ-001: `TurnFailedError` docstring claims properties that don't exist
  - MAJ-002: `docs/05_ERROR_HANDLING.md` hierarchy tree is stale
  - MAJ-003: Regression test mocks exception class rather than triggering real failure
  - MAJ-004: `TurnFailedError` lacks `turn_number`/`save_path` properties despite context enrichment
  - MAJ-005: `GameSession` init recovery emits no ERROR log
  - MAJ-006: `tkinter_utils.py` broad-catch comments are pro-forma boilerplate
  - MAJ-007 through MAJ-014: Test quality issues (from Agent 5 in the multi-agent review)

### Task 2.2: Address each MAJOR finding individually
**Files:** Various — see source review per-finding
**Tests:** Per-task focused tests

- [ ] MAJ-001: Fix `TurnFailedError` docstring (remove non-existent properties)
- [ ] MAJ-002: Update `docs/05_ERROR_HANDLING.md` hierarchy tree to include `TurnFailedError`, `BattleResolutionError`, `SessionInitializationError`, `ImageUnexpectedError`
- [ ] MAJ-003: Rewrite the B-5 regression test to trigger an actual `EnginePhaseError` rather than mocking the exception class. Hint: use a planted error in a test-only turn-engine subclass.
- [ ] MAJ-004: Add `turn_number` and `save_path` as `@property` accessors on `TurnFailedError` (or document why they live in `context` only)
- [ ] MAJ-005: Add ERROR log in `GameSession.__init__` recovery path so the null-object substitution is visible in operator logs
- [ ] MAJ-006: Replace pro-forma broad-catch comments in `game/ui/services/tkinter_utils.py` with substantive `# Intentional broad catch: <reason>` comments
- [ ] MAJ-007 through MAJ-014: Address each test-quality finding (read the review for specifics — generally about brittle string assertions, mocked exceptions, missing happy-path tests)

### Task 2.3: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved
- [ ] Verify: pytest passes

---

## Phase Completion Checklist
- [ ] All 14 MAJOR items closed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/`_
