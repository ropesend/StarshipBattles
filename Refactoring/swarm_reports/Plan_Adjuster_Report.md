# Plan_Adjuster Report: Phase 2 - Core Logic & Stability

**Generated:** 2026-01-06
**Focus:** Detailed Specifications for Phase 2 Tasks
**Status:** Phase 1 ✅ COMPLETE | Phase 2 ⏳ PENDING

---

## Executive Summary

Phase 1 successfully established the data foundations: Hull components exist in `components.json`, `default_hull_id` is defined in `vehicleclasses.json`, and resource persistence is implemented. Phase 2 must now **bridge the data to the runtime**: auto-equipping hulls, unifying stat calculation, and purging legacy initialization patterns.

---

## Task 1: Auto-Equip `default_hull_id` in `Ship.__init__`

### Current State
```python
# ship.py:__init__ (lines ~33-40)
class_def = get_vehicle_classes().get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
self.base_mass: float = class_def.get('hull_mass', 50)  # LEGACY: Still reading hull_mass
```
The `default_hull_id` field added in Phase 1 is **never read**.

### Target State
```python
# ship.py:__init__ - AFTER REFACTOR
class_def = get_vehicle_classes().get(self.ship_class, {})
default_hull_id = class_def.get('default_hull_id')

if default_hull_id:
    hull_component = create_component(default_hull_id)
    if hull_component:
        self.add_component(hull_component, LayerType.CORE)
    else:
        print(f"WARNING: Hull component '{default_hull_id}' not found for class {self.ship_class}")
```

### Detailed Steps
1. **Import `create_component`** from `game.simulation.components.component`.
2. **Remove** the `self.base_mass` assignment from `class_def.get('hull_mass', ...)`.
3. **After `_initialize_layers()`**, call `create_component(default_hull_id)` and add to `CORE` layer.
4. **Handle edge cases:**
   - Missing `default_hull_id` → Log warning, ship has no hull (invalid state for gameplay, but valid for tests).
   - Component registry not loaded → Graceful failure (don't crash `__init__`).

### Dependencies
- `data/components.json` must contain Hull components (Phase 1 ✅).
- `data/vehicleclasses.json` must contain `default_hull_id` (Phase 1 ✅).
- Component registry must be loaded before ship instantiation.

---

## Task 2: Switch `Ship.mass` and `Ship.hp` to Cached Properties

### Current State
```python
# ship.py:__init__ (line ~42)
self.mass: float = 0.0  # Attribute, set manually

# ship.py (lines ~95-108)
@property
def max_hp(self) -> int:
    """Total HP of all components."""  # Calculated on every access - O(n) components
    total = 0
    for layer in self.layers.values():
        for c in layer['components']:
            total += c.max_hp
    return total

@property
def hp(self) -> int:
    """Current HP of all components."""  # Also O(n) on every access
    ...
```

### Target State
`ShipStatsCalculator.calculate(ship)` should set:
- `ship._cached_mass`
- `ship._cached_max_hp`

Properties should read from cache:
```python
@property
def mass(self) -> float:
    return self._cached_mass

@property
def max_hp(self) -> int:
    return self._cached_max_hp
```

### Detailed Steps
1. **Locate `ShipStatsCalculator`** (file not provided in context, likely `ship_stats.py` based on imports).
2. **In `ShipStatsCalculator.calculate()`:**
   - Sum component masses → `ship._cached_mass`
   - Sum component max_hp → `ship._cached_max_hp`
   - Sum component current_hp → `ship._cached_hp`
3. **In `Ship.__init__`:**
   - Replace `self.mass = 0.0` with `self._cached_mass = 0.0`
   - Add `self._cached_max_hp = 0` and `self._cached_hp = 0`
4. **Convert `mass`, `hp`, `max_hp` to read-only properties.**
5. **Invalidation:** `recalculate_stats()` already calls `self.stats_calculator.calculate(self)`, so cache is refreshed on component add/remove.

### File to Modify
- `ship_stats.py` (or `game/simulation/ships/ship_stats_calculator.py`)
- `ship.py`

---

## Task 3: Implement `CommandAndControl` and `CrewRequired` in `update_derelict_status`

### Current State
```python
# ship.py:update_derelict_status (lines ~164-190)
def update_derelict_status(self) -> None:
    class_def = get_vehicle_classes().get(self.ship_class, {})
    requirements = class_def.get('requirements', {})  # LEGACY: Reading from JSON
    
    # Checks requirements dict for ability minimums
    for req_ability, min_val in requirements.items():
        current_val = totals.get(req_ability, 0)
        ...
```
This uses the **legacy `requirements` dict** from `vehicleclasses.json`, which Phase 5 will remove.

### Target State
Derelict status should be determined by **ability-based checks**:
1. **`CommandAndControl` Ability:** If a ship has no operational component with this ability → Derelict.
2. **`CrewRequired` Ability:** Sum of `CrewRequired` across all components must be ≤ `CrewCapacity` provided by life support/quarters.

### Detailed Steps
1. **Define new abilities (if not already in `abilities.py`):**
   ```python
   class CommandAndControl(Ability):
       """Marks a component as a command center (Bridge, CIC, etc.)."""
       pass
   
   class CrewRequired(Ability):
       """Defines crew requirement for a component."""
       def __init__(self, component, data):
           super().__init__(component, data)
           self.crew_count = data.get('crew_count', 0)
   ```

2. **Update `update_derelict_status()`:**
   ```python
   def update_derelict_status(self) -> None:
       # Check 1: Command and Control
       has_command = False
       for layer in self.layers.values():
           for comp in layer['components']:
               if comp.is_operational and comp.has_ability('CommandAndControl'):
                   has_command = True
                   break
           if has_command:
               break
       
       if not has_command:
           self.is_derelict = True
           self.bridge_destroyed = True  # Semantic flag for UI
           return
       
       # Check 2: Crew Capacity (Optional - depends on game design)
       total_crew_req = self.get_total_ability_value('CrewRequired')
       total_crew_cap = self.get_total_ability_value('CrewCapacity')
       
       if total_crew_req > total_crew_cap:
           self.is_derelict = True
           return
       
       self.is_derelict = False
   ```

3. **Add `CommandAndControl` ability to Bridge/CIC components in `components.json`.**

### Migration Note
Until Phase 5, the legacy `requirements` check can remain as a **fallback**:
```python
# Fallback for classes without ability-based requirements
if not has_command and not requirements:
    # No command component AND no legacy requirements = assume valid
    self.is_derelict = False
```

---

## Task 4: Remove Duplicate To-Hit/Derelict Initializations

### Current State (Duplicates Found)
```python
# ship.py:__init__
# FIRST OCCURRENCE (lines ~50-51)
self.baseline_to_hit_offense = 0.0  # Score
self.to_hit_profile = 0.0  # Score

# ... 40 lines later ...

# SECOND OCCURRENCE (lines ~88-89)
self.to_hit_profile: float = 1.0       # Defensive Multiplier - DIFFERENT VALUE!
self.baseline_to_hit_offense: float = 1.0  # Offensive Multiplier - DIFFERENT VALUE!
```

### Target State
**Single initialization** with correct default values:
```python
# ship.py:__init__ - Consolidated
# Combat Modifiers
self.baseline_to_hit_offense: float = 1.0  # Offensive Multiplier (1.0 = neutral)
self.to_hit_profile: float = 1.0           # Defensive Multiplier (1.0 = neutral)
self.total_defense_score: float = 0.0      # Sum of Size + Maneuver + ECM
```

### Detailed Steps
1. **Remove lines ~50-51** (the `= 0.0` assignments).
2. **Keep lines ~88-89** (the `= 1.0` assignments with type hints).
3. **Verify `recalculate_stats()` updates these values** from `ShipStatsCalculator`.

### Derelict Initialization
```python
# Currently:
self.is_derelict: bool = False
self.bridge_destroyed: bool = False
```
These are **not duplicated**, but ensure `bridge_destroyed` is updated by `update_derelict_status()`.

---

## Task 5: Standardize MRO-Based Identity Checks

### Current State (Brittle String Checks)
```python
# ship.py:max_weapon_range (lines ~110-130)
for cls in ab.__class__.mro():
    if cls.__name__ == 'WeaponAbility':  # STRING CHECK
        is_weapon = True
        break

if ab.__class__.__name__ == 'SeekerWeaponAbility':  # STRING CHECK
    ...
```

### Target State
Use `isinstance()` with imported classes:
```python
from game.simulation.components.abilities import WeaponAbility, SeekerWeaponAbility

# In max_weapon_range
for ab in comp.ability_instances:
    if isinstance(ab, WeaponAbility):  # POLYMORPHIC CHECK
        rng = getattr(ab, 'range', 0.0)
        if isinstance(ab, SeekerWeaponAbility):
            if rng <= 0:
                rng = ab.projectile_speed * ab.endurance
        if rng > max_rng:
            max_rng = rng
```

### Locations Requiring Update
| File | Method | Line(s) | Current Pattern |
|------|--------|---------|-----------------|
| `ship.py` | `max_weapon_range` | ~115-130 | `cls.__name__ == 'WeaponAbility'` |
| `ship.py` | `max_weapon_range` | ~125 | `ab.__class__.__name__ == 'SeekerWeaponAbility'` |
| `component.py` | `get_abilities()` | ~180-190 | `cls.__name__ == ability_name` (Acceptable for dynamic lookup) |

### Exception: `component.get_abilities()`
The MRO name check in `get_abilities()` is **intentional** for dynamic ability lookup by string name. This should remain as-is since it's a fallback for when the caller doesn't have access to the class reference.

---

## Verification Checklist (Phase 3 Preview)

After Phase 2 implementation, the following tests should pass:

| Test Case | Validates |
|-----------|-----------|
| `test_ship_auto_equips_hull` | Task 1: Hull component added on init |
| `test_ship_mass_from_components` | Task 2: Mass = sum of component masses |
| `test_ship_hp_cached` | Task 2: HP properties read from cache |
| `test_derelict_on_bridge_destroyed` | Task 3: CommandAndControl logic |
| `test_no_duplicate_init` | Task 4: AST check for single init |
| `test_isinstance_checks` | Task 5: No string-based class checks |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Hull component missing from registry | High | Add null check in `__init__`, log warning |
| Cached stats stale after damage | Medium | Ensure `take_damage()` triggers recalculation |
| `CommandAndControl` ability undefined | High | Define in Phase 2, add to Bridge components |
| Circular import with abilities | Medium | Use local imports or TYPE_CHECKING pattern |

---

## Summary

Phase 2 transforms the **static data** from Phase 1 into **active runtime logic**. The critical path is:

1. **Task 1** (Hull auto-equip) → Enables Tasks 2 & 3
2. **Task 2** (Cached stats) → Performance + correctness
3. **Task 3** (Ability-based derelict) → Migrates away from legacy requirements
4. **Tasks 4 & 5** (Cleanup) → Code quality, can be parallelized

**Estimated Effort:** 2-3 hours for implementation, 1 hour for test verification.
