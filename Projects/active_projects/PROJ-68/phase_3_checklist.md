# Phase 3: Population Growth Engine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** PopulationEngine class using DI pattern. Processes logistic growth for all species on all colonies per turn. Integrates into TurnEngine.

**Depends on:** Phase 1 (populations on Planet, race_config on Empire), Phase 2 (habitability scoring)

---

## Tasks

### Task 3.1: IPopulationEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py` (after `IResourceEngine`, line 262)

- [x] Add `IPopulationEngine(ABC)` with abstract `process_population_growth(empires)` method
- [x] Add to `__all__` list

**Notes:** Added interface with docstring explaining logistic growth, habitability, and happiness modifiers.

---

### Task 3.2: PopulationEngine Implementation [Medium]
**New file:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [x] `PopulationEngine(IPopulationEngine)` class
- [x] `process_population_growth(empires)` — iterate empires -> colonies -> populations
- [x] `_grow_species(pop, colony, race_config)` — single species growth:
  - Lookup habitability via `score_planet_for_race(colony, race_config)`
  - Calculate effective carrying capacity: `max_population * habitability`
  - **Logistic formula:** `growth = r * P * (1 - P/K) * happiness_modifier`
  - `r` derived from `aptitude_population_growth`: scale 1->0.5%, 5->2.5%, 10->5.0%
  - Apply growth (can be negative if P > K due to changing conditions)
  - Clamp count to >= 0
- [x] `_get_race_config(race_id, empire)` — lookup race config (empire's own or future multi-race registry)
- [x] `_aptitude_to_growth_rate(aptitude: int) -> float` — static conversion

**Notes:** Implemented with clean DI pattern. Used score_planet_for_race from Phase 2.

---

### Task 3.3: TurnEngine Integration [Simple]
**File:** `game/strategy/engine/turn_engine.py`

- [x] Add `population_engine: Optional['IPopulationEngine'] = None` to `__init__` kwargs (line 92)
- [x] Store `self._population_engine = population_engine` (line 134)
- [x] Add lazy property `population_engine` (after `resource_engine` property, line 178)
- [x] Call `self.population_engine.process_population_growth(empires)` in `process_turn()` after production (line 201)

**Notes:** Added as Phase 5 in process_turn(), after fleet production. Uses lazy initialization pattern like other engines.

---

### Task 3.4: Tests [Medium]
**New file:** `tests/unit/strategy/engine/test_population_engine.py`

- [x] `test_logistic_growth_basic` — single species, good habitability
- [x] `test_growth_slows_near_capacity` — S-curve behavior verified
- [x] `test_zero_population_no_growth` — empty colony stays empty
- [x] `test_low_happiness_slows_growth`
- [x] `test_low_habitability_reduces_carrying_capacity`
- [x] `test_population_shrinks_above_carrying_capacity` — if conditions worsen
- [x] `test_multiple_species_grow_independently`
- [x] `test_high_aptitude_faster_growth`
- [x] `test_turn_engine_calls_population_engine` — mock injection test
- [x] Verify: `pytest tests/unit/strategy/engine/test_population_engine.py -v` — all pass
- [x] Verify: `pytest tests/ --testmon` — no regressions

**Notes:** 15 tests total. Added additional tests for aptitude conversion and edge cases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/engine/test_population_engine.py -v`
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
