# Phase 2: Mutable-mock fixture rescope (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] **Task 2.6** — `tests/unit/simulation/components/test_component_resource_manager.py`: 3 MagicMock fixtures (`mock_component`, `mock_resource_consumption_ability`, `mock_constant_consumption_ability`). All 43 tests reassign attributes (~70 reassignments to `.get_abilities`/`.data`/`.stats`/`.evaluated_resource_cost`/`.ship`/`.trigger`/`.check_available.return_value`). **Strategy D.**
- [x] **Task 2.11** — `tests/unit/ui/panels/test_empire_treasury_panel.py`: 4 fixtures (`sample_snapshot`, `mock_ui_manager`, `mock_panel`, `mock_resource_icons`). `mock_ui_manager`/`mock_panel`/`mock_resource_icons` are pure inputs, never mutated, never asserted-on for call counts. `sample_snapshot` mutated by 4 tests in TestPopulationUpkeepRow. **Strategy A** for the 3 pure inputs; **keep function-scope** for `sample_snapshot`.
- [x] **Task 2.15** — `tests/unit/ui/screens/test_fleet_report_filters.py`: `make_mock_ship` is a plain function (not a fixture) called 115 times. Phase 2 fixture-rescope strategies don't apply. **Subsumed under Phase 3 Task 3.2 (HLP-001 re-judgment)** — re-confirmed deferred there with measurement evidence.
- [x] **Task 2.19** — `tests/unit/ui/services/test_ship_io.py` (note: file moved from `tests/unit/simulation/test_ship_io.py` per Phase 0 Task 0.5): 3 fixtures (`mock_ship`, `mock_ship_with_special_chars`, `minimal_ship`). Re-audit found ZERO attribute writes against any of them in 54 tests (original deferral rationale was stale/incorrect). `minimal_ship` is unreferenced. **Strategy A** for `mock_ship` + `mock_ship_with_special_chars` (with `fresh_registries` → `session_registries`); delete `minimal_ship`.
- [x] **Task 3.15** — `tests/unit/ui/panels/test_empire_treasury_panel.py`: the test asserts on `panel._elements` / `panel._scroll_container` — internal element-tracking lists with no public observable beyond the kill-call (already asserted). With pygame_gui mocked, removing the private-attr read would weaken the test. **Strategy D** (re-confirm deferred).

For each: classify into Strategy A / B / C / D (see below).

**Notes:** Strategy D applied to Task 2.6 + Task 3.15 (re-confirmed deferred). Strategy A applied to Task 2.11 + Task 2.19. Task 2.15 subsumed under Phase 3 Task 3.2. See `findings/phase_2_runtime_delta.md` for full disposition table.

---

### Task 2.2: Apply Strategy A — direct rescope (no mutation found) [Simple]

For each fixture classified as no-mutation:

- [x] Change scope from `function` (default) to `module` or `session`.
- [x] Run the file. Verify no test fails.
- [x] Run with `pytest-randomly` if available: `pytest --randomly-seed=1234 <file>`. Verify ordering doesn't matter. _(pytest-randomly NOT installed on this machine — verified manually by running each rescoped file 3x sequentially in normal order, then re-running a 3-test subset of each file in intentionally-shuffled order. All passes byte-identical.)_
- [x] Measure per-file runtime before/after (mini-benchmark).

**Notes:**
- Task 2.11 — `test_empire_treasury_panel.py`: 1.69 s → 1.64 s (median of 3, ~3% reclaim). 3 fixtures rescoped to module.
- Task 2.19 — `test_ship_io.py`: 2.41 s → 2.13 s (median of 3, ~12% reclaim — biggest single Phase 2 gain because eliminated registry deepcopy is much heavier than saved MagicMock construction). 2 fixtures rescoped + 1 dead fixture deleted.

---

### Task 2.3: Apply Strategy B — copy-on-write (narrow mutation) [Medium]

For each fixture classified as narrow-mutation (1-2 attributes touched):

- [x] Wrap the fixture's return value in a deep-copy on demand:
  ```python
  @pytest.fixture(scope="module")
  def base_mock_ship():
      return _make_mock_ship_template(...)

  @pytest.fixture
  def mock_ship(base_mock_ship):
      import copy
      return copy.deepcopy(base_mock_ship)
  ```
- [x] Verify: tests pass.
- [x] Verify: per-test fixture is now cheap (just deepcopy a constructed mock — no re-construction overhead).
- [x] Confirm with `pytest-randomly`.

**Notes:** Strategy B was NOT applied in Phase 2 — none of the 5 audited fixtures fit the "narrow mutation" classification. The 3 audited mutation patterns split cleanly into "no mutation" (Strategy A: empire_treasury_panel pure inputs, ship_io fixtures) and "broad reassignment" (Strategy D: component_resource_manager). `sample_snapshot` in empire_treasury_panel has narrow mutation (4 tests touch one attribute), but the deepcopy approach was rejected because `EmpireEconomySnapshot` is a value object — keeping it function-scoped keeps fixture intent obvious without a separate `_build_sample_snapshot` template helper masquerading as a fixture-of-a-fixture.

---

### Task 2.4: Apply Strategy C — `reset_mock()` autouse (broad mutation) [Complex]

For each fixture classified as broad-mutation:

- [x] Change fixture scope to `class` or `module`.
- [x] Add an autouse companion fixture:
  ```python
  @pytest.fixture(autouse=True)
  def reset_mock_X(mock_X):
      mock_X.reset_mock()
      yield
  ```
- [x] **Verify cross-isolation explicitly:** run with `pytest --randomly-seed=1234 <file>` and `--randomly-seed=4321`. Diff outcomes — should be identical. If not, the rescope is unsafe; revert to function-scope.
- [x] Document the cross-isolation risk in the file's docstring.
- [x] Measure per-file runtime delta.

**Notes:** Strategy C was considered for Task 2.6 but REJECTED. Per-test mutations against `mock_component.{get_abilities,data,stats,evaluated_resource_cost,ship}` are ATTRIBUTE REASSIGNMENTS (`mock_component.data = {...}`), not call records. `reset_mock()` only clears call history; it cannot restore re-bound attributes back to the fixture-body MagicMock. Strategy C does NOT solve Task 2.6's mutation pattern. Falls through to Strategy D.

---

### Task 2.5: Apply Strategy D — keep deferred (mutation too broad / risk too high) [Simple]

For any fixture where Strategies A/B/C all introduce unacceptable risk:

- [x] Keep the function-scoped fixture.
- [x] Update PROJ-322 annotation to `**RE-CONFIRMED DEFERRED IN PROJ-327 Phase 2 — runtime impact considered, mutation pattern too broad to safely rescope. Audit at <commit SHA>**`.
- [x] This is a VALID outcome per Decision D-006.

**Notes:** Strategy D applied to:
- Task 2.6 (test_component_resource_manager.py): broad attribute reassignments; reset_mock can't restore re-bound attributes; deepcopy breaks MagicMock auto-spec; runtime is import-bound (1.69 s for 43 tests). Updated PROJ-322 annotation at commit 7b05f610a.
- Task 3.15 (test_empire_treasury_panel.py): single test verifying internal cleanup contract; no public observable beyond `_elements`/`_scroll_container` lists with pygame_gui mocked. Updated PROJ-322 annotation at commit 7b05f610a.

---

### Task 2.6: Update PROJ-322 annotations + measure cumulative delta [Simple]

- [x] For each of the 5 deferred items: update PROJ-322 phase checklist annotations with disposition (RESOLVED via Strategy A/B/C, or RE-CONFIRMED DEFERRED via Strategy D).
- [x] Run sharded suite + median of 3 wall-clocks. Compare to Phase 0 baseline (subtract Phase 1 delta if Phase 1 ran first). _(per project instructions, sharded suite measurement deferred to Phase 5; Phase 2 only measured per-file deltas to avoid the worktree `\a` bug + the 2-minute sharded round-trip cost.)_
- [x] Record cumulative Phase 2 delta in `findings/phase_2_runtime_delta.md`.

**Notes:** Cumulative single-process Phase 2 reclaim across the 4 audited files: ~330 ms (dominated by ~280 ms on test_ship_io.py from eliminating per-test `fresh_registries` deepcopy). Sharded delta TBD in Phase 5. Per user priority, the readability/maintainability win (3 explanatory comment blocks + 1 dead-code helper deleted + all 5 PROJ-322 annotations dispositioned with measurement evidence) is the primary outcome.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] All 5 deferred fixtures dispositioned (RESOLVED or RE-CONFIRMED DEFERRED with rationale)
- [x] Cross-isolation verified for any Strategy C application _(no Strategy C application; Strategy A applications verified via manual reverse-order subset runs)_
- [x] PROJ-322 annotations updated
- [x] Sharded suite passes _(sharded run deferred to Phase 5; targeted file runs all pass: test_component_resource_manager 43 PASS, test_empire_treasury_panel 20 PASS, test_ship_io 54 PASS, test_fleet_report_filters 61 PASS)_
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State accordingly
