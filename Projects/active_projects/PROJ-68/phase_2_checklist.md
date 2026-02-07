# Phase 2: Habitability Scoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Pure function that scores planet-race compatibility (0.0-1.0). Uses existing Planet surface properties + RaceConfig tolerance fields.

**Depends on:** Phase 1 (uses RaceConfig fields and Planet properties)

---

## Tasks

### Task 2.1: Habitability Module [Medium]
**New file:** `game/strategy/formulas/habitability.py`
**New file:** `game/strategy/formulas/__init__.py` (if dir doesn't exist)
**Tests:** `pytest tests/unit/strategy/formulas/test_habitability.py`

- [ ] Create `game/strategy/formulas/` directory with `__init__.py`
- [ ] Create `calculate_habitability()` function with individual parameters:
  - **Gravity factor:** 1.0 when within tolerance of ideal, linear falloff to 0.0 outside. Planet gravity in m/s², convert race ideal from g (x9.81)
  - **Temperature factor:** Same linear falloff pattern
  - **Water factor:** Same linear falloff pattern
  - **Atmosphere factor:** Score based on how well planet atmosphere matches race preferences. Beneficial gases boost, toxic gases penalize. Normalize to 0.0-1.0
  - **Radiation factor:** magnetic_field provides shielding. Species with high radiation_tolerance can survive low-field planets
  - **Final score:** Weighted geometric mean (any zero factor -> near-zero result)
- [ ] Create `score_planet_for_race(planet, race_config) -> float` convenience wrapper

**Notes:**

---

### Task 2.2: Tests [Simple]
**New file:** `tests/unit/strategy/formulas/test_habitability.py`

- [ ] `test_perfect_match_returns_near_1` — homeworld conditions match ideal
- [ ] `test_completely_incompatible_returns_near_0` — extreme mismatch (magma planet for ice species)
- [ ] `test_gravity_outside_tolerance_reduces_score`
- [ ] `test_temperature_outside_tolerance_reduces_score`
- [ ] `test_water_outside_tolerance_reduces_score`
- [ ] `test_toxic_atmosphere_reduces_score` — negative preference gas at high pressure
- [ ] `test_beneficial_atmosphere_boosts_score`
- [ ] `test_low_magnetic_field_penalizes_sensitive_species`
- [ ] `test_score_planet_for_race_convenience` — integration with real objects
- [ ] Verify: `pytest tests/unit/strategy/formulas/test_habitability.py -v` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/formulas/test_habitability.py -v`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
