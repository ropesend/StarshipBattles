# Phase 1: Measure (profile + characterization tests)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Produce a defensible, reproducible measurement of where turn-processing time goes on the tiny reference scenario, *and* the characterization tests that will protect mid-turn invariants during later phases. No production-code optimizations land in this phase except for the explicitly-trivial late-import moves authorized for Phase 2.

---

## Tasks

### Task 1.1: Establish test baseline [Simple]

**File:** n/a (verification step)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run `git status --short` to confirm no surprise uncommitted state beyond the PROJ-412/411 init
- [ ] Run `python Tools/test_sharded/test_sharded.py` and confirm a green baseline; expected ~minutes
- [ ] Note any pre-existing flakes (per CLAUDE.md memory: LLM background timing test is a known intermittent on Windows)
- [ ] Record total wall-clock and any unexpected failures in `findings/test_baseline.md`

**Notes:**

### Task 1.2: Add `tests/performance/bench_turn_processing.py` [Medium]

**File:** `tests/performance/bench_turn_processing.py` (new)
**Tests:** `pytest tests/performance/bench_turn_processing.py -v`

- [ ] Mirror the structure of [`tests/performance/bench_galaxy_planet_star.py`](../../../tests/performance/bench_galaxy_planet_star.py): fixed seed, min-of-N-runs, JSON baseline sibling
- [ ] Scenario: 2 empires, 2 planets, a handful of ships, no active combat — driven from the existing quickstart-style fixture if one exists, otherwise build a minimal `GameSession` directly
- [ ] Drive 10 turns via `session.process_turn()` (or the canonical entry path)
- [ ] After each turn, capture `turn_engine._phase_times` dict and the total time
- [ ] Emit per-phase mean/min/max and total mean/min/max
- [ ] Write `tests/performance/bench_turn_processing.baseline.json` with first-run numbers
- [ ] Verify: total CI runtime < 30 s
- [ ] Verify: re-running on the same machine reproduces numbers within ~10%

**Notes:**

### Task 1.3: Capture Scalene CPU profile of the benchmark [Medium]

**File:** invoke `Tools/profiling/run_scalene.py`; outputs land under `output/profiles/scalene/` (gitignored)
**Tests:** n/a (profiling pass)

- [ ] Dry-run: `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance/bench_turn_processing.py --dry-run`
- [ ] Real run with `--timestamp 20260510T0000` for comparability later
- [ ] Render: `python -m scalene view output/profiles/scalene/<file>.json --cli`
- [ ] Copy the rendered summary into `findings/profile_baseline_cpu.md` with the top 30 functions by exclusive CPU time
- [ ] Cross-reference Scalene's hotspots against `_phase_times` buckets and the swarm-02 hypothesis ranking; flag mismatches
- [ ] If Python time is dominant, that's the expected case; if native or copy-volume dominates, escalate to a full-mode run

**Notes:**

### Task 1.4: Isolate the unaccounted overhead [Medium]

**File:** scratch file under `AgentCoordination/Scratchpad/reports/proj-412-overhead-probe.md`
**Tests:** rerun `bench_turn_processing.py` after each probe variation

- [ ] Probe A: Patch `TurnStateSnapshot.capture` to return a dummy (or pass `session=None`) and re-measure. Record `total` delta.
- [ ] Probe B: Replace the UI progress callback with `lambda *a: None` and re-measure. Record `total` delta.
- [ ] Probe C: Replace each per-tick phase callable with `lambda *a, **k: None` one at a time (production, harvesting, environmental, planet_energy, movement_calc) and record `total` delta — confirms the per-phase wall-clock cost beyond what `_phase_times` shows.
- [ ] Write the attribution table to `findings/profile_baseline_cpu.md` mapping ~each ~100 ms of the 2.5–3.7 s gap to a specific call site
- [ ] If anything remains unattributed after all probes, run `cProfile` on the benchmark and append the top stack frames

**Notes:**

### Task 1.5: Add three mid-turn characterization tests [Medium]

**Files:** `tests/integration/strategy/turn_engine/test_mid_turn_invariants.py` (new) or split per concern under existing turn-engine test folders
**Tests:** `pytest tests/integration/strategy/turn_engine/test_mid_turn_invariants.py -v`

- [ ] **Test A — mid-turn facility completion**: at tick 50 a storage facility completes; tick 51's harvest respects the new capacity. Drive via a deterministic queue that completes mid-loop. Assert: `max_stockpile[res]` reflects the new facility's contribution from tick 51 onward; pre-tick-50 harvest still capped at old capacity.
- [ ] **Test B — mid-turn harvester destruction**: at tick 50 a harvester facility's `is_operational` flips to False (simulate destruction). Tick 51+ contributes zero from that harvester. Assert: per-tick harvest sum drops by exactly the destroyed harvester's contribution.
- [ ] **Test C — mid-turn booster arrival**: a fleet carrying `ResourceHarvestBooster` enters the relevant scope at tick 25 via `move_apply`. Harvest from tick 26 onward is scaled by the booster. Assert: tick-25 harvest unchanged; tick-26+ harvest scaled.
- [ ] All three tests must pass against the *current* unchanged code (they characterize present behavior, not target behavior)
- [ ] Verify: tests fail loudly and informatively if invalidation is broken (e.g. by mocking a cache that ignores mid-turn changes)

**Notes:**

### Task 1.6: Rewrite `test_recalculate_storage_called_each_tick` as a behavior assertion [Simple]

**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -k storage`

- [ ] Locate the existing test (~line 926 per swarm-05)
- [ ] Convert from "asserts call count == 100" to "asserts the *invariant*: storage capacity reflects mid-turn facility completion". Reuse the Test-A characterization pattern from 1.5.
- [ ] Leave a comment referencing PROJ-412 explaining why the implementation-detail assertion was retired
- [ ] Run the test, confirm it still passes against unchanged code

**Notes:**

### Task 1.7: Decide Phase 2+ ordering [Simple]

**File:** `Projects/active_projects/PROJ-412/decisions.md`
**Tests:** n/a

- [ ] Cross-reference the measured Phase-1 attribution table against the pre-profile hypothesis (swarm_02 + swarm_03)
- [ ] If the measurement confirms harvesting + snapshot + callback as the top three: proceed to Phases 2-4 as planned
- [ ] If something else dominates (e.g. environmental scan, or movement pathfinding): add a new decisions-log entry justifying the reordering and update `plan.md`'s Quick Status table
- [ ] User checkpoint: surface the measured attribution and proposed Phase 2 starting point; wait for confirmation before beginning Phase 2

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `findings/profile_baseline_cpu.md` exists with the top-30 hotspot list and the unaccounted-overhead attribution table
- [ ] `tests/performance/bench_turn_processing.py` is green with a stable baseline JSON
- [ ] Three new mid-turn characterization tests are green against unchanged production code
- [ ] Full sharded suite is green (`python Tools/test_sharded/test_sharded.py`)
- [ ] User has reviewed the Phase 1 deliverables and confirmed the Phase 2 starting point
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
