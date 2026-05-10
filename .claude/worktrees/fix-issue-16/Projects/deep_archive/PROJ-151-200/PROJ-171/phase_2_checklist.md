# Phase 2: Galaxy Core (Galaxy, StarSystem, WarpPoint)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 2`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/strategy/galaxy/ -v`

## Task 2.1: Validate WarpPoint.from_dict() [Simple]
**File:** `game/strategy/data/galaxy.py:35-41`
**Tests:** `pytest tests/unit/strategy/galaxy/test_warp_point_validation.py`

- [x] Add import for `require_keys` from `game.core.validation_helpers`
- [x] Add import for `PersistenceException` from `game.core.exceptions`
- [x] Add `require_keys(data, ['destination_id', 'location'], 'WarpPoint')` at start of from_dict
- [x] Wrap `hex_from_dict(data['location'])` in try/except, convert to PersistenceException
- [x] Create test file `tests/unit/strategy/galaxy/test_warp_point_validation.py`
- [x] Test: valid data → WarpPoint created successfully
- [x] Test: missing 'destination_id' → PersistenceException with 'WarpPoint' in message
- [x] Test: missing 'location' → PersistenceException
- [x] Test: malformed location (e.g. `{'q': 1}` missing 'r') → PersistenceException

**Notes:** Complete - 5 tests

## Task 2.2: Validate StarSystem.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:77-93`
**Tests:** `pytest tests/unit/strategy/galaxy/test_star_system_validation.py`

- [x] Add `require_keys(data, ['name', 'global_location'], 'StarSystem')` at start of from_dict
- [x] Wrap each `Star.from_dict(s)` call in try/except — on failure, log warning and skip star
- [x] Wrap each `WarpPoint.from_dict(wp)` call — on failure, log warning and skip
- [x] Wrap each `Planet.from_dict(p)` call — on failure, log warning and skip
- [x] Create test file `tests/unit/strategy/galaxy/test_star_system_validation.py`
- [x] Test: valid data → StarSystem created with all children
- [x] Test: missing 'name' → PersistenceException mentioning 'StarSystem'
- [x] Test: missing 'global_location' → PersistenceException
- [x] Test: one bad star in list → system loads, bad star skipped
- [x] Test: one bad planet in list → system loads, bad planet skipped
- [x] Test: empty children lists → system loads with empty lists

**Notes:** Complete - 8 tests. Resilient degradation with warning logs.

## Task 2.3: Validate Galaxy.from_dict() [Medium]
**File:** `game/strategy/data/galaxy.py:879-928`
**Tests:** `pytest tests/unit/strategy/galaxy/test_galaxy_validation.py`

- [x] Add `require_keys(data, ['radius'], 'Galaxy')` at start
- [x] Add `validate_positive(data['radius'], 'radius', 'Galaxy')` after require_keys
- [x] Wrap each system entry deserialization — validate 'coord' and 'system' keys exist
- [x] If one system fails, log warning and skip (don't lose entire galaxy)
- [x] Create test file `tests/unit/strategy/galaxy/test_galaxy_validation.py`
- [x] Test: valid data → Galaxy created
- [x] Test: missing 'radius' → PersistenceException
- [x] Test: radius <= 0 → PersistenceException
- [x] Test: system entry missing 'coord' → system skipped with warning
- [x] Test: one bad system → galaxy loads without it

**Notes:** Complete - 9 tests. Validation runs before indexing.

## Phase 2 Completion
- [x] All tasks above checked
- [x] `pytest tests/unit/strategy/galaxy/ -v` — 22 passed
- [x] Existing serialization tests still pass
- [x] Full suite: 12015 passed, 1 skipped
