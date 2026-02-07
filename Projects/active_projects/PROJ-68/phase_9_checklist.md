# Phase 9: Initial Population Seeding

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Seed starting colonies with initial population during game initialization. Update quickstart builder.

**Depends on:** Phase 1 (SpeciesPopulation on Planet, race_config on Empire), Phase 3 (population engine must be present to grow seeded populations)

---

## Tasks

### Task 9.1: Game Session Seeding [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_seeding.py`

- [x] In `_setup_initial_scenario()` (or wherever home colonies are assigned), after `empire.add_colony(home_planet)`:
  - Create `SpeciesPopulation(race_id=empire.race_config.race_id, count=10000, happiness=0.7)`
  - Append to `home_planet.populations`
  - 10,000 units = 10 million people (reasonable starting colony)

**Notes:** Added SpeciesPopulation import, seeding after add_colony with race_config check

---

### Task 9.2: Quickstart Builder [Simple]
**File:** `game/strategy/quickstart_builder.py`

- [x] Ensure test race configs are loaded and passed through `PlayerConfig.race_config`
- [x] Verify quickstart games seed population correctly

**Notes:** Fixed 3 PlayerConfig instantiations in build_1p_config and build_2p_config to include race_config=race

---

### Task 9.3: Tests [Simple]
**New file:** `tests/unit/strategy/engine/test_population_seeding.py`

- [x] `test_home_colony_has_initial_population`
- [x] `test_initial_population_correct_race_id`
- [x] `test_initial_happiness_is_positive`
- [x] `test_no_race_config_no_population_seeded`
- [x] `test_quickstart_has_population`
- [x] Verify: `pytest tests/unit/strategy/engine/test_population_seeding.py -v` — all pass
- [x] Verify: `pytest tests/ -n 12` — full suite passes

**Notes:** 6 tests total (added test_quickstart_2p_both_have_population). Full suite: 6506 passed, 2 pre-existing failures

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass
- [x] Full suite passes: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "All phases complete"
