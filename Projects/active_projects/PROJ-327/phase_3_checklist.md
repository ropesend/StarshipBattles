# Phase 3: DUP-001 + HLP-001 reconsideration (PROJ-322 Tasks 6.1 + 6.4)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED on Phase 0)
**Objective:** Re-judge the DUP-001 (superweapon handler factory) and HLP-001 (`make_mock_ship` consolidation) deferrals with test-runtime context. PROJ-322 + OpenCode 322-review both rejected these as net complexity-positive — re-evaluate, but a re-confirmation as deferred is a valid outcome (Decision D-006).

**Required reading:**
- [`design.md`](design.md) — Phase 3 section
- PROJ-322 phase_6_checklist.md Tasks 6.1 + 6.4 deferral annotations
- OpenCode 322-review Section 6 ("Phase 6 Shared-Fixture Decisions") — has detailed shape-mismatch analysis

**Parallelism:** May run in parallel with Phase 1 + Phase 2 (file-disjoint or near-disjoint — Task 2.15's `make_mock_ship` audit overlaps with HLP-001 but the work strategies differ; coordinate if both phases run simultaneously).

---

## Tasks

### Task 3.1: DUP-001 superweapon handler factory re-judgment [Medium]

- [ ] Read PROJ-322 Task 6.1 deferral annotation in [`Projects/active_projects/PROJ-322/phase_6_checklist.md`](Projects/active_projects/PROJ-322/phase_6_checklist.md).
- [ ] Identify the 5+ handler classes × 2 contracts (execution path vs DI validation). Locate the test files.
- [ ] Measure: how much of the cited test runtime is spent constructing per-test mock sessions (vs running test bodies)?
  - Add `pytest.profile` or instrument with `--profile-svg` (if pytest-profiling available).
  - If not available: use `cProfile` against the test file directly.
- [ ] Decision tree:
  - **Construction is dominant:** Pursue a shared session fixture (rescoped) rather than a builder factory. Smaller scope; closer to Phase 2 strategies than DUP-001's original builder proposal.
  - **Construction is small:** Re-confirm deferral. Builder factory remains net complexity-positive even with runtime context.
- [ ] Whichever outcome: update PROJ-322 Task 6.1 annotation with disposition + measurement evidence.

**Notes:** [Filled during implementation. Record measurement + decision.]

---

### Task 3.2: HLP-001 `make_mock_ship` re-judgment [Medium]

- [ ] Read PROJ-322 Task 6.4 deferral annotation.
- [ ] Identify the 4 cited files: `test_fleet_report_filters.py`, `test_fleet_cargo_resources.py`, `test_resupply_engine.py`, `test_strategy_session_facade.py` (verify exact paths).
- [ ] Measure construction overhead: how much per-test runtime is `make_mock_ship` itself?
  - Quick profile per file: `python -c "import cProfile, pytest; cProfile.run('pytest.main([file])', sort='cumulative')"`.
- [ ] Three possible outcomes:
  - **Memoization wins:** Wrap `make_mock_ship` in `functools.lru_cache` keyed on a frozenset of common parameter sets. Document the hot-path parameter combinations.
  - **Per-file optimization sufficient:** Address the slowest file individually (likely `test_fleet_report_filters.py` per Phase 2 Task 2.15 work).
  - **Re-confirm deferral:** Construction overhead is small; the disparate shapes don't warrant a builder. Document re-rejection.
- [ ] If memoization wins: implement. Verify cache hit ratio is high. Verify test correctness preserved (mocks are mutated... can the cache return a deepcopy?).
- [ ] Update PROJ-322 Task 6.4 annotation with disposition.

**Notes:** [Filled during implementation. Record measurement + decision.]

---

### Task 3.3: Cumulative delta measurement [Simple]

- [ ] Run sharded suite + median of 3 wall-clocks.
- [ ] Compare to Phase 0 baseline minus Phase 1 + Phase 2 deltas.
- [ ] Record Phase 3 delta in `findings/phase_3_runtime_delta.md`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] DUP-001 + HLP-001 dispositioned (RESOLVED with strategy or RE-CONFIRMED DEFERRED with rationale)
- [ ] Measurement evidence captured for both
- [ ] PROJ-322 annotations updated
- [ ] Sharded suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State accordingly
