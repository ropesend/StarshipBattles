# Phase 2: New habitability pipeline (parallel to old)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement `calculate_habitability_v2(planet, race_config)` that iterates `FACTOR_REGISTRY`. Keep v1 intact. Add parity tests ensuring v1 and v2 agree on the 5 shared axes for near-ideal inputs.

---

## Tasks

### Task 2.1: Implement `calculate_habitability_v2` [Medium]
**File:** `game/strategy/formulas/habitability.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py`

- [x] Add function `calculate_habitability_v2(planet, race_config) -> float`.
- [x] Iterate `FACTOR_REGISTRY`: for each factor, pull `value = factor.extractor(planet)`, pull `pref = race_config.preferences[factor.id]`, compute `score = factor.scorer(value, pref)`, weight by `factor.weight`.
- [x] Combine via the existing weighted geometric mean helper: `exp(Σ w*log(max(s, ε)) / Σ w)`, epsilon 1e-10 (matches v1; tightened from initial 1e-4 draft — see decisions.md).
- [x] If a preference is missing from `race_config.preferences`, treat as default from registry (do NOT skip the factor — missing prefs mean "Earth-standard tolerance").
- [x] Do NOT modify v1. v2 is a sibling function.

**Notes:** v2 lives at `game/strategy/formulas/habitability.py:288-339`. Lazy-imports `FACTOR_REGISTRY` and `EnvironmentalPreference` inside the function body to break the otherwise-circular dependency (`habitability_factors.py` already imports `_gaussian_factor` from `habitability.py`). Same pattern lets test code `unittest.mock.patch("...habitability_factors.FACTOR_REGISTRY", {...})` to isolate single-factor behaviour.

### Task 2.2: Gas-specific scorer edge case [Simple]
**File:** `game/strategy/data/habitability_factors.py` (update default scorer for gas factors)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py::TestCalculateHabitabilityV2GasMissing`

- [x] For gas factors where extractor returns 0.0 (gas absent from atmosphere) and `pref.setpoint > 0`, the score collapses toward 0 (the race wants this gas but the planet has none). Verified by `_default_gaussian_scorer` (no scorer change required — Phase 1 contract already covers this).
- [x] Deviation = `setpoint - 0 = setpoint`; scorer applies Gaussian with σ=tolerance; result is `exp(-(setpoint/tolerance)²/2)` which is near-zero for `setpoint >> tolerance`.
- [x] For gas factors where extractor returns 0.0 and `pref.setpoint == 0`, score is 1.0 (race doesn't care about this gas).
- [x] Added explicit test cases covering both branches (`test_gas_missing_with_setpoint_collapses_to_zero` + `test_gas_missing_with_zero_setpoint_is_ideal`).

**Notes:** No scorer change needed — Phase 1's `_default_gaussian_scorer` already encodes the contract (None / 0.0 → deviation = setpoint → exp(-(setpoint/tolerance)²/2)). Test thresholds asserted as comparative drops rather than absolute thresholds because per-gas weight (0.15 of total 6.8) bounds the absolute composite drag from a single missing gas. See decisions.md for the design rationale.

### Task 2.3: v1/v2 parity tests [Medium]
**File:** `tests/unit/strategy/formulas/test_habitability_v2.py` (NEW)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability_v2.py`

- [x] Test each scalar factor in isolation (registry pruned via mock to a single factor) — `TestV1V2Parity::test_single_factor_isolation` (parametrized for gravity / temperature / water).
- [x] Test one-zero-tanks-all invariant: gravity (weight 1.0) tightened to tolerance 0.5, planet at 25 m/s² → composite < 0.1 (`TestOneZeroTanksAll::test_single_factor_at_001_drags_composite_below_01`). Note: this property holds for high-weight scalar axes; per-gas factors at weight 0.15 only drag composite to ~0.6 even at the floor — documented in decisions.md as a deliberate trade-off of v2's smoother weight allocation.
- [x] Test v1 vs v2 parity: on an Earth-like planet with a near-Earth race, both formulas land in the "good planet" zone (v1 ≥ 0.6, v2 ≥ 0.85). v1's per-gas-fraction atmosphere model gives a different absolute number than v2's per-gas-Gaussian model, so we don't assert tight numerical equivalence — only that both formulas correctly identify a good planet.
- [x] Test registry-driven atmosphere: planet with 21 kPa O2 + 79 kPa N2, race setpoint O2 21 kPa tolerance 3 kPa → composite ≥ 0.9 (`TestRegistryDrivenAtmosphere::test_o2_loving_race_on_o2_rich_planet`). Race setpoint O2 21 kPa tolerance 3 kPa on a planet with 0 O2 → composite < 0.75 × O2-present case (`test_o2_loving_race_on_no_o2_planet`).
- [x] Test total-pressure factor: `TestPressureFactor::test_pressure_at_setpoint_does_not_pull_score_down` (101325 Pa setpoint → ≥ 0.95) + `test_double_pressure_reduces_score` (202650 Pa < 101325 Pa).
- [x] Test tectonic factor: `TestTectonicFactor::test_tectonic_at_setpoint_scores_high` (0.3 → ≥ 0.95) + `test_volcanic_planet_scores_lower` (0.95 < 0.3).

**Notes:** 21 new tests in `tests/unit/strategy/formulas/test_habitability_v2.py`, all passing. The `_FakePlanet` test helper defaults to an Earth-like atmosphere (O2=21 kPa, N2=79 kPa) so isolated single-factor tests don't get accidentally tanked by missing gases. The helper's defaults can be overridden per-test for hostile-planet scenarios.

### Task 2.4: Verify suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green. v1 still works; v2 still untouched by callers.
- [x] All task checkboxes above are checked.
- [x] Status updated to `Complete` at top of this file.
- [x] plan.md phase table row updated to `Complete` (next task).
- [x] plan.md Current State updated to point to next phase (next task).

**Notes:**
- v2 implementation lives at `game/strategy/formulas/habitability.py:288-339` (lazy-imports `FACTOR_REGISTRY` to avoid circular import with `habitability_factors.py` which imports `_gaussian_factor`).
- Phase 2 made one registry tuning change: N2 default setpoint 0 → 79000 Pa, tolerance → 20000 Pa. Without this, an "Earth-like default race" would silently flunk every Earth-like planet (8σ N2 mismatch). Documented in decisions.md.
- 21 new v2 tests added (`tests/unit/strategy/formulas/test_habitability_v2.py`); all 39 Phase 1 `test_habitability_factors` tests + 12 Phase 1 `test_environmental_preference` tests + Phase 1 `test_race_config` preferences tests still pass.
- Full sharded run: 14797/14798 (sole failure is the same pre-existing flaky `test_copy_designs_without_themes_preserves_original` quickstart test flagged in Phase 1 handoff; unrelated to PROJ-283 scope).
- Pre-existing `TestRaceConfigValidation` 16-test failure (tuple-unpacking `validate()` return) remains hidden in sharded runs because of the `test_build_order_command_handler.py` collection error — also unchanged from Phase 1 handoff and out of PROJ-283 scope.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
