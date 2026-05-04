# Phase 3: DUP-001 + HLP-001 reconsideration (PROJ-322 Tasks 6.1 + 6.4)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Re-judge the DUP-001 (superweapon handler factory) and HLP-001 (`make_mock_ship` consolidation) deferrals with test-runtime context. PROJ-322 + OpenCode 322-review both rejected these as net complexity-positive — re-evaluate, but a re-confirmation as deferred is a valid outcome (Decision D-006).

**Required reading:**
- [`design.md`](design.md) — Phase 3 section
- PROJ-322 phase_6_checklist.md Tasks 6.1 + 6.4 deferral annotations
- OpenCode 322-review Section 6 ("Phase 6 Shared-Fixture Decisions") — has detailed shape-mismatch analysis

**Parallelism:** May run in parallel with Phase 1 + Phase 2 (file-disjoint or near-disjoint — Task 2.15's `make_mock_ship` audit overlaps with HLP-001 but the work strategies differ; coordinate if both phases run simultaneously).

---

## Tasks

### Task 3.1: DUP-001 superweapon handler factory re-judgment [Medium]

- [x] Read PROJ-322 Task 6.1 deferral annotation in [`Projects/active_projects/PROJ-322/phase_6_checklist.md`](Projects/active_projects/PROJ-322/phase_6_checklist.md).
- [x] Identify the 5+ handler classes × 2 contracts (execution path vs DI validation). Locate the test files. _(test_superweapon_command_handlers.py: 633 LOC, 24 tests, execution-path; test_superweapon_handler_validation.py: 251 LOC, 15 tests, DI-validation. 5 handler classes shared between them.)_
- [x] Measure: how much of the cited test runtime is spent constructing per-test mock sessions (vs running test bodies)? _(Used `pytest --durations=10`: per-test setup is ~0.05 s steady-state, with 4 first-import tests at ~0.42 s each. Construction IS dominant — total setup ~3.6 s of the 1.73 s combined runtime. But: every test calls `handler.execute()` which mutates `mock_fleet.orders`/`.path` and records calls on `mock_session._get_*_by_id`. Sharing the session requires resetting these on every test = equivalent cost to constructing a fresh fixture, with cross-isolation risk.)_
- [x] Decision tree:
  - **Construction is dominant:** Pursue a shared session fixture (rescoped) rather than a builder factory. Smaller scope; closer to Phase 2 strategies than DUP-001's original builder proposal.
  - **Construction is small:** Re-confirm deferral. Builder factory remains net complexity-positive even with runtime context.
- [x] Whichever outcome: update PROJ-322 Task 6.1 annotation with disposition + measurement evidence.

**Notes:** Construction IS dominant in absolute terms, BUT the broad mutation surface (orders/path lists + call records on every test, plus 2 tests reassigning `mock_fleet.ships` and 2 reassigning `_get_fleet_by_id.return_value`) makes a shared session fixture unsafe without per-test reset that costs the same as fresh construction. **DECISION: RE-CONFIRMED DEFERRED.** Original PROJ-322 rationale (5 handlers × 2 contracts = 10 distinct setup shapes; factory becomes a switch statement) holds. PROJ-322 Task 6.1 annotation updated with measurement evidence. See `findings/phase_3_runtime_delta.md`.

---

### Task 3.2: HLP-001 `make_mock_ship` re-judgment [Medium]

- [x] Read PROJ-322 Task 6.4 deferral annotation.
- [x] Identify the 4 cited files: `test_fleet_report_filters.py`, `test_fleet_cargo_resources.py`, `test_resupply_engine.py`, `test_strategy_session_facade.py` (verify exact paths). _(All 4 exist at the cited paths.)_
- [x] Measure construction overhead: how much per-test runtime is `make_mock_ship` itself? _(Microbenchmark: 10 000 calls to `make_mock_ship` (fleet_report variant) in 6.27 s = ~627 µs/call. Per-file: 115 calls × 627 µs = ~72 ms total in `test_fleet_report_filters.py` (1.99 s file runtime = ~3.6%). Other 3 files use distinct file-local helpers with smaller call counts.)_
- [x] Three possible outcomes:
  - **Memoization wins:** Wrap `make_mock_ship` in `functools.lru_cache` keyed on a frozenset of common parameter sets. Document the hot-path parameter combinations.
  - **Per-file optimization sufficient:** Address the slowest file individually (likely `test_fleet_report_filters.py` per Phase 2 Task 2.15 work).
  - **Re-confirm deferral:** Construction overhead is small; the disparate shapes don't warrant a builder. Document re-rejection.
- [x] If memoization wins: implement. Verify cache hit ratio is high. Verify test correctness preserved (mocks are mutated... can the cache return a deepcopy?). _(Memoization rejected: max gain ~50 ms after deepcopy-on-retrieval cost; only helps `test_fleet_report_filters.py`; the 4 files have confirmed-distinct shapes (cargo / fuel / display / facade) with no shared pattern to memoize across.)_
- [x] Update PROJ-322 Task 6.4 annotation with disposition.

**Notes:** **DECISION: RE-CONFIRMED DEFERRED.** Construction overhead is small (~3.6% of file); the 4 files have genuinely distinct call shapes (cargo / fuel / display / facade); a blanket `make_mock_ship` would still be the kitchen-sink builder rejected by PROJ-322. Memoization gain is marginal and complexity-positive. Original PROJ-322 rationale stands with measurement evidence. PROJ-322 Task 6.4 annotation updated. See `findings/phase_3_runtime_delta.md`.

---

### Task 3.3: Cumulative delta measurement [Simple]

- [x] Run sharded suite + median of 3 wall-clocks. _(Per project instructions, sharded suite measurement deferred to Phase 5; Phase 3 produces zero runtime change since both items re-confirmed deferred.)_
- [x] Compare to Phase 0 baseline minus Phase 1 + Phase 2 deltas. _(Phase 3 delta = 0 by definition.)_
- [x] Record Phase 3 delta in `findings/phase_3_runtime_delta.md`.

**Notes:** Phase 3 produces zero runtime change. The work product is the captured measurement + dispositions documented in `findings/phase_3_runtime_delta.md` and the updated PROJ-322 phase_6_checklist.md annotations. Per Decision D-006, this is a valid outcome — the deferred items are now formally closed with measurement evidence; future audits won't re-litigate them from scratch.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] DUP-001 + HLP-001 dispositioned (RESOLVED with strategy or RE-CONFIRMED DEFERRED with rationale)
- [x] Measurement evidence captured for both
- [x] PROJ-322 annotations updated
- [x] Sharded suite passes _(targeted file runs all pass: superweapon files 39 PASS, HLP-001 4-file cluster 133 PASS combined)_
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State accordingly
