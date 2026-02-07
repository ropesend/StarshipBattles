# Phase 8: UI Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Display population in planet reports, add population to DTOs, show cargo in fleet info, add TRANSFER order display.

**Depends on:** Phase 1 (population data on Planet), Phase 5 (cargo on ships)

---

## Tasks

### Task 8.1: DTO Updates [Simple]
**File:** `game/strategy/facade/dto/planet_dto.py`
**File:** `game/strategy/facade/dto/empire_dto.py`
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_population_dtos.py`

- [ ] Add to `PlanetInfo`: `total_population: int = 0`, `max_population: int = 0`, `population_details: tuple = ()` (each: race_id, count, happiness)
- [ ] Update `PlanetInfo.from_planet()` to populate new fields
- [ ] Add `total_population: int = 0` to `ColonySummary`
- [ ] Update `ColonySummary` factory method
- [ ] Add cargo summary fields to ship/fleet DTOs

**Notes:**

---

### Task 8.2: Planet Info Formatter [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`

- [ ] Update `format_planet_info()` to show population section for colonized planets:
  - Total population with max capacity
  - Per-species breakdown (race name, count, happiness indicator)

**Notes:**

---

### Task 8.3: Fleet Orders Window [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`

- [ ] Add TRANSFER order type display in order description formatting

**Notes:**

---

### Task 8.4: Tests [Simple]
**New file:** `tests/unit/strategy/facade/test_population_dtos.py`

- [ ] `test_planet_info_includes_population`
- [ ] `test_colony_summary_includes_population`
- [ ] `test_format_planet_info_shows_population`
- [ ] Verify: `pytest tests/unit/strategy/facade/test_population_dtos.py -v` — all pass
- [ ] Verify: `pytest tests/unit/ui/ -v` — no UI regressions
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
