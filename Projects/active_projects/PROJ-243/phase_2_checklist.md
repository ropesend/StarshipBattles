# Phase 2 Checklist: Extract `_initialize_ship()` Helper and Add `register_ship()`
**Status:** Complete

## Task 2.1: Write failing tests for `_initialize_ship()` [Medium]
**File:** `tests/unit/simulation/systems/test_battle_engine_init_ship.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py -v`
- [x] Create test file `tests/unit/simulation/systems/test_battle_engine_init_ship.py`
- [x] Write test: `_initialize_ship(ship)` wires `ship.combat_engine._event_bus` to `self.combat_events`
- [x] Write test: `_initialize_ship(ship)` calls `comp.update()` for all active components
- [x] Write test: `_initialize_ship(ship)` calls `ship.recalculate_stats()`
- [x] Write test: `_initialize_ship(ship)` calls `ship.update_derelict_status()`
- [x] Run tests -- confirm they fail (`_initialize_ship` does not exist yet)
**Notes:** All 4 tests failed with AttributeError as expected.

## Task 2.2: Extract `_initialize_ship()` from `start()` [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [x] Add new method after `_log_initial_status()`:
- [x] Replace the two separate for-loops in `start()` with a single loop calling `_initialize_ship()`:
- [x] Run new tests from Task 2.1 -- confirm they pass
- [x] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** Collapsed two for-loops (event bus wiring + component update/stats/derelict) into one loop calling _initialize_ship(). 374 tests pass (systems + battle_controller).

## Task 2.3: Write failing test for `FleetAuraManager.register_ship()` [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_register.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_register.py -v`
- [x] Create test file `tests/unit/simulation/combat/test_fleet_aura_register.py`
- [x] Write test: `register_ship(ship, all_ships)` calls `_scan_ship(ship)` (new ship's abilities scanned)
- [x] Write test: `register_ship(ship, all_ships)` calls `_recalculate(all_ships)` (bonuses updated)
- [x] Write test: after `register_ship()`, the new ship has correct `fleet_attack_bonus`
- [x] Write test: after `register_ship()`, existing ships receive bonuses from the new ship's fleet-scope abilities
- [x] Run tests -- confirm they fail (`register_ship` does not exist yet)
**Notes:** All 5 tests failed with AttributeError. Added extra test for dead ship not being scanned.

## Task 2.4: Add `register_ship()` to FleetAuraManager [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_register.py -v`
- [x] Add new method after `_scan_ship()`:
- [x] Run new tests from Task 2.3 -- confirm they pass
- [x] Run existing aura tests (if any): `pytest tests/unit/simulation/combat/ -v`
**Notes:** All 5 new tests pass, all 173 combat tests pass (0 regressions).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
