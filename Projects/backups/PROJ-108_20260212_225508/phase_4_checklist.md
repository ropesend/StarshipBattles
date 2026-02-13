# Phase 4: Migrate Strategy Callers + AI Callers to Shared Utilities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all strategy validators and AI modules to use ComponentInspector and combat_utils.
**Findings:** DUP-STR-001, DUP-STR-002, DUP-STR-003, DUP-STR-006, DUP-FND-002, DUP-FND-004
**Depends on:** Phase 3 (utilities must exist and pass tests)

---

## Tasks

### Task 4.1: Migrate SuperweaponValidator [Simple]
**File:** `game/strategy/validation/superweapon_validator.py`
**Tests:** `pytest tests/ -k superweapon -v`

- [x] Add import: `from game.strategy.services.component_inspector import find_ship_with_ability, ship_has_ability`
- [x] Delete `_get_component_abilities()` static method -- use ComponentInspector
- [x] Rewrite `find_ship_with_ability()` to delegate to ComponentInspector
- [x] Update `validate_self_destruct()` to use `ship_has_ability()`
- [x] Verify: `pytest tests/ -k superweapon -v` passes
- [x] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/engine/superweapon_order_processor.py` imports `SuperweaponValidator`

### Task 4.2: Migrate ColonizeValidator [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/integration/colonization/ -v`

- [x] Add import: `from game.strategy.services.component_inspector import iterate_design_components`
- [x] Delete `_get_component_abilities()` static method
- [x] Rewrite `find_ship_with_colony_pod()` to use `iterate_design_components()`
- [x] Rewrite `get_available_colony_pods()` to use `iterate_design_components()`
- [x] Verify: `pytest tests/integration/colonization/ -v` passes
- [x] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/facade/strategy_session_facade.py` (line 424)

### Task 4.3: Migrate FleetCapabilityCalculator [Medium]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_capability_calculator.py -v`

- [x] Add import: `from game.strategy.services.component_inspector import ship_has_ability, count_ability`
- [x] Rewrite `ship_has_spaceyard()` to use ComponentInspector
- [x] Rewrite `space_shipyard_count` property to use `count_ability()`
- [x] Rewrite `_ship_has_ability()` to delegate to ComponentInspector
- [x] Updated iterate_design_components to support inline abilities (backward compat for test mocks)
- [x] Verify: `pytest tests/unit/strategy/test_fleet_capability_calculator.py -v` passes (27 passed)
- [x] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/data/fleet.py` (line 4), `game/ui/screens/fleet_report_filters.py`, `game/ui/screens/column_manager.py`

### Task 4.4: Migrate AI target_evaluator to combat_utils [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Add import: `from game.ai.combat_utils import get_position, get_rotation, get_all_components, safe_distance, get_hp_percent, is_in_pdc_arc`
- [x] Delete `_is_vector2_like()` function
- [x] Delete `_get_position()` function
- [x] Delete `_get_rotation()` function
- [x] Delete `_get_all_components()` function
- [x] Delete `_safe_distance()` function
- [x] Delete `_default_get_hp_percent()` and `_default_is_in_pdc_arc()` methods (now in combat_utils)
- [x] Update internal references to use imported names
- [x] Update default stat_helpers to use combat_utils functions
- [x] Verify: `pytest tests/unit/ai/ -v` passes (266 passed)
- [x] Verify: `pytest tests/ -n 12` passes

### Task 4.5: Migrate AI controller to combat_utils [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Add import: `from game.ai.combat_utils import get_hp_percent, is_in_pdc_arc`
- [x] Update `_get_hp_percent()` to delegate to `get_hp_percent()` from combat_utils
- [x] Update `_is_in_pdc_arc()` to delegate to `is_in_pdc_arc()` from combat_utils
- [x] Updated test files to use combat_utils instead of deleted TargetEvaluator methods
- [x] Verify: `pytest tests/unit/ai/ -v` passes (266 passed)
- [x] Verify: `pytest tests/ -n 12` passes

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No `_get_component_abilities()` exists in colonize_validator.py or superweapon_validator.py
- [x] No `_get_position()` or `_get_rotation()` exists in target_evaluator.py
- [x] `pytest tests/ -n 12` -- full suite passes (8237 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Implementation Notes

1. **ComponentInspector Enhancement**: Added fallback for inline abilities in `iterate_design_components()` to support test mocks that embed abilities directly in design_data without registry lookup.

2. **Test Updates**: Updated test files that were directly testing the now-deleted private methods:
   - `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
   - `tests/unit/ai/test_ai_exceptions.py`

3. **Lines Removed**:
   - target_evaluator.py: ~105 lines (helper functions and default methods)
   - superweapon_validator.py: ~24 lines (_get_component_abilities)
   - colonize_validator.py: ~24 lines (_get_component_abilities)
   - fleet_capability_calculator.py: Refactored to use ComponentInspector

4. **Total deduplication this phase**: ~150+ lines consolidated into shared utilities
