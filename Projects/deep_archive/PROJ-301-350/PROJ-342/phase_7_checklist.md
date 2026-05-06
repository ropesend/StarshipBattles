# Phase 7: Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm the full sharded test suite passes, the original crash does not recur, and the project is ready for user sign-off.

---

## Tasks

### Task 7.1: Targeted verification [Simple]
**Tests:** `pytest tests/unit/test_lab tests/unit/combat_lab/services tests/unit/ui -x`

- [ ] Run targeted suites for affected areas
- [ ] All tests pass
- [ ] If anything fails, return to the relevant phase rather than papering over

**Notes:** [Filled during implementation]

### Task 7.2: Full sharded suite [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the canonical full-suite command per AGENTS.md
- [ ] Baseline pre-PROJ-342 was **17,202 tests / 17,198 passed / 0 failed / 4 skipped / 53.1s wall** (recorded 2026-05-04). Post-PROJ-342 should show:
  - Net change: +N tests for new regression coverage minus M tests removed for deleted services. Expected magnitude: small (single-digit to low-double-digit change).
  - 0 failures
  - Skipped count unchanged or reduced
- [ ] If failures appear that aren't covered by Phases 5-6, **STOP** and diagnose. They likely reveal a missed caller or a hidden coupling not surfaced in the design phase.

**Notes:** [Filled during implementation]

### Task 7.3: Manual smoke — original crash does not recur [Simple]
**Tests:** Manual UI verification

- [ ] `python launcher.py`
- [ ] Click "Combat Lab" from main menu
- [ ] Click "Run All" (the exact path that triggered the original crash)
- [ ] Confirm: no `AttributeError: 'ScreenRouter' object has no attribute 'screen'`. Progress overlay renders correctly. Tests run to completion.
- [ ] As a side check: verify the progress overlay text is centered correctly (the dimensions came from constants before via `WIDTH/HEIGHT`; after the change they come from `self.screen_width/height` which match the live display — so centering should be identical)
- [ ] Resize the window mid-batch (if possible) to spot-check that `BattleStateViewer.handle_resize` forwarding works

**Notes:** [Filled during implementation. If UI cannot be tested in your environment, document explicitly per CLAUDE.md "if you can't test the UI, say so explicitly rather than claiming success".]

### Task 7.4: Doc consistency check [Simple]
**Tests:** Manual review

- [ ] Read `combat_lab/COMBAT_LAB_DOCUMENTATION.md` end-to-end. Does it accurately describe the post-refactor architecture?
- [ ] Spot-check `docs/03_CONVENTIONS.md §2.4` — does the screen-constructor convention still match the codebase? (No edit expected; this is just a sanity check.)
- [ ] Verify the legacy `# NB: TestLabScreen still asks for self...` comment is gone from `screen_router.py` (Phase 3 should have removed it)

**Notes:** [Filled during implementation]

### Task 7.5: Update Current State and request user sign-off [Simple]

- [ ] Update `plan.md` Current State:
  - **Last Updated:** [implementation completion date]
  - **Active Phase:** Complete
  - **Last Action:** Phase 7 verification passed
  - **Next Action:** Awaiting user verification + project archival
  - **Blockers:** None
- [ ] Update `plan.md` Quick Status table — all phases marked `Complete`
- [ ] Update `Projects/projects_index.md` — mark PROJ-342 as awaiting-confirmation per ticket-system convention
- [ ] Inform user: implementation complete; manual smoke confirmed; ready for verification

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

- [ ] Targeted tests pass
- [ ] Full sharded suite passes (no regression vs baseline)
- [ ] Manual smoke test passes (original crash gone, progress overlay works, resize forwards correctly)
- [ ] Documentation is consistent with code
- [ ] `plan.md` Current State, Quick Status, and `projects_index.md` are updated
- [ ] Update status at top of this file to `Complete`
- [ ] Inform user implementation is complete and request verification
