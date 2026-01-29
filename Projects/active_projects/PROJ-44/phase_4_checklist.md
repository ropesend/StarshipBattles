# Phase 4: Component System Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Break down the 878-line Component god class into focused managers.

---

## Tasks

### Task 4.1: Extract AbilityManager [Complex]
**File:** Create `game/simulation/components/ability_manager.py`
**Issue:** CQ-01 - Component has 40+ methods
**Tests:** `pytest tests/unit/entities/test_components.py`

- [ ] Create `AbilityManager` class with:
  - `instantiate_abilities(data, component_ref) -> List[Ability]`
  - `get_abilities(ability_name, instances) -> List[Ability]`
  - `get_ability(ability_name, instances) -> Optional[Ability]`
  - `has_ability(ability_name, instances) -> bool`
  - `has_pdc_ability(instances) -> bool`
  - `get_ui_rows(instances) -> List[Dict]`
- [ ] Move methods from `component.py` lines 182-314
- [ ] Update Component to delegate to AbilityManager
- [ ] Verify: Ability querying works in combat and UI

**Notes:**

---

### Task 4.2: Extract ModifierManager [Complex]
**File:** Create `game/simulation/components/modifier_manager.py`
**Issue:** CQ-01 - Modifier handling mixed with other concerns
**Tests:** `pytest tests/unit/entities/test_components.py`

- [ ] Create `ModifierManager` class with:
  - `add_modifier(modifiers_list, mod_id, value, registry) -> bool`
  - `remove_modifier(modifiers_list, mod_id) -> bool`
  - `get_modifier(modifiers_list, mod_id) -> Optional[Modifier]`
  - `get_all_effects(modifiers_list) -> Dict`
  - `get_stat_summary(modifiers_list, base_stats) -> Dict`
- [ ] Move methods from `component.py` lines 412-512
- [ ] Update Component to delegate to ModifierManager
- [ ] Verify: Modifier application and stacking works

**Notes:**

---

### Task 4.3: Extract ComponentStatsCalculator [Complex]
**File:** Create `game/simulation/components/component_stats_calculator.py`
**Issue:** CQ-01 - Stats recalculation is complex multi-phase
**Tests:** `pytest tests/unit/entities/test_components.py`

- [ ] Create `ComponentStatsCalculator` class with:
  - `recalculate(component, context) -> Dict`
  - `_reset_and_evaluate_formulas(data, context) -> Dict`
  - `_calculate_modifier_stats(modifiers) -> Dict`
  - `_apply_base_stats(component, stats, old_max_hp) -> None`
- [ ] Move methods from `component.py` lines 514-640
- [ ] Update Component.recalculate_stats() to delegate
- [ ] Verify: Component stats calculation unchanged

**Notes:**

---

### Task 4.4: Simplify Component Class [Medium]
**File:** `game/simulation/components/component.py`
**Issue:** CQ-01 - Reduce to coordinator role
**Tests:** `pytest tests/unit/entities/test_components.py`

- [ ] Component should now be ~300-400 lines
- [ ] Keep: `__init__`, `update`, `take_damage`, `reset_hp`, `clone`, properties
- [ ] Delegate: abilities -> AbilityManager, modifiers -> ModifierManager, stats -> ComponentStatsCalculator
- [ ] Add clear docstring explaining delegation pattern
- [ ] Verify: Full test suite passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
