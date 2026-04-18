# Phase 2: New habitability pipeline (parallel to old)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement `calculate_habitability_v2(planet, race_config)` that iterates `FACTOR_REGISTRY`. Keep v1 intact. Add parity tests ensuring v1 and v2 agree on the 5 shared axes for near-ideal inputs.

---

## Tasks

### Task 2.1: Implement `calculate_habitability_v2` [Medium]
**File:** `game/strategy/formulas/habitability.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py`

- [ ] Add function `calculate_habitability_v2(planet, race_config) -> float`.
- [ ] Iterate `FACTOR_REGISTRY`: for each factor, pull `value = factor.extractor(planet)`, pull `pref = race_config.preferences[factor.id]`, compute `score = factor.scorer(value, pref)`, weight by `factor.weight`.
- [ ] Combine via the existing weighted geometric mean helper: `exp(Σ w*log(max(s, ε)) / Σ w)`, epsilon 1e-4.
- [ ] If a preference is missing from `race_config.preferences`, treat as default from registry (do NOT skip the factor — missing prefs mean "Earth-standard tolerance").
- [ ] Do NOT modify v1. v2 is a sibling function.

### Task 2.2: Gas-specific scorer edge case [Simple]
**File:** `game/strategy/data/habitability_factors.py` (update default scorer for gas factors)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py::test_gas_missing_with_setpoint_collapses_to_zero`

- [ ] For gas factors where extractor returns 0.0 (gas absent from atmosphere) and `pref.setpoint > 0`, the score must collapse toward 0 (the race wants this gas but the planet has none).
- [ ] Deviation = `setpoint - 0 = setpoint`; scorer applies Gaussian with σ=tolerance; result should be `exp(-(setpoint/tolerance)²/2)` which is near-zero for `setpoint >> tolerance`.
- [ ] For gas factors where extractor returns 0.0 and `pref.setpoint == 0`, score should be 1.0 (race doesn't care about this gas).
- [ ] Add explicit test cases covering both branches.

### Task 2.3: v1/v2 parity tests [Medium]
**File:** `tests/unit/strategy/formulas/test_habitability_v2.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py`

- [ ] Test each scalar factor in isolation (registry pruned via mock to a single factor).
- [ ] Test one-zero-tanks-all invariant: if any factor scores 0.01, overall habitability < 0.1.
- [ ] Test v1 vs v2 parity: on an Earth-like planet with a near-Earth race, v1 and v2 differ by ≤ 0.05 for the 5 shared axes (gravity/temp/water/atmosphere/radiation). Magnetic/tectonic/pressure factors will differ — expected.
- [ ] Test registry-driven atmosphere: planet with 21 kPa O2 + 79 kPa N2, race setpoint O2 21 kPa tolerance 3 kPa → atmosphere factor contribution ≈ 1.0. Race setpoint O2 21 kPa tolerance 3 kPa on a planet with 0 O2 → contribution ≈ 0.
- [ ] Test total-pressure factor: planet with 101325 Pa pressure, race setpoint 101325 tolerance 20000 → pressure factor ≈ 1.0. Planet at 202650 Pa → significantly reduced.
- [ ] Test tectonic factor: planet with activity 0.1, race setpoint 0.1 → ≈ 1.0. Planet with activity 0.9 → low.

### Task 2.4: Verify suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green. v1 still works; v2 still untouched by callers.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
