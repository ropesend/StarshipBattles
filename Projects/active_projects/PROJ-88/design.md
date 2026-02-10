# PROJ-88: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Three god classes identified in the simulation core tier via the PROJ-84 audit:

1. **Ship** (`game/simulation/entities/ship.py`): 870 lines, 136 importers
2. **Component** (`game/simulation/components/component.py`): 756 lines, 161 importers
3. **Game/app.py** (`game/app.py`): 723 lines, 4 importers

All three exceed the 500-line threshold. Ship and Component have CRITICAL importer counts, meaning any API-breaking change cascades across 100+ files. The decomposition strategy must preserve existing public APIs via facade methods.

## Findings Summary

### Ship (870 lines, 136 importers)

**History:** PROJ-12 extracted `ShipComponentManager` as a god class decomposition. However, it was **never adopted** -- Ship still has all 11 component methods inline. Subsequently, PROJ-49 added dirty-flag caching to Ship's `get_all_components()` and tick-based `get_weapon_components_cached()`, which permanently diverges from the uncached ShipComponentManager extraction. Zero production files import ShipComponentManager.

**Method Groups (by cohesion):**
- **Component Access** (7 methods, ~100 lines): `get_all_components`, `iter_components`, `get_components_by_ability`, `get_weapon_components_cached`, `get_components_by_layer`, `has_components`, `find_component_with_index` -- Already thin, well-cached from PROJ-49. Leave in Ship.
- **Component Mutation** (5 methods, ~120 lines): `add_component`, `add_components_bulk`, `remove_component`, `change_class`, `clear_non_hull_components` -- Core Ship responsibility. Leave in Ship.
- **Stat Aggregation** (6 methods, ~80 lines): `get_ability_total`, `get_total_ability_value`, `get_total_ecm_score`, `get_total_sensor_score`, `max_weapon_range`, `cached_summary` -- Cohesive query group, extractable.
- **Validation** (3 methods, ~30 lines): `check_validity`, `get_validation_warnings`, `get_missing_requirements` -- Cohesive validation group, extractable.
- **Lifecycle/Physics/Combat**: Already delegated to `ShipPhysicsMixin`, `ShipCombatEngine`, `ShipStatsCalculator`, `ShipFormation`.

**Dead Code:** `ship_component_manager.py` (345 lines) -- zero production imports. Only imported by its own test files:
- `tests/unit/entities/test_ship_component_manager_di.py`
- `tests/unit/simulation/ship_component_manager/conftest.py`
- `tests/unit/simulation/ship_component_manager/test_creation_and_layers.py`
- `tests/unit/simulation/ship_component_manager/test_queries_and_iteration.py`

### Component (756 lines, 161 importers)

**Structure:** 463 lines for the Component class (31 methods + ComponentCacheManager), 293 lines for module-level loader functions. The loaders are already well-separated.

**Method Groups (by cohesion):**
- **Ability Access** (5 methods): `get_abilities`, `get_ability`, `has_ability`, `has_pdc_ability`, `get_ui_rows` -- Already delegates to AbilityManager. Leave as-is.
- **Modifier Management** (5 methods): `add_modifier`, `remove_modifier`, `get_modifier`, `get_all_modifier_effects`, `get_modifier_stat_summary` -- Already delegates to ModifierManager. Leave as-is.
- **Stats Calculation** (3 methods): `recalculate_stats`, `_reset_and_evaluate_base_formulas`, `_calculate_modifier_stats` -- Already delegates to ComponentStatsCalculator. Leave as-is.
- **Resource/Activation** (4 methods, ~80 lines): `can_afford_activation`, `try_activate`, `consume_activation`, `get_resource_cost` -- Cohesive resource concern, extractable.
- **Health/Damage** (3 methods, ~40 lines): `take_damage`, `reset_hp`, `hp_ratio` -- Cohesive health concern, extractable.
- **Core** (remaining): `__init__`, `update`, `is_operational`, `clone`, `_instantiate_abilities`, `cooldown_timer` -- Must stay in Component.

**Hot Path Concern:** `can_afford_activation` and `try_activate` are called during weapon firing every tick. Extraction must not add function call overhead beyond a single method delegation.

### Game/app.py (723 lines, 4 importers)

**Structure:** 41 methods in the Game class. PROJ-65 introduced the IScene protocol and `_switch_scene()` method, and most scenes now use unified dispatch via `active_scene.handle_event()`.

**Legacy Dispatch (still present):**
- `_handle_click()` (lines 573-582): Still dispatches `handle_click(mx, my, button)` to StrategyScreen
- `_handle_scroll()` (lines 652-659): Still dispatches `handle_scroll(event.y, height)` to StrategyScreen
- `_update_and_draw()` (lines 661-686): Still calls `update_input(dt, events)` for StrategyScreen, and `handle_input(dt, events)` for ResearchTree and GalaxyTest

**StrategyScreen IScene Status:**
- Has `handle_event()` method (line 213) that delegates to `self._input.handle_event()`
- Still has separate `handle_click()` (line 217) that delegates to `self._input.handle_click()`
- Has `update_input()` (line 221) which processes keyboard/mouse state per-frame
- Does NOT have `handle_scroll()` -- this is called directly from app.py

**Blast Radius:** Only 4 files import from `game.app` (launcher.py, 2 test files, 1 legacy doc). Changes to app.py are LOW risk.

### Blast Radius Summary
| Class | Importers | Risk |
|-------|-----------|------|
| Component | 161 | CRITICAL -- facade mandatory |
| Ship | 136 | HIGH -- facade mandatory |
| Game/app | 4 | LOW -- can refactor freely |

### Test Coverage Summary
| Class | Test Files | Quality |
|-------|-----------|---------|
| Component | ~130 | EXCELLENT -- comprehensive unit, integration, regression coverage |
| Ship | ~95 | EXCELLENT -- comprehensive unit, integration, regression coverage |
| Game/app | 2 | POOR -- only test_app_integration.py and test_strategy_menu_actions.py |

## Architecture

### Extraction Pattern: Facade + Helper

For Ship and Component, we use the **Facade Pattern**:
1. Create a new helper class (e.g., `ShipStatQuerier`) with the extracted logic
2. Ship/Component creates the helper as a composed member (e.g., `self._stat_querier`)
3. Ship/Component retains the original public methods as one-line facades that delegate to the helper
4. **No callers change** -- 136/161 importers continue using `ship.get_ability_total()` etc.
5. The helper class can be tested independently with a mock ship/component

This is the same pattern already used for:
- `ShipStatsCalculator` (stats calculation)
- `ShipCombatEngine` (combat logic)
- `AbilityManager`, `ModifierManager`, `ComponentStatsCalculator` (component sub-concerns)

### Lazy vs Eager Initialization

Helpers should use **lazy initialization** (created on first use) to avoid import cycles and keep `__init__` fast:
```python
@property
def _stat_querier(self):
    if not hasattr(self, '__stat_querier'):
        self.__stat_querier = ShipStatQuerier(self)
    return self.__stat_querier
```

### IScene Completion Strategy

StrategyScreen needs to fold `handle_click()` and scroll handling into `handle_event()`:
1. In `handle_event()`, detect `MOUSEBUTTONDOWN` events and call internal click logic
2. In `handle_event()`, detect `MOUSEWHEEL` events and call internal scroll logic
3. Fold `update_input()` frame-based input into `update(dt)` or keep as separate call
4. Remove legacy dispatch from app.py's `_handle_click()`, `_handle_scroll()`, `_update_and_draw()`

## Key Patterns to Reuse

- **ShipCombatEngine pattern** (`ship.py:210-222`): Lazy property initialization with late import to avoid cycles
- **AbilityManager delegation** (`component.py:193-224`): Static methods on helper, component passes self data
- **ShipStatsCalculator pattern** (`ship.py:573-591`): Helper created once, called with ship reference
- **_switch_scene()** (`app.py:154-157`): Clean state + scene assignment pattern from PROJ-65

## Dependencies & Risks

1. **Component hot path performance** -- Resource methods are called every tick during combat. Extraction must use direct method delegation, not dynamic dispatch. Mitigation: benchmark before/after with simulation stress test.
2. **Ship stat cache coherency** -- `_cached_summary` and stat aggregation are intertwined. The querier must invalidate properly. Mitigation: existing tests cover stat recalculation thoroughly.
3. **StrategyScreen event migration** -- Moving click/scroll into handle_event could subtly change event ordering. Mitigation: test_strategy_menu_actions.py covers key interactions; manual smoke test recommended.
4. **Import cycle risk** -- New helper files in `entities/` and `components/` must not create circular imports. Mitigation: Use TYPE_CHECKING imports and lazy initialization per existing patterns.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
