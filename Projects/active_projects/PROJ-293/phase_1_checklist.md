# Phase 1: Add display fields to HabitabilityFactor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-293 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extend the `HabitabilityFactor` dataclass schema with `display_unit` and `display_precision` fields, populate them on every factor, and lock in the contract via registry tests. **No UI behavior changes in this phase.**

---

## Tasks

### Task 1.1: Write failing registry tests first (TDD per CLAUDE.md Rule 1) [Simple]
**File:** [tests/unit/strategy/data/test_habitability_factors.py](../../../tests/unit/strategy/data/test_habitability_factors.py)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py -v`

- [ ] Add a new test class `TestDisplayFields` (after the existing `TestRegistryShape`):
  ```python
  class TestDisplayFields:
      """Every factor must declare its UI display contract — display_unit
      (string suffix; '' for bare number) and display_precision (decimals).
      Catches new factors that fall back to verbose formatting."""

      def test_every_factor_has_display_unit(self):
          for factor in FACTOR_REGISTRY.values():
              assert hasattr(factor, "display_unit"), f"{factor.id} missing display_unit"
              assert isinstance(factor.display_unit, str), f"{factor.id}.display_unit must be str"

      def test_every_factor_has_display_precision(self):
          for factor in FACTOR_REGISTRY.values():
              assert hasattr(factor, "display_precision"), f"{factor.id} missing display_precision"
              assert isinstance(factor.display_precision, int), f"{factor.id}.display_precision must be int"
              assert factor.display_precision >= 0, f"{factor.id}.display_precision must be >= 0"

      def test_scalar_factor_display_units(self):
          """Lock in the per-factor display contract from PROJ-293."""
          expected = {
              "gravity":     ("g",   1),
              "temperature": ("K",   0),
              "water":       ("%",   0),
              "pressure":    ("kPa", 1),
              "tectonic":    ("",    2),  # bare number — no verbose unit
              "magnetic":    ("EE",  2),
              "radiation":   ("",    0),  # bare number — no verbose unit
          }
          for fid, (unit, precision) in expected.items():
              factor = FACTOR_REGISTRY[fid]
              assert factor.display_unit == unit, f"{fid}: expected display_unit={unit!r}, got {factor.display_unit!r}"
              assert factor.display_precision == precision, f"{fid}: expected display_precision={precision}, got {factor.display_precision}"

      def test_gas_factors_use_kpa(self):
          """All gases share the same display contract: kPa with 1 decimal."""
          gas_ids = ["gas_o2", "gas_n2", "gas_co2", "gas_h2o", "gas_ch4",
                     "gas_h2", "gas_he", "gas_ar", "gas_nh3", "gas_so2"]
          for fid in gas_ids:
              factor = FACTOR_REGISTRY[fid]
              assert factor.display_unit == "kPa", f"{fid}: expected display_unit='kPa', got {factor.display_unit!r}"
              assert factor.display_precision == 1, f"{fid}: expected display_precision=1, got {factor.display_precision}"
  ```
- [ ] Run the new test class — confirm 4 tests fail (`AttributeError: ... has no attribute 'display_unit'`)
- [ ] Verify the failure message mentions `display_unit` not `display_precision` (proves test runs in order)

**Notes:** [Filled during implementation]

---

### Task 1.2: Add fields to `HabitabilityFactor` dataclass [Simple]
**File:** [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py::TestDisplayFields::test_every_factor_has_display_unit -v`

- [ ] Read [game/strategy/data/habitability_factors.py:44-77](../../../game/strategy/data/habitability_factors.py#L44-L77) to see the dataclass shape
- [ ] Add two fields with defaults to `HabitabilityFactor` (after existing fields, before `extractor`/`scorer` callables):
  ```python
  # PROJ-293: declarative display contract — overrides the verbose
  # `f"{value:.2f} {unit}"` fallback. display_unit="" means bare number.
  display_unit: str = ""
  display_precision: int = 2
  ```
- [ ] Update the docstring at the top of the dataclass to mention these new fields and their meaning (storage `unit` vs display `display_unit`)
- [ ] Confirm the test `test_every_factor_has_display_unit` and `test_every_factor_has_display_precision` now pass (defaults satisfy the existence check)

**Notes:**

---

### Task 1.3: Populate display_unit/display_precision on the 7 scalar factors [Simple]
**File:** [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py) lines 143-248
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py::TestDisplayFields::test_scalar_factor_display_units -v`

Per the design document mapping:

- [ ] **gravity** (line ~144): add `display_unit="g", display_precision=1`
- [ ] **temperature** (line ~158): add `display_unit="K", display_precision=0`
- [ ] **water** (line ~174): add `display_unit="%", display_precision=0`
- [ ] **pressure** (line ~188): add `display_unit="kPa", display_precision=1`
- [ ] **tectonic** (line ~202): add `display_unit="", display_precision=2`
- [ ] **magnetic** (line ~216): add `display_unit="EE", display_precision=2`
- [ ] **radiation** (line ~230): add `display_unit="", display_precision=0`
- [ ] Run `test_scalar_factor_display_units` — confirm all 7 pass

**Notes:**

---

### Task 1.4: Populate display_unit/display_precision on the gas factor builder [Simple]
**File:** [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py) `_build_gas_factors` (~line 281)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py::TestDisplayFields::test_gas_factors_use_kpa -v`

- [ ] Read the gas builder around line 281
- [ ] In the `HabitabilityFactor(...)` call inside `_build_gas_factors`, add `display_unit="kPa", display_precision=1` to the kwargs (alongside existing `unit="Pa"` / `display_scale=0.001`)
- [ ] Run `test_gas_factors_use_kpa` — confirm pass (all 10 gases get the kwargs through the shared builder)

**Notes:**

---

### Task 1.5: Run full habitability registry test file [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py -v`

- [ ] All `TestDisplayFields` tests pass (4)
- [ ] Existing `TestRegistryShape`, `TestGasFactorWeights`, etc. still pass — no regression
- [ ] Confirm zero new failures

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
