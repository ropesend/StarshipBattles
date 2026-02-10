# Phase 2: Ship Stat Aggregation Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract stat aggregation methods from Ship into `ship_stat_querier.py`. Ship retains facade methods that delegate to the querier. Target: ~80 lines of logic moved, Ship reduced by ~60 lines net (facades remain).

**File:** `game/simulation/entities/ship.py`
**New File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ tests/unit/combat/ -n 12`

---

## Tasks

### Task 2.1: Create ShipStatQuerier Class [Medium]
**File:** `game/simulation/entities/ship_stat_querier.py`
- [ ] Create `ship_stat_querier.py` in `game/simulation/entities/`
- [ ] Define `ShipStatQuerier` class that takes a ship reference in `__init__`
- [ ] Move `get_ability_total()` logic (ship.py lines 612-621): uses `get_all_components()` and `stats_calculator.calculate_ability_totals()`
- [ ] Move `get_total_ability_value()` logic (ship.py lines 623-641): iterates components, sums `ab.get_primary_value()`
- [ ] Move `get_total_ecm_score()` logic (ship.py lines 653-661): wraps `get_ability_total('ToHitDefenseModifier')`
- [ ] Move `get_total_sensor_score()` logic (ship.py lines 643-651): wraps `get_ability_total('ToHitAttackModifier')`
- [ ] Move `max_weapon_range` logic (ship.py lines 240-261): iterates components for weapon range calculation (includes late import of WeaponAbility/SeekerWeaponAbility)
- [ ] Move `cached_summary` property logic (ship.py lines 518-521): return `self._ship._cached_summary`
- [ ] Add type hints and docstrings to all methods
- [ ] Add `__all__` export

**Notes:** The querier needs access to `ship.get_all_components()`, `ship.stats_calculator`, and `ship._registries`. These are accessed via the ship reference passed at construction.

---

### Task 2.2: Write Tests for ShipStatQuerier [Medium]
**File:** `tests/unit/entities/test_ship_stat_querier.py`
- [ ] Create test file `tests/unit/entities/test_ship_stat_querier.py`
- [ ] Test `get_ability_total()` returns correct totals (use a ship with known components)
- [ ] Test `get_total_ability_value()` with operational_only=True and False
- [ ] Test `get_total_ecm_score()` returns float
- [ ] Test `get_total_sensor_score()` returns float
- [ ] Test `max_weapon_range` returns correct range for weapon-equipped ship
- [ ] Test `max_weapon_range` returns 0.0 for ship with no weapons
- [ ] Test `cached_summary` returns the ship's cached summary dict
- [ ] Run tests: `pytest tests/unit/entities/test_ship_stat_querier.py -v`

**Notes:**

---

### Task 2.3: Wire Ship Facade Methods [Simple]
**File:** `game/simulation/entities/ship.py`
- [ ] Add lazy `_stat_querier` property to Ship (creates ShipStatQuerier on first access)
- [ ] Replace `get_ability_total()` body with `return self._stat_querier.get_ability_total(ability_name)`
- [ ] Replace `get_total_ability_value()` body with `return self._stat_querier.get_total_ability_value(ability_name, operational_only)`
- [ ] Replace `get_total_ecm_score()` body with `return self._stat_querier.get_total_ecm_score()`
- [ ] Replace `get_total_sensor_score()` body with `return self._stat_querier.get_total_sensor_score()`
- [ ] Replace `max_weapon_range` property body with `return self._stat_querier.max_weapon_range`
- [ ] Replace `cached_summary` property body with `return self._cached_summary` (keep as-is, it's already 1 line)
- [ ] Remove `_format_ability_name()` helper if no longer used (ship.py line 607-610)

**Notes:** `cached_summary` is already a one-liner returning `self._cached_summary`. Consider whether it's worth delegating or just leaving it. The `_format_ability_name` method (line 607) appears unused -- verify with grep before removing.

---

### Task 2.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Confirm all tests pass with zero new failures
- [ ] Verify Ship importers (136 files) are unaffected -- no import changes needed
- [ ] Record test count: _____ passed, _____ failed

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
