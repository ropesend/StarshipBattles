# Phase 1: EnvironmentalPreference + Factor Registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce `EnvironmentalPreference` dataclass and `FACTOR_REGISTRY` alongside the legacy `RaceConfig` fields. No habitability or UI code changes yet — new structures live in parallel with old ones.

---

## Tasks

### Task 1.1: Add `EnvironmentalPreference` dataclass [Simple]
**File:** `game/strategy/data/environmental_preference.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_environmental_preference.py`

- [ ] Create the module with a `@dataclass` `EnvironmentalPreference`:
  ```python
  @dataclass
  class EnvironmentalPreference:
      setpoint: float
      tolerance: float
      min_value: float
      max_value: float
      step: float  # units per tolerance-cost step
  ```
- [ ] Implement `to_dict(self) -> Dict[str, Any]` and classmethod `from_dict(cls, data) -> "EnvironmentalPreference"` with `require_keys` validation (mirror existing `PlanetaryFacility.from_dict` style).
- [ ] Add `validate()` raising `ValidationException` if `min_value > max_value`, `setpoint` outside `[min_value, max_value]`, or `tolerance < 0`.
- [ ] Add `__post_init__` calling `validate()`.

### Task 1.2: Write `EnvironmentalPreference` unit tests [Simple]
**File:** `tests/unit/strategy/data/test_environmental_preference.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_environmental_preference.py`

- [ ] Test defaults construct cleanly.
- [ ] Test `to_dict` round-trips via `from_dict`.
- [ ] Test `validate()` raises on `min_value > max_value`.
- [ ] Test `validate()` raises on setpoint outside bounds.
- [ ] Test `validate()` raises on negative tolerance.

### Task 1.3: Add `HabitabilityFactor` dataclass + `FACTOR_REGISTRY` [Medium]
**File:** `game/strategy/data/habitability_factors.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py`

- [ ] Define `HabitabilityFactor` dataclass:
  ```python
  @dataclass(frozen=True)
  class HabitabilityFactor:
      id: str
      display_name: str
      unit: str              # "g", "K", "Pa", "fraction", etc.
      display_scale: float   # Pa -> kPa conversion is 0.001; default 1.0
      weight: float
      default_setpoint: float
      default_tolerance: float
      min_value: float
      max_value: float
      step: float
      extractor: Callable[["Planet"], Optional[float]]
      scorer: Callable[[Optional[float], EnvironmentalPreference], float]
  ```
- [ ] Implement default `_gaussian_scorer(value, pref) -> float` using existing `_gaussian_factor` from `habitability.py` (or a copy to avoid circular import; reuse via import in Phase 2).
- [ ] Implement missing-data handling: if `extractor` returns `None` and `pref.setpoint > 0`, use `setpoint` as full deviation (factor collapses to near-zero). Document this in scorer docstring.
- [ ] Register all 7 scalar factors: `gravity`, `temperature`, `water`, `pressure` (total surface pressure), `tectonic`, `magnetic`, `radiation`. Weights per design.md: 1.0, 1.0, 0.8, 0.9, 0.4, 0.6, 0.6.
- [ ] Register all 10 gases as `gas.O2`, `gas.N2`, `gas.CO2`, `gas.H2O`, `gas.CH4`, `gas.H2`, `gas.He`, `gas.Ar`, `gas.NH3`, `gas.SO2`. Per-gas weight: `1.5 / 10 = 0.15` each. Unit: `Pa`, display_scale: `0.001` (Pa -> kPa).
- [ ] Set defaults from Earth-standard: `gravity` setpoint 9.81 m/s² tolerance 2.0; `temperature` 293 K tolerance 50; `water` 0.5 tolerance 0.2; `pressure` 101325 Pa tolerance 20000; `tectonic` 0.3 tolerance 0.2; `magnetic` 1.0 tolerance 0.3; `radiation` 0 tolerance 50; `gas.O2` 21000 Pa tolerance 5000; other gases setpoint 0 tolerance 10000 (race doesn't care by default).
- [ ] Add module-level `get_factor(factor_id) -> HabitabilityFactor` helper; raise `KeyError` on unknown.
- [ ] Add module-level `iter_scalar_factors()` and `iter_gas_factors()` iterators (filter by `id.startswith("gas.")`).

### Task 1.4: Write factor registry unit tests [Simple]
**File:** `tests/unit/strategy/data/test_habitability_factors.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_habitability_factors.py`

- [ ] Test every registry entry has a valid extractor signature (callable with 1 arg).
- [ ] Test every `id` is unique.
- [ ] Test every `default_setpoint` is within `[min_value, max_value]`.
- [ ] Test every `default_tolerance` is positive.
- [ ] Test `get_factor("gas.O2")` returns the expected factor.
- [ ] Test `get_factor("nonexistent")` raises KeyError.
- [ ] Test `iter_scalar_factors()` yields exactly 7 entries.
- [ ] Test `iter_gas_factors()` yields exactly 10 entries.
- [ ] Test default gas extractors read from `planet.atmosphere.get(formula)` and return 0.0 (not None) when missing — design choice for gas-absence-is-zero-partial-pressure.

### Task 1.5: Add `preferences`, `base_reproduction_rate`, `base_happiness` fields to `RaceConfig` (parallel to legacy) [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py`

- [ ] Add `preferences: Dict[str, EnvironmentalPreference] = field(default_factory=dict)` to the dataclass.
- [ ] Add `base_reproduction_rate: float = 0.03`.
- [ ] Add `base_happiness: float = 0.5`.
- [ ] In `__post_init__`, populate `preferences` from `FACTOR_REGISTRY` defaults when empty (iterate `iter_scalar_factors()` + `iter_gas_factors()` and create an `EnvironmentalPreference` from each factor's defaults).
- [ ] Update `to_dict` to serialize `preferences` as `{factor_id: env_pref.to_dict()}`.
- [ ] Update `from_dict` to rehydrate `preferences`.
- [ ] Keep legacy fields untouched for this phase — parallel only.
- [ ] Update `validate()` to call each `EnvironmentalPreference.validate()`.

### Task 1.6: Verify existing tests still green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full suite — every test must still pass.
- [ ] Update the `RaceConfig` roundtrip test if it exists to exercise the new fields.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
