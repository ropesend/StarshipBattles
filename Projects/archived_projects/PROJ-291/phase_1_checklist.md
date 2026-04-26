# Phase 1: C1 — Treasury Total includes Population Upkeep + e2e test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-291 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the Treasury Total aggregation in `EmpireEconomyCalculator.calculate()` to include `total_population_upkeep`. Pin the contract with a unit test AND an end-to-end render test (which also closes prior-audit M3).

---

## Tasks

### Task 1.1: Write the failing unit test [Simple]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py::TestTreasuryTotalIncludesUpkeep -v`

- [x] Add a new test class `TestTreasuryTotalIncludesUpkeep` at the end of the file.
- [x] Test 1: `test_total_expenses_includes_population_upkeep_per_resource`. Construct an empire with 2 colonies, each with 2 species + non-zero population (humans + voidari, count=1000 each) + a populated `economy.population_consumption = {"organics": 0.001, "metals": 0.0001}`. Call `EmpireEconomyCalculator(...).calculate(empire)`. Assert that for EVERY resource `r` in `_PLANETARY_IDS`:
  ```python
  expected = (
      snapshot.tribute_expenses.get(r, 0.0)
      + snapshot.construction_expenses_ships.get(r, 0.0)
      + snapshot.construction_expenses_complexes.get(r, 0.0)
      + snapshot.total_population_upkeep.get(r, 0.0)
  )
  assert snapshot.total_expenses[r] == pytest.approx(expected), \
      f"Total expenses for {r} should include population upkeep: {snapshot.total_expenses[r]} != {expected}"
  ```
- [x] Test 2: `test_net_resources_reflects_upkeep_in_total`. Same empire setup. Assert `snapshot.net_resources[r] == snapshot.total_production[r] - snapshot.total_expenses[r]` for every resource, AND that this equals the expected value with upkeep included.
- [x] Run the test. Confirm it FAILS with the current code (Total is too high by the upkeep amount). Confirmed: `total_expenses[metals] = 0.0` but expected `0.4`.

**Notes:** This is the test that should have caught C1 in PROJ-290's review cycle. It needs to live in the canonical engine-test file so it runs in every full-suite cycle.

### Task 1.2: Apply the one-line fix [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py -v`

- [x] At lines 144-151 of `calculate()`, add the upkeep term to the `total_expenses[r]` summation:
  ```python
  # Total expenses = sum of all expense categories
  snapshot.total_expenses = {}
  for r in _PLANETARY_IDS:
      snapshot.total_expenses[r] = (
          snapshot.tribute_expenses.get(r, 0.0)
          + snapshot.construction_expenses_ships.get(r, 0.0)
          + snapshot.construction_expenses_complexes.get(r, 0.0)
          + snapshot.total_population_upkeep.get(r, 0.0)   # PROJ-291 C1: include upkeep
      )
  ```
- [x] Run the new tests from Task 1.1 — both should now pass.
- [x] Run the full file: `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py -v`. Existing 7 `TestPopulationUpkeepAggregation` tests still pass. (26 passed total.)

**Notes:** Inline-comment marker `# PROJ-291 C1` is intentional — makes the change traceable in `git blame` and grep-able for future audits.

### Task 1.3: Write the e2e integration test (also closes prior-audit M3) [Medium]
**File:** `tests/integration/strategy/test_treasury_panel_e2e.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_treasury_panel_e2e.py -v`

- [x] Create the new test file. Follow the patterns in existing `tests/integration/strategy/test_*.py` files for setup style.
- [x] Test 1: `test_treasury_panel_total_row_equals_sum_of_expense_rows`. Build a snapshot via `EmpireEconomyCalculator(...).calculate(empire)` for an empire with non-zero values in all four expense categories (tributes, ships, complexes, upkeep). Then call `EmpireTreasuryPanel._get_expense_rows(snapshot)` (use the bypass-init pattern if needed; mock pygame_gui where necessary). Assert:
  - The "Population Upkeep" row appears in the rows list.
  - The "Total" row's per-resource cells equal the SUM of all four expense rows' cells (negated for drains).
- [x] Test 2: `test_treasury_panel_omits_upkeep_row_when_zero`. Same panel + render path, but with `snapshot.total_population_upkeep` empty/zero. Assert the "Population Upkeep" row is NOT inserted (existing behaviour — see `_get_expense_rows` lines 277-282 in the panel).
- [x] Run the tests. Confirm both pass.

**Notes:** This is the test the prior audit's M3 finding called out as missing. It's the regression-prevention contract for C1. Reuse the construction patterns from existing `test_empire_treasury_panel.py` unit tests where possible.

### Task 1.4: Run the targeted suite [Simple]
**Tests:** `pytest tests/unit/strategy/engine/ tests/integration/strategy/ -q`

- [x] Full unit + integration suite for the strategy engine + integration tests is green. (1072 passed, 1 skipped.)
- [x] No regressions in any neighbouring `test_*` file. (One pre-existing import error in `test_build_order_command_handler.py` confirmed unrelated by stashing PROJ-291 changes and re-running.)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
