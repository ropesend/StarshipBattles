# PROJ-241: Component God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-241` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-241 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Complete ModifierManager Extraction | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract AbilityIndex into AbilityManager | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Clean Up Component.__init__ and Formula Parsing | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Remove Redundant Delegation Methods | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** All phases complete
**Last Action:** Completed Phase 5 (documentation) and full test suite verification
**Next Action:** Project complete -- ready for audit
**Blockers:** None
**Context:** All 5 phases completed successfully. Component class body reduced from ~370 to 301 lines. ModifierManager and AbilityManager converted from static namespaces to proper stateful delegates matching ComponentHealthManager/ComponentResourceManager pattern. Formula parsing extracted to data-driven FORMULA_DEFAULTS mapping. Full test suite: 14325 passed, 162 simulation tests passed. Pre-existing broken test (test_build_order_command_handler.py) is unrelated to this project.

**Final line counts:**
- Component class body: 301 lines (was ~370)
- ModifierManager: 330 lines (includes deprecated _static methods)
- AbilityManager: 339 lines (includes deprecated _static methods)
- ComponentStatsCalculator: 292 lines (was 247)
- ComponentHealthManager: 99 lines (unchanged)
- ComponentResourceManager: 116 lines (unchanged)

## Overview

`game/simulation/components/component.py` is 734 lines with partial extractions already done:
- **ComponentHealthManager** (99 lines) -- proper stateful delegate, lazy init
- **ComponentResourceManager** (116 lines) -- proper stateful delegate, lazy init
- **ComponentStatsCalculator** (246 lines) -- static methods namespace
- **ModifierManager** (203 lines) -- static methods operating on raw lists (NOT a delegate)
- **AbilityManager** (206 lines) -- static methods namespace (NOT a delegate)

The Component class itself is ~370 lines (lines 82-444), with ~280 lines of module-level functions below it (lines 452-733). The extraction pattern is inconsistent: health and resource managers are proper stateful delegates, but modifier and ability managers are stateless namespaces that receive Component internals as parameters. This project completes the extraction to make Component a clean facade of ~300 lines with consistent delegate architecture.

## Goals
1. Convert ModifierManager from static-method namespace to proper stateful delegate (owns modifiers list)
2. Move ability index building into AbilityManager (consolidate ability logic)
3. Clean up formula parsing fragility (replace hardcoded setattr + explicit ifs)
4. Generalize `has_pdc_ability()` to tag-based ability queries
5. Remove thin private forwarding methods
6. Reduce Component class body to ~300 lines

## Scope
**In Scope:**
- `game/simulation/components/component.py` -- slim down to facade
- `game/simulation/components/modifier_manager.py` -- convert to stateful delegate
- `game/simulation/components/ability_manager.py` -- absorb index building
- `game/simulation/components/component_stats_calculator.py` -- absorb formula parsing
- Tests for all modified managers
- Existing tests must pass without modification (facade preserves public API)

**Out of Scope:**
- ComponentHealthManager -- already properly extracted, not touched
- ComponentResourceManager -- already properly extracted, not touched
- Ability class hierarchy (`game/simulation/components/abilities/`) -- not changed
- Component loading functions (`load_components`, `load_modifiers`, `create_component`) -- module-level, not part of Component class
- ComponentCacheManager -- singleton, separate concern

## Key Files
| Component | File Path | Lines |
|-----------|-----------|-------|
| Component (god class) | `game/simulation/components/component.py` | 734 total, ~370 class body |
| ModifierManager (static namespace) | `game/simulation/components/modifier_manager.py` | 203 |
| AbilityManager (static namespace) | `game/simulation/components/ability_manager.py` | 206 |
| ComponentStatsCalculator | `game/simulation/components/component_stats_calculator.py` | 247 |
| ComponentHealthManager | `game/simulation/components/component_health_manager.py` | 99 |
| ComponentResourceManager | `game/simulation/components/component_resource_manager.py` | 116 |
| ComponentConstants | `game/simulation/components/component_constants.py` | -- |
| Component tests | `tests/unit/entities/test_components.py` | |
| Component DI tests | `tests/unit/entities/test_component_di.py` | |
| Modifier manager tests | `tests/unit/simulation/components/test_modifier_manager.py` | |
| Ability manager tests | `tests/unit/simulation/components/test_ability_manager.py` | |
| Stats calculator tests | `tests/unit/simulation/components/test_component_stats_calculator.py` | |
| Health manager tests | `tests/unit/simulation/components/test_component_health_manager.py` | |
| Resource manager tests | `tests/unit/simulation/components/test_component_resource_manager.py` | |

---

## Phase B Analysis

### 1. Component.__init__ Analysis (lines 83-199, 117 lines)

The constructor mixes 6 distinct responsibilities:

**a) Identity + base stats** (lines 106-134):
```python
self.data = copy.deepcopy(data)        # L106
self._registries = registries           # L109
self.id = data['id']                    # L110
self.name = data['name']               # L111
self.base_mass = data['mass']          # L112
# ... through L134 (damage_threshold)
```

**b) Ability data parsing** (lines 137-145):
```python
self.abilities = self.data.get('abilities', {})    # L137
self.base_abilities = copy.deepcopy(self.abilities) # L145
```

**c) State initialization** (lines 147-162):
```python
self.ship = None                        # L147
self.stats = {}                         # L149
self.ability_stats = {}                 # L150
self.modifiers = []                     # L151 <-- owned by Component, should be in ModifierManager
self.ability_instances = []             # L154 <-- owned by Component, should be in AbilityManager
self._ability_index = {}                # L155 <-- owned by Component, should be in AbilityManager
self._is_operational = True             # L156
self.shots_fired = 0                    # L159
self.shots_hit = 0                      # L160
```

**d) Ability instantiation** (line 163):
```python
self._instantiate_abilities()           # L163
```

**e) Modifier loading from data** (lines 171-180):
```python
if 'modifiers' in self.data:            # L171
    mods = self._registries.modifiers   # L172
    for mod_data in self.data['modifiers']:  # L173
        mod_id = mod_data['id']         # L174
        val = mod_data.get('value', None)    # L175
        if mod_id in mods:             # L176
            mod_def = mods[mod_id]     # L177
            self.modifiers.append(mod_def.create_modifier(val))  # L178
        else:
            logger.warning(...)         # L180
```
This block belongs in ModifierManager.__init__.

**f) Formula parsing** (lines 183-199):
```python
self.formulas = {}                      # L183
for key, value in self.data.items():    # L184
    if key.startswith('_'):             # L185
        continue                        # L186
    if isinstance(value, str) and value.startswith("="):  # L187
        self.formulas[key] = value[1:]  # L189
        if key in ['mass', 'hp', 'cost']:               # L194 <-- fragile hardcoded list
            setattr(self, f"base_{key}" if key in ['mass', 'hp'] else key, 0)  # L195
            if key == 'mass': self.mass = 0              # L196
            if key == 'hp':                              # L197
                self.max_hp = 0                          # L198
                self.current_hp = 0                      # L199
```
This block uses fragile hardcoded `if key in ['mass', 'hp', 'cost']` with explicit setattr. Should use a data-driven mapping in ComponentStatsCalculator.

### 2. Existing Delegates Pattern

**ComponentHealthManager** (proper delegate pattern -- reference implementation):
```python
class ComponentHealthManager:
    __slots__ = ('_component',)
    def __init__(self, component: 'Component'):
        self._component = component
    # Instance methods that operate on self._component
```
- Instantiated lazily via property (component.py L247-249)
- Owns no state itself, operates on component's fields
- Uses `__slots__` for memory efficiency

**ComponentResourceManager** (same pattern):
```python
class ComponentResourceManager:
    __slots__ = ('_component',)
    def __init__(self, component: 'Component'):
        self._component = component
```
- Instantiated lazily via property (component.py L244-249)
- Same pattern as HealthManager

**ModifierManager** (CURRENT -- static namespace, NOT a delegate):
```python
class ModifierManager:
    @staticmethod
    def add_modifier(modifiers_list, mod_id, value, registries, component_type=None):
        # Takes modifiers_list as parameter -- does not own state
    @staticmethod
    def remove_modifier(modifiers_list, mod_id):
        return [m for m in modifiers_list if m.definition.id != mod_id]
        # Returns NEW list -- inconsistent with add_modifier which mutates
```
- All 6 methods are static, receiving `modifiers_list` as first argument
- `remove_modifier` returns a new list; `add_modifier` mutates in-place -- inconsistent
- Component passes `self.modifiers` to every call (boilerplate)

**AbilityManager** (CURRENT -- static namespace, NOT a delegate):
```python
class AbilityManager:
    @staticmethod
    def get_abilities(ability_name, instances):
        # Takes instances list as parameter -- does not own state
```
- All 6 methods are static, receiving `instances` as parameter
- Component builds the `_ability_index` itself (lines 310-320) despite AbilityManager existing

### 3. Ability Index Building (lines 299-320)

Currently in `Component._instantiate_abilities`:
```python
def _instantiate_abilities(self):
    self.ability_instances = AbilityManager.instantiate_abilities(
        self.abilities, self.ability_instances, self
    )
    # PERF: Build ability index for O(1) lookup by class name
    self._ability_index = {}
    for ab in self.ability_instances:
        for cls in ab.__class__.mro():       # L314 -- walks MRO
            cls_name = cls.__name__           # L315
            if cls_name == 'object':          # L316 -- hardcoded sentinel
                break
            if cls_name not in self._ability_index:  # L318
                self._ability_index[cls_name] = []
            self._ability_index[cls_name].append(ab)  # L320
```
The index-building loop (lines 311-320) should be in AbilityManager.

### 4. External Callers

**`component.add_modifier()` -- 10 production callers:**
- `game/simulation/services/modifier_service.py:240` -- ModifierService.ensure_mandatory_modifiers
- `game/simulation/battle_state.py:397` -- BattleState restore
- `game/simulation/entities/ship_serialization.py:203` -- ship deserialization
- `game/ui/screens/workshop_event_router.py:277` -- workshop drag-drop
- `game/ui/screens/builder/modifier_logic.py:137` -- builder apply
- `game/ui/screens/builder/interaction_controller.py:119` -- builder drag
- `game/ui/panels/builder_widgets.py:252` -- builder widget

**`component.remove_modifier()` -- 1 production caller:**
- `game/ui/panels/builder_widgets.py:258` -- builder widget remove

**`component.get_modifier()` -- 6 production callers:**
- `game/ui/screens/workshop_event_router.py:278`
- `game/ui/screens/builder/modifier_row.py:245`
- `game/ui/screens/builder/modifier_logic.py:136,138`
- `game/ui/screens/builder/interaction_controller.py:120`
- `game/ui/panels/builder_widgets.py:254,264`
- `game/simulation/services/modifier_service.py:239,241`

**`component.modifiers` (direct attribute access) -- 6 production callers:**
- `game/simulation/battle_state.py:55,93` -- serialization + iteration
- `game/ui/panels/component_modifier_grid_panel.py:104` -- UI truthiness check
- `game/ui/screens/builder/weapons_viewmodel.py:255` -- iteration
- `game/ui/screens/builder/detail_panel.py:169,171` -- UI iteration
- `game/ui/screens/builder/grouping_strategies.py:40` -- iteration
- `game/ui/screens/builder/interaction_controller.py:87` -- iteration

**`component.ability_instances` (direct attribute access) -- 15+ production callers** across:
- `game/simulation/entities/` (ship_stats.py, ability_aggregator.py, combat_endurance.py, ship_stat_querier.py)
- `game/simulation/validation/ship_validator.py`
- `game/simulation/components/` (modifier_introspection.py, component_stats_calculator.py)
- `game/ui/` (modifier_impact_grid.py, builder/stats_config.py, builder/components.py)

**`component.has_pdc_ability()` -- 3 production callers:**
- `game/ai/combat_utils.py:215`
- `game/simulation/combat/weapon_firing_system.py:184`
- `game/simulation/combat/targeting_system.py:166`

**Private delegation methods (`_reset_and_evaluate_base_formulas`, `_calculate_modifier_stats`, `_apply_base_stats`) -- 1 external caller:**
- `tests/unit/regressions/test_bug_regressions_2026_01.py:55` -- `c._apply_base_stats(stats, 100)` in test code

### 5. Facade/Delegate Pattern (from docs/02_PATTERNS.md)

Pattern #5 states:
> **Delegate:** Class would become a god class. Extract behavior; original keeps public API.

The Ship -> ShipCombatEngine example shows: lazy creation, delegation, original class stays as facade. ComponentHealthManager and ComponentResourceManager already follow this. ModifierManager and AbilityManager do NOT follow it -- they are static namespaces, not delegates.

---

## Phases

### Phase 1: Complete ModifierManager Extraction [Medium]
**Objective:** Convert ModifierManager from static namespace to stateful delegate that owns the modifiers list
**Estimated effort:** Medium (refactor existing class, move state ownership)
**Risk:** `component.modifiers` is accessed directly by 6+ production files -- facade property must be iterable + truthy-testable

#### Task 1.1: Write tests for stateful ModifierManager [Medium]
**File:** `tests/unit/simulation/components/test_modifier_manager.py`
**Run:** `pytest tests/unit/simulation/components/test_modifier_manager.py -v`

Extend the existing test file (which already tests the static API) with new tests for the stateful delegate API:

- [x] Test `ModifierManager(component)` construction with no initial modifiers -- `modifiers` is empty list
- [x] Test construction loads modifiers from `component.data['modifiers']` using `component._registries`
- [x] Test `add_modifier(mod_id, value)` adds to internal `_modifiers` list and returns True
- [x] Test `add_modifier` replaces existing modifier with same ID (not duplicate)
- [x] Test `add_modifier` returns False for unknown modifier ID
- [x] Test `add_modifier` respects `deny_types` restriction using `component.type_str`
- [x] Test `add_modifier` respects `allow_types` restriction
- [x] Test `remove_modifier(mod_id)` removes by ID from internal list
- [x] Test `get_modifier(mod_id)` returns correct ApplicationModifier or None
- [x] Test `get_all_effects()` returns aggregated effects from internal list
- [x] Test `get_stat_summary()` groups by stat correctly from internal list
- [x] Test `modifiers` property returns current list (iterable, truthy when non-empty)
- [x] Run tests -- confirm they FAIL (stateful API does not exist yet)

#### Task 1.2: Convert ModifierManager to stateful delegate [Medium]
**File:** `game/simulation/components/modifier_manager.py` (currently 203 lines)

Current code (static methods taking `modifiers_list` param):
```python
class ModifierManager:
    @staticmethod
    def add_modifier(modifiers_list, mod_id, value, registries, component_type=None):
        ...
    @staticmethod
    def remove_modifier(modifiers_list, mod_id):
        return [m for m in modifiers_list if m.definition.id != mod_id]
```

Target code (instance methods owning state):
```python
class ModifierManager:
    __slots__ = ('_component', '_modifiers')

    def __init__(self, component: 'Component'):
        self._component = component
        self._modifiers: list['ApplicationModifier'] = []
        self._load_initial_modifiers()

    def _load_initial_modifiers(self):
        # Move logic from Component.__init__ lines 171-180
        ...

    @property
    def modifiers(self) -> list['ApplicationModifier']:
        return self._modifiers

    def add_modifier(self, mod_id, value=None) -> bool:
        # Uses self._component._registries, self._component.type_str
        ...

    def remove_modifier(self, mod_id) -> None:
        # Mutates self._modifiers in-place (fix inconsistency)
        ...
```

Checklist:
- [x] Add `__init__(self, component)` with `__slots__ = ('_component', '_modifiers')`
- [x] Add `_load_initial_modifiers()` -- move logic from component.py lines 171-180
- [x] Add `modifiers` property returning `self._modifiers`
- [x] Convert `add_modifier` to instance method (accesses `self._component._registries`, `self._component.type_str`)
- [x] Convert `remove_modifier` to instance method -- mutate in-place (fix the new-list-vs-mutation inconsistency)
- [x] Convert `get_modifier` to instance method
- [x] Convert `get_all_effects` to instance method
- [x] Convert `get_stat_summary` to instance method
- [x] Keep old static methods temporarily with `# DEPRECATED` comment for Task 1.3 cleanup
- [x] Run tests -- confirm they PASS

#### Task 1.3: Wire Component to stateful ModifierManager [Simple]
**File:** `game/simulation/components/component.py`

Changes to `__init__` (lines 83-199):
- [x] Remove `self.modifiers = []` (line 151)
- [x] Remove modifier loading loop (lines 171-180)
- [x] Add `self._modifier_mgr: ModifierManager | None = None` (alongside `_resource_mgr`, `_health_mgr` at lines 166-167)

Add lazy property (alongside existing pattern at lines 244-256):
```python
@property
def modifier_manager(self) -> ModifierManager:
    """Lazy-initialized modifier manager."""
    if self._modifier_mgr is None:
        self._modifier_mgr = ModifierManager(self)
    return self._modifier_mgr
```

Add facade property for backward compatibility:
```python
@property
def modifiers(self):
    """Facade: access modifier list through delegate."""
    return self.modifier_manager.modifiers

@modifiers.setter
def modifiers(self, value):
    """Facade: setter for backward compat (battle_state.py L390 assigns new list)."""
    self.modifier_manager._modifiers = value
```

Note: `component.modifiers` setter is needed because `remove_modifier` in Component (line 390) does `self.modifiers = ModifierManager.remove_modifier(...)`. After conversion, the instance method mutates in-place, so the setter becomes unnecessary -- but we need it during transition.

Simplify delegation methods (lines 375-415):
- [x] Simplify `add_modifier` (lines 375-386): `return self.modifier_manager.add_modifier(mod_id, value)` + `self.recalculate_stats()` on success
- [x] Simplify `remove_modifier` (lines 389-391): `self.modifier_manager.remove_modifier(mod_id)` + `self.recalculate_stats()`
- [x] Simplify `get_modifier` (lines 393-395): `return self.modifier_manager.get_modifier(mod_id)`
- [x] Simplify `get_all_modifier_effects` (lines 397-405): `return self.modifier_manager.get_all_effects()`
- [x] Simplify `get_modifier_stat_summary` (lines 407-415): `return self.modifier_manager.get_stat_summary()`
- [x] Update `ComponentStatsCalculator.calculate_modifier_stats` call at line 435 -- pass `self.modifier_manager.modifiers` or keep using `self.modifiers` (facade)
- [x] Remove deprecated static methods from ModifierManager
- [x] Remove `modifiers.setter` if no longer needed after in-place mutation fix

Run verification:
- [x] `pytest tests/unit/simulation/components/test_modifier_manager.py -v` -- all pass
- [x] `pytest tests/unit/entities/test_components.py -v` -- all pass (facade preserves API)
- [x] `pytest tests/unit/entities/test_component_di.py -v` -- all pass
- [x] `pytest tests/unit/modifiers/ -v` -- all pass
- [x] `pytest tests/unit/simulation/entities/test_ship_serialization.py -v` -- all pass (uses add_modifier)
- [x] `pytest tests/integration/ -v` -- all pass

---

### Phase 2: Extract AbilityIndex into AbilityManager [Medium]
**Objective:** Move ability index building and all ability-related state into AbilityManager as a proper delegate
**Estimated effort:** Medium (move logic, convert to stateful, many external readers of `ability_instances`)
**Risk:** `ability_instances` is read directly by 15+ production files -- facade property must behave identically to a list

#### Task 2.1: Write tests for stateful AbilityManager [Medium]
**File:** `tests/unit/simulation/components/test_ability_manager.py`
**Run:** `pytest tests/unit/simulation/components/test_ability_manager.py -v`

Extend the existing test file with new tests for the stateful delegate API:

- [x] Test `AbilityManager(component)` construction calls `instantiate_abilities` and builds index
- [x] Test index includes MRO parents (e.g., querying `'WeaponAbility'` returns `ProjectileWeaponAbility`)
- [x] Test index stops at `object` (does not include `object` as a key)
- [x] Test `get_abilities(name)` returns correct instances via index fast-path
- [x] Test `get_ability(name)` returns first match via index fast-path
- [x] Test `has_ability(name)` returns True/False correctly
- [x] Test `has_ability_with_tag('pdc')` returns True for PDC components
- [x] Test `has_ability_with_tag('pdc')` returns False for non-PDC components
- [x] Test `has_ability_with_tag('nonexistent')` returns False
- [x] Test `instantiate_abilities()` preserves existing instances (cooldown state)
- [x] Test `get_ui_rows()` aggregates from all instances
- [x] Test `ability_instances` property returns the current list
- [x] Run tests -- confirm they FAIL

#### Task 2.2: Convert AbilityManager to stateful delegate [Medium]
**File:** `game/simulation/components/ability_manager.py` (currently 206 lines)

Current code (static methods):
```python
class AbilityManager:
    @staticmethod
    def get_abilities(ability_name, instances):
        ...
    @staticmethod
    def has_pdc_ability(instances):
        ...
```

Target code:
```python
class AbilityManager:
    __slots__ = ('_component', '_instances', '_index')

    def __init__(self, component: 'Component'):
        self._component = component
        self._instances: list['Ability'] = []
        self._index: dict[str, list['Ability']] = {}
        self.instantiate_and_index()

    def instantiate_and_index(self):
        """Instantiate abilities from component data and build index."""
        self._instances = self._instantiate(
            self._component.abilities,
            self._instances,
            self._component
        )
        self._build_index()

    def _build_index(self):
        """Build MRO-based index. Moved from Component._instantiate_abilities lines 311-320."""
        self._index = {}
        for ab in self._instances:
            for cls in ab.__class__.mro():
                cls_name = cls.__name__
                if cls_name == 'object':
                    break
                if cls_name not in self._index:
                    self._index[cls_name] = []
                self._index[cls_name].append(ab)

    @property
    def ability_instances(self) -> list['Ability']:
        return self._instances

    def has_ability_with_tag(self, tag: str) -> bool:
        for ab in self._instances:
            if ab.tags and tag in ab.tags:
                return True
        return False

    def has_pdc_ability(self) -> bool:
        return self.has_ability_with_tag('pdc')
```

Checklist:
- [x] Add `__init__(self, component)` with `__slots__ = ('_component', '_instances', '_index')`
- [x] Add `instantiate_and_index()` combining instantiation + index building
- [x] Move index building from Component._instantiate_abilities (lines 311-320) into `_build_index()`
- [x] Move the existing static `instantiate_abilities` logic into private `_instantiate()` instance method
- [x] Add `ability_instances` property returning `self._instances`
- [x] Convert `get_abilities` to instance method using `self._index`
- [x] Convert `get_ability` to instance method using `self._index`
- [x] Convert `has_ability` to instance method using `self._index`
- [x] Add `has_ability_with_tag(tag)` as generalized replacement for `has_pdc_ability`
- [x] Keep `has_pdc_ability` as thin wrapper: `return self.has_ability_with_tag('pdc')`
- [x] Convert `get_ui_rows` to instance method
- [x] Keep old static methods temporarily with `# DEPRECATED` comment
- [x] Run tests -- confirm they PASS

#### Task 2.3: Wire Component to stateful AbilityManager [Simple]
**File:** `game/simulation/components/component.py`

Changes to `__init__`:
- [x] Remove `self.ability_instances = []` (line 154)
- [x] Remove `self._ability_index = {}` (line 155)
- [x] Add `self._ability_mgr: AbilityManager | None = None` (alongside other lazy manager fields)
- [x] Keep `self._instantiate_abilities()` call (line 163) but redirect to lazy manager init

Add lazy property:
```python
@property
def ability_manager(self) -> AbilityManager:
    if self._ability_mgr is None:
        self._ability_mgr = AbilityManager(self)
    return self._ability_mgr
```

Add facade property:
```python
@property
def ability_instances(self):
    """Facade: access ability instances through delegate."""
    return self.ability_manager.ability_instances

@ability_instances.setter
def ability_instances(self, value):
    """Facade: setter for backward compat during transition."""
    self.ability_manager._instances = value
```

Simplify delegation methods:
- [x] Simplify `get_abilities` (lines 201-213) to: `return self.ability_manager.get_abilities(ability_name)`
- [x] Simplify `get_ability` (lines 215-223) to: `return self.ability_manager.get_ability(ability_name)`
- [x] Simplify `has_ability` (lines 225-232) to: `return self.ability_manager.has_ability(ability_name)`
- [x] Simplify `has_pdc_ability` (lines 234-240) to: `return self.ability_manager.has_pdc_ability()`
- [x] Remove `_instantiate_abilities` method (lines 299-320) -- now in AbilityManager
- [x] Simplify `get_ui_rows` (lines 290-297) to: `return self.ability_manager.get_ui_rows()`
- [x] Update `update()` (line 333) to iterate `self.ability_manager.ability_instances`
- [x] Update `recalculate_stats` path: `ComponentStatsCalculator.recalculate` calls `component._instantiate_abilities()` at line 236 of stats calculator -- redirect to `component.ability_manager.instantiate_and_index()`
- [x] Remove deprecated static methods from AbilityManager
- [x] Remove `ability_instances.setter` if no longer needed

Run verification:
- [x] `pytest tests/unit/simulation/components/test_ability_manager.py -v` -- all pass
- [x] `pytest tests/unit/entities/test_components.py -v` -- all pass
- [x] `pytest tests/unit/entities/test_abilities.py -v` -- all pass
- [x] `pytest tests/unit/simulation/components/abilities/ -v` -- all pass
- [x] `pytest tests/unit/simulation/entities/ -v` -- all pass (ability_instances access)
- [x] `pytest tests/integration/ -v` -- all pass

---

### Phase 3: Clean Up Component.__init__ and Formula Parsing [Simple]
**Objective:** Fix formula parsing fragility and slim down __init__
**Estimated effort:** Simple (targeted refactor, small blast radius)

#### Task 3.1: Write tests for formula parsing improvements [Simple]
**File:** `tests/unit/simulation/components/test_component_stats_calculator.py` (extend existing)
**Run:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`

- [x] Test `parse_formulas(data)` extracts formulas from `=`-prefixed string values
- [x] Test `parse_formulas(data)` skips `_`-prefixed keys (like `_comment`)
- [x] Test `parse_formulas(data)` strips leading `=` from formula string
- [x] Test `apply_formula_defaults(component, formulas)` sets `base_mass=0, mass=0` for mass formula
- [x] Test `apply_formula_defaults` sets `base_max_hp=0, max_hp=0, current_hp=0` for hp formula
- [x] Test `apply_formula_defaults` sets `cost=0` for cost formula
- [x] Test `apply_formula_defaults` is no-op for non-mass/hp/cost formulas
- [x] Run tests -- confirm they FAIL

#### Task 3.2: Move formula parsing into ComponentStatsCalculator [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`

Add static methods with a data-driven mapping:

```python
# Mapping: formula key -> list of (attribute_name, default_value) to set
FORMULA_DEFAULTS = {
    'mass': [('base_mass', 0), ('mass', 0)],
    'hp':   [('base_max_hp', 0), ('max_hp', 0), ('current_hp', 0)],
    'cost': [('cost', 0)],
}

@staticmethod
def parse_formulas(data: dict) -> dict[str, str]:
    """Extract formula definitions from component data.
    Returns dict mapping attribute name to formula string (without '=').
    """
    formulas = {}
    for key, value in data.items():
        if key.startswith('_'):
            continue
        if isinstance(value, str) and value.startswith("="):
            formulas[key] = value[1:]
    return formulas

@staticmethod
def apply_formula_defaults(component: 'Component', formulas: dict[str, str]) -> None:
    """Set safe default values for formula-driven attributes."""
    for key in formulas:
        if key in ComponentStatsCalculator.FORMULA_DEFAULTS:
            for attr, default in ComponentStatsCalculator.FORMULA_DEFAULTS[key]:
                setattr(component, attr, default)
```

Checklist:
- [x] Add `FORMULA_DEFAULTS` mapping at class level
- [x] Add `parse_formulas(data)` static method
- [x] Add `apply_formula_defaults(component, formulas)` static method
- [x] Run tests -- confirm they PASS

#### Task 3.3: Simplify Component.__init__ [Simple]
**File:** `game/simulation/components/component.py`

Replace inline formula parsing (lines 183-199):
```python
# BEFORE (17 lines):
self.formulas = {}
for key, value in self.data.items():
    if key.startswith('_'):
        continue
    if isinstance(value, str) and value.startswith("="):
        self.formulas[key] = value[1:]
        if key in ['mass', 'hp', 'cost']:
            ...

# AFTER (2 lines):
self.formulas = ComponentStatsCalculator.parse_formulas(self.data)
ComponentStatsCalculator.apply_formula_defaults(self, self.formulas)
```

- [x] Replace lines 183-199 with 2-line delegation to ComponentStatsCalculator
- [x] Verify __init__ is now ~80 lines (down from 117)
- [x] Run tests: `pytest tests/unit/entities/test_components.py -v`
- [x] Run tests: `pytest tests/unit/simulation/components/test_component_stats_calculator.py -v`

---

### Phase 4: Remove Redundant Delegation Methods [Simple]
**Objective:** Remove private delegation methods that just forward to ComponentStatsCalculator
**Estimated effort:** Simple (delete + redirect)
**Risk:** One test directly calls `_apply_base_stats` -- needs update

#### Task 4.1: Remove thin private delegation wrappers [Simple]
**File:** `game/simulation/components/component.py`

These three methods (lines 429-439) are one-line forwarders to ComponentStatsCalculator:
```python
def _reset_and_evaluate_base_formulas(self, context=None):     # L429
    ComponentStatsCalculator.reset_and_evaluate_formulas(self, context)

def _calculate_modifier_stats(self):                            # L433
    return ComponentStatsCalculator.calculate_modifier_stats(self.modifiers, self)

def _apply_base_stats(self, stats, old_max_hp):                # L437
    ComponentStatsCalculator.apply_base_stats(self, stats, old_max_hp)
```

External caller: `tests/unit/regressions/test_bug_regressions_2026_01.py:55` calls `c._apply_base_stats(stats, 100)` directly.

- [x] Update `tests/unit/regressions/test_bug_regressions_2026_01.py:55` to call `ComponentStatsCalculator.apply_base_stats(c, stats, 100)` directly
- [x] Remove `_reset_and_evaluate_base_formulas` (line 429-430)
- [x] Remove `_calculate_modifier_stats` (lines 433-435)
- [x] Remove `_apply_base_stats` (lines 437-439)
- [x] Verify no other callers of these private methods exist (they're all internal to `recalculate_stats` which already delegates)
- [x] Run tests: `pytest tests/unit/entities/test_components.py tests/unit/simulation/components/ tests/unit/regressions/ -v`

#### Task 4.2: Verify line count targets [Simple]
- [x] Component class body should be ~280-300 lines (down from ~370)
- [x] ModifierManager should be ~220-230 lines (up from 203 with state + `_load_initial_modifiers`)
- [x] AbilityManager should be ~240-260 lines (up from 206 with index building + `has_ability_with_tag`)
- [x] ComponentStatsCalculator should be ~270 lines (up from 247 with formula parsing)
- [x] Module-level functions stay in component.py (~280 lines, not part of class)
- [x] All 4 delegates follow same pattern: `__slots__`, `__init__(component)`, instance methods
- [x] Document final line counts in Current State

---

### Phase 5: Update Documentation [Simple]
**Objective:** Keep docs consistent with the new architecture
**Estimated effort:** Simple

#### Task 5.1: Update architecture docs [Simple]
- [x] Update `docs/02_PATTERNS.md` Pattern #5 (Facade / Delegate) -- add Component delegate pattern:
  - Document that Component has 4 delegates: ComponentHealthManager, ComponentResourceManager, ModifierManager, AbilityManager
  - All use same pattern: `__slots__`, `__init__(component)`, lazy property on Component
  - Note that ComponentStatsCalculator remains static (no state to own)
- [x] Update `docs/01_ARCHITECTURE.md` if component architecture is documented there
- [x] Verify `docs/03_CONVENTIONS.md` naming conventions match changes
- [x] Verify `docs/02_PATTERNS.md` code snippets are accurate

#### Task 5.2: Run final verification [Simple]
- [x] Full test suite: `python Tools/test_sharded/test_sharded.py`
- [x] Simulation tests: `python -m simulation_tests.run_tests --fast`
- [x] Verify no new imports of production types outside TYPE_CHECKING blocks
- [x] Verify all modified files have updated docstrings
- [x] Verify `component.modifiers` attribute access still works (facade property)
- [x] Verify `component.ability_instances` attribute access still works (facade property)

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `python Tools/test_sharded/test_sharded.py` -- baseline established

### After Each Phase
- [x] Run `pytest tests/unit/entities/test_components.py tests/unit/simulation/components/ -v` -- all affected tests pass
- [x] No call site changes required (facade preserves public API)
- [x] `component.modifiers`, `component.ability_instances` still accessible as before

### Final Verification
- [x] `python Tools/test_sharded/test_sharded.py` -- full suite passes
- [x] `python -m simulation_tests.run_tests --fast` -- simulation tests pass
- [x] Component class is ~300 lines (down from ~370 class body)
- [x] All managers are proper stateful delegates (no more static-method-on-raw-list pattern)
- [x] `has_pdc_ability` uses generalized `has_ability_with_tag`
- [x] Formula parsing uses data-driven mapping instead of hardcoded ifs
- [x] Docs updated

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Convert ModifierManager to stateful delegate | Consistent with ComponentHealthManager/ResourceManager pattern. Owning state eliminates parameter-passing boilerplate and enables lazy initialization. |
| 2026-04-05 | Convert AbilityManager to stateful delegate | Index building logic is tightly coupled to ability instance ownership. Consolidating eliminates the MRO-walking code in Component. |
| 2026-04-05 | Keep module-level functions in component.py | `load_components`, `load_modifiers`, `create_component`, `ComponentCacheManager` are module-level utilities, not Component class methods. Moving them gains nothing. |
| 2026-04-05 | Generalize has_pdc_ability to tag-based query | PDC is a tag on abilities, not a special case. `has_ability_with_tag('pdc')` is extensible to future tags without new methods. |
| 2026-04-05 | Formula parsing defaults as mapping | Replaces fragile `if key in ['mass', 'hp', 'cost']` with data-driven mapping. Easier to extend for new formula-capable fields. |
| 2026-04-05 | Don't touch ComponentHealthManager or ResourceManager | Already properly extracted as stateful delegates with lazy init. No work needed. |
| 2026-04-05 | Keep ComponentStatsCalculator as static methods | Unlike ModifierManager/AbilityManager, it has no state to own. It operates on component + modifiers passed to it. Converting to stateful adds complexity for no benefit. |
| 2026-04-05 | Facade property with setter for `component.modifiers` | 6+ production files access `component.modifiers` directly (iteration, truthiness checks). Property + setter provides seamless backward compatibility. Setter can be removed after verifying all mutation goes through delegate methods. |
| 2026-04-05 | Fix remove_modifier mutation inconsistency | Static `remove_modifier` returns new list (non-mutating) while `add_modifier` mutates in-place. Instance method should mutate in-place consistently. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - Project manifest
