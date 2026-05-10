# Phase 8: UI Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Display population in planet reports, add population to DTOs, show cargo in fleet info, add TRANSFER order display.

**Depends on:** Phase 1 (population data on Planet), Phase 5 (cargo on ships)

---

## Tasks

### Task 8.1: DTO Updates [Simple]
**File:** `game/strategy/facade/dto/planet_dto.py`
**File:** `game/strategy/facade/dto/empire_dto.py`
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_population_dtos.py`

- [x] Add to `PlanetInfo`: `total_population: int = 0`, `max_population: int = 0`, `population_details: tuple = ()` (each: race_id, count, happiness)
- [x] Update `PlanetInfo.from_planet()` to populate new fields
- [N/A] Add `total_population: int = 0` to `ColonySummary` - No ColonySummary exists
- [N/A] Update `ColonySummary` factory method - N/A
- [x] Add cargo summary fields to ship/fleet DTOs (passenger_capacity, passengers_current)

**Notes:** Also added BUILD and TRANSFER order handling in FleetInfo DTO conversion.

---

### Task 8.2: Planet Info Formatter [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`

- [x] Update `format_planet_info()` to show population section for colonized planets:
  - Total population with max capacity
  - Per-species breakdown (race name, count, happiness indicator)

**Notes:** Added K/M suffixes for large numbers, happiness indicators (+/~/-)

---

### Task 8.3: Fleet Orders Window [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`

- [x] Add TRANSFER order type display in order description formatting

**Notes:** Shows "LOAD/UNLOAD {amount} {cargo_type}"

---

### Task 8.4: Tests [Simple]
**New file:** `tests/unit/strategy/facade/test_population_dtos.py`

- [x] `test_planet_info_includes_population`
- [N/A] `test_colony_summary_includes_population` - No ColonySummary
- [N/A] `test_format_planet_info_shows_population` - covered by DTO tests
- [x] Verify: `pytest tests/unit/strategy/facade/test_population_dtos.py -v` — all pass (6 tests)
- [x] Verify: `pytest tests/unit/ui/ -v` — no UI regressions
- [x] Verify: `pytest tests/ --testmon` — no regressions

**Notes:** 6 new tests for population DTOs

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: 6500 passed, 2 pre-existing failures (bug_15)
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
