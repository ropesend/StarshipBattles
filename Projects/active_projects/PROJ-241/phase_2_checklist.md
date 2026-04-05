# Phase 2 Checklist: Extract AbilityIndex into AbilityManager
**Status:** Not Started

**Objective:** Move ability index building and all ability-related state into AbilityManager as a proper delegate
**Estimated effort:** Medium (move logic, convert to stateful, many external readers of `ability_instances`)
**Risk:** `ability_instances` is read directly by 15+ production files -- facade property must behave identically to a list

## Task 2.1: Write tests for stateful AbilityManager [Medium]
**File:** `tests/unit/simulation/components/test_ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py -v`

Extend the existing test file with new tests for the stateful delegate API:

- [ ] Test `AbilityManager(component)` construction calls `instantiate_abilities` and builds index
- [ ] Test index includes MRO parents (e.g., querying `'WeaponAbility'` returns `ProjectileWeaponAbility`)
- [ ] Test index stops at `object` (does not include `object` as a key)
- [ ] Test `get_abilities(name)` returns correct instances via index fast-path
- [ ] Test `get_ability(name)` returns first match via index fast-path
- [ ] Test `has_ability(name)` returns True/False correctly
- [ ] Test `has_ability_with_tag('pdc')` returns True for PDC components
- [ ] Test `has_ability_with_tag('pdc')` returns False for non-PDC components
- [ ] Test `has_ability_with_tag('nonexistent')` returns False
- [ ] Test `instantiate_abilities()` preserves existing instances (cooldown state)
- [ ] Test `get_ui_rows()` aggregates from all instances
- [ ] Test `ability_instances` property returns the current list
- [ ] Run tests -- confirm they FAIL

## Task 2.2: Convert AbilityManager to stateful delegate [Medium]
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

- [ ] Add `__init__(self, component)` with `__slots__ = ('_component', '_instances', '_index')`
- [ ] Add `instantiate_and_index()` combining instantiation + index building
- [ ] Move index building from Component._instantiate_abilities (lines 311-320) into `_build_index()`
- [ ] Move the existing static `instantiate_abilities` logic into private `_instantiate()` instance method
- [ ] Add `ability_instances` property returning `self._instances`
- [ ] Convert `get_abilities` to instance method using `self._index`
- [ ] Convert `get_ability` to instance method using `self._index`
- [ ] Convert `has_ability` to instance method using `self._index`
- [ ] Add `has_ability_with_tag(tag)` as generalized replacement for `has_pdc_ability`
- [ ] Keep `has_pdc_ability` as thin wrapper: `return self.has_ability_with_tag('pdc')`
- [ ] Convert `get_ui_rows` to instance method
- [ ] Keep old static methods temporarily with `# DEPRECATED` comment
- [ ] Run tests -- confirm they PASS

## Task 2.3: Wire Component to stateful AbilityManager [Simple]
**File:** `game/simulation/components/component.py`

Changes to `__init__`:
- [ ] Remove `self.ability_instances = []` (line 154)
- [ ] Remove `self._ability_index = {}` (line 155)
- [ ] Add `self._ability_mgr: AbilityManager | None = None` (alongside other lazy manager fields)
- [ ] Keep `self._instantiate_abilities()` call (line 163) but redirect to lazy manager init

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
- [ ] Simplify `get_abilities` (lines 201-213) to: `return self.ability_manager.get_abilities(ability_name)`
- [ ] Simplify `get_ability` (lines 215-223) to: `return self.ability_manager.get_ability(ability_name)`
- [ ] Simplify `has_ability` (lines 225-232) to: `return self.ability_manager.has_ability(ability_name)`
- [ ] Simplify `has_pdc_ability` (lines 234-240) to: `return self.ability_manager.has_pdc_ability()`
- [ ] Remove `_instantiate_abilities` method (lines 299-320) -- now in AbilityManager
- [ ] Simplify `get_ui_rows` (lines 290-297) to: `return self.ability_manager.get_ui_rows()`
- [ ] Update `update()` (line 333) to iterate `self.ability_manager.ability_instances`
- [ ] Update `recalculate_stats` path: `ComponentStatsCalculator.recalculate` calls `component._instantiate_abilities()` at line 236 of stats calculator -- redirect to `component.ability_manager.instantiate_and_index()`
- [ ] Remove deprecated static methods from AbilityManager
- [ ] Remove `ability_instances.setter` if no longer needed

Run verification:
- [ ] `pytest tests/unit/simulation/components/test_ability_manager.py -v` -- all pass
- [ ] `pytest tests/unit/entities/test_components.py -v` -- all pass
- [ ] `pytest tests/unit/entities/test_abilities.py -v` -- all pass
- [ ] `pytest tests/unit/simulation/components/abilities/ -v` -- all pass
- [ ] `pytest tests/unit/simulation/entities/ -v` -- all pass (ability_instances access)
- [ ] `pytest tests/integration/ -v` -- all pass
**Notes:**
