# Phase 4: Final verification + audit-script green

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-316 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm the remediation closed all 5 audit findings,
PROJ-313 is genuinely audit-ready, and no regressions were introduced.

---

## Tasks

### Task 4.1: PROJ-313 audit script green [Simple]
**Command:** `python Projects/scripts/validate_audit_ready.py PROJ-313`
**Tests:** Exit code 0.

- [ ] Run the script. Capture output.
- [ ] Acceptance: exit code 0. No errors. Warnings tolerable.
- [ ] If any errors remain, address them (most likely additional checklist items missed in Phase 1).

**Notes:**

---

### Task 4.2: Full sharded test suite [Simple]
**Command:** `python Tools/test_sharded/test_sharded.py`
**Tests:** Pass count matches kick-off baseline modulo PROJ-315.

- [ ] Run the full sharded suite.
- [ ] Compare pass/fail count to PROJ-316 kick-off baseline.
- [ ] **Acceptance:** failures should be limited to the PROJ-315 cases recorded at kick-off (the 8 in `tests/unit/strategy/test_ship_instance_damage.py`, or 0 if PROJ-315 has been fixed by then). Anything else is a regression and must be fixed before Phase 4 is Complete.

**Notes:**

---

### Task 4.3: Doc cross-reference walk [Simple]
**Files:** `docs/02_PATTERNS.md`, `docs/06_UI_STYLE_GUIDE.md`
**Tests:** Manual re-read; cross-reference every claim against live code.

- [ ] Re-read `docs/02_PATTERNS.md` Pattern #31. Cross-reference every claim:
      - Adopter count: count `class.*StrategyModalWindow` declarations in `game/ui/screens/`.
      - "Both methods walk `iter_live_modals()`": read `strategy_event_router.py:has_modal_open` and confirm.
      - "New structural test at `tests/unit/ui/screens/test_strategy_modal_window.py`": confirm file exists and tests pass.
      - "Legacy `TestModalSlotCleanupContract` retained": confirm class still in `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`.
      All claims must be accurate.
- [ ] Re-read `docs/02_PATTERNS.md` Pattern #30 SUPERSEDED banner. Confirm the clarification from Phase 1 Task 1.4 is in place.
- [ ] Re-read `docs/06_UI_STYLE_GUIDE.md` Window Management section. Confirm the example shows `window_manager: "StrategyWindowManager"` (required) for strategy-screen-only adopters per Phase 2 Task 2.4.

**Notes:**

---

### Task 4.4: Manual smoke-test of the fix's intent [Simple]
**Tests:** Manual.

- [ ] In a Python REPL, attempt to construct a strategy-screen-only window without `window_manager=`. Confirm `TypeError: missing 1 required keyword-only argument: 'window_manager'` is raised (per Phase 2's structural guarantee).
- [ ] Apply the three Phase 3 mutation tests one more time as a regression check on the new test suite.

**Notes:** This is the "would my future self regret this remediation" check.

---

### Task 4.5: Update PROJ-316 plan.md + project index [Simple]
**File:** `Projects/active_projects/PROJ-316/plan.md`
**Tests:** N/A.

- [ ] Mark all 4 PROJ-316 phases Complete in the Quick Status table.
- [ ] Update Current State: "All 4 phases complete — ready for user verification."
- [ ] Update `Projects/projects_index.md` (or `Tracking/active_projects` index if present) to reflect PROJ-316 status.
- [ ] Bump `Last verified:` blockquote on plan.md.

**Notes:**

---

### Task 4.6: Hand-off summary [Simple]
**File:** `Projects/active_projects/PROJ-316/plan.md` Current State paragraph; user message.

- [ ] Write a one-paragraph hand-off summary of what was changed and what the user should verify.
- [ ] Audit findings closed: list all 5 by ID (P1.1, P1.2 docs, P1.3, P2.4, P2.5) with brief evidence.
- [ ] Hand off to user for verification.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0
- [ ] `python Tools/test_sharded/test_sharded.py` shows only PROJ-315 failures
- [ ] All 5 audit findings have evidence of closure
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State: project complete, awaiting user verification
- [ ] Update `Projects/projects_index.md`
