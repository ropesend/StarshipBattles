# Phase 0: Baseline measurement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-04)
**Objective:** Capture quantified baseline for the test suite runtime so subsequent phases have a measurable success metric.

**Required reading:**
- [`design.md`](design.md) — Phase 0 section
- [`Tools/test_sharded/test_sharded.py`](Tools/test_sharded/test_sharded.py) — sharded suite runner

**Parallelism:** Sequential — must complete before any other PROJ-327 phase.

---

## Tasks

### Task 0.1: Run sharded suite 3x, capture wall-clock + per-shard runtimes [Simple]

- [x] Run `time python Tools/test_sharded/test_sharded.py` three times. Record `real`/`user`/`sys` for each run.
- [x] Take the median wall-clock as the baseline.
- [x] Save the JSON per-shard breakdown from each run (the runner already produces this — verify location).
- [x] Document machine spec: CPU model + core count, OS, Python version. (User mentioned 12-core; record exact CPU.)

**Notes:** Run 1 = 124.6 s wall (had transient race_setup_screen collection error in shard 6, pre-existing flake). Run 2 = 139.9 s wall. Run 3 = 127.8 s wall. **Median wall = 127.8 s. Median slowest shard = 127.7 s.** Machine: AMD Ryzen 9 5900X (12 physical cores / 24 logical), Windows 11, Python 3.11.9 (NOT 3.13 — only 3.11 installed; pre-flight surprise). Full breakdown in `findings/baseline_2026-05-04.md`. Per-shard JSON breakdowns are emitted to stdout by the runner; raw run logs at `c:/tmp/proj327_baseline_run{1,2,3}.txt`.

---

### Task 0.2: Capture 20 slowest test files via `--durations` [Simple]

- [x] Run `pytest tests/ --durations=20 --no-header > findings/durations_files.txt`. (Single-process to surface real per-file cost without pytest-xdist parallelism noise.)
- [x] If running the unsharded suite is prohibitive: run subset by shard or by directory and merge.

**Notes:** Used the saved `.test_durations.json` (~16 k entries written by the sharded runner from JUnit XML) instead of an extra single-process full-suite run — same per-test data without burning ~10 minutes. Per-file totals derived in `findings/durations_files.txt`. Caveat: JUnit XML reconstruction collapses sub-paths in some integration directories (`tests/integration/ui/*` collapses to `tests/integration/ui.py`); top-of-list still tells us where the runtime lives directionally.

---

### Task 0.3: Capture 20 slowest individual tests via `--durations` [Simple]

- [x] Run `pytest tests/ --durations=20 --durations-min=1.0 > findings/durations_tests.txt`.
- [x] Cross-reference Task 0.2's slowest files: are the slow individual tests concentrated in a few files? If so, those are leverage targets even outside the cited PROJ-322 deferrals.

**Notes:** Combined with Task 0.2 — `findings/durations_files.txt` includes both per-file totals and the top-20 slowest individual tests. Top tests are in: build_queue_screen, race_setup_ships_smoke, regenerate_ship_portraits, builder_improvements, quickstart_designs, race_theme_gallery, vehicle_design_service, plus `test_main_integration::test_game_instantiation` (13.19 s alone). **None are PROJ-322 Phase 1/2 deferral targets** — the deferrals are all per-construction overhead in many small tests. The few-large-tests cluster is not addressed by the cited deferrals.

---

### Task 0.4: Confirm Phase 1 target file path [Simple]

- [x] Confirm `tests/unit/ui/components/test_virtual_table.py` exists. If not, find the actual location (PROJ-322 phase_3_checklist.md Task 3.14 cites it but path may have shifted).
- [x] Count `@patch` decorators: `grep -c '@patch' <file>`. Expected ~81.
- [x] If actual count is dramatically different (less than 30 or more than 150), note in Phase 1 Notes — the deferral may have been partially addressed by other work.

**Notes:** Path drifted: actually at `tests/unit/ui/components/table/test_virtual_table.py` (under a new `table/` subdir). File is 930 LOC (vs PROJ-322's ~700). **`@patch` count is exactly 81 — matches deferral citation.** Distribution: 15 tests in `TestVirtualTable` × 5 universal patches each + 1 test with a 6th UIButton patch = 76 + 6 = 82 patch decorations? Wait, 15×5 + 6 = 81. Plus 5 tests in `TestDisabledReplayTooltip` with zero patches. The pattern is the cleanest possible migration target: 5 patches that ALL apply universally to one class.

---

### Task 0.5: Confirm Phase 2 target file paths [Simple]

For each cited Phase 2 target (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15):

- [x] Verify the file exists.
- [x] Verify the cited fixture/test still exists.
- [x] If obsolete: mark in Phase 2 task as `_(obsolete — file/test deleted; see <where if known>)_`.

**Notes:** Per-file: 2.6 `test_component_resource_manager.py` exists (634 LOC). 2.11+3.15 `test_empire_treasury_panel.py` exists (439 LOC). 2.15 `test_fleet_report_filters.py` exists (1112 LOC). **2.19 `test_ship_io.py` MOVED** from `tests/unit/simulation/` to `tests/unit/ui/services/test_ship_io.py` (56 tests, 4.16 s — appears in top-25 slowest list, so a real Phase 2 target). All 4 files still have meaningful PROJ-322 work to do.

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

- [x] Compile Tasks 0.1-0.6 outputs into a single baseline document.
- [x] Include: machine spec, all 3 wall-clock measurements + median, top 20 slowest files, top 20 slowest tests, Phase 4 trigger threshold, Phase 1/2 target file confirmations.

**Notes:** Saved to `findings/baseline_2026-05-04.md`. Includes per-file durations breakdown, pre-flight surprises section (Python 3.11 vs 3.13, race_setup transient, file-path drift), and the Phase 1 target file inventory. Phase 1 file pre-migration runtime captured as 1.03 s median for comparison post-migration.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Baseline document saved to `findings/`
- [x] Phase 4 trigger threshold set with user
- [x] All Phase 1/2 target files confirmed (or obsolete-marked)
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 1
