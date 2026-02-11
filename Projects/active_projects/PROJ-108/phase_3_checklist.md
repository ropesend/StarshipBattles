# Phase 3: ComponentInspector Utility + AI Combat Utils

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create shared utilities for component/ability inspection (strategy layer) and AI combat helpers. Write comprehensive tests before modifying callers.
**Findings:** DUP-STR-001, DUP-STR-002, DUP-STR-003, DUP-STR-006, DUP-FND-002, DUP-FND-004

---

## Tasks

### Task 3.1: Create ComponentInspector utility [Medium]
**File:** `game/strategy/services/component_inspector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_component_inspector.py -v`

- [x] Create `game/strategy/services/component_inspector.py`
- [x] Implement `get_component_abilities(comp_def) -> Dict[str, Any]`:
  - Handles `None` -> `{}`
  - Handles `dict` -> `comp_def.get('abilities', {})`
  - Handles Component objects -> `getattr(comp_def, 'abilities', {})`
  - This is the shared version of `ColonizeValidator._get_component_abilities()` and `SuperweaponValidator._get_component_abilities()`
- [x] Implement `iterate_design_components(design_data, component_registry)`:
  - Yields `(comp_entry, comp_def, abilities)` for each component across all layers
  - Handles `design_data.get('layers', {})` -> iterate values
  - Skips layers where `not isinstance(layer_components, list)`
  - For each `comp_entry`: extracts `comp_id`, looks up `comp_def` in registry, gets abilities
- [x] Implement `ship_has_ability(ship, ability_name, component_registry) -> bool`:
  - Uses `iterate_design_components(ship.design_data, component_registry)`
  - Returns True if any component has `ability_name` in abilities
- [x] Implement `find_ship_with_ability(fleet_ships, ability_name, component_registry) -> Optional`:
  - Iterates ships, returns first where `ship_has_ability()` is True
- [x] Implement `count_ability(ship, ability_name, component_registry) -> int`:
  - Counts components with the given ability name
- [x] Add `__all__` export list

### Task 3.2: Write tests for ComponentInspector [Medium]
**File:** `tests/unit/strategy/test_component_inspector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_component_inspector.py -v`

- [x] Test: `get_component_abilities(None)` returns `{}`
- [x] Test: `get_component_abilities({"abilities": {"Foo": 1}})` returns `{"Foo": 1}`
- [x] Test: `get_component_abilities(component_obj)` uses getattr
- [x] Test: `iterate_design_components()` yields correct tuples for multi-layer design
- [x] Test: `iterate_design_components()` skips non-list layers
- [x] Test: `ship_has_ability()` returns True when ability present
- [x] Test: `ship_has_ability()` returns False when ability absent
- [x] Test: `find_ship_with_ability()` returns correct ship from list
- [x] Test: `find_ship_with_ability()` returns None when no match
- [x] Test: `count_ability()` returns correct count for multiple components

### Task 3.3: Create AI combat utils module [Simple]
**File:** `game/ai/combat_utils.py` (NEW)
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

Extract from `game/ai/target_evaluator.py:26-132`:

- [x] Create `game/ai/combat_utils.py`
- [x] Move `_is_vector2_like()` from `target_evaluator.py:26-32`
- [x] Move `_get_position()` from `target_evaluator.py:35-67` -> rename to `get_position()`
- [x] Move `_get_rotation()` from `target_evaluator.py:70-98` -> rename to `get_rotation()`
- [x] Move `_get_all_components()` from `target_evaluator.py:101-105` -> rename to `get_all_components()`
- [x] Move `_safe_distance()` from `target_evaluator.py:108-132` -> rename to `safe_distance()`
- [x] Add HP percent function: extract from `game/ai/controller.py:268-274` pattern
  - `TargetEvaluator._default_get_hp_percent(ship)` is the canonical impl
- [x] Add PDC arc check: extract from `game/ai/controller.py:276-282` pattern
  - `TargetEvaluator._default_is_in_pdc_arc(ship, target)` is the canonical impl
- [x] Add `__all__` export

### Task 3.4: Write tests for AI combat utils [Simple]
**File:** `tests/unit/ai/test_combat_utils.py` (NEW)
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

- [x] Test: `get_position()` with interface method
- [x] Test: `get_position()` with direct attribute fallback
- [x] Test: `get_rotation()` with interface method
- [x] Test: `get_rotation()` with direct attribute fallback
- [x] Test: `safe_distance()` with valid positions
- [x] Test: `safe_distance()` returns inf when position is None
- [x] Test: `get_hp_percent()` basic calculation
- [x] Test: `is_in_pdc_arc()` basic check
- [x] Verify: `pytest tests/ -n 12` passes

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/test_component_inspector.py -v` passes (18 tests)
- [x] `pytest tests/unit/ai/test_combat_utils.py -v` passes (20 tests)
- [x] `pytest tests/ -n 12` -- full suite passes (8237 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
