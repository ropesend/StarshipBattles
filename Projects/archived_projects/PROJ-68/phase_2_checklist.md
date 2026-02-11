# Phase 2: Habitability Scoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Pure function that scores planet-race compatibility (0.0-1.0). Uses existing Planet surface properties + RaceConfig tolerance fields.

**Depends on:** Phase 1 (uses RaceConfig fields and Planet properties)

---

## Tasks

### Task 2.1: Habitability Module [Medium]
**New file:** `game/strategy/formulas/habitability.py`
**New file:** `game/strategy/formulas/__init__.py` (if dir doesn't exist)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability.py`

- [x] Create `game/strategy/formulas/` directory with `__init__.py`
- [x] Create `calculate_habitability()` function with individual parameters:
  - **Gravity factor:** Gaussian falloff centered on ideal, with tolerance as sigma
  - **Temperature factor:** Same Gaussian falloff pattern
  - **Water factor:** Same Gaussian falloff pattern
  - **Atmosphere factor:** Weighted scoring based on gas fractions and preferences
  - **Radiation factor:** Linear falloff below field threshold based on tolerance
  - **Final score:** Weighted geometric mean (any zero factor -> near-zero result)
- [x] Create `score_planet_for_race(planet, race_config) -> float` convenience wrapper

**Notes:** Used Gaussian (exp(-0.5*(x/sigma)^2)) falloff for smoother curves than linear. Weighted geometric mean via log-sum for numerical stability.

---

### Task 2.2: Tests [Simple]
**New file:** `tests/unit/strategy/formulas/test_habitability.py`

- [x] `test_perfect_match_returns_near_1` — homeworld conditions match ideal
- [x] `test_completely_incompatible_returns_near_0` — extreme mismatch (magma planet for ice species)
- [x] `test_gravity_outside_tolerance_reduces_score`
- [x] `test_temperature_outside_tolerance_reduces_score`
- [x] `test_water_outside_tolerance_reduces_score`
- [x] `test_toxic_atmosphere_reduces_score` — negative preference gas at high pressure
- [x] `test_beneficial_atmosphere_boosts_score`
- [x] `test_low_magnetic_field_penalizes_sensitive_species`
- [x] `test_score_planet_for_race_convenience` — integration with real objects
- [x] Verify: `pytest tests/unit/strategy/formulas/test_habitability.py -v` — all pass

**Notes:** 34 tests total covering all factor functions + edge cases. All passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/formulas/test_habitability.py -v`
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
