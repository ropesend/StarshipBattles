# Phase 3: Population Growth Engine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** PopulationEngine class using DI pattern. Processes logistic growth for all species on all colonies per turn. Integrates into TurnEngine.

**Depends on:** Phase 1 (populations on Planet, race_config on Empire), Phase 2 (habitability scoring)

---

## Tasks

### Task 3.1: IPopulationEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py` (after `IResourceEngine`, line 262)

- [ ] Add `IPopulationEngine(ABC)` with abstract `process_population_growth(empires)` method
- [ ] Add to `__all__` list

**Notes:**

---

### Task 3.2: PopulationEngine Implementation [Medium]
**New file:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [ ] `PopulationEngine(IPopulationEngine)` class
- [ ] `process_population_growth(empires)` — iterate empires -> colonies -> populations
- [ ] `_grow_species(pop, colony, race_config)` — single species growth:
  - Lookup habitability via `score_planet_for_race(colony, race_config)`
  - Calculate effective carrying capacity: `max_population * habitability`
  - **Logistic formula:** `growth = r * P * (1 - P/K) * happiness_modifier`
  - `r` derived from `aptitude_population_growth`: scale 1->0.5%, 5->2.5%, 10->5.0%
  - Apply growth (can be negative if P > K due to changing conditions)
  - Clamp count to >= 0
- [ ] `_get_race_config(race_id, empire)` — lookup race config (empire's own or future multi-race registry)
- [ ] `_aptitude_to_growth_rate(aptitude: int) -> float` — static conversion

**Notes:**

---

### Task 3.3: TurnEngine Integration [Simple]
**File:** `game/strategy/engine/turn_engine.py`

- [ ] Add `population_engine: Optional['IPopulationEngine'] = None` to `__init__` kwargs (line 92)
- [ ] Store `self._population_engine = population_engine` (line 134)
- [ ] Add lazy property `population_engine` (after `resource_engine` property, line 178)
- [ ] Call `self.population_engine.process_population_growth(empires)` in `process_turn()` after production (line 201)

**Notes:**

---

### Task 3.4: Tests [Medium]
**New file:** `tests/unit/strategy/engine/test_population_engine.py`

- [ ] `test_logistic_growth_basic` — single species, good habitability
- [ ] `test_growth_slows_near_capacity` — S-curve behavior verified
- [ ] `test_zero_population_no_growth` — empty colony stays empty
- [ ] `test_low_happiness_slows_growth`
- [ ] `test_low_habitability_reduces_carrying_capacity`
- [ ] `test_population_shrinks_above_carrying_capacity` — if conditions worsen
- [ ] `test_multiple_species_grow_independently`
- [ ] `test_high_aptitude_faster_growth`
- [ ] `test_turn_engine_calls_population_engine` — mock injection test
- [ ] Verify: `pytest tests/unit/strategy/engine/test_population_engine.py -v` — all pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/engine/test_population_engine.py -v`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
