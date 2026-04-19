# Phase 4: HappinessEngine + PopulationEngine read aggregated ratio

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify — through tests only, zero source changes — that `HappinessEngine` and `PopulationEngine` read `cfg.last_food_ratio` (now a computed MIN property) and behave identically to PROJ-284 for equivalent aggregate ratios. This phase is the verification seam.

---

## Tasks

### Task 4.1: Equivalence tests — single-resource config matches PROJ-284 behavior [Medium]
**File:** `tests/unit/strategy/engine/test_happiness_engine.py` + `test_population_engine.py` (may add new tests)
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/engine/test_population_engine.py`

- [ ] Add parity test to HappinessEngine tests: construct two identical scenarios — one with `cfg.last_consumption_ratios = {"organics": 0.5}`, one with dict containing exactly one resource at 0.5. Assert happiness matches for both. (Trivially true via the property; the test pins the contract.)
- [ ] Add parity test to PopulationEngine tests: same pattern. Assert `_grow_species` output matches for both.

**Notes:** If time-pressed, 4.1 can be rolled into 4.2 since it's exercising the same MIN-aggregation property.

### Task 4.2: Multi-resource starvation tests — new PROJ-286 behavior [Medium]
**File:** new class `TestMultiResourceStarvation` in `test_happiness_engine.py` and `test_population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/engine/test_population_engine.py`

- [ ] HappinessEngine: seed `cfg.last_consumption_ratios = {"organics": 1.0, "metals": 0.0}`. Assert happiness == 0 (min=0 collapses the formula).
- [ ] HappinessEngine: seed `{"organics": 0.5, "metals": 0.8, "radioactives": 1.0}`. Assert happiness == `base * 0.5 * habitability` (min=0.5).
- [ ] PopulationEngine: seed `cfg.last_consumption_ratios = {"organics": 1.0, "metals": 0.0}`. Assert `_grow_species` applies full decline_term (min=0 → decline_rate * pop).
- [ ] PopulationEngine: seed `{"organics": 0.5, "metals": 1.0}`. Assert decline_term applies at 0.5 ratio.

**Notes:**

### Task 4.3: Full Happiness + Population suites green [Simple]
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/engine/test_population_engine.py`

- [ ] All 12 HappinessEngine tests green.
- [ ] All 19 PopulationEngine tests green (6 `TestFoodRatioAndDecline` + legacy + new parity + new multi-resource).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 5: docs + cleanup)
