# PROJ-240: Ship God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-240` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-240 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract ShipComponentManager | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract ShipCombatManager | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Cache Safety and Mixin Issues | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Slim Down Ship.__init__ | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Documentation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** Planning
**Last Action:** Phase B swarm analysis complete, plan written with line numbers and code snippets
**Next Action:** Begin Phase 1 -- write tests for ShipComponentManager
**Blockers:** PROJ-241 (Component Decomposition) and PROJ-243 (Mid-Battle Fix) should complete first.
**Cross-project notes:**
- PROJ-243 adds `fleet_attack_bonus`/`fleet_defense_bonus` to Ship.__init__ — Phase 4 must incorporate these
- PROJ-241 stabilizes Component internal structure before ShipComponentManager wraps it
- After Phase 2, run simulation tests as performance checkpoint (9 delegates is a lot)
- Phase 2 should add `ship.set_event_bus(bus)` facade method to avoid 3-level delegation chain

## Overview
`game/simulation/entities/ship.py` is 850 lines with 9+ distinct responsibilities spread across __init__, component lifecycle, combat orchestration, caching, resource tracking, AI state, and serialization. Several responsibilities have already been partially extracted (ShipStatsCalculator, ShipCombatEngine, ShipSerializer, ShipPhysicsMixin, ShipStatQuerier, ShipValidatorHelper, ShipFormation) but the core class still owns component lifecycle management and combat orchestration directly. This project extracts ShipComponentManager and ShipCombatManager as proper delegates, fixes cache safety bugs, and reduces Ship to ~300 lines acting as a pure facade.

## Goals
- Extract component lifecycle (add, remove, bulk add, cache, iteration, layer management) into ShipComponentManager (~250 lines)
- Extract combat orchestration (update loop, derelict status, combat engine wiring, firing logic, projectile list) into ShipCombatManager (~200 lines)
- Fix mutable cache exposure bug (get_all_components returns internal list)
- Fix weapons cache tick-coupling that causes silent misses
- Document mixin initialization order
- Reduce Ship to ~300 lines of pure facade/delegation code

## Scope
**In Scope:**
- `game/simulation/entities/ship.py` -- decompose into facade + 2 new delegates
- New file `game/simulation/entities/ship_component_manager.py` -- component lifecycle
- New file `game/simulation/entities/ship_combat_manager.py` -- combat orchestration
- All call sites in `game/` that access extracted methods (facade preserves API)
- Tests for new managers
- Existing tests must pass without modification (facade preserves public API)

**Out of Scope:**
- ShipStatsCalculator, ShipSerializer, ShipStatQuerier -- already extracted, not touched
- ShipPhysicsMixin -- physics stays as mixin (small, 99 lines)
- ShipFormation -- already extracted
- Resource system internals (ResourceRegistry) -- not a Ship responsibility
- AI targeting logic -- only the state properties (current_target, etc.) live on Ship
- Serialization changes -- ShipSerializer is already a delegate

## Key Files
| Component | File Path | Lines |
|-----------|-----------|-------|
| Ship (god class) | `game/simulation/entities/ship.py` | 850 |
| ShipCombatEngine (existing delegate) | `game/simulation/entities/ship_combat_engine.py` | 250 |
| ShipStatsCalculator (existing delegate) | `game/simulation/entities/ship_stats.py` | 569 |
| ShipSerializer (existing delegate) | `game/simulation/entities/ship_serialization.py` | 240 |
| ShipPhysicsMixin (existing mixin) | `game/simulation/entities/ship_physics.py` | 99 |
| ShipStatQuerier (existing delegate) | `game/simulation/entities/ship_stat_querier.py` | 145 |
| ShipValidatorHelper (existing delegate) | `game/simulation/entities/ship_validator_helper.py` | 69 |
| ShipFormation (existing delegate) | `game/simulation/entities/ship_formation.py` | 112 |
| ShipLoader (existing helper) | `game/simulation/entities/ship_loader.py` | 173 |
| Ship tests | `tests/unit/entities/test_ship.py` | - |
| Component operations tests | `tests/unit/entities/ship_helpers/test_component_operations.py` | - |
| Component getter tests | `tests/unit/entities/ship_helpers/test_component_getters.py` | - |

---

## Initial Analysis

### Current Responsibility Map (ship.py lines, exact)

| # | Responsibility | Lines | Methods | Lines Count |
|---|---------------|-------|---------|-------------|
| 1 | Identity/Init | 34-192 | `__init__` | 160 |
| 2 | Default Hull | 195-212 | `_equip_default_hull` | 18 |
| 3 | Property accessors | 214-247 | `registries`, `mass`, `max_hp`, `hp` (get/set) | 34 |
| 4 | Combat engine | 253-262 | `combat_engine` property | 10 |
| 5 | Death | 264-269 | `die()` | 6 |
| 6 | Cache management | 275-278 | `_invalidate_components_cache` | 4 |
| 7 | Delegate accessors | 281-297 | `stat_querier`, `validator_helper`, `max_weapon_range` | 17 |
| 8 | Combat update | 299-336 | `update()` | 38 |
| 9 | Derelict status | 338-373 | `update_derelict_status()` | 36 |
| 10 | Layer init | 375-433 | `_initialize_layers()` | 59 |
| 11 | Class change | 435-499 | `change_class()` | 65 |
| 12 | Component attach | 501-521 | `_attach_component()` | 21 |
| 13 | Component add | 523-543 | `add_component()` | 21 |
| 14 | Component bulk | 550-582 | `add_components_bulk()` | 33 |
| 15 | Component remove | 584-592 | `remove_component()` | 9 |
| 16 | Stat recalculation | 594-613 | `recalculate_stats()` | 20 |
| 17 | Stat query delegation | 615-665 | 6 delegation methods | 51 |
| 18 | Component access | 671-800 | 8 methods (get_all, iter, by_ability, cached, by_layer, has, find, clear) | 130 |
| 19 | Validation | 802-804 | `check_validity()` | 3 |
| 20 | Serialization | 809-844 | `to_dict()`, `from_dict()` | 36 |

### Already Extracted (Existing Delegates)
- **ShipStatsCalculator** (ship_stats.py, 569 lines): 5-phase stats aggregation, physics, resources
- **ShipCombatEngine** (ship_combat_engine.py, 250 lines): Weapon firing, targeting, damage, shield regen
- **ShipSerializer** (ship_serialization.py, 240 lines): to_dict/from_dict
- **ShipStatQuerier** (ship_stat_querier.py, 145 lines): Ability totals, sensor/ECM scores
- **ShipValidatorHelper** (ship_validator_helper.py, 69 lines): Validation, missing requirements
- **ShipFormation** (ship_formation.py, 112 lines): Formation data
- **ShipPhysicsMixin** (ship_physics.py, 99 lines): Physics movement, thrust, rotation

### Bugs to Fix

**Bug 1: Mutable cache exposure** (ship.py lines 682-688)
```python
# CURRENT (BUG): Returns internal cache -- caller can corrupt it
def get_all_components(self) -> List[Component]:
    if self._components_dirty or self._components_cache is None:
        result = []
        for layer_data in self.layers.values():
            result.extend(layer_data.components)
        self._components_cache = result
        self._components_dirty = False
    return self._components_cache  # BUG: mutable reference
```
**Fix:** Return `list(self._components_cache)` (defensive copy).

**Bug 2: Weapons cache tick coupling** (ship.py lines 740-743)
```python
# CURRENT (BUG): Requires caller to know current tick
def get_weapon_components_cached(self, current_tick: int) -> List[Component]:
    if self._weapons_cache is None or self._weapons_cache_tick != current_tick:
        self._weapons_cache = self.get_components_by_ability('WeaponAbility', operational_only=True)
        self._weapons_cache_tick = current_tick
    return self._weapons_cache
```
**Fix:** Use dirty-flag invalidation like `_components_cache`. Invalidate on component add/remove.

**Bug 3: change_class silent fallback** (ship.py lines 462-465)
```python
# CURRENT: Silent fallback to empty dict
class_def = self._registries.vehicle_classes.get(self.ship_class)
if class_def is None:
    logger.error(f"Ship.change_class: Unknown vehicle class '{self.ship_class}', using defaults")
    class_def = {}
```
**Fix:** Raise `ValidationException` instead of silently falling back.

**Bug 4: Mixin MRO undocumented** (ship.py line 32)
```python
class Ship(PhysicsBody, ShipPhysicsMixin):  # MRO not explained
```
**Fix:** Add class docstring documenting MRO: PhysicsBody.__init__ called via super(), ShipPhysicsMixin has no __init__.

### External Call Site Audit

**Component lifecycle methods (to be extracted to ShipComponentManager):**

| Method | External Call Sites | Files |
|--------|-------------------|-------|
| `add_component()` | 30 calls | ship_serialization.py, battle_state.py, designs.py, vehicle_design_service.py, ship.py (change_class) |
| `add_components_bulk()` | 2 calls | vehicle_design_service.py:235, layer_panel.py:400 |
| `remove_component()` | 3 calls | vehicle_design_service.py:285, workshop_viewmodel.py:455, workshop_event_router.py:222,238 |
| `get_all_components()` | 21 calls | ship_stats.py, ship_stat_querier.py, ship_combat_engine.py, battle_engine.py, ship_validator.py, combat_endurance.py, fleet_aura_manager.py, battle_results_data.py, ai/controllable.py, ai/combat_utils.py, vehicle_design_service.py, workshop_event_router.py, component_service.py, battle_end_conditions.py |
| `get_components_by_ability()` | 11 calls | ship.py (update_derelict_status, weapon_cache), ai/target_evaluator.py, ai/combat_utils.py, ai/controller.py, ai/controllable.py, battle_ui.py |
| `iter_components()` | 2 calls | weapon_firing_system.py:66, ship_stats.py:453 |
| `get_components_by_layer()` | 1 call | ai/target_evaluator.py:189 |
| `has_components()` | 2 calls | workshop_event_router.py:357,386 |
| `find_component_with_index()` | 0 external calls | unused outside Ship |
| `clear_non_hull_components()` | 1 call | workshop_viewmodel.py:556 |
| `get_weapon_components_cached()` | 0 external calls | only Ship internal |

**Combat methods (to be extracted to ShipCombatManager):**

| Method | External Call Sites | Files |
|--------|-------------------|-------|
| `update()` | Called by battle_engine tick loop | battle_engine.py |
| `die()` | 0 direct external calls | only damage_calculator triggers via is_alive |
| `update_derelict_status()` | 2 calls | damage_calculator.py:145, battle_engine.py:297 |
| `combat_engine` property | multiple | battle_engine.py, damage_calculator.py, weapon_firing_system.py |
| `just_fired_projectiles` | 3 accesses | battle_engine.py:442-444 |
| `comp_trigger_pulled` | 1 write | ai/controllable.py:394 |

**All facade-preserved:** Ship keeps every public method signature. Zero call-site changes needed.

---

## Phases

### Phase 1: Extract ShipComponentManager [Medium]
**Objective:** Move all component lifecycle and access methods into a new delegate class
**Estimated effort:** Medium (new file, ~250 lines moved, tests for new class)
**Risk:** Low -- pure extraction with facade preservation

#### Task 1.1: Write tests for ShipComponentManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py`
**Run:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

- [ ] Test `add_component` delegates validation and attaches correctly
- [ ] Test `add_component` returns False for None component
- [ ] Test `add_components_bulk` defers recalculation until end, returns count
- [ ] Test `add_components_bulk` stops on validation failure
- [ ] Test `remove_component` by valid index returns removed component
- [ ] Test `remove_component` by invalid index returns None
- [ ] Test `get_all_components` returns correct list from all layers
- [ ] Test `get_all_components` returns **defensive copy** (not mutable cache) -- BUG FIX
- [ ] Test `get_all_components` cache invalidation on add/remove
- [ ] Test `iter_components` yields `(LayerType, Component)` tuples in layer order
- [ ] Test `get_components_by_ability` with `operational_only=True` (skips non-operational)
- [ ] Test `get_components_by_ability` with `operational_only=False` (returns all)
- [ ] Test `get_weapon_components_cached` returns same list on second call (cache hit)
- [ ] Test `get_weapon_components_cached` invalidates on component add/remove -- BUG FIX
- [ ] Test `get_components_by_layer` returns fresh list (not internal reference)
- [ ] Test `get_components_by_layer` returns empty list for missing layer
- [ ] Test `has_components` returns True when any layer has components
- [ ] Test `has_components` returns False on empty ship
- [ ] Test `find_component_with_index` returns `(LayerType, int, Component)` for match
- [ ] Test `find_component_with_index` returns None for no match
- [ ] Test `clear_non_hull_components` preserves hull, clears all others
- [ ] Test `_invalidate_components_cache` clears both `_components_cache` and `_weapons_cache`
- [ ] Run tests -- confirm they fail (no implementation yet)

#### Task 1.2: Implement ShipComponentManager [Medium]
**File:** `game/simulation/entities/ship_component_manager.py`

Create the manager class. It takes a `ship` reference and owns all component state:

```python
"""ShipComponentManager -- Component lifecycle and access for Ship.

PROJ-240 Phase 1: Extracted from Ship god class.
Ship retains facade methods that delegate here.
"""
import logging
from typing import Callable, List, Dict, Tuple, Optional, Iterator, TYPE_CHECKING

from game.core.constants import LayerType
from game.simulation.components.component import Component

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


class ShipComponentManager:
    """Manages component lifecycle, caching, and queries for a Ship.

    Owns:
    - Component add/remove/bulk operations
    - Flat component list cache (dirty-flag invalidation)
    - Weapon component cache (dirty-flag invalidation)
    - Component iteration and query methods

    Args:
        ship: The Ship instance this manager serves.
    """

    def __init__(self, ship: 'Ship') -> None:
        self._ship = ship
        # Cache state (moved from Ship.__init__ lines 129-134)
        self._components_cache: Optional[List[Component]] = None
        self._components_dirty: bool = True
        self._weapons_cache: Optional[List[Component]] = None
        self._weapons_cache_dirty: bool = True  # BUG FIX: dirty-flag replaces tick coupling
```

Methods to move (with source line numbers in ship.py):

- [ ] Move `_invalidate_components_cache` (lines 275-278) -- also invalidate `_weapons_cache_dirty`
- [ ] Move `_attach_component` (lines 501-521)
- [ ] Move `add_component` (lines 523-543)
- [ ] Move `add_components_bulk` (lines 550-582)
- [ ] Move `remove_component` (lines 584-592)
- [ ] Move `get_all_components` (lines 671-688) -- **FIX: return `list(self._components_cache)`**
- [ ] Move `iter_components` (lines 690-700)
- [ ] Move `get_components_by_ability` (lines 702-725)
- [ ] Move `get_weapon_components_cached` (lines 727-743) -- **FIX: use dirty-flag, remove tick param**
- [ ] Move `get_components_by_layer` (lines 745-760)
- [ ] Move `has_components` (lines 762-772)
- [ ] Move `find_component_with_index` (lines 774-790)
- [ ] Move `clear_non_hull_components` (lines 792-800)
- [ ] Run tests -- confirm they pass

**Key implementation detail for `get_all_components` fix:**
```python
def get_all_components(self) -> List[Component]:
    """Return a cached list of all components across all layers.

    Returns a defensive copy -- callers cannot corrupt the internal cache.
    """
    if self._components_dirty or self._components_cache is None:
        result = []
        for layer_data in self._ship.layers.values():
            result.extend(layer_data.components)
        self._components_cache = result
        self._components_dirty = False
    return list(self._components_cache)  # FIX: defensive copy
```

**Key implementation detail for `get_weapon_components_cached` fix:**
```python
def get_weapon_components_cached(self) -> List[Component]:
    """Get weapon components, cached until invalidated.

    PROJ-240: Uses dirty-flag invalidation instead of tick parameter.
    """
    if self._weapons_cache_dirty or self._weapons_cache is None:
        self._weapons_cache = self.get_components_by_ability(
            'WeaponAbility', operational_only=True
        )
        self._weapons_cache_dirty = False
    return self._weapons_cache
```

**Note on `_attach_component`:** This method does a late import of `ModifierService` (line 519). Keep the late import in the new file -- circular dependency still applies.

**Note on `add_component`:** Uses `get_or_create_validator` (line 530) and `get_default_registry_provider` (line 530). These imports move to the new file.

#### Task 1.3: Wire Ship facade to ShipComponentManager [Simple]
**File:** `game/simulation/entities/ship.py`

- [ ] Add `_component_manager` lazy property (like existing `_combat_engine` pattern at line 253):
```python
@property
def component_manager(self) -> 'ShipComponentManager':
    if self._component_manager is None:
        from .ship_component_manager import ShipComponentManager
        self._component_manager = ShipComponentManager(self)
    return self._component_manager
```
- [ ] Add `self._component_manager = None` to `__init__` (replace lines 129-134 cache vars)
- [ ] Replace 13 moved methods with one-line delegations:
```python
def add_component(self, component: Component, layer_type: LayerType) -> bool:
    return self.component_manager.add_component(component, layer_type)

def get_all_components(self) -> List[Component]:
    return self.component_manager.get_all_components()

# ... etc for all 13 methods
```
- [ ] Update `recalculate_stats` (line 599) to call `self.component_manager._invalidate_components_cache()` instead of `self._invalidate_components_cache()`
- [ ] Update `get_weapon_components_cached` signature: remove `current_tick` parameter (no callers outside Ship)
- [ ] Run existing ship tests: `pytest tests/unit/entities/test_ship.py tests/unit/entities/ship_helpers/ -v`
- [ ] Run full simulation tests: `pytest tests/unit/simulation/ -v`
- [ ] Run simulation lab: `python -m simulation_tests.run_tests --fast`

---

### Phase 2: Extract ShipCombatManager [Medium]
**Objective:** Move combat orchestration (update loop, derelict, firing) into a new delegate
**Estimated effort:** Medium (new file, ~150 lines, tests)
**Risk:** Medium -- `update()` orchestrates multiple subsystems; ordering is critical

#### Task 2.1: Write tests for ShipCombatManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_combat_manager.py`
**Run:** `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`

- [ ] Test `update()` short-circuits when `ship.is_alive` is False
- [ ] Test `update()` calls resources.update(), component.update(), recalculate_stats(), physics, combat cooldowns in order
- [ ] Test `update()` firing: when `comp_trigger_pulled=True`, `fire_weapons` results extend `just_fired_projectiles`
- [ ] Test `update()` firing: when `comp_trigger_pulled=False`, no firing occurs
- [ ] Test `update_derelict_status` crew check: insufficient crew capacity -> derelict
- [ ] Test `update_derelict_status` capability check: no weapons AND no engines -> derelict
- [ ] Test `update_derelict_status` recovery: was derelict, now has weapons -> not derelict
- [ ] Test `update_derelict_status` resets `bridge_destroyed` to False
- [ ] Test `die()` sets `is_alive=False`, zeroes velocity, calls `recalculate_stats`
- [ ] Run tests -- confirm they fail

#### Task 2.2: Implement ShipCombatManager [Medium]
**File:** `game/simulation/entities/ship_combat_manager.py`

```python
"""ShipCombatManager -- Combat orchestration for Ship.

PROJ-240 Phase 2: Extracted from Ship god class.
Ship retains facade methods that delegate here.
"""
import logging
from typing import List, Optional, Any, TYPE_CHECKING

from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.ship_combat_engine import ShipCombatEngine

logger = logging.getLogger(__name__)


class ShipCombatManager:
    """Manages combat orchestration for a Ship.

    Owns:
    - The per-tick update loop (resources, components, physics, combat, firing)
    - Derelict status computation
    - Death handling
    - Combat engine lazy initialization
    - Firing state (just_fired_projectiles, comp_trigger_pulled, aim_point)

    Args:
        ship: The Ship instance this manager serves.
    """

    def __init__(self, ship: 'Ship') -> None:
        self._ship = ship
        # Combat state (moved from Ship.__init__)
        self.just_fired_projectiles: List[Any] = []
        self.total_shots_fired: int = 0
        self.comp_trigger_pulled: bool = False
        self.aim_point: Optional[Any] = None
        self._combat_engine: Optional['ShipCombatEngine'] = None
```

Methods to move (with source line numbers in ship.py):

- [ ] Move `combat_engine` property (lines 253-262)
- [ ] Move `die()` (lines 264-269)
- [ ] Move `update()` (lines 299-336) -- update references: `self.get_all_components()` -> `self._ship.get_all_components()`, etc.
- [ ] Move `update_derelict_status()` (lines 338-373)
- [ ] Move combat state from Ship.__init__: `just_fired_projectiles` (line 158), `total_shots_fired` (line 159), `comp_trigger_pulled` (line 154), `aim_point` (line 157)
- [ ] Run tests -- confirm they pass

**Critical ordering in `update()` (lines 299-336):**
```
1. Resources update (tick-based regen)
2. Component update (consumption, cooldowns)
3. recalculate_stats (reflect operational changes)
4. Physics movement
5. Combat cooldowns (shield regen, repair)
6. Firing logic (if trigger pulled)
```
This ordering MUST be preserved exactly.

**Note on `just_fired_projectiles`:** `battle_engine.py` (lines 442-444) reads and clears this directly:
```python
if s.just_fired_projectiles:
    new_attacks.extend(s.just_fired_projectiles)
    s.just_fired_projectiles = []
```
The facade must expose `just_fired_projectiles` as a read/write property that delegates to `combat_manager`.

**Note on `comp_trigger_pulled`:** `ai/controllable.py` (line 394) writes this directly:
```python
self._ship.comp_trigger_pulled = value
```
The facade must expose this as a read/write property too.

#### Task 2.3: Wire Ship facade to ShipCombatManager [Simple]
**File:** `game/simulation/entities/ship.py`

- [ ] Add `_combat_manager` lazy property:
```python
@property
def combat_manager(self) -> 'ShipCombatManager':
    if self._combat_manager is None:
        from .ship_combat_manager import ShipCombatManager
        self._combat_manager = ShipCombatManager(self)
    return self._combat_manager
```
- [ ] Add `self._combat_manager = None` to `__init__` (replace lines 154, 157-159, 191)
- [ ] Replace `combat_engine` property with delegation to combat_manager
- [ ] Replace `update()`, `die()`, `update_derelict_status()` with delegations
- [ ] Add `just_fired_projectiles` as property delegating to combat_manager:
```python
@property
def just_fired_projectiles(self) -> List[Any]:
    return self.combat_manager.just_fired_projectiles

@just_fired_projectiles.setter
def just_fired_projectiles(self, value: List[Any]) -> None:
    self.combat_manager.just_fired_projectiles = value
```
- [ ] Add `comp_trigger_pulled` as property delegating to combat_manager:
```python
@property
def comp_trigger_pulled(self) -> bool:
    return self.combat_manager.comp_trigger_pulled

@comp_trigger_pulled.setter
def comp_trigger_pulled(self, value: bool) -> None:
    self.combat_manager.comp_trigger_pulled = value
```
- [ ] Add `aim_point` as property delegating to combat_manager
- [ ] Remove moved state from `__init__`
- [ ] Run existing tests: `pytest tests/unit/entities/test_ship.py tests/unit/simulation/ -v`
- [ ] Run integration tests: `pytest tests/integration/ -v`
- [ ] Run simulation lab: `python -m simulation_tests.run_tests --fast`

---

### Phase 3: Fix Cache Safety and Mixin Issues [Simple]
**Objective:** Fix identified bugs and document mixin order
**Estimated effort:** Simple (targeted fixes)

#### Task 3.1: Regression tests for cache safety [Simple]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py` (extend)
**Run:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

- [ ] Test that appending to `get_all_components()` result does NOT affect next call (defensive copy verified)
- [ ] Test that weapons cache auto-invalidates when `add_component` is called (no tick param needed)
- [ ] Test that weapons cache auto-invalidates when `remove_component` is called
- [ ] Run tests -- confirm they pass (should already pass if Phase 1 did the fix)

#### Task 3.2: Fix change_class fallback [Simple]
**File:** `game/simulation/entities/ship.py`
**Run:** `pytest tests/unit/entities/test_ship.py -v`

Current code (lines 462-465):
```python
class_def = self._registries.vehicle_classes.get(self.ship_class)
if class_def is None:
    logger.error(f"Ship.change_class: Unknown vehicle class '{self.ship_class}', using defaults")
    class_def = {}
```

Fix:
```python
class_def = self._registries.vehicle_classes.get(self.ship_class)
if class_def is None:
    raise ValidationException(
        f"Unknown vehicle class '{self.ship_class}'",
        code=ErrorCode.VALIDATION_ERROR.value,
        context={"class": "Ship", "method": "change_class", "ship_class": self.ship_class}
    )
```

- [ ] Write test: `change_class("nonexistent_class")` raises `ValidationException`
- [ ] Apply fix
- [ ] Run tests -- confirm pass

#### Task 3.3: Document mixin initialization order [Simple]
**File:** `game/simulation/entities/ship.py`

- [ ] Add class-level docstring to Ship:
```python
class Ship(PhysicsBody, ShipPhysicsMixin):
    """Ship entity -- facade over extracted subsystem delegates.

    Inheritance:
        PhysicsBody: Provides position, velocity, angle, forward_vector().
            __init__(x, y) called via super() in Ship.__init__.
        ShipPhysicsMixin: Provides update_physics_movement(), thrust_forward(),
            rotate(). No __init__ -- relies on Ship attributes being set first.

    Delegates:
        ShipComponentManager: Component lifecycle, caching, queries
        ShipCombatManager: Combat orchestration, derelict, death, firing
        ShipCombatEngine: Weapon firing, targeting, damage, shield regen
        ShipStatsCalculator: 5-phase stat aggregation
        ShipSerializer: to_dict / from_dict
        ShipStatQuerier: Ability totals, sensor/ECM scores
        ShipValidatorHelper: Design validation
        ShipFormation: Formation data
    """
```
- [ ] Run tests (no behavior change)

---

### Phase 4: Slim Down Ship.__init__ [Simple]
**Objective:** Group remaining __init__ properties into logical sections, remove dead code
**Estimated effort:** Simple (reorganization only)

#### Task 4.1: Organize remaining __init__ properties [Simple]
**File:** `game/simulation/entities/ship.py`

After Phases 1-2, __init__ should have lost:
- Cache state (lines 129-134) -> ShipComponentManager
- `comp_trigger_pulled` (line 154) -> ShipCombatManager
- `aim_point` (line 157) -> ShipCombatManager
- `just_fired_projectiles` (line 158) -> ShipCombatManager
- `total_shots_fired` (line 159) -> ShipCombatManager
- `_combat_engine` (line 191) -> ShipCombatManager

Group remaining into sections with headers:

```python
def __init__(self, ...):
    # === Identity ===
    # id, name, color, team_id, ship_class, theme_id, vehicle_type

    # === Registries (DI) ===
    # _registries

    # === Layers & Hull ===
    # layers, _initialize_layers, _equip_default_hull

    # === Stats (populated by ShipStatsCalculator) ===
    # mass, max_hp, hp, base_mass, total_thrust, max_speed, turn_speed, etc.

    # === Resources ===
    # resources, _resources_initialized, _prev_max_resources, etc.

    # === Combat Stats (populated by ShipStatsCalculator) ===
    # max_shields, current_shields, emissive_armor, etc.

    # === Budget & Validation ===
    # max_mass_budget, mass_limits_ok, layer_status, construction_cost

    # === AI & Targeting ===
    # current_target, secondary_targets, max_targets, ai_strategy

    # === Formation & Physics ===
    # formation, turn_throttle, engine_throttle, current_speed, etc.

    # === Delegates (lazy) ===
    # stats_calculator, _stat_querier, _validator_helper
    # _component_manager, _combat_manager
```

- [ ] Reorganize __init__ into the sections above
- [ ] Remove any properties now owned by delegates
- [ ] Verify no duplicate initialization between Ship and delegates
- [ ] Run full test suite: `python scripts/test_sharded.py`

#### Task 4.2: Verify line count targets [Simple]
- [ ] Ship.__init__ should be ~80 lines (down from ~160)
- [ ] Ship total should be ~300 lines (down from 850)
- [ ] ShipComponentManager should be ~250 lines
- [ ] ShipCombatManager should be ~150 lines
- [ ] Document final line counts in Current State

---

### Phase 5: Update Documentation [Simple]
**Objective:** Keep docs consistent with the new architecture
**Estimated effort:** Simple

#### Task 5.1: Update architecture docs [Simple]
- [ ] Update `docs/01_ARCHITECTURE.md` if Ship entity architecture is documented there
- [ ] Update `docs/02_PATTERNS.md` section 5 (Facade/Delegate) -- add ShipComponentManager and ShipCombatManager to the delegate list:
```markdown
**Ship -> ShipComponentManager delegation:** Ship lazily creates a
`ShipComponentManager` and delegates all component lifecycle operations to it.

**Ship -> ShipCombatManager delegation:** Ship lazily creates a
`ShipCombatManager` and delegates combat orchestration (update loop, derelict
status, death, firing) to it.
```
- [ ] Verify `docs/03_CONVENTIONS.md` naming conventions match new file names

#### Task 5.2: Run final verification [Simple]
- [ ] Full test suite: `python scripts/test_sharded.py`
- [ ] Simulation tests: `python -m simulation_tests.run_tests --fast`
- [ ] Verify no new imports of production types outside TYPE_CHECKING blocks
- [ ] Verify all new files have module-level docstrings

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python scripts/test_sharded.py` -- baseline established

### After Each Phase
- [ ] Run `pytest tests/unit/entities/ tests/unit/simulation/ -v` -- all affected tests pass
- [ ] No call site changes required (facade preserves public API)

### Final Verification
- [ ] `python scripts/test_sharded.py` -- full suite passes
- [ ] `python -m simulation_tests.run_tests --fast` -- simulation tests pass
- [ ] Ship.py is ~300 lines (down from 850)
- [ ] All new managers have comprehensive test coverage
- [ ] `get_all_components()` no longer exposes mutable cache
- [ ] `get_weapon_components_cached()` uses dirty-flag (no tick parameter)
- [ ] Docs updated

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Facade pattern: Ship stays as public API, delegates to managers | Consistent with PROJ-86/87/88/89 pattern per docs/02_PATTERNS.md section 5. Zero call-site changes. |
| 2026-04-05 | Layer management stays on Ship (not extracted) | `_initialize_layers` and `change_class` are identity-level operations tied to Ship construction. Moving them would create circular references with ShipComponentManager. |
| 2026-04-05 | AI state (current_target, ai_strategy) stays on Ship | Simple properties, not a responsibility -- no logic to extract. Moving would break too many AI call sites for no benefit. |
| 2026-04-05 | Resource state stays on Ship | ResourceRegistry is already a separate object; Ship just holds the reference. No logic to extract. |
| 2026-04-05 | Fix mutable cache in Phase 1 (not Phase 3) | The extraction naturally creates the opportunity to fix the return type. Phase 3 adds regression tests to prove it. |
| 2026-04-05 | `just_fired_projectiles` and `comp_trigger_pulled` exposed as Ship properties | battle_engine.py and ai/controllable.py write these directly. Property delegation preserves existing access pattern with zero call-site changes. |
| 2026-04-05 | `get_weapon_components_cached` loses tick parameter | Only used internally by Ship. Dirty-flag is simpler and more reliable. No external callers to update. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
