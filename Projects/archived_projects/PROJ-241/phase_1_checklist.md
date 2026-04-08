# Phase 1 Checklist: Complete ModifierManager Extraction
**Status:** Complete

**Objective:** Convert ModifierManager from static namespace to stateful delegate that owns the modifiers list
**Estimated effort:** Medium (refactor existing class, move state ownership)
**Risk:** `component.modifiers` is accessed directly by 6+ production files -- facade property must be iterable + truthy-testable

## Task 1.1: Write tests for stateful ModifierManager [Medium]
**File:** `tests/unit/simulation/components/test_modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py -v`

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

## Task 1.2: Convert ModifierManager to stateful delegate [Medium]
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

## Task 1.3: Wire Component to stateful ModifierManager [Simple]
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
- [x] Update `ComponentStatsCalculator.calculate_modifier_stats` call at line 435 -- uses `self.modifiers` facade (returns delegate's list)
- [x] Deprecated static methods renamed to `_static` suffix on ModifierManager
- [x] `modifiers.setter` KEPT -- still needed by production code (modifier_utils.py, test code)

Run verification:
- [x] `pytest tests/unit/simulation/components/test_modifier_manager.py -v` -- 34 passed
- [x] `pytest tests/unit/entities/test_components.py -v` -- all pass (facade preserves API)
- [x] `pytest tests/unit/entities/test_component_di.py -v` -- all pass
- [x] `pytest tests/unit/modifiers/ -v` -- all pass
- [x] `pytest tests/unit/simulation/entities/test_ship_serialization.py -v` -- all pass (uses add_modifier)
- [x] `pytest tests/integration/ -v` -- 1113 passed, 2 skipped
**Notes:** ModifierManager now follows ComponentHealthManager/ComponentResourceManager delegate pattern. Static methods renamed to `_static` suffix for backward compat. `modifiers.setter` kept because `modifier_utils.py` and test code assign `comp.modifiers = []`.
