# Phase 2: Mutable-mock fixture rescope (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED on Phase 0)
**Objective:** Rescope 5 deferred fixtures from function-scope to class/module/session scope where safe. Audit each before changing — fixtures with mutation may need copy-on-write or `reset_mock()` autouse companion.

**Required reading:**
- [`design.md`](design.md) — Phase 2 section + `reset_mock()` autouse companion pattern
- PROJ-322 phase_2_checklist.md Tasks 2.6, 2.11, 2.15, 2.19; phase_3_checklist.md Task 3.15
- Each target file in full before editing

**Parallelism:** May run in parallel with Phase 1 + Phase 3 (file-disjoint). Sequential after Phase 0.

---

## Tasks

### Task 2.1: Per-fixture mutation audit [Medium]

For each of the 5 deferred fixtures, perform:

- [ ] **Task 2.6** — `tests/unit/simulation/components/test_component_resource_manager.py`: which fixture? Search the file for the cited MagicMock-tree. Identify whether tests assign attributes to it.
- [ ] **Task 2.11** — `tests/unit/ui/panels/test_empire_treasury_panel.py`: which autouse fixture? Same audit.
- [ ] **Task 2.15** — `tests/unit/ui/screens/test_fleet_report_filters.py`: `make_mock_ship` audit. The fixture has 20+ params per OpenCode 322-review; identify which params are mutated post-construction.
- [ ] **Task 2.19** — `tests/unit/simulation/test_ship_io.py`: which Ship fixtures? Audit round-trip mutation pattern.
- [ ] **Task 3.15** — `tests/unit/ui/panels/test_empire_treasury_panel.py` (overlap with 2.11): private-attr read on `_elements`/`_scroll_container` lists. Identify whether the list contents survive the rescope.

For each: classify into Strategy A / B / C / D (see below).

**Notes:** [Filled during implementation. Record per-task strategy.]

---

### Task 2.2: Apply Strategy A — direct rescope (no mutation found) [Simple]

For each fixture classified as no-mutation:

- [ ] Change scope from `function` (default) to `module` or `session`.
- [ ] Run the file. Verify no test fails.
- [ ] Run with `pytest-randomly` if available: `pytest --randomly-seed=1234 <file>`. Verify ordering doesn't matter.
- [ ] Measure per-file runtime before/after (mini-benchmark).

**Notes:** [Filled during implementation. Record per-task delta.]

---

### Task 2.3: Apply Strategy B — copy-on-write (narrow mutation) [Medium]

For each fixture classified as narrow-mutation (1-2 attributes touched):

- [ ] Wrap the fixture's return value in a deep-copy on demand:
  ```python
  @pytest.fixture(scope="module")
  def base_mock_ship():
      return _make_mock_ship_template(...)

  @pytest.fixture
  def mock_ship(base_mock_ship):
      import copy
      return copy.deepcopy(base_mock_ship)
  ```
- [ ] Verify: tests pass.
- [ ] Verify: per-test fixture is now cheap (just deepcopy a constructed mock — no re-construction overhead).
- [ ] Confirm with `pytest-randomly`.

**Notes:** [Filled during implementation. Record per-task delta.]

---

### Task 2.4: Apply Strategy C — `reset_mock()` autouse (broad mutation) [Complex]

For each fixture classified as broad-mutation:

- [ ] Change fixture scope to `class` or `module`.
- [ ] Add an autouse companion fixture:
  ```python
  @pytest.fixture(autouse=True)
  def reset_mock_X(mock_X):
      mock_X.reset_mock()
      yield
  ```
- [ ] **Verify cross-isolation explicitly:** run with `pytest --randomly-seed=1234 <file>` and `--randomly-seed=4321`. Diff outcomes — should be identical. If not, the rescope is unsafe; revert to function-scope.
- [ ] Document the cross-isolation risk in the file's docstring.
- [ ] Measure per-file runtime delta.

**Notes:** [Filled during implementation. Record per-task delta + cross-isolation verification.]

---

### Task 2.5: Apply Strategy D — keep deferred (mutation too broad / risk too high) [Simple]

For any fixture where Strategies A/B/C all introduce unacceptable risk:

- [ ] Keep the function-scoped fixture.
- [ ] Update PROJ-322 annotation to `**RE-CONFIRMED DEFERRED IN PROJ-327 Phase 2 — runtime impact considered, mutation pattern too broad to safely rescope. Audit at <commit SHA>**`.
- [ ] This is a VALID outcome per Decision D-006.

**Notes:** [Filled during implementation. List which fixtures fell into this strategy.]

---

### Task 2.6: Update PROJ-322 annotations + measure cumulative delta [Simple]

- [ ] For each of the 5 deferred items: update PROJ-322 phase checklist annotations with disposition (RESOLVED via Strategy A/B/C, or RE-CONFIRMED DEFERRED via Strategy D).
- [ ] Run sharded suite + median of 3 wall-clocks. Compare to Phase 0 baseline (subtract Phase 1 delta if Phase 1 ran first).
- [ ] Record cumulative Phase 2 delta in `findings/phase_2_runtime_delta.md`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] All 5 deferred fixtures dispositioned (RESOLVED or RE-CONFIRMED DEFERRED with rationale)
- [ ] Cross-isolation verified for any Strategy C application
- [ ] PROJ-322 annotations updated
- [ ] Sharded suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State accordingly
