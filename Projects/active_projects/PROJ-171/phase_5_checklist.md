# Phase 5: Simulation State (ShipState, ComponentState, Event, DesignMetadata)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 5`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/simulation/test_battle_state_validation.py tests/unit/strategy/events/ tests/unit/strategy/data/ -v`

## Task 5.1: Validate ComponentState.from_dict() [Simple]
**File:** `game/simulation/battle_state.py:50-59`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`

- [ ] Add imports for `require_keys`, `validate_non_negative`, `validate_positive` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['component_id', 'current_hp', 'max_hp', 'is_active', 'layer'], 'ComponentState')` at start
- [ ] Add `validate_non_negative(data['current_hp'], 'current_hp', 'ComponentState')`
- [ ] Add `validate_positive(data['max_hp'], 'max_hp', 'ComponentState')`
- [ ] Create test file `tests/unit/simulation/test_battle_state_validation.py` (or add to existing)
- [ ] Test: valid data → ComponentState created
- [ ] Test: missing 'component_id' → PersistenceException
- [ ] Test: missing 'current_hp' → PersistenceException
- [ ] Test: negative current_hp → PersistenceException
- [ ] Test: zero max_hp → PersistenceException
- [ ] Verify existing tests: `pytest tests/unit/simulation/test_battle_state_serialization.py -v`

**Notes:** 5 required fields. Simple leaf node.

## Task 5.2: Validate ShipState.from_dict() [Medium]
**File:** `game/simulation/battle_state.py:146-174`
**Tests:** `pytest tests/unit/simulation/test_battle_state_validation.py`

- [ ] Add `require_keys(data, ['ship_id', 'name', 'ship_class', 'theme_id', 'team_id', 'color', 'ai_strategy', 'position', 'velocity', 'angle', 'current_hp', 'max_hp', 'current_shields', 'max_shields'], 'ShipState')` at start
- [ ] Add validation for color format: check `isinstance(data['color'], (list, tuple))` and `len(data['color']) >= 3`
- [ ] Add validation for position format: check `isinstance(data['position'], (list, tuple))` and `len(data['position']) >= 2`
- [ ] Add validation for velocity format: same as position
- [ ] Wrap nested ComponentState.from_dict() calls — skip bad components per layer with warning log
- [ ] Test: valid data → ShipState created
- [ ] Test: missing 'ship_id' → PersistenceException
- [ ] Test: invalid color (not a list/tuple or too short) → PersistenceException
- [ ] Test: bad component in a layer → component skipped, ship state loads
- [ ] Verify existing tests: `pytest tests/unit/simulation/test_battle_state_serialization.py -v`

**Notes:** 14 required fields. Has tuple conversions that can fail with TypeError.

## Task 5.3: Validate Event.from_dict() [Simple]
**File:** `game/strategy/events/event_log.py:40-50`
**Tests:** `pytest tests/unit/strategy/events/test_event_validation.py`

- [ ] Add import for `require_keys` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['event_type', 'category', 'turn', 'empire_id', 'message'], 'Event')` at start
- [ ] Create test file `tests/unit/strategy/events/test_event_validation.py`
- [ ] Test: valid data → Event created
- [ ] Test: missing 'event_type' → PersistenceException
- [ ] Test: missing 'turn' → PersistenceException

**Notes:** 5 required fields. Simple leaf node.

## Task 5.4: Validate DesignMetadata.from_dict() [Simple]
**File:** `game/strategy/data/design_metadata.py:58-79`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata_validation.py`

- [ ] Add import for `require_keys` from `game.core.validation_helpers`
- [ ] Add `require_keys(data, ['design_id', 'name'], 'DesignMetadata')` at start
- [ ] Create test file `tests/unit/strategy/data/test_design_metadata_validation.py`
- [ ] Test: valid data → DesignMetadata created
- [ ] Test: missing 'design_id' → PersistenceException
- [ ] Test: missing 'name' → PersistenceException
- [ ] Test: other fields missing → still works (all have .get() defaults)

**Notes:** Only 2 required fields. Rest already have .get() defaults.

## Phase 5 Completion
- [ ] All tasks above checked
- [ ] All new validation tests pass
- [ ] Existing battle state serialization tests still pass
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Run full suite: `pytest tests/ -n 12` — final verification
