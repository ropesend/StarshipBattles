# Phase 7: Audit remediation — Status honesty (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address Codex audit finding F1 (project status not justified by recorded work — ~41 tasks marked NEEDS_REWORK while phases marked Complete). This is a status-hygiene phase only; the deferred work itself is being surfaced to the user for batch-end decision, not redone here.

See `findings/audit_verification.md` for the full verdict table.

---

## Tasks

### Task 7.1: Fix Phase 6 internal status inconsistency [Simple]
**File:** `Projects/active_projects/PROJ-479/phase_6_checklist.md`

- [x] Phase 6 header at line 8 says `Status: Complete` while Task 6.2 is PARTIAL, Task 6.4 is PARTIAL, Task 6.5 is NEEDS_REWORK. Change header to `Status: Partial`.
- [x] Add a `**Partial completion summary:**` section right under the status line listing the 3 tasks not fully done with their disposition.

---

### Task 7.2: Relabel partial phases in plan.md Quick Status [Simple]
**File:** `Projects/active_projects/PROJ-479/plan.md`

- [x] Phase 2 row: change Status column from "Complete (partial)" to "Partial (6/18)"
- [x] Phase 3 row: change Status column from "Complete (partial)" to "Partial (7/34)"
- [x] Phase 6 row: change Status column from "Complete" to "Partial (4/6)"
- [x] Active Phase line in Current State: change "All 6 phases complete (Phase 2/3/6 partial — many tasks marked NEEDS_REWORK per skeptical-check)" to "Phases 1/4/5 Complete; Phases 2/3/6 Partial (~41 NEEDS_REWORK tasks deferred for user decision)"

---

### Task 7.3: Update Current State with deferred-work handoff list [Simple]
**File:** `Projects/active_projects/PROJ-479/plan.md`

- [x] Replace the `**Blockers:** None` line with a `**Deferred work (requires user decision):**` block enumerating:
  - Phase 2: 12 CAT-5 tasks marked NEEDS_REWORK — mutation-isolation rationale (Codex sampled 3 deferrals and found them credible: `test_theme_discovery.py`, `test_ai.py`, `test_combat.py` all mutate live state)
  - Phase 3: 27 CAT-6 tasks marked NEEDS_REWORK — heavy DI-introduction rationale **EXCEPT** Task 3.32 (ActionExecutionEngine) which was wrongly deferred (DI seam already exists in production — see DI-2026-05-23-003)
  - Phase 4 Task 4.2: 5 sleeps reclassified as polling micro-yields / absence-assertions
  - Phase 6 Task 6.2: HLP-002 nested copies (12+ method-local copies of MockPlanetType)
  - Phase 6 Task 6.4: HLP-004 full 43-file _make_fleet sweep
  - Phase 6 Task 6.5: HLP-005 setup_tmpdir — needs strategy decision

- [x] Add `**Audit findings:**` line: `findings/audit_verification.md` — Codex mid-project audit; F1 (status hygiene) addressed in Phase 7; F2 (Task 3.32 wrongly deferred) logged as DI-2026-05-23-003; F3 (make_mock_empire byte-identity claim) informational, no action.

---

### Task 7.4: Verify [Simple]

- [x] `python Projects/scripts/validate_phase.py PROJ-479 7` returns PASSED.
- [x] Phase 6 checklist Status no longer says Complete.
- [x] plan.md Quick Status no longer overstates phase completion.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row for Phase 7 to `Complete`
- [x] Update plan.md Current State to point to next phase (or close)
