# Phase 3: Replace Ability Duck Typing (~35 instances)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `getattr(ability, 'attr', default)` with protocol-typed access using `isinstance()` checks and direct attribute access.

---

## Tasks

### Task 3.1: combat_endurance.py [Medium]
**File:** `game/simulation/entities/combat_endurance.py`
**Tests:** `pytest tests/unit/simulation/entities/test_combat_endurance.py`

- [ ] Add imports: `from game.simulation.interfaces import IResourceConsumptionAbility, IWeaponAbility` (under TYPE_CHECKING or direct)
- [ ] Line ~43: Replace `getattr(c, 'ability_instances', [])` → `c.ability_instances` (IComponent typed)
- [ ] Lines ~49-51: Replace `getattr(ab, 'trigger', 'constant')` / `getattr(ab, 'resource_type', '')` / `getattr(ab, 'amount', 0.0)` → `isinstance(ab, IResourceConsumptionAbility)` then direct access `ab.trigger`, `ab.resource_type`, `ab.amount`
- [ ] Line ~70: Replace `getattr(inst, 'reload_time', 1.0)` → `isinstance(inst, IWeaponAbility)` then `inst.reload_time`
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.2: ship_stats.py [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [ ] Add imports for ability protocols: `IResourceStorageAbility`, `IResourceGenerationAbility`, `IResourceConsumptionAbility`, `IWarpJumpAbility`
- [ ] Line ~282: Replace `getattr(comp, 'ability_instances', [])` → `comp.ability_instances` (IComponent typed)
- [ ] Lines ~286-287: Replace `getattr(ability, 'resource_type', '')` / `getattr(ability, 'max_amount', 0.0)` → `isinstance(ability, IResourceStorageAbility)` then direct access
- [ ] Lines ~296-297: Same for `IResourceGenerationAbility` → `ability.resource_type`, `ability.rate`
- [ ] Lines ~315-319: Replace warp detection → `isinstance(ab, IWarpJumpAbility)` then `ab.max_tonnage`, `ab.energy_cost`
- [ ] Lines ~344-345: Replace shield cost detection → `isinstance(ab, IResourceConsumptionAbility)` check
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.3: ability_aggregator.py [Simple]
**File:** `game/simulation/entities/ability_aggregator.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [ ] Line ~102: Replace `getattr(comp, 'ability_instances', None)` → `comp.ability_instances` (IComponent typed)
- [ ] Line ~124: Replace `getattr(ab, 'stack_group', None)` → `ab.stack_group` (IAbility typed)
- [ ] Line ~139: Replace `getattr(comp, 'abilities', {})` → `comp.abilities`
- [ ] Line ~207: Replace `getattr(comp, 'ability_instances', None)` → `comp.ability_instances`
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.4: abilities/base.py [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 12`

- [ ] Line ~236: Replace `getattr(self.component, 'ability_stats', {})` → `self.component.ability_stats`
- [ ] Line ~243: Replace `getattr(self.component, 'stats', {})` → `self.component.stats`
- [ ] Line ~311: Replace `getattr(self.component, 'stats', {})` → `self.component.stats`
- [ ] Lines ~325, 329: `getattr(self, base_attr, None)` and `getattr(self, binding.attribute_name, base_value)` — these are self-introspection within base class. **Keep as-is** (internal dynamic attribute resolution for modifier bindings, not duck typing)
- [ ] Lines ~370, 393, 402, 407: Class-level introspection for descriptor protocol. **Keep as-is** (meta-programming, not duck typing)
- [ ] Verify: tests pass

**Notes:** Several getattr calls in base.py are legitimate meta-programming for the modifier binding system and should be preserved. Only replace calls that access component properties.

---

### Task 3.5: ability_manager.py [Simple]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [ ] Line ~120: Replace `hasattr(ab, 'tags') and 'pdc' in ab.tags` → `isinstance(ab, IAbility) and ab.tags and 'pdc' in ab.tags`
- [ ] Line ~140: Replace `hasattr(ab, 'get_ui_rows')` → `isinstance(ab, IAbility)` (IAbility protocol includes get_ui_rows)
- [ ] Line ~195: Replace `hasattr(ab, 'sync_data')` → `isinstance(ab, IAbility)` (IAbility protocol includes sync_data)
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.6: modifier_introspection.py [Simple]
**File:** `game/simulation/components/modifier_introspection.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [ ] Line ~141: Replace `hasattr(mod_def, 'evaluate_effects')` → typed check or direct call with try/except
- [ ] Line ~146: Replace `hasattr(mod_def, 'display_name')` → `mod_def.display_name if hasattr(mod_def, 'display_name') else mod_def.id` → use getattr pattern or add to protocol
- [ ] Line ~153: Replace `hasattr(component, 'display_name')` → `component.name` (IComponent has `name`)
- [ ] Line ~155: Replace `hasattr(component, 'stats')` → `component.stats` (IComponent typed)
- [ ] Lines ~185, 271: Replace `hasattr(ability, 'get_effect_summary')` → `isinstance(ability, IAbility)` then `ability.get_effect_summary()`
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.7: abilities/weapons.py [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 12`

- [ ] Line ~170: Replace `hasattr(self.component, 'facing_angle')` → check component stats dict
- [ ] Lines ~258, 278-279, 334-340: Multiple `getattr(self.component, 'prop', default)` for weapon properties → access via `self.component.stats.get('prop', default)` or direct attribute if guaranteed
- [ ] Verify: tests pass

**Notes:** Weapon properties like projectile_speed, endurance, turn_rate are set on the component from JSON data. They may be better accessed via `self.component.stats` dict rather than direct attribute access.

---

### Task 3.8: Component support files [Simple]
**Files:** `game/simulation/components/component_stats_calculator.py`, `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [ ] `component_stats_calculator.py` line ~82: Replace `hasattr(component, prop)` → direct access (IComponent guarantees it)
- [ ] `component_stats_calculator.py` line ~91: Replace `hasattr(component, 'cost')` → `component.cost` (IComponent has `cost`)
- [ ] `component_stats_calculator.py` line ~147: Replace `getattr(component.ship, 'max_mass_budget', 1000)` → typed access
- [ ] `component_stats_calculator.py` lines ~159-160: Replace `hasattr(component, attr)` / `getattr(component, attr)` → direct access
- [ ] `component_resource_manager.py` line ~51: Replace `getattr(ability, 'trigger', None)` → isinstance check
- [ ] `component_resource_manager.py` line ~52: Replace `getattr(ability, 'check_available', None)` → isinstance check
- [ ] `component_resource_manager.py` line ~96: Replace `getattr(component, 'evaluated_resource_cost', None)` → `component.evaluated_resource_cost` (initialized in Phase 2)
- [ ] `component_resource_manager.py` line ~107: Replace `getattr(...)` for ship_class_mass
- [ ] Verify: tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/simulation/ -n 12` — all pass
- [ ] No `getattr(ability, ...)` or `hasattr(ability, ...)` calls remain for ability properties
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
