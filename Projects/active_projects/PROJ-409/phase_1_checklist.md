# Phase 1: Close MAJ-013 and MAJ-014

**Status:** Not Started
**Objective:** Land definitive closure (active or ratified) on the two PROJ-395 deferrals.

---

## Tasks

### Task 1.1: Investigate MAJ-013 — EventBus Pattern #10 shim [Medium]
**File:** TBD — discover

- [ ] Read `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-395_report.md` for the MAJ-013 writeup.
- [ ] Read PROJ-395's findings/verification_report.md for detailed context.
- [ ] Locate the shim: `rg -n "Pattern #10|pattern_10|EventBus.*shim" game/ docs/`. Also search `docs/02_PATTERNS.md` for Pattern #10's definition.
- [ ] Decide: (a) actively delete (preferred per Rule 3 — no shims), (b) ratify as won't-fix with a written reason in `decisions.md`, (c) roll into a future cleanup project with a clear handle.
- [ ] If (a): delete the shim, run focused tests, commit.
- [ ] If (b) or (c): document in `decisions.md` and proceed.

**Notes:**

### Task 1.2: TDD — write failing test for MAJ-014 canonical path [Medium]
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py` (or closest)

- [ ] Read `game/ui/screens/strategy_game_state_manager.py:19, 149-158` to see the current import + defensive catch.
- [ ] Find or create the test module.
- [ ] Write a test that:
  - Patches the underlying call (`facade.process_turn(...)` or wherever the manager invokes it) to raise `TurnFailedError`.
  - Asserts the manager handles it correctly (sets the dialog, clears progress overlay state, skips autosave/event-log).
  - Assert NO ImportError or test failure if `EnginePhaseError` is removed from the import list.
- [ ] Run the test against unmodified production — should currently PASS (the canonical path already works). The point is to add coverage that PINS the canonical path before we delete the defensive catch.
- [ ] Add a second test that asserts raw `EnginePhaseError` is NOT caught by the manager after the deletion (i.e., it propagates raw — the architectural contract). Run against current code — this test should FAIL (the defensive catch swallows it). Confirms RED.

**Notes:**

### Task 1.3: Remove the defensive `EnginePhaseError` catch [Simple]
**File:** `game/ui/screens/strategy_game_state_manager.py:19, 149-158`

- [ ] Delete the `EnginePhaseError` import at line 19 (and from the `except` tuple at line 149-158, leaving only `TurnFailedError`).
- [ ] If the `except` clause was specifically `except (TurnFailedError, EnginePhaseError):`, narrow to `except TurnFailedError:`.
- [ ] Run the regression test from Task 1.2 — should now pass (raw `EnginePhaseError` propagates).
- [ ] Run the broader UI suite to confirm no callers depend on the dropped catch: `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py -v` and `pytest tests/integration/ui/ -k turn -v`.

**Notes:**

### Task 1.4: Document the closure in `decisions.md` [Simple]

- [ ] MAJ-013 row: decision (delete / ratify / defer), rationale, file:line if deleted, future-project handle if deferred.
- [ ] MAJ-014 row: "Removed defensive catch on 2026-05-09. Facade conversion is unit-tested by PROJ-408 C-02. Per CLAUDE.md Rule 4, dead defensive code removed."
- [ ] Cross-reference: PROJ-395 verification report should be updated to point at PROJ-409's resolution. (Wave 2 PROJ-406 already closed PROJ-395's bookkeeping with the deferral note — extend or replace that note here.)

**Notes:**

### Task 1.5: Cross-reference closure in PROJ-395 plan
**File:** `Projects/active_projects/PROJ-395/{plan,decisions}.md`

- [ ] Add a note in PROJ-395's `decisions.md` (or equivalent) pointing to PROJ-409 commit SHAs as the final closure of MAJ-013 + MAJ-014.
- [ ] Re-run `python Projects/scripts/validate_audit_ready.py PROJ-395` — still PASS.

**Notes:**

### Task 1.6: Closeout
- [ ] Phase 1 status `Complete`
- [ ] Plan.md updated
- [ ] `Projects/projects_index.md` row for PROJ-409 set to `Complete`
- [ ] Validators PASS
- [ ] Commit (one or more): `PROJ-409 phase 1: close MAJ-013 (...) and MAJ-014 (remove defensive EnginePhaseError catch)`
- [ ] Verification report at `findings/verification_report.md`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] Focused suites pass
- [ ] `python Projects/scripts/validate_phase.py PROJ-409 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-409` PASSED
