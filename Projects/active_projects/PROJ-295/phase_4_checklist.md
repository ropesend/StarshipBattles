# Phase 4: Closeout & Monitor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** A 2-week observation window after Phase 3 closes. Catch any subtle issues from the upgrade (e.g. semantic differences in stdlib `asyncio`, `dataclass`, or `typing` between 3.10 and the target). Cheap insurance.

---

## Tasks

### Task 4.1: Set up a watchlist [Simple]
**File:** [findings/watchlist.md](findings/watchlist.md) (create new)
**Tests:** N/A

- [ ] Create the watchlist file with these monitoring items:
  - Any new warnings appearing in `python qa_launcher.py` output
  - Any new test flakes (compare against the green baseline log from Phase 2 Task 2.5)
  - Any unexpected behavior in long-running games (multi-hour campaigns)
  - Any deprecation warnings from dependencies
- [ ] Note the start date of the observation window

**Notes:**

---

### Task 4.2: Run the sharded suite at least twice during the window [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the suite at start of window
- [ ] Run again at midpoint
- [ ] Run at end of window
- [ ] If any new flake appears that wasn't on 3.10, investigate; document in [findings/watchlist.md](findings/watchlist.md)

**Notes:**

---

### Task 4.3: Confirm Tools/qa_observer/processor.py is warning-free [Simple]
**File:** N/A
**Tests:** Manual via qa_launcher

- [ ] One brief QA session via `python qa_launcher.py`
- [ ] Confirm the only warnings (if any) are unrelated to Google EOL or Python version

**Notes:**

---

### Task 4.4: Close out — archive the project [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Run `python Projects/scripts/archive_project.py PROJ-295`
- [ ] Confirm `Projects/projects_index.md` moves PROJ-295 from Active → Archived

**Notes:** If the watchlist surfaced unresolved issues, do NOT archive; spawn follow-up tickets and keep PROJ-295 open until clean.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] 2-week observation window completed
- [ ] No regressions in the watchlist
- [ ] Project archived
- [ ] Update plan.md Current State to "Archived"
- [ ] User signs off
