# Phase 5: Simulation State (ShipState, ComponentState, Event, DesignMetadata)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 5`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/simulation/test_battle_state_validation.py tests/unit/strategy/events/ tests/unit/strategy/data/ -v`

## Task 5.1: Validate ComponentState.from_dict() [Simple]
**File:** `game/simulation/battle_state.py:50-59`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`

- [x] Add imports for `require_keys`, `validate_non_negative`, `validate_positive` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['component_id', 'current_hp', 'max_hp', 'is_active', 'layer'], 'ComponentState')` at start
- [x] Add `validate_non_negative(data['current_hp'], 'current_hp', 'ComponentState')`
- [x] Add `validate_positive(data['max_hp'], 'max_hp', 'ComponentState')`
- [x] Create test file `tests/unit/simulation/test_battle_state_validation.py` (or add to existing)
- [x] Test: valid data → ComponentState created
- [x] Test: missing 'component_id' → PersistenceException
- [x] Test: missing 'current_hp' → PersistenceException
- [x] Test: negative current_hp → PersistenceException
- [x] Test: zero max_hp → PersistenceException
- [x] Verify existing tests: `pytest tests/unit/simulation/test_battle_state_serialization.py -v`

**Notes:** 5 required fields. Simple leaf node. 11 tests added for ComponentState.

## Task 5.2: Validate ShipState.from_dict() [Medium]
**File:** `game/simulation/battle_state.py:146-174`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`

- [x] Add `require_keys(data, ['ship_id', 'name', 'ship_class', 'theme_id', 'team_id', 'color', 'ai_strategy', 'position', 'velocity', 'angle', 'current_hp', 'max_hp', 'current_shields', 'max_shields'], 'ShipState')` at start
- [x] Add validation for color format: check `isinstance(data['color'], (list, tuple))` and `len(data['color']) >= 3`
- [x] Add validation for position format: check `isinstance(data['position'], (list, tuple))` and `len(data['position']) >= 2`
- [x] Add validation for velocity format: same as position
- [x] Wrap nested ComponentState.from_dict() calls — skip bad components per layer with warning log
- [x] Test: valid data → ShipState created
- [x] Test: missing 'ship_id' → PersistenceException
- [x] Test: invalid color (not a list/tuple or too short) → PersistenceException
- [x] Test: bad component in a layer → component skipped, ship state loads
- [x] Verify existing tests: `pytest tests/unit/simulation/test_battle_state_serialization.py -v`

**Notes:** 14 required fields. Has tuple conversions that can fail with TypeError. 11 tests added for ShipState.

## Task 5.3: Validate Event.from_dict() [Simple]
**File:** `game/strategy/events/event_log.py:40-50`
**Tests:** `pytest tests/unit/strategy/events/test_event_validation.py`

- [x] Add import for `require_keys` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['event_type', 'category', 'turn', 'empire_id', 'message'], 'Event')` at start
- [x] Create test file `tests/unit/strategy/events/test_event_validation.py`
- [x] Test: valid data → Event created
- [x] Test: missing 'event_type' → PersistenceException
- [x] Test: missing 'turn' → PersistenceException

**Notes:** 5 required fields. Simple leaf node. 8 tests added.

## Task 5.4: Validate DesignMetadata.from_dict() [Simple]
**File:** `game/strategy/data/design_metadata.py:58-79`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata_validation.py`

- [x] Add import for `require_keys` from `game.core.validation_helpers`
- [x] Add `require_keys(data, ['design_id', 'name'], 'DesignMetadata')` at start
- [x] Create test file `tests/unit/strategy/data/test_design_metadata_validation.py`
- [x] Test: valid data → DesignMetadata created
- [x] Test: missing 'design_id' → PersistenceException
- [x] Test: missing 'name' → PersistenceException
- [x] Test: other fields missing → still works (all have .get() defaults)

**Notes:** Only 2 required fields. Rest already have .get() defaults. 9 tests added.

## Phase 5 Completion
- [x] All tasks above checked
- [x] All new validation tests pass (39 tests)
- [x] Existing battle state serialization tests still pass (55 tests)
- [x] `pytest tests/ --testmon` — no regressions
- [x] Run full suite: `pytest tests/ -n 12` — 12139 passed, 1 skipped
