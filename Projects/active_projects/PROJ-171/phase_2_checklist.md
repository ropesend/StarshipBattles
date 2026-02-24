# Phase 2: Galaxy Core (Galaxy, StarSystem, WarpPoint)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 2`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/galaxy/ -v`

## Task 2.1: Validate WarpPoint.from_dict() [Simple]
**File:** `game/strategy/data/galaxy.py:35-41`
**Tests:** `pytest tests/unit/strategy/galaxy/test_warp_point_validation.py`

- [ ] Add import for `require_keys` from `game.core.validation_helpers`
- [ ] Add import for `PersistenceException` from `game.core.exceptions`
- [ ] Add `require_keys(data, ['destination_id', 'location'], 'WarpPoint')` at start of from_dict
- [ ] Wrap `hex_from_dict(data['location'])` in try/except, convert to PersistenceException
- [ ] Create test file `tests/unit/strategy/galaxy/test_warp_point_validation.py`
- [ ] Test: valid data → WarpPoint created successfully
- [ ] Test: missing 'destination_id' → PersistenceException with 'WarpPoint' in message
- [ ] Test: missing 'location' → PersistenceException
- [ ] Test: malformed location (e.g. `{'q': 1}` missing 'r') → PersistenceException

**Notes:**

## Task 2.2: Validate StarSystem.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:77-93`
**Tests:** `pytest tests/unit/strategy/galaxy/test_star_system_validation.py`

- [ ] Add `require_keys(data, ['name', 'global_location'], 'StarSystem')` at start of from_dict
- [ ] Wrap each `Star.from_dict(s)` call in try/except — on failure, log warning and skip star
- [ ] Wrap each `WarpPoint.from_dict(wp)` call — on failure, log warning and skip
- [ ] Wrap each `Planet.from_dict(p)` call — on failure, log warning and skip
- [ ] Create test file `tests/unit/strategy/galaxy/test_star_system_validation.py`
- [ ] Test: valid data → StarSystem created with all children
- [ ] Test: missing 'name' → PersistenceException mentioning 'StarSystem'
- [ ] Test: missing 'global_location' → PersistenceException
- [ ] Test: one bad star in list → system loads, bad star skipped
- [ ] Test: one bad planet in list → system loads, bad planet skipped
- [ ] Test: empty children lists → system loads with empty lists

**Notes:** Decision: skip bad children with logging (resilient degradation).

## Task 2.3: Validate Galaxy.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:879-928`
**Tests:** `pytest tests/unit/strategy/galaxy/test_galaxy_validation.py`

- [ ] Add `require_keys(data, ['radius'], 'Galaxy')` at start
- [ ] Add `validate_positive(data['radius'], 'radius', 'Galaxy')` after require_keys
- [ ] Wrap each system entry deserialization — validate 'coord' and 'system' keys exist
- [ ] If one system fails, log warning and skip (don't lose entire galaxy)
- [ ] Create test file `tests/unit/strategy/galaxy/test_galaxy_validation.py`
- [ ] Test: valid data → Galaxy created
- [ ] Test: missing 'radius' → PersistenceException
- [ ] Test: radius <= 0 → PersistenceException
- [ ] Test: system entry missing 'coord' → system skipped with warning
- [ ] Test: one bad system → galaxy loads without it

**Notes:** Galaxy.from_dict() rebuilds indexes after deserialization. Validation runs before indexing.

## Phase 2 Completion
- [ ] All tasks above checked
- [ ] `pytest tests/unit/strategy/galaxy/ -v` — all pass
- [ ] Existing serialization tests still pass: `pytest tests/ -k "galaxy or star_system" --testmon`
- [ ] `pytest tests/ --testmon` — no regressions
