# Phase 7: Colonization Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update process_colonize() so founding population comes from ship passenger cargo. If no passengers, seed minimum founding population.

**Depends on:** Phase 1 (SpeciesPopulation), Phase 5 (cargo on ships)

---

## Tasks

### Task 7.1: Update Colonization Flow [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_population.py`

- [ ] In `process_colonize()`, after `empire.add_colony(final_planet)`:
  - Get passengers from colony ship (or fleet) cargo: `fleet.get_fleet_cargo_current('passengers')`
  - If passengers > 0: unload from fleet, create `SpeciesPopulation` on planet with that count
  - If no passengers and empire has race_config: seed minimum 100 units (100K people)
  - Set initial happiness to 0.5 (neutral)

**Notes:**

---

### Task 7.2: Tests [Simple]
**New file:** `tests/unit/strategy/engine/test_colonize_population.py`

- [ ] `test_colonize_transfers_passengers_to_colony`
- [ ] `test_colonize_without_passengers_seeds_minimum`
- [ ] `test_colonize_no_race_config_no_population`
- [ ] `test_colonize_passengers_unloaded_from_ships`
- [ ] `test_existing_colonize_tests_still_pass` — verify no regression
- [ ] Verify: `pytest tests/unit/strategy/engine/test_colonize_population.py -v` — all pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
