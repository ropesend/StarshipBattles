# Phase 2: Refactor format_value to data-driven

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-293 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the 26-line if-tree in `PreferenceRow.format_value()` with a one-line data-driven formatter that reads `factor.display_unit` and `factor.display_precision`. The 5 currently-handled units must produce **bit-identical output strings** to today; the 2 currently-broken units (`tectonic`, `radiation`) and verbose-suffix bug get fixed as a side effect.

---

## Tasks

### Task 2.1: Extend test_preference_row.py to lock in tectonic + radiation outputs (TDD) [Simple]
**File:** [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py::TestDisplayScaling -v`

- [ ] Read the existing `TestDisplayScaling` class (~line 176) to understand the test pattern (calls `PreferenceRow.format_value(factor, raw_value)` directly)
- [ ] Add new tests INSIDE `TestDisplayScaling`:
  ```python
  def test_tectonic_format_no_unit_suffix(self):
      """PROJ-293: tectonic activity is a 0-1 fraction; the verbose 'fraction'
      suffix was removed. Output is a bare 2-decimal number."""
      from game.strategy.data.habitability_factors import FACTOR_REGISTRY
      factor = FACTOR_REGISTRY["tectonic"]
      assert PreferenceRow.format_value(factor, 0.30) == "0.30"
      assert PreferenceRow.format_value(factor, 0.20) == "0.20"

  def test_radiation_format_no_unit_suffix(self):
      """PROJ-293: radiation shielding is an abstract score; the verbose
      'shielding' suffix was removed. Output is a bare integer."""
      from game.strategy.data.habitability_factors import FACTOR_REGISTRY
      factor = FACTOR_REGISTRY["radiation"]
      assert PreferenceRow.format_value(factor, 0.0) == "0"
      assert PreferenceRow.format_value(factor, 50.0) == "50"
      assert PreferenceRow.format_value(factor, -25.0) == "-25"

  def test_format_uses_factor_display_fields(self):
      """The formatter reads display_unit and display_precision from the
      factor itself, not a hardcoded if-tree. Synthesize a fake factor and
      check the output picks up its declared format."""
      from game.strategy.data.habitability_factors import HabitabilityFactor
      fake = HabitabilityFactor(
          id="test", display_name="Test", unit="raw",
          display_scale=1.0, weight=1.0,
          default_setpoint=0.0, default_tolerance=1.0,
          min_value=0.0, max_value=10.0, step=1.0,
          extractor=lambda p: 0.0, scorer=lambda v, pref, w: 1.0,
          display_unit="zorps", display_precision=3,
      )
      assert PreferenceRow.format_value(fake, 1.234567) == "1.235 zorps"
  ```
- [ ] Run `pytest tests/unit/ui/widgets/test_preference_row.py::TestDisplayScaling -v` — the three new tests should FAIL (current code produces `"0.30 fraction"`, `"0.00 shielding"`, etc.)
- [ ] Confirm existing tests in `TestDisplayScaling` (gravity → "1.0 g", pressure → "101.3 kPa", water → "50%", temperature → "288 K") still pass — they continue to use the if-tree path

**Notes:**

---

### Task 2.2: Replace `format_value` with data-driven implementation [Simple]
**File:** [game/ui/widgets/preference_row.py](../../../game/ui/widgets/preference_row.py) lines 73-98
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py -v`

- [ ] Read [game/ui/widgets/preference_row.py:73-98](../../../game/ui/widgets/preference_row.py#L73-L98) — the current `format_value` method
- [ ] Replace the entire if-tree body with the data-driven implementation:
  ```python
  @staticmethod
  def format_value(factor: "HabitabilityFactor", raw_value: float) -> str:
      """Render a raw factor value in its display unit.

      PROJ-293: Display formatting is data-driven via `factor.display_unit`
      and `factor.display_precision`. To add a new factor with a custom
      display, set those fields in the registry — no UI code change required.

      Convention: percent unit is glued to the number ('50%'); all other
      non-empty units take a separating space ('1.0 g'); empty unit
      produces a bare number ('0.30').
      """
      scaled = raw_value * factor.display_scale
      text = f"{scaled:.{factor.display_precision}f}"
      if factor.display_unit == "%":
          return f"{text}%"
      if factor.display_unit:
          return f"{text} {factor.display_unit}"
      return text
  ```
- [ ] Run `pytest tests/unit/ui/widgets/test_preference_row.py::TestDisplayScaling -v` — all tests now pass:
  - 4 existing tests: gravity, pressure, water, temperature still produce identical strings
  - 3 new tests: tectonic, radiation, fake-factor produce expected outputs

**Notes:**

---

### Task 2.3: Run all preference_row tests [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py -v`

- [ ] All test classes pass: `TestPreferenceRowConstruction`, `TestDisplayScaling`, `TestOnChangeCallback`, `TestCostLabel`, `TestCostLabelLiveUpdate`
- [ ] No new failures
- [ ] If `TestCostLabelLiveUpdate.refresh_from_sliders()` produces a different label string after the refactor, investigate — but per the design doc, identical strings are expected for the 5 already-handled units

**Notes:**

---

### Task 2.4: Run full sharded suite to catch any indirect regressions [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green (15109+ tests; no new failures vs. PROJ-293 baseline)
- [ ] If any test outside `tests/unit/ui/widgets/` or `tests/unit/strategy/data/` fails, investigate — `format_value` may be called through a path the research missed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
