# Phase 4: Component System Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Break down the 878-line Component god class into focused managers.

---

## Tasks

### Task 4.1: Extract AbilityManager [Complex]
**File:** Create `game/simulation/components/ability_manager.py`
**Issue:** CQ-01 - Component has 40+ methods
**Tests:** `pytest tests/unit/entities/test_components.py`

- [x] Create `AbilityManager` class with:
  - `instantiate_abilities(data, component_ref) -> List[Ability]`
  - `get_abilities(ability_name, instances) -> List[Ability]`
  - `get_ability(ability_name, instances) -> Optional[Ability]`
  - `has_ability(ability_name, instances) -> bool`
  - `has_pdc_ability(instances) -> bool`
  - `get_ui_rows(instances) -> List[Dict]`
- [x] Move methods from `component.py` lines 182-314
- [x] Update Component to delegate to AbilityManager
- [x] Verify: Ability querying works in combat and UI

**Notes:** Created ability_manager.py (211 lines). All static methods for flexibility. Component delegates get_abilities, get_ability, has_ability, has_pdc_ability, get_ui_rows, and _instantiate_abilities.

---

### Task 4.2: Extract ModifierManager [Complex]
**File:** Create `game/simulation/components/modifier_manager.py`
**Issue:** CQ-01 - Modifier handling mixed with other concerns
**Tests:** `pytest tests/unit/entities/test_components.py`

- [x] Create `ModifierManager` class with:
  - `add_modifier(modifiers_list, mod_id, value, registry) -> bool`
  - `remove_modifier(modifiers_list, mod_id) -> bool`
  - `get_modifier(modifiers_list, mod_id) -> Optional[Modifier]`
  - `get_all_effects(modifiers_list) -> Dict`
  - `get_stat_summary(modifiers_list, base_stats) -> Dict`
- [x] Move methods from `component.py` lines 412-512
- [x] Update Component to delegate to ModifierManager
- [x] Verify: Modifier application and stacking works

**Notes:** Created modifier_manager.py (203 lines). All static methods. Component delegates add_modifier, remove_modifier, get_modifier, get_all_modifier_effects, and get_modifier_stat_summary.

---

### Task 4.3: Extract ComponentStatsCalculator [Complex]
**File:** Create `game/simulation/components/component_stats_calculator.py`
**Issue:** CQ-01 - Stats recalculation is complex multi-phase
**Tests:** `pytest tests/unit/entities/test_components.py`

- [x] Create `ComponentStatsCalculator` class with:
  - `recalculate(component, context) -> Dict`
  - `reset_and_evaluate_formulas(component, context) -> None`
  - `calculate_modifier_stats(modifiers) -> Dict`
  - `apply_base_stats(component, stats, old_max_hp) -> None`
- [x] Move methods from `component.py` lines 514-640
- [x] Update Component.recalculate_stats() to delegate
- [x] Verify: Component stats calculation unchanged

**Notes:** Created component_stats_calculator.py (235 lines). Static methods. Component delegates recalculate_stats, _reset_and_evaluate_base_formulas, _calculate_modifier_stats, and _apply_base_stats.

---

### Task 4.4: Simplify Component Class [Medium]
**File:** `game/simulation/components/component.py`
**Issue:** CQ-01 - Reduce to coordinator role
**Tests:** `pytest tests/unit/entities/test_components.py`

- [x] Component reduced from 898 to 665 lines (-233 lines, 26% reduction)
- [x] Keep: `__init__`, `update`, `take_damage`, `reset_hp`, `clone`, properties
- [x] Delegate: abilities -> AbilityManager, modifiers -> ModifierManager, stats -> ComponentStatsCalculator
- [x] Component now imports and delegates to three manager classes
- [x] Verify: Full test suite passes (5448 passed, 3 skipped)

**Notes:** Component is now a coordinator class that delegates specialized work to manager modules. Note: Original target of 300-400 lines not achieved - Component still at 665 lines due to retaining __init__, properties, update, take_damage, etc. which are essential. Further reduction would require more aggressive decomposition.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass (5448 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
