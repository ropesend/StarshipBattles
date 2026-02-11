# Phase 3: ComponentInspector Utility + AI Combat Utils

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create shared utilities for component/ability inspection (strategy layer) and AI combat helpers. Write comprehensive tests before modifying callers.
**Findings:** DUP-STR-001, DUP-STR-002, DUP-STR-003, DUP-STR-006, DUP-FND-002, DUP-FND-004

---

## Tasks

### Task 3.1: Create ComponentInspector utility [Medium]
**File:** `game/strategy/services/component_inspector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_component_inspector.py -v`

- [ ] Create `game/strategy/services/component_inspector.py`
- [ ] Implement `get_component_abilities(comp_def) -> Dict[str, Any]`:
  - Handles `None` -> `{}`
  - Handles `dict` -> `comp_def.get('abilities', {})`
  - Handles Component objects -> `getattr(comp_def, 'abilities', {})`
  - This is the shared version of `ColonizeValidator._get_component_abilities()` and `SuperweaponValidator._get_component_abilities()`
- [ ] Implement `iterate_design_components(design_data, component_registry)`:
  - Yields `(comp_entry, comp_def, abilities)` for each component across all layers
  - Handles `design_data.get('layers', {})` -> iterate values
  - Skips layers where `not isinstance(layer_components, list)`
  - For each `comp_entry`: extracts `comp_id`, looks up `comp_def` in registry, gets abilities
- [ ] Implement `ship_has_ability(ship, ability_name, component_registry) -> bool`:
  - Uses `iterate_design_components(ship.design_data, component_registry)`
  - Returns True if any component has `ability_name` in abilities
- [ ] Implement `find_ship_with_ability(fleet_ships, ability_name, component_registry) -> Optional`:
  - Iterates ships, returns first where `ship_has_ability()` is True
- [ ] Implement `count_ability(ship, ability_name, component_registry) -> int`:
  - Counts components with the given ability name
- [ ] Add `__all__` export list

### Task 3.2: Write tests for ComponentInspector [Medium]
**File:** `tests/unit/strategy/test_component_inspector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_component_inspector.py -v`

- [ ] Test: `get_component_abilities(None)` returns `{}`
- [ ] Test: `get_component_abilities({"abilities": {"Foo": 1}})` returns `{"Foo": 1}`
- [ ] Test: `get_component_abilities(component_obj)` uses getattr
- [ ] Test: `iterate_design_components()` yields correct tuples for multi-layer design
- [ ] Test: `iterate_design_components()` skips non-list layers
- [ ] Test: `ship_has_ability()` returns True when ability present
- [ ] Test: `ship_has_ability()` returns False when ability absent
- [ ] Test: `find_ship_with_ability()` returns correct ship from list
- [ ] Test: `find_ship_with_ability()` returns None when no match
- [ ] Test: `count_ability()` returns correct count for multiple components

### Task 3.3: Create AI combat utils module [Simple]
**File:** `game/ai/combat_utils.py` (NEW)
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

Extract from `game/ai/target_evaluator.py:26-132`:

- [ ] Create `game/ai/combat_utils.py`
- [ ] Move `_is_vector2_like()` from `target_evaluator.py:26-32`
- [ ] Move `_get_position()` from `target_evaluator.py:35-67` -> rename to `get_position()`
- [ ] Move `_get_rotation()` from `target_evaluator.py:70-98` -> rename to `get_rotation()`
- [ ] Move `_get_all_components()` from `target_evaluator.py:101-105` -> rename to `get_all_components()`
- [ ] Move `_safe_distance()` from `target_evaluator.py:108-132` -> rename to `safe_distance()`
- [ ] Add HP percent function: extract from `game/ai/controller.py:268-274` pattern
  - `TargetEvaluator._default_get_hp_percent(ship)` is the canonical impl
- [ ] Add PDC arc check: extract from `game/ai/controller.py:276-282` pattern
  - `TargetEvaluator._default_is_in_pdc_arc(ship, target)` is the canonical impl
- [ ] Add `__all__` export

### Task 3.4: Write tests for AI combat utils [Simple]
**File:** `tests/unit/ai/test_combat_utils.py` (NEW)
**Tests:** `pytest tests/unit/ai/test_combat_utils.py -v`

- [ ] Test: `get_position()` with interface method
- [ ] Test: `get_position()` with direct attribute fallback
- [ ] Test: `get_rotation()` with interface method
- [ ] Test: `get_rotation()` with direct attribute fallback
- [ ] Test: `safe_distance()` with valid positions
- [ ] Test: `safe_distance()` returns inf when position is None
- [ ] Test: `get_hp_percent()` basic calculation
- [ ] Test: `is_in_pdc_arc()` basic check
- [ ] Verify: `pytest tests/ -n 12` passes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/test_component_inspector.py -v` passes
- [ ] `pytest tests/unit/ai/test_combat_utils.py -v` passes
- [ ] `pytest tests/ -n 12` -- full suite passes (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
