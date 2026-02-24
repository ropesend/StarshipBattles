# Phase 4: Empire & Fleet (Empire, Fleet, ShipInstance)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 4`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/fleet/ tests/unit/strategy/empire/ -v`

## Task 4.1: Validate ShipInstance.from_dict() [Simple]
**File:** `game/strategy/data/ship_instance.py:632-652`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`

- [x] Add import for `require_keys` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['instance_id', 'design_id', 'name', 'owner_id'], 'ShipInstance')` at start
- [x] Create test file `tests/unit/strategy/ship_instance/test_validation.py`
- [x] Test: valid data → ShipInstance created
- [x] Test: missing 'instance_id' → PersistenceException
- [x] Test: missing 'design_id' → PersistenceException
- [x] Test: missing 'name' → PersistenceException
- [x] Test: missing 'owner_id' → PersistenceException
- [x] Verify existing tests still pass: `pytest tests/unit/strategy/ship_instance/test_serialization.py -v`

**Notes:** 7 tests written. All passed.

## Task 4.2: Validate Fleet.from_dict() [Complex]
**File:** `game/strategy/data/fleet.py:343-417`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_validation.py`

- [x] Add imports for `require_keys`, `validate_enum` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['id', 'owner_id'], 'Fleet')` at start
- [x] Wrap `OrderType[order_data['type']]` (around line 384) with `validate_enum(order_data['type'], OrderType, 'type', f'Fleet order')`
- [x] Wrap each `ShipInstance.from_dict(ship_data)` in try/except — skip bad ships with warning log
- [x] Wrap order restoration loop body in try/except per order — skip bad orders with warning log
- [x] Create test file `tests/unit/strategy/fleet/test_fleet_validation.py`
- [x] Test: valid data → Fleet created with ships and orders
- [x] Test: missing 'id' → PersistenceException
- [x] Test: missing 'owner_id' → PersistenceException
- [x] Test: invalid OrderType → PersistenceException with valid values
- [x] Test: bad ship in ships list → ship skipped, fleet loads with remaining ships
- [x] Test: bad order in orders list → order skipped, fleet loads with remaining orders
- [x] Verify existing tests still pass: `pytest tests/unit/strategy/fleet/test_serialization.py -v`

**Notes:** 10 tests written. All passed. Added logger for skip warnings.

## Task 4.3: Validate Empire.from_dict() [Medium]
**File:** `game/strategy/data/empire.py:168-225`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`

- [x] Add imports for `require_keys`, `safe_from_dict` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['id', 'name', 'color'], 'Empire')` at start
- [x] Wrap `RaceConfig.from_dict(data['race_config'])` with safe_from_dict or try/except with context
- [x] Wrap each `Fleet.from_dict(f)` in try/except — skip bad fleets with warning log
- [x] Create test file `tests/unit/strategy/empire/test_empire_validation.py`
- [x] Test: valid data → Empire created
- [x] Test: missing 'id' → PersistenceException
- [x] Test: missing 'name' → PersistenceException
- [x] Test: missing 'color' → PersistenceException
- [x] Test: bad fleet in list → fleet skipped, empire loads with remaining fleets
- [x] Test: race_config loads with defaults (RaceConfig.from_dict is fully defensive)

**Notes:** 10 tests written. RaceConfig.from_dict uses .get() for ALL fields so doesn't raise on missing data. Test adjusted to reflect actual behavior.

## Phase 4 Completion
- [x] All tasks above checked
- [x] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/fleet/ tests/unit/strategy/empire/ -v` — 200 passed
- [x] Existing serialization tests still pass
- [x] `pytest tests/ -n 12` — 12109 passed, 1 skipped (no regressions)
