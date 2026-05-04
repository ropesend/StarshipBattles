# Phase 0: Baseline measurement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED until PROJ-326 reports Complete)
**Objective:** Capture quantified baseline for the test suite runtime so subsequent phases have a measurable success metric.

**Required reading:**
- [`design.md`](design.md) — Phase 0 section
- [`Tools/test_sharded/test_sharded.py`](Tools/test_sharded/test_sharded.py) — sharded suite runner

**Parallelism:** Sequential — must complete before any other PROJ-327 phase.

---

## Tasks

### Task 0.1: Run sharded suite 3x, capture wall-clock + per-shard runtimes [Simple]

- [ ] Run `time python Tools/test_sharded/test_sharded.py` three times. Record `real`/`user`/`sys` for each run.
- [ ] Take the median wall-clock as the baseline.
- [ ] Save the JSON per-shard breakdown from each run (the runner already produces this — verify location).
- [ ] Document machine spec: CPU model + core count, OS, Python version. (User mentioned 12-core; record exact CPU.)

**Notes:** [Filled during implementation. Record all 3 wall-clock times + median.]

---

### Task 0.2: Capture 20 slowest test files via `--durations` [Simple]

- [ ] Run `pytest tests/ --durations=20 --no-header > findings/durations_files.txt`. (Single-process to surface real per-file cost without pytest-xdist parallelism noise.)
- [ ] If running the unsharded suite is prohibitive: run subset by shard or by directory and merge.

**Notes:** [Filled during implementation]

---

### Task 0.3: Capture 20 slowest individual tests via `--durations` [Simple]

- [ ] Run `pytest tests/ --durations=20 --durations-min=1.0 > findings/durations_tests.txt`.
- [ ] Cross-reference Task 0.2's slowest files: are the slow individual tests concentrated in a few files? If so, those are leverage targets even outside the cited PROJ-322 deferrals.

**Notes:** [Filled during implementation]

---

### Task 0.4: Confirm Phase 1 target file path [Simple]

- [ ] Confirm `tests/unit/ui/components/test_virtual_table.py` exists. If not, find the actual location (PROJ-322 phase_3_checklist.md Task 3.14 cites it but path may have shifted).
- [ ] Count `@patch` decorators: `grep -c '@patch' <file>`. Expected ~81.
- [ ] If actual count is dramatically different (less than 30 or more than 150), note in Phase 1 Notes — the deferral may have been partially addressed by other work.

**Notes:** [Filled during implementation. Record actual @patch count + file path.]

---

### Task 0.5: Confirm Phase 2 target file paths [Simple]

For each cited Phase 2 target (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15):

- [ ] Verify the file exists.
- [ ] Verify the cited fixture/test still exists.
- [ ] If obsolete: mark in Phase 2 task as `_(obsolete — file/test deleted; see <where if known>)_`.

**Notes:** [Filled during implementation. Record per-file disposition.]

---

### Task 0.6: Set Phase 4 trigger threshold with user [Simple]

- [x] Surface the baseline measurement to the user.
- [x] Ask the user to set a target runtime (recommend ≤90 seconds = 50% reduction; user may set differently).
- [x] Document the target in this task's Notes.
- [x] If the user opts to skip Phase 4 regardless of Phases 1-3 outcome, note that here too.

**Notes (2026-05-04, set during PROJ-324/325/326 planning hand-off):**
- **User-reported baseline (just-run, slowest shard): 137s** on a 12-core machine.
- **Target: as low as possible. Stretch goal: slowest shard < 90s** (~34% reduction). User said "if we can get the slowest thread under 90s I'll be amazed."
- **Phase 4 trigger:** if Phases 1-3 cumulative delta does not bring the slowest shard under 90s, execute Phase 4. Phase 4 is NOT optional — execute if needed to hit the target.
- **Phase 0 in PROJ-327 itself** still runs (re-measure baseline at the time PROJ-327 starts, after PROJ-324/325/326 have all landed — those projects may already shave a few seconds via the LLMBackgroundCall Event refactor and other small wins).

---

### Task 0.7: Save baseline document [Simple]

**File:** `Projects/active_projects/PROJ-327/findings/baseline_<YYYY-MM-DD>.md` (NEW)

- [ ] Compile Tasks 0.1-0.6 outputs into a single baseline document.
- [ ] Include: machine spec, all 3 wall-clock measurements + median, top 20 slowest files, top 20 slowest tests, Phase 4 trigger threshold, Phase 1/2 target file confirmations.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Baseline document saved to `findings/`
- [ ] Phase 4 trigger threshold set with user
- [ ] All Phase 1/2 target files confirmed (or obsolete-marked)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 1
