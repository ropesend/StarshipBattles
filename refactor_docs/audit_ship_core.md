# Audit Report: Ship Core Files

**Date:** 2026-01-02
**Target:** `ship.py`, `ship_stats.py`, `ship_physics.py`
**Objective:** Identify legacy component patterns and blocking issues for legacy removal.

## 1. `ship.py`

### Finding 1: Legacy Component Imports
- **Location:** Lines 10-15
- **Code:**
```python
from components import (
    Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, 
    Generator, BeamWeapon, ProjectileWeapon, CrewQuarters, LifeSupport, 
    Sensor, Electronics, Shield, ShieldRegenerator, SeekerWeapon,
    COMPONENT_REGISTRY, MODIFIER_REGISTRY
)
```
- **Blocking Legacy Removal?** YES
- **Recommended Fix:** Remove unused imports. If used for type hinting only, wrap in `if TYPE_CHECKING:`. Replace actual usage with `has_ability()` checks or `Component` type if generic.

### Finding 2: `max_weapon_range` Legacy Fallbacks
- **Location:** Lines 248-249
- **Code:**
```python
if max_rng == 0.0 and hasattr(comp, 'range') and hasattr(comp, 'damage'):
    rng = getattr(comp, 'range', 0)
```
- **Blocking Legacy Removal?** NO (Shim)
- **Recommended Fix:** Remove fallback once all data is migrated. If data migration (Phase 6) is complete, this block can be deleted.

### Finding 3: `get_total_sensor_score` Legacy Check
- **Location:** Line 598
- **Code:** 
```python
if isinstance(comp, Sensor) and comp.is_active:
```
- **Blocking Legacy Removal?** YES
- **Recommended Fix:** Replace with `comp.has_ability('SensorAbility')` or check for `ToHitAttackModifier` ability presence if that maps to sensors. Consider adding `SensorAbility` if not present, or use `Ability.tags`.

### Finding 4: `get_total_ecm_score` Legacy Checks
- **Location:** Lines 607, 610
- **Code:**
```python
if isinstance(comp, Electronics) and comp.is_active:
    # ...
if isinstance(comp, Armor) and comp.is_active:
```
- **Blocking Legacy Removal?** YES
- **Recommended Fix:** Replace `isinstance(Electronics)` with `comp.has_ability('EcmAbility')` or similar. Replace `isinstance(Armor)` with check for `ToHitDefenseModifier` ability or specific Armor ability.

---

## 2. `ship_stats.py`

### Finding 5: Legacy Component Imports
- **Location:** Line 1
- **Code:**
```python
from components import ComponentStatus, LayerType, Engine, Thruster, Generator, Tank, Armor, Shield, ShieldRegenerator, Weapon, Bridge, Hangar
```
- **Blocking Legacy Removal?** YES
- **Recommended Fix:** Remove imports. Use strings for classification matching if absolutely necessary (temporary), or refrain from importing subclasses entirely.

### Finding 6: Legacy Armor Classification Check (Activity)
- **Location:** Lines 72, 78
- **Code:**
```python
if comp.major_classification != "Armor":
    # ...
if comp.major_classification == "Armor" and comp.current_hp <= 0:
```
- **Blocking Legacy Removal?** YES (Relies on legacy `major_classification` field)
- **Recommended Fix:** Armor behavior (sharing HP pool vs individual threshold) should be driven by an `ArmorAbility` or a flag in `Component` data, e.g., `component.tags` containing 'armor'.

### Finding 7: Legacy Armor Classification Check (Layer Assignment)
- **Location:** Line 182
- **Code:**
```python
if comp.major_classification == "Armor":
```
- **Blocking Legacy Removal?** YES
- **Recommended Fix:** Use `comp.has_ability('ArmorAbility')` or `StructureAbility`.

### Finding 8: Redundant/Bugged Shield Calculation
- **Location:** Lines 325-330 vs Lines 187-191
- **Code:**
```python
# Lines 325-330 (OVERWRITES previous calculation!)
ship.max_shields = self._get_ability_total(component_pool, 'ShieldProjection')
ship.shield_regen_rate = self._get_ability_total(component_pool, 'ShieldRegeneration')
```
- **Blocking Legacy Removal?** YES (Critical Bug)
- **Recommended Fix:** Remove lines 325-330 entirely. The logic at Lines 187-198 correctly aggregates stats from `ability_instances`. The code at 325-330 uses `_get_ability_total` which iterates the raw `comp.abilities` dictionary, potentially missing runtime modifiers and ignoring the object-oriented design.

### Finding 9: Legacy Sorting Logic
- **Location:** Line 464
- **Code:**
```python
if t == "Engine" or t == "Thruster": return 1
```
- **Blocking Legacy Removal?** YES (Relies on `type_str`)
- **Recommended Fix:** `if comp.has_ability('CombatPropulsion') or comp.has_ability('ManeuveringThruster'): return 1`

### Finding 10: Legacy Crew/LifeSupport Dictionary Access
- **Location:** Lines 86, 91, 114
- **Code:**
```python
c_cap = abilities.get('CrewCapacity', 0)
ls_cap = abilities.get('LifeSupportCapacity', 0)
req_crew = comp.abilities.get('CrewRequired', 0)
```
- **Blocking Legacy Removal?** NO (but poor practice)
- **Recommended Fix:** Should access via `ability_instances` if these are proper abilities now. Use `comp.get_ability_value('CrewCapacity')` helper if it exists, or iterate instances.

---

## 3. `ship_physics.py`

### Finding 11: Direct Attribute Access (Minor)
- **Location:** Lines 62, 98
- **Code:**
```python
step = self.acceleration_rate
turn_per_tick = (self.turn_speed * ...)
```
- **Blocking Legacy Removal?** NO
- **Recommended Fix:** These are properties of `Ship`, meant to be calculated by `ShipStatsCalculator`. As long as the calculator is updated (see Finding 8), this is fine.

## Summary
The most critical issue is **Finding 8** in `ship_stats.py`, where the new ability-based shield calculation is being overwritten by the legacy dictionary-based aggregation. This negates the benefits of the `Ability` system for shields (modifiers to instances won't reflect).

Overall, `ship_stats.py` contains the bulk of the legacy logic that needs refactoring. `ship.py` has a few `isinstance` checks for Sensors/ECM that need a new ability-based pattern.
