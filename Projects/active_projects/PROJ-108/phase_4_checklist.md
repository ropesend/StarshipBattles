# Phase 4: Migrate Strategy Callers + AI Callers to Shared Utilities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all strategy validators and AI modules to use ComponentInspector and combat_utils.
**Findings:** DUP-STR-001, DUP-STR-002, DUP-STR-003, DUP-STR-006, DUP-FND-002, DUP-FND-004
**Depends on:** Phase 3 (utilities must exist and pass tests)

---

## Tasks

### Task 4.1: Migrate SuperweaponValidator [Simple]
**File:** `game/strategy/validation/superweapon_validator.py`
**Tests:** `pytest tests/ -k superweapon -v`

- [ ] Add import: `from game.strategy.services.component_inspector import ComponentInspector`
- [ ] Delete `_get_component_abilities()` static method (lines 13-36) -- use `ComponentInspector.get_component_abilities()`
- [ ] Rewrite `find_ship_with_ability()` (lines 38-70) to delegate:
  ```python
  @staticmethod
  def find_ship_with_ability(fleet, ability_name, component_registry):
      return ComponentInspector.find_ship_with_ability(
          fleet.ships, ability_name, component_registry
      )
  ```
- [ ] Update `validate_self_destruct()` inner loop (lines 385-399) to use `ComponentInspector.ship_has_ability()`
- [ ] Verify: `pytest tests/ -k superweapon -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/engine/superweapon_order_processor.py` imports `SuperweaponValidator`

### Task 4.2: Migrate ColonizeValidator [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/integration/colonization/ -v`

- [ ] Add import: `from game.strategy.services.component_inspector import ComponentInspector`
- [ ] Delete `_get_component_abilities()` static method (lines 14-37) -- use `ComponentInspector.get_component_abilities()`
- [ ] Rewrite `find_ship_with_colony_pod()` (lines 124-167) to use `ComponentInspector.iterate_design_components()`:
  ```python
  for ship in fleet.ships:
      for comp_entry, comp_def, abilities in ComponentInspector.iterate_design_components(
          getattr(ship, 'design_data', {}), component_registry
      ):
          if 'ColonizePlanet' in abilities:
              # existing ability_data extraction logic
              ...
  ```
- [ ] Rewrite `get_available_colony_pods()` (lines 169-212) similarly using `iterate_design_components()`
- [ ] Verify: `pytest tests/integration/colonization/ -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/facade/strategy_session_facade.py` (line 424)

### Task 4.3: Migrate FleetCapabilityCalculator [Medium]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_capability_calculator.py -v`

- [ ] Add import: `from game.strategy.services.component_inspector import ComponentInspector`
- [ ] Rewrite `ship_has_spaceyard()` (lines 24-45):
  ```python
  @staticmethod
  def ship_has_spaceyard(ship):
      from game.core.registry import get_default_registries
      registry = get_default_registries().components
      return ComponentInspector.ship_has_ability(ship, 'SpaceShipyard', registry)
  ```
  **Note:** Also check for hardcoded `fleet_space_yard` ID -- if needed, keep as fallback
  or ensure component has `SpaceShipyard` ability in registry.
- [ ] Rewrite `space_shipyard_count` property (lines 67-81):
  ```python
  @property
  def space_shipyard_count(self):
      from game.core.registry import get_default_registries
      registry = get_default_registries().components
      count = 0
      for ship in self._fleet.get_combat_capable_ships():
          count += ComponentInspector.count_ability(ship, 'SpaceShipyard', registry)
      return count
  ```
- [ ] Rewrite `_ship_has_ability()` (lines 181-202) to delegate to `ComponentInspector.ship_has_ability()`
- [ ] Update `ships_with_ability()` and `has_ability()` if they call `_ship_has_ability()`
- [ ] Verify: `pytest tests/unit/strategy/test_fleet_capability_calculator.py -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/strategy/data/fleet.py` (line 4), `game/ui/screens/fleet_report_filters.py`, `game/ui/screens/column_manager.py`

**Important:** `ship_has_spaceyard()` currently checks `comp.get("id") == "fleet_space_yard"` as a
shortcut. If the component registry lookup works (component has SpaceShipyard ability), this
shortcut becomes unnecessary. Verify with tests before removing.

### Task 4.4: Migrate AI target_evaluator to combat_utils [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Add import: `from game.ai.combat_utils import get_position, get_rotation, get_all_components, safe_distance, is_vector2_like`
- [ ] Delete `_is_vector2_like()` function (lines 26-32)
- [ ] Delete `_get_position()` function (lines 35-67)
- [ ] Delete `_get_rotation()` function (lines 70-98)
- [ ] Delete `_get_all_components()` function (lines 101-105)
- [ ] Delete `_safe_distance()` function (lines 108-132)
- [ ] Update all internal references to use imported names (no underscore prefix)
- [ ] Verify: `pytest tests/unit/ai/ -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

### Task 4.5: Migrate AI controller to combat_utils [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Verify `_stat_get_hp_percent()` (line 269) and `_get_hp_percent()` (line 273) already delegate to `TargetEvaluator._default_get_hp_percent()`
- [ ] Verify `_stat_is_in_pdc_arc()` (line 277) and `_is_in_pdc_arc()` (line 281) already delegate to `TargetEvaluator._default_is_in_pdc_arc()`
- [ ] If TargetEvaluator still owns these, update both to delegate to `combat_utils` instead
- [ ] Verify: `pytest tests/unit/ai/ -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `_get_component_abilities()` exists in colonize_validator.py or superweapon_validator.py
- [ ] No `_get_position()` or `_get_rotation()` exists in target_evaluator.py
- [ ] `pytest tests/ -n 12` -- full suite passes (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
