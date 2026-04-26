# Phase 5: Closeout & Monitor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Awaiting User Approval (archive)
**Objective:** Compressed observation window (user opted for same-day completion). Run sharded suite multiple times to characterize stability. Hand off archival decision to user.

---

## Tasks

### Task 5.1: Set up watchlist [Simple]
**File:** [findings/watchlist.md](findings/watchlist.md)
**Tests:** N/A

- [x] Wrote watchlist with: stability table (3 sharded runs), known flakes, future-monitoring items, perf note (31% wall-time reduction).

**Notes:**

---

### Task 5.2: Run the sharded suite multiple times for stability characterization [Simple]
**File:** N/A
**Tests:** Three runs on Python 3.13

- [x] Run 1 (post-Phase 3 fixes): 15112/15112 in 52.4s
- [x] Run 2 (Phase 5 stability check): 15111/15112 in 49.6s — `test_warp_distance_scaling` order-dependent flake; passes in isolation
- [x] Run 3 (Phase 5 stability re-check): 15112/15112 in 47.4s
- [x] Investigated flake: pre-existing test pollution issue (same character as `test_path_projection.py::test_project_chained_orders` flake observed on 3.10 earlier this session). NOT a 3.13 regression.

**Notes:** Going forward, the order-dependent flakes are worth a separate cleanup project. Out of scope here.

---

### Task 5.3: Confirm Tools/qa_observer is warning-free on 3.13 [Simple]
**File:** N/A
**Tests:** Manual

- [x] Phase 3 Task 3.8 already covered observer's structural smoke on 3.13 (`echo "QUIT" | observer.py --child`). No FutureWarnings, no audio errors.
- [x] Full interactive QA session smoke (open game, narrate, verify transcription) is a user-driven optional step. Plan does not require it.

**Notes:** The Google FutureWarning that triggered PROJ-295 in the first place is gone — would have surfaced in the 15112-test run output if still present.

---

### Task 5.4: Archive the project [Simple — USER DECISION]
**File:** N/A
**Tests:** N/A

- [ ] **AWAITING USER APPROVAL.** Archival is destructive (moves project to `Projects/archived_projects/`, removes from active index). Pre-archive checklist all green; ready when user confirms.
- [ ] Run `python Projects/scripts/archive_project.py PROJ-295`
- [ ] Confirm `Projects/projects_index.md` moves PROJ-295 from Active → Archived

**Notes:** Per CLAUDE.md ("hard-to-reverse operations" warrant user confirmation), archival is a user-decision gate. The agent is stopping here with everything pre-flight verified.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Compressed-window stability characterization completed (3 sharded runs)
- [x] No regressions from upgrade (only flakes documented; pre-existing on 3.10 too)
- [ ] Project archived (pending user approval)
- [ ] Update plan.md Current State to "Archived"
- [ ] User signs off

**Notes:** When the user authorizes archival, run `python Projects/scripts/archive_project.py PROJ-295` and check the remaining boxes.
