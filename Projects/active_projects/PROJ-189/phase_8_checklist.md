# Phase 8: Integration Testing & Balance

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full integration testing across all storm systems and gameplay balance tuning.

---

## Tasks

### Task 8.1: Galaxy generation integration test [Simple]
**File:** `tests/integration/strategy/test_galaxy_generation_storms.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_galaxy_generation_storms.py`

- [ ] Write test: generate full galaxy, verify storms exist in at least some systems
- [ ] Write test: storm counts per system match blueprint constraints
- [ ] Write test: no storm hexes overlap star occupied hexes
- [ ] Write test: all storms are registered as zones (queryable via `galaxy.get_zones_at_global_hex()`)
- [ ] Write test: storm serialization/deserialization round-trip for full galaxy (to_dict/from_dict)

**Notes:**

### Task 8.2: Turn processing integration test [Simple]
**File:** `tests/integration/strategy/test_turn_storms.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_turn_storms.py`

- [ ] Write test: create galaxy with a fleet in a storm hex, process full turn (100 ticks):
  - Verify fleet took environmental damage (ship component HP reduced)
  - Verify fleet fuel drained
  - Verify environmental events were recorded
- [ ] Write test: fleet movement speed reduced in storm hex
  - Fleet in storm with strategic_mult=0.5 takes more ticks to move
- [ ] Write test: fleet outside storm takes no damage and has normal speed

**Notes:**

### Task 8.3: Balance tuning [Simple]
**File:** `data/storms.json`
**Tests:** Manual playtesting

- [ ] Verify no storm type is immediately lethal:
  - `damage_per_tick * 1 turn` should not destroy a healthy ship
  - Calculate: damage_per_tick is applied across 100 ticks, so total damage/turn = damage_per_tick
  - Compare against typical ship HP values
- [ ] Verify `strategic_mult` never goes below 0.2 (always possible to escape)
  - Even with overlapping storms: 0.4 * 0.5 = 0.2 minimum
- [ ] Verify fuel drain is survivable:
  - Fuel drain per turn should not strand a healthy fleet in a single turn
  - Compare against typical fleet fuel reserves
- [ ] Adjust values in storms.json if balance is off
- [ ] Run all tests after any balance changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/ -n 12` (full suite, not testmon)
- [ ] Manual playtesting: storms appear, effects work, game is fun
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
