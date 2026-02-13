# Phase 2: Ship Stat Aggregation Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract stat aggregation methods from Ship into `ship_stat_querier.py`. Ship retains facade methods that delegate to the querier. Target: ~80 lines of logic moved, Ship reduced by ~60 lines net (facades remain).

**File:** `game/simulation/entities/ship.py`
**New File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ tests/unit/combat/ -n 12`

---

## Tasks

### Task 2.1: Create ShipStatQuerier Class [Medium]
**File:** `game/simulation/entities/ship_stat_querier.py`
- [x] Create `ship_stat_querier.py` in `game/simulation/entities/`
- [x] Define `ShipStatQuerier` class that takes a ship reference in `__init__`
- [x] Move `get_ability_total()` logic (ship.py lines 612-621): uses `get_all_components()` and `stats_calculator.calculate_ability_totals()`
- [x] Move `get_total_ability_value()` logic (ship.py lines 623-641): iterates components, sums `ab.get_primary_value()`
- [x] Move `get_total_ecm_score()` logic (ship.py lines 653-661): wraps `get_ability_total('ToHitDefenseModifier')`
- [x] Move `get_total_sensor_score()` logic (ship.py lines 643-651): wraps `get_ability_total('ToHitAttackModifier')`
- [x] Move `max_weapon_range` logic (ship.py lines 240-261): iterates components for weapon range calculation (includes late import of WeaponAbility/SeekerWeaponAbility)
- [x] Move `cached_summary` property logic (ship.py lines 518-521): return `self._ship._cached_summary`
- [x] Add type hints and docstrings to all methods
- [x] Add `__all__` export

**Notes:** The querier needs access to `ship.get_all_components()`, `ship.stats_calculator`, and `ship._registries`. These are accessed via the ship reference passed at construction.

---

### Task 2.2: Write Tests for ShipStatQuerier [Medium]
**File:** `tests/unit/entities/test_ship_stat_querier.py`
- [x] Create test file `tests/unit/entities/test_ship_stat_querier.py`
- [x] Test `get_ability_total()` returns correct totals (use a ship with known components)
- [x] Test `get_total_ability_value()` with operational_only=True and False
- [x] Test `get_total_ecm_score()` returns float
- [x] Test `get_total_sensor_score()` returns float
- [x] Test `max_weapon_range` returns correct range for weapon-equipped ship
- [x] Test `max_weapon_range` returns 0.0 for ship with no weapons
- [x] Test `cached_summary` returns the ship's cached summary dict
- [x] Run tests: `pytest tests/unit/entities/test_ship_stat_querier.py -v`

**Notes:** 15 tests written and passing.

---

### Task 2.3: Wire Ship Facade Methods [Simple]
**File:** `game/simulation/entities/ship.py`
- [x] Add lazy `_stat_querier` property to Ship (creates ShipStatQuerier on first access)
- [x] Replace `get_ability_total()` body with `return self._stat_querier.get_ability_total(ability_name)`
- [x] Replace `get_total_ability_value()` body with `return self._stat_querier.get_total_ability_value(ability_name, operational_only)`
- [x] Replace `get_total_ecm_score()` body with `return self._stat_querier.get_total_ecm_score()`
- [x] Replace `get_total_sensor_score()` body with `return self._stat_querier.get_total_sensor_score()`
- [x] Replace `max_weapon_range` property body with `return self._stat_querier.max_weapon_range`
- [x] Replace `cached_summary` property body with `return self._cached_summary` (keep as-is, it's already 1 line)
- [x] Remove `_format_ability_name()` helper if no longer used (ship.py line 607-610)

**Notes:** `cached_summary` left as-is (already 1-liner). `_format_ability_name` removed (unused). Lazy `stat_querier` property added.

---

### Task 2.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Confirm all tests pass with zero new failures
- [x] Verify Ship importers (136 files) are unaffected -- no import changes needed
- [x] Record test count: 7503 passed, 0 failed

**Notes:** Ship.py reduced from 870 to 812 lines (-58 lines). ShipStatQuerier is 149 lines. All existing tests pass unchanged.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
