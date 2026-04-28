# Phase 2: Hygiene (R5 + R6)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-317 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make `validate_audit_ready.py PROJ-315` and
`validate_audit_ready.py PROJ-317` exit 0. Trim trailing whitespace
flagged by `git diff --check`.

---

## Tasks

### Task 2.1: R5 — clear PROJ-315 audit blockers [Simple]
**File:** `Projects/active_projects/PROJ-315/plan.md`
**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-315`

- [ ] Edit `Projects/active_projects/PROJ-315/plan.md` line 25
  (`**Blockers:**` field). Trim everything after `None.` so the line
  reads:
  ```markdown
  **Blockers:** None.
  ```
  The original narrative ("Two spec ambiguities resolved with the
  user during Phase C…") already lives in PROJ-315 `decisions.md`
  rows 12 and 13 — no information is lost.
- [ ] Edit lines 241, 248, 254 — the `**Status:** Not Started — see
  [phase_X_checklist.md].` lines in the `## Phases` section. Replace
  each with:
  ```markdown
  **Status:** Complete
  ```
- [ ] Run `python Projects/scripts/validate_audit_ready.py PROJ-315`.
  Confirm `RESULT: PASSED`. The "Awaiting User Verification" warning
  on the index status is informational and does not fail the gate.
- [ ] Run `python Projects/scripts/validate_audit_ready.py PROJ-317`
  to confirm PROJ-317 itself doesn't trip the gate (Phase 1 just
  flipped to Complete; should pass).
- [ ] Verify: both audit gates exit 0.

**Notes:**

---

### Task 2.2: R6 — trim EOF whitespace [Simple]
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** `git diff --check`

- [ ] Open `tests/unit/ui/panels/test_ship_detail_panel.py`. Confirm
  the file currently ends with two CRLF blank lines (`cat -A` shows
  trailing `^M$\n^M$\n`).
- [ ] Trim the file so it ends with exactly one final newline after
  the last assertion in the last test class.
- [ ] Run `git diff --check e26f00f74..HEAD`. Expect no whitespace
  errors against the file. (The pre-PROJ-317 baseline can be
  whatever HEAD was before this phase began — the assertion is "no
  whitespace errors against this file in the post-PROJ-317 state".)
- [ ] Verify: `git diff --check` clean for the whole project diff.

**Notes:**

---

### Task 2.3: Validate against full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite. The whitespace trim is purely
  cosmetic and should not affect test discovery or execution.
- [ ] Expected: same count as end of Phase 1 (~16000–16002 passed,
  0 failed).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 3.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-317 2`.
