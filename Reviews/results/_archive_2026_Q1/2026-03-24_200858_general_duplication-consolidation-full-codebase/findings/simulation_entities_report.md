# Simulation Entities Duplication Report

**Scope:** `game/simulation/entities/`, `game/simulation/interfaces/`
**Date:** 2026-03-24
**Files Reviewed:** 17 Python files (13 entities, 4 interfaces)

---

## Summary

Found **10 duplication findings** across the simulation entities and interfaces modules. The most impactful duplications are:

1. **Physics formulas duplicated** between `ship_stats.py` and `ship_physics.py` (identical acceleration/max_speed formulas)
2. **Hull auto-equip logic** copy-pasted in `Ship.__init__` and `Ship.change_class`
3. **Component addition boilerplate** duplicated between `add_component` and `add_components_bulk`
4. **`_has_attrs` helper** defined identically in two interface modules
5. **`max_mass_budget` lookup** repeated 3 times across 2 files

Overall, the codebase is reasonably well-factored with good delegation patterns (ShipStatQuerier, ShipStatsCalculator, ShipCombatEngine, etc.). The duplication that remains is mostly within `ship.py` and between `ship_stats.py`/`ship_physics.py`.

---

## Findings

#### MAJOR: Duplicated Physics Formulas (acceleration, max_speed)
**ID:** DUP-SIM-001
**Location:** `ship_stats.py:237-241` and `ship_physics.py:33-34`
**Issue:** The acceleration and max_speed formulas are implemented identically in two places:
- `ShipStatsCalculator._phase_physics_and_limits()` computes `acceleration_rate = (thrust * K_THRUST) / (mass^2)` and `max_speed = (thrust * K_SPEED) / mass` for the **design-time** stat display.
- `ShipPhysicsMixin.update_physics_movement()` recomputes the same formulas at **runtime** from operational engine thrust.

Both import `K_SPEED` and `K_THRUST` from `physics_constants.py` and apply identical math. If the formula changes in one place but not the other, gameplay will diverge between displayed stats and actual behavior.
**Impact:** High risk of formula drift. A change to the physics model requires updating two files. The runtime version uses `get_total_ability_value('CombatPropulsion')` while the design-time version uses a pre-accumulated `ship.total_thrust`, but the core formula is identical.
**Recommendation:** Extract a shared `compute_acceleration(thrust, mass)` and `compute_max_speed(thrust, mass)` function into `physics_constants.py` or a new `physics_formulas.py`. Both call sites use the extracted functions.
**Effort:** Simple

---

#### MAJOR: Hull Auto-Equip Logic Duplicated in __init__ and change_class
**ID:** DUP-SIM-002
**Location:** `ship.py:78-88` and `ship.py:466-475`
**Issue:** The hull auto-equip sequence is copy-pasted nearly identically:
```python
default_hull_id = class_def.get('default_hull_id')
if default_hull_id:
    hull_component = create_component(default_hull_id, registries=self._registries)
    if hull_component:
        self.layers[LayerType.HULL].components.append(hull_component)
        hull_component.layer_assigned = LayerType.HULL
        hull_component.ship = self
```
The only difference is `__init__` has a warning log on failure while `change_class` does not.
**Impact:** If hull equip logic needs to change (e.g., validation, event logging), it must be updated in two places. The missing warning in `change_class` is likely a bug.
**Recommendation:** Extract `_equip_default_hull(class_def)` private method on Ship. Both `__init__` and `change_class` call it.
**Effort:** Simple

---

#### MAJOR: Component Addition Boilerplate Duplicated Between add_component and add_components_bulk
**ID:** DUP-SIM-003
**Location:** `ship.py:502-531` and `ship.py:538-576`
**Issue:** Both methods share ~15 lines of near-identical logic:
1. Call `get_or_create_validator().validate_addition()`
2. Append to layer, set `layer_assigned`, set `ship` reference
3. Call `comp.recalculate_stats()`
4. Late-import `ModifierService`, create with `self._registries.modifiers`
5. Call `service.ensure_mandatory_modifiers(component)`
6. Call `self.recalculate_stats()`

`add_components_bulk` is essentially a loop around the same logic with deferred `recalculate_stats`.
**Impact:** Any change to the component addition pipeline (e.g., new post-add hook, different validation) must be synchronized across both methods. The late import of `ModifierService` inside a loop in `add_components_bulk` is also wasteful.
**Recommendation:** Extract `_attach_component(component, layer_type) -> bool` that handles validation, attachment, and modifier setup. `add_component` calls it + `recalculate_stats()`. `add_components_bulk` loops it then calls `recalculate_stats()` once.
**Effort:** Medium

---

#### MINOR: `_has_attrs` Duck Typing Helper Duplicated Across Interface Modules
**ID:** DUP-SIM-004
**Location:** `interfaces/ability_protocols.py:315-317` and `interfaces/entity_protocols.py:480-482`
**Issue:** The `_has_attrs` function is defined identically in both modules:
```python
def _has_attrs(obj: Any, *attrs: str) -> bool:
    return all(hasattr(obj, attr) for attr in attrs)
```
Both are private helpers used by their respective TypeGuard functions.
**Impact:** Low - it's a tiny utility. But it violates DRY and if the implementation needs to change (e.g., add caching or logging), both must be updated.
**Recommendation:** Extract to a shared location, e.g., `interfaces/_type_utils.py` or directly into `interfaces/__init__.py`. Both modules import from there.
**Effort:** Simple

---

#### MINOR: `max_mass_budget` Lookup Repeated 3 Times
**ID:** DUP-SIM-005
**Location:** `ship.py:103`, `ship_stats.py:396`, `ship_stats.py:479-482`
**Issue:** The pattern `vehicle_classes.get(ship.ship_class, {}).get('max_mass', 1000)` appears three times:
1. `Ship.__init__` line 103: `class_def.get('max_mass', 1000)`
2. `ShipStatsCalculator._phase_resource_allocation` line 396: same lookup
3. `ShipStatsCalculator._check_mass_limits` line 479-482: same lookup with slightly different structure

Additionally, `ship.py:461` in `change_class` does the same thing. The magic number `1000` as the default max mass appears in all of them.
**Impact:** The default value `1000` is a magic number repeated 4 times. If the default changes, all must be updated. The redundant lookups in `_check_mass_limits` (which sets `max_mass_budget`) and `_phase_resource_allocation` (which also sets it) mean the value gets set twice during a single `calculate()` call.
**Recommendation:** Define `DEFAULT_MAX_MASS = 1000` as a named constant. Compute `max_mass_budget` once at the start of `ShipStatsCalculator.calculate()` and pass it through, or set it on ship once. Remove the redundant set in `_check_mass_limits`.
**Effort:** Simple

---

#### MINOR: Overlapping Ability Aggregation APIs (get_ability_total vs get_total_ability_value)
**ID:** DUP-SIM-006
**Location:** `ship.py:617-633`, `ship_stat_querier.py:30-78`, `ability_aggregator.py:171-182`, `ship_stats.py:544-553`
**Issue:** There are two similar but semantically different ability aggregation paths:
1. **`get_ability_total(ability_name)`** -- Uses `calculate_ability_totals()` with stack_group rules (MAX within group, SUM/MULTIPLY across groups). Goes through `ShipStatQuerier -> ShipStatsCalculator -> ability_aggregator.calculate_ability_totals()`.
2. **`get_total_ability_value(ability_name, operational_only)`** -- Simple sum using `ab.get_primary_value()`. Direct iteration in `ShipStatQuerier`.

Both are facade methods on Ship. The naming is confusingly similar (`get_ability_total` vs `get_total_ability_value`), and callers must know which one to use. `ShipStatsCalculator._get_ability_total` is a thin wrapper around `ability_aggregator.get_ability_total`.
**Impact:** API confusion. Callers must understand the subtle difference (stack_group-aware vs simple sum). Some callers may use the wrong one.
**Recommendation:** Rename for clarity: e.g., `get_stacked_ability_total()` vs `get_simple_ability_sum()`. Consider whether both are needed or if the stack-group version should always be used. Remove the thin `ShipStatsCalculator._get_ability_total` wrapper -- call `ability_aggregator.get_ability_total` directly.
**Effort:** Medium (requires updating all call sites)

---

#### MINOR: `cached_summary` Property Exists on Both Ship and ShipStatQuerier
**ID:** DUP-SIM-007
**Location:** `ship.py:533-536` and `ship_stat_querier.py:143-151`
**Issue:** Both `Ship.cached_summary` and `ShipStatQuerier.cached_summary` expose the same `_cached_summary` dict. The Ship property is used directly by callers; the ShipStatQuerier property exists but provides no additional value since it just forwards to `self._ship._cached_summary`.
**Impact:** Low. Redundant accessor that could confuse developers about which to use.
**Recommendation:** Remove `ShipStatQuerier.cached_summary`. The Ship facade property is sufficient since `_cached_summary` is populated by `combat_endurance._calculate_cached_summary()` which writes directly to the ship.
**Effort:** Simple

---

#### MINOR: Validator Helper Calls validate_design 3 Times Without Caching
**ID:** DUP-SIM-008
**Location:** `ship_validator_helper.py:44`, `ship_validator_helper.py:55`, `ship_validator_helper.py:64`
**Issue:** All three methods (`check_validity`, `get_validation_warnings`, `get_missing_requirements`) independently call `get_or_create_validator().validate_design(self._ship)`. If a caller checks validity and then asks for warnings, the full validation runs twice. Each call also reconstructs the validator-access chain `get_or_create_validator(registry_provider=get_default_registry_provider())`.
**Impact:** Performance waste when multiple validation queries are needed. The repeated `get_or_create_validator(registry_provider=get_default_registry_provider())` pattern is verbose and repeated identically 5 times across entities (3 in validator_helper, 2 in ship.py).
**Recommendation:** Add a `_validate()` method that caches the result and is invalidated when stats change. All three public methods call `_validate()`. Extract `_get_validator()` helper to reduce the boilerplate chain.
**Effort:** Simple

---

#### MINOR: Modifier Service Late Import and Creation Repeated in Loop
**ID:** DUP-SIM-009
**Location:** `ship.py:522-525` and `ship.py:567-570`
**Issue:** Both `add_component` and `add_components_bulk` perform the same late import and instantiation:
```python
from game.simulation.services.modifier_service import ModifierService
service = ModifierService(modifier_registry=self._registries.modifiers)
service.ensure_mandatory_modifiers(component)
```
In `add_components_bulk`, this happens inside a loop, creating a new `ModifierService` instance for every component added.
**Impact:** Unnecessary repeated imports and object creation. Minor performance impact in bulk operations.
**Recommendation:** Part of DUP-SIM-003 fix. Extract to `_attach_component()` and create the service once for bulk operations.
**Effort:** Simple (addressed as part of DUP-SIM-003)

---

#### MINOR: Ship.layers_dict Property Duplicates Serialization Logic from ShipSerializer.to_dict
**ID:** DUP-SIM-010
**Location:** `ship.py:800-815` and `ship_serialization.py:78-101`
**Issue:** `Ship.layers_dict` and `ShipSerializer.to_dict()` both iterate layers and serialize components to dictionaries with `id` and `modifiers`. The formats differ slightly:
- `layers_dict` includes ALL layers (including HULL) and always includes `modifiers: []`
- `to_dict` skips HULL layer and only includes `modifiers` if non-empty

Both iterate `self.layers.items()`, access `layer_data.components`, and serialize each component's `id` and `modifiers`.
**Impact:** Two similar serialization paths that could diverge. If the component dict format changes, both must be updated.
**Recommendation:** Determine if `layers_dict` is still needed. If it serves a different purpose (e.g., UI display), document that clearly. If it's unused, remove it. If both are needed, extract a shared `_serialize_component(comp)` helper.
**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Title | Severity | Effort |
|----------|-----|-------|----------|--------|
| 1 | DUP-SIM-001 | Duplicated Physics Formulas | MAJOR | Simple |
| 2 | DUP-SIM-003 | Component Addition Boilerplate | MAJOR | Medium |
| 3 | DUP-SIM-002 | Hull Auto-Equip Logic | MAJOR | Simple |
| 4 | DUP-SIM-005 | max_mass_budget Magic Number | MINOR | Simple |
| 5 | DUP-SIM-006 | Confusing Ability Aggregation APIs | MINOR | Medium |

---

## Statistics

- **MAJOR findings:** 3
- **MINOR findings:** 7
- **Total estimated effort:** 4 Simple, 2 Medium (DUP-SIM-009 merged with DUP-SIM-003)
- **Files most affected:** `ship.py` (involved in 7/10 findings), `ship_stats.py` (3/10)
