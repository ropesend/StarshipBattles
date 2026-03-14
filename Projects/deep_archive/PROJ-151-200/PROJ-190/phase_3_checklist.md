# Phase 3: Replace Ability Duck Typing (~35 instances)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace `getattr(ability, 'attr', default)` with protocol-typed access using `isinstance()` checks and direct attribute access.

---

## Tasks

### Task 3.1: combat_endurance.py [Medium]
**File:** `game/simulation/entities/combat_endurance.py`
**Tests:** `pytest tests/unit/simulation/entities/test_combat_endurance.py`

- [x] Add imports: `from game.simulation.interfaces import IResourceConsumptionAbility, IWeaponAbility` (under TYPE_CHECKING or direct)
- [x] Line ~43: Replace `getattr(c, 'ability_instances', [])` → `c.ability_instances` (IComponent typed)
- [x] Lines ~49-51: Replace `getattr(ab, 'trigger', 'constant')` / `getattr(ab, 'resource_type', '')` / `getattr(ab, 'amount', 0.0)` → `isinstance(ab, IResourceConsumptionAbility)` then direct access `ab.trigger`, `ab.resource_type`, `ab.amount`
- [x] Line ~70: Replace `getattr(inst, 'reload_time', 1.0)` → `isinstance(inst, IWeaponAbility)` then `inst.reload_time`
- [x] Verify: tests pass (45 passed)

**Notes:** Updated test mocks to use spec=IResourceConsumptionAbility and spec=IWeaponAbility for protocol compatibility.

---

### Task 3.2: ship_stats.py [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [x] Add imports for ability protocols: `IResourceStorageAbility`, `IResourceGenerationAbility`, `IResourceConsumptionAbility`, `IWarpJumpAbility`
- [x] Line ~282: Replace `getattr(comp, 'ability_instances', [])` → `comp.ability_instances` (IComponent typed)
- [x] Lines ~286-287: Replace `getattr(ability, 'resource_type', '')` / `getattr(ability, 'max_amount', 0.0)` → `isinstance(ability, IResourceStorageAbility)` then direct access
- [x] Lines ~296-297: Same for `IResourceGenerationAbility` → `ability.resource_type`, `ability.rate`
- [x] Lines ~315-319: Replace warp detection → `isinstance(ab, IWarpJumpAbility)` then `ab.max_tonnage`, `ab.energy_cost`
- [x] Lines ~344-345: Replace shield cost detection → `isinstance(ab, IResourceConsumptionAbility)` check
- [x] Verify: tests pass (448 passed)

**Notes:** Used is_resource_storage, is_resource_generation, is_resource_consumption, is_warp_jump TypeGuard functions.

---

### Task 3.3: ability_aggregator.py [Simple]
**File:** `game/simulation/entities/ability_aggregator.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [x] Line ~102: Replace `getattr(comp, 'ability_instances', None)` → `comp.ability_instances` (IComponent typed)
- [x] Line ~124: Replace `getattr(ab, 'stack_group', None)` → `ab.stack_group` (IAbility typed)
- [x] Line ~139: Replace `getattr(comp, 'abilities', {})` → `comp.abilities`
- [x] Line ~207: Replace `getattr(comp, 'ability_instances', None)` → `comp.ability_instances`
- [x] Verify: tests pass (83 passed)

**Notes:** Updated edge case tests that were testing non-IComponent objects.

---

### Task 3.4: abilities/base.py [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 12`

- [x] Line ~236: Replace `getattr(self.component, 'ability_stats', {})` → `self.component.ability_stats`
- [x] Line ~243: Replace `getattr(self.component, 'stats', {})` → `self.component.stats`
- [x] Line ~311: Replace `getattr(self.component, 'stats', {})` → `self.component.stats`
- [x] Lines ~325, 329: `getattr(self, base_attr, None)` and `getattr(self, binding.attribute_name, base_value)` — these are self-introspection within base class. **Kept as-is** (internal dynamic attribute resolution for modifier bindings, not duck typing)
- [x] Lines ~370, 393, 402, 407: Class-level introspection for descriptor protocol. **Kept as-is** (meta-programming, not duck typing)
- [x] Verify: tests pass (102 passed)

**Notes:** Updated test mock to have stats and ability_stats attributes per IComponent protocol.

---

### Task 3.5: ability_manager.py [Simple]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [x] Line ~120: Replace `hasattr(ab, 'tags') and 'pdc' in ab.tags` → direct access `ab.tags and 'pdc' in ab.tags`
- [x] Line ~140: Replace `hasattr(ab, 'get_ui_rows')` → direct call (Ability base class guarantees this method)
- [x] Line ~195: Replace `hasattr(ab, 'sync_data')` → direct call (Ability base class guarantees this method)
- [x] Verify: tests pass (15 passed)

**Notes:** Used direct attribute access since Ability base class guarantees these members exist. IAbility protocol check not used because Ability.trigger is only on some subclasses.

---

### Task 3.6: modifier_introspection.py [Simple]
**File:** `game/simulation/components/modifier_introspection.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [x] Line ~141: Kept `hasattr(mod_def, 'evaluate_effects')` (ModifierDefinition interface, not component)
- [x] Line ~146: Replace `hasattr(mod_def, 'display_name')` → `getattr(mod_def, 'display_name', mod_def.id)`
- [x] Line ~153: Replace `hasattr(component, 'display_name')` → `component.name` (IComponent protocol)
- [x] Line ~155: Replace `hasattr(component, 'stats')` → `component.stats` (IComponent protocol)
- [x] Lines ~185, 271: Replace `hasattr(ability, 'get_effect_summary')` → direct call (Ability base class guarantees this)
- [x] Verify: tests pass (46 passed)

**Notes:** Updated test mocks to include 'name' attribute per IComponent protocol.

---

### Task 3.7: abilities/weapons.py [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 12`

- [x] Line ~170: Replace `hasattr(self.component, 'facing_angle')` → `getattr(self.component, 'facing_angle', None) is None`
- [x] Lines ~258, 278-279, 334-340: These are in else branches for non-dict data fallback - kept as-is (legitimate getattr with defaults for edge cases)
- [x] Verify: tests pass (622 passed)

**Notes:** The getattr calls in else branches are intentional fallbacks when data is not a dict. They're properly guarded with defaults.

---

### Task 3.8: Component support files [Simple]
**Files:** `game/simulation/components/component_stats_calculator.py`, `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [x] `component_stats_calculator.py` line ~82: Remove hasattr guard for properties (they're dynamic modifier properties)
- [x] `component_stats_calculator.py` line ~91: Replace `hasattr(component, 'cost')` → direct access (IComponent has `cost`)
- [x] `component_stats_calculator.py` line ~147: Kept getattr (ship.max_mass_budget is runtime-set by ShipStatsCalculator)
- [x] `component_stats_calculator.py` lines ~159-160: Use getattr for dynamic formula attributes with None check
- [x] `component_resource_manager.py` line ~51-52: Replace `getattr(ability, 'trigger/check_available')` → `is_resource_consumption(ability)` protocol check
- [x] `component_resource_manager.py` line ~96: Kept getattr (evaluated_resource_cost may not be set yet on fresh components)
- [x] `component_resource_manager.py` line ~107: Kept getattr (ship.max_mass_budget is runtime-set)
- [x] Verify: tests pass (927 component tests passed)

**Notes:** Some getattr calls retained for runtime-set attributes that may not exist on fresh objects.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/ -n 12` — all pass (2594 passed)
- [x] No `getattr(ability, ...)` or `hasattr(ability, ...)` calls remain for ability properties (except legitimate meta-programming in base.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
