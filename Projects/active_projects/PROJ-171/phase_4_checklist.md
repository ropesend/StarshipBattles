# Phase 4: Empire & Fleet (Empire, Fleet, ShipInstance)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 4`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/fleet/ tests/unit/strategy/empire/ -v`

## Task 4.1: Validate ShipInstance.from_dict() [Simple]
**File:** `game/strategy/data/ship_instance.py:632-652`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`

- [ ] Add import for `require_keys` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['instance_id', 'design_id', 'name', 'owner_id'], 'ShipInstance')` at start
- [ ] Create test file `tests/unit/strategy/ship_instance/test_validation.py`
- [ ] Test: valid data → ShipInstance created
- [ ] Test: missing 'instance_id' → PersistenceException
- [ ] Test: missing 'design_id' → PersistenceException
- [ ] Test: missing 'name' → PersistenceException
- [ ] Test: missing 'owner_id' → PersistenceException
- [ ] Verify existing tests still pass: `pytest tests/unit/strategy/ship_instance/test_serialization.py -v`

**Notes:** 4 required fields, rest have .get() defaults. Simplest method in this phase.

## Task 4.2: Validate Fleet.from_dict() [Complex]
**File:** `game/strategy/data/fleet.py:343-417`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_validation.py`

- [ ] Add imports for `require_keys`, `validate_enum` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['id', 'owner_id'], 'Fleet')` at start
- [ ] Wrap `OrderType[order_data['type']]` (around line 384) with `validate_enum(order_data['type'], OrderType, 'type', f'Fleet order')`
- [ ] Wrap each `ShipInstance.from_dict(ship_data)` in try/except — skip bad ships with warning log
- [ ] Wrap order restoration loop body in try/except per order — skip bad orders with warning log
- [ ] Create test file `tests/unit/strategy/fleet/test_fleet_validation.py`
- [ ] Test: valid data → Fleet created with ships and orders
- [ ] Test: missing 'id' → PersistenceException
- [ ] Test: missing 'owner_id' → PersistenceException
- [ ] Test: invalid OrderType → PersistenceException with valid values
- [ ] Test: bad ship in ships list → ship skipped, fleet loads with remaining ships
- [ ] Test: bad order in orders list → order skipped, fleet loads with remaining orders
- [ ] Verify existing tests still pass: `pytest tests/unit/strategy/fleet/test_serialization.py -v`

**Notes:** Fleet has complex order restoration with multiple format variants. Validate enum conversion; don't deep-validate every order variant.

## Task 4.3: Validate Empire.from_dict() [Medium]
**File:** `game/strategy/data/empire.py:168-225`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`

- [ ] Add imports for `require_keys`, `safe_from_dict` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['id', 'name', 'color'], 'Empire')` at start
- [ ] Wrap `RaceConfig.from_dict(data['race_config'])` with safe_from_dict or try/except with context
- [ ] Wrap each `Fleet.from_dict(f)` in try/except — skip bad fleets with warning log
- [ ] Create test file `tests/unit/strategy/empire/test_empire_validation.py`
- [ ] Test: valid data → Empire created
- [ ] Test: missing 'id' → PersistenceException
- [ ] Test: missing 'name' → PersistenceException
- [ ] Test: missing 'color' → PersistenceException
- [ ] Test: bad fleet in list → fleet skipped, empire loads with remaining fleets
- [ ] Test: corrupt race_config → PersistenceException with context

**Notes:** Empire already handles missing planets gracefully. Main gap is required field validation and fleet error isolation.

## Phase 4 Completion
- [ ] All tasks above checked
- [ ] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/fleet/ tests/unit/strategy/empire/ -v` — all pass
- [ ] Existing serialization tests still pass
- [ ] `pytest tests/ --testmon` — no regressions
