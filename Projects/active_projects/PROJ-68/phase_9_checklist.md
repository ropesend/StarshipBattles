# Phase 9: Initial Population Seeding

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Seed starting colonies with initial population during game initialization. Update quickstart builder.

**Depends on:** Phase 1 (SpeciesPopulation on Planet, race_config on Empire), Phase 3 (population engine must be present to grow seeded populations)

---

## Tasks

### Task 9.1: Game Session Seeding [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_seeding.py`

- [ ] In `_setup_initial_scenario()` (or wherever home colonies are assigned), after `empire.add_colony(home_planet)`:
  - Create `SpeciesPopulation(race_id=empire.race_config.race_id, count=10000, happiness=0.7)`
  - Append to `home_planet.populations`
  - 10,000 units = 10 million people (reasonable starting colony)

**Notes:**

---

### Task 9.2: Quickstart Builder [Simple]
**File:** `game/strategy/quickstart_builder.py`

- [ ] Ensure test race configs are loaded and passed through `PlayerConfig.race_config`
- [ ] Verify quickstart games seed population correctly

**Notes:**

---

### Task 9.3: Tests [Simple]
**New file:** `tests/unit/strategy/engine/test_population_seeding.py`

- [ ] `test_home_colony_has_initial_population`
- [ ] `test_initial_population_correct_race_id`
- [ ] `test_initial_happiness_is_positive`
- [ ] `test_no_race_config_no_population_seeded`
- [ ] `test_quickstart_has_population`
- [ ] Verify: `pytest tests/unit/strategy/engine/test_population_seeding.py -v` — all pass
- [ ] Verify: `pytest tests/ -n 12` — full suite passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass
- [ ] Full suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete"
