# Phase 1: EnvironmentalPreference + Factor Registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Introduce `EnvironmentalPreference` dataclass and `FACTOR_REGISTRY` alongside the legacy `RaceConfig` fields. No habitability or UI code changes yet — new structures live in parallel with old ones.

---

## Tasks

### Task 1.1: Add `EnvironmentalPreference` dataclass [Simple]
**File:** `game/strategy/data/environmental_preference.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_environmental_preference.py`

- [x] Create the module with a `@dataclass` `EnvironmentalPreference`:
  ```python
  @dataclass
  class EnvironmentalPreference:
      setpoint: float
      tolerance: float
      min_value: float
      max_value: float
      step: float  # units per tolerance-cost step
  ```
- [x] Implement `to_dict(self) -> Dict[str, Any]` and classmethod `from_dict(cls, data) -> "EnvironmentalPreference"` with `require_keys` validation (mirror existing `PlanetaryFacility.from_dict` style).
- [x] Add `validate()` raising `ValidationException` if `min_value > max_value`, `setpoint` outside `[min_value, max_value]`, or `tolerance < 0`.
- [x] Add `__post_init__` calling `validate()`.

**Notes:** Added `step > 0` check too (guards the point-budget cost-curve denominator). `from_dict` casts values to `float` so int-typed JSON payloads round-trip cleanly. Validation messages prefix `EnvironmentalPreference:` for easier grepping in logs.

### Task 1.2: Write `EnvironmentalPreference` unit tests [Simple]
**File:** `tests/unit/strategy/data/test_environmental_preference.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_environmental_preference.py`

- [x] Test defaults construct cleanly.
- [x] Test `to_dict` round-trips via `from_dict`.
- [x] Test `validate()` raises on `min_value > max_value`.
- [x] Test `validate()` raises on setpoint outside bounds.
- [x] Test `validate()` raises on negative tolerance.

**Notes:** 12 tests written, all pass. Added `test_rejects_non_positive_step` (covers the extra step validation), `test_tolerance_may_be_zero` (documents the edge), and `test_from_dict_casts_int_to_float` (JSON compatibility).

### Task 1.3: Add `HabitabilityFactor` dataclass + `FACTOR_REGISTRY` [Medium]
**File:** `game/strategy/data/habitability_factors.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py`

- [x] Define `HabitabilityFactor` dataclass.
- [x] Implement default `_default_gaussian_scorer(value, pref) -> float` by calling existing `_gaussian_factor` from `habitability.py` (no circular import risk — habitability.py uses `TYPE_CHECKING` for RaceConfig).
- [x] Implement missing-data handling: `value is None` → treat as 0.0 (scorer contract; same outcome as gas-absence = 0 Pa).
- [x] Register all 7 scalar factors with weights 1.0/1.0/0.8/0.9/0.4/0.6/0.6.
- [x] Register all 10 gases with per-gas weight `1.5 / 10 = 0.15`, unit Pa, display_scale 0.001.
- [x] Earth-standard defaults per checklist. (Small deviation: chose `step=0.98` for gravity so one step is ~0.1 g in m/s² units; 0.1 g × 9.81 m/s²/g = 0.981, rounded to 0.98. The check for "step >= 0.1 g" is preserved.)
- [x] `get_factor(factor_id)` raises KeyError on unknown id.
- [x] `iter_scalar_factors()` / `iter_gas_factors()` iterators partition the registry.

**Notes:** Radiation extractor reads `planet.radiation_shielding` — Planet has no intrinsic "incident radiation" field today. Default setpoint 0 / tolerance 50 documents the "race doesn't care by default" stance; Phase 2 parity tests will flag if this feels off.

`_default_gaussian_scorer` coerces `None` to 0.0 before calling `_gaussian_factor`. Net effect: race with setpoint > 0 and missing planet value scores `exp(-0.5*(setpoint/tolerance)²)` (near zero when setpoint >> tolerance); race with setpoint = 0 and missing value scores 1.0. Documented in the scorer docstring.

### Task 1.4: Write factor registry unit tests [Simple]
**File:** `tests/unit/strategy/data/test_habitability_factors.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py`

- [x] Test every registry entry has a valid extractor signature (callable with 1 arg).
- [x] Test every `id` is unique.
- [x] Test every `default_setpoint` is within `[min_value, max_value]`.
- [x] Test every `default_tolerance` is positive.
- [x] Test `get_factor("gas.O2")` returns the expected factor.
- [x] Test `get_factor("nonexistent")` raises KeyError.
- [x] Test `iter_scalar_factors()` yields exactly 7 entries.
- [x] Test `iter_gas_factors()` yields exactly 10 entries.
- [x] Test default gas extractors read from `planet.atmosphere.get(formula)` and return 0.0 (not None) when missing.

**Notes:** 39 tests written and passing. Added explicit scalar-factor-weight parametrization, gas-bucket-sums-to-1.5 check, per-factor dataclass-frozen check, and scorer behavior at setpoint / at 1σ / far / missing-with-zero-setpoint / missing-with-nonzero-setpoint.

### Task 1.5: Add `preferences`, `base_reproduction_rate`, `base_happiness` fields to `RaceConfig` (parallel to legacy) [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py`

- [x] Add `preferences: Dict[str, EnvironmentalPreference] = field(default_factory=dict)` to the dataclass.
- [x] Add `base_reproduction_rate: float = 0.03`.
- [x] Add `base_happiness: float = 0.5`.
- [x] In `__post_init__`, populate `preferences` from `FACTOR_REGISTRY` defaults when missing (per-factor backfill — preserves any explicit entries).
- [x] Update `to_dict` to serialize `preferences` as `{factor_id: env_pref.to_dict()}`.
- [x] Update `from_dict` to rehydrate `preferences`.
- [x] Keep legacy fields untouched for this phase — parallel only.
- [x] Update `validate()` to call each `EnvironmentalPreference.validate()` (via new `_validate_preferences()` hook).

**Notes:** 11 new tests added (3 classes: Preferences / BaseReproductionAndHappiness / ValidateWithPreferences). All pass. `from_dict` calls `EnvironmentalPreference.from_dict` on each nested entry; the `__post_init__` backfill then tops up any factor id missing from the incoming data — lets old saves upgrade cleanly.

**Pre-existing failures in `TestRaceConfigValidation` (16 tests) are unrelated:** they unpack `config.validate()` as a tuple, but `validate()` has long returned a `ValidationResult` object. Confirmed via `git stash` to predate this project. Hidden from the sharded runner because a sibling file (`test_build_order_command_handler.py`) collection error aborts the sweep before `test_race_config.py` is scanned. Leaving those tests as-is for now — they're a separate project.

### Task 1.6: Verify existing tests still green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full suite — every test must still pass.
- [x] Update the `RaceConfig` roundtrip test if it exists to exercise the new fields.

**Notes:** Sharded suite result: 14776/14777. Sole failure is the pre-existing flaky `test_copy_designs_without_themes_preserves_original` in `tests/unit/quickstart/`; verified unrelated multiple times in earlier sessions (`git stash` reproduces without any PROJ-283 changes). Two tick_mechanics tests transiently flake under parallel execution but pass in isolation — matches the flakiness pattern seen in previous sessions.

Roundtrip test already exercised in `TestRaceConfigPreferencesField.test_preferences_round_trip` and `TestRaceConfigBaseReproductionAndHappiness.test_round_trip_preserves_values`. Legacy `test_round_trip_serialization` continues to pass unchanged.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
