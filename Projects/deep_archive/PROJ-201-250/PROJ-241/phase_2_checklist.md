# Phase 2 Checklist: Extract AbilityIndex into AbilityManager
**Status:** Complete

**Objective:** Move ability index building and all ability-related state into AbilityManager as a proper delegate
**Estimated effort:** Medium (move logic, convert to stateful, many external readers of `ability_instances`)
**Risk:** `ability_instances` is read directly by 15+ production files -- facade property must behave identically to a list

## Task 2.1: Write tests for stateful AbilityManager [Medium]
**File:** `tests/unit/simulation/components/test_ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py -v`

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
- [x] Keep old static methods temporarily with `# DEPRECATED` comment (renamed with `_static` suffix)
- [x] Run tests -- confirm they PASS

## Task 2.3: Wire Component to stateful AbilityManager [Simple]
**File:** `game/simulation/components/component.py`

Changes to `__init__`:
- [x] Remove `self.ability_instances = []` (line 154)
- [x] Remove `self._ability_index = {}` (line 155)
- [x] Add `self._ability_mgr: AbilityManager` (eagerly initialized -- abilities needed during construction)
- [x] Replace `self._instantiate_abilities()` call with eager `AbilityManager(self)` construction

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
- [x] Simplify `get_abilities` to: `return self._ability_mgr.get_abilities(ability_name)`
- [x] Simplify `get_ability` to: `return self._ability_mgr.get_ability(ability_name)`
- [x] Simplify `has_ability` to: `return self._ability_mgr.has_ability(ability_name)`
- [x] Simplify `has_pdc_ability` to: `return self._ability_mgr.has_pdc_ability()`
- [x] Replace `_instantiate_abilities` body with delegation to `self._ability_mgr.instantiate_and_index()`
- [x] Simplify `get_ui_rows` to: `return self._ability_mgr.get_ui_rows()`
- [x] `update()` iterates via `self.ability_instances` facade -- works through delegate
- [x] `ComponentStatsCalculator.recalculate` calls `component._instantiate_abilities()` which delegates to ability_mgr
- [x] Deprecated static methods renamed with `_static` suffix
- [x] `ability_instances.setter` KEPT -- needed by test code that assigns `comp.ability_instances = [...]`

Run verification:
- [x] `pytest tests/unit/simulation/components/test_ability_manager.py -v` -- 32 passed
- [x] `pytest tests/unit/entities/test_components.py -v` -- all pass
- [x] `pytest tests/unit/entities/test_abilities.py -v` -- all pass
- [x] `pytest tests/unit/simulation/components/abilities/ -v` -- all pass
- [x] `pytest tests/unit/simulation/entities/ -v` -- all pass (ability_instances access)
- [x] `pytest tests/integration/ -v` -- 1177 passed, 2 skipped
**Notes:** AbilityManager now follows delegate pattern. Eagerly initialized (not lazy) because abilities are needed during Component.__init__. `_instantiate_abilities()` kept as thin wrapper to `ability_mgr.instantiate_and_index()` for backward compat with ComponentStatsCalculator.
