# Phase 6: Deferred Import Analysis

## Overview

This document analyzes deferred imports (imports inside function bodies) in the simulation layer.
These imports exist to avoid circular dependencies but indicate architectural coupling issues.

---

## Ship.py Deferred Imports

**File:** `game/simulation/entities/ship.py`

### 1. Line 262: WeaponAbility, SeekerWeaponAbility in max_weapon_range
```python
@property
def max_weapon_range(self) -> float:
    from game.simulation.components.abilities import SeekerWeaponAbility, WeaponAbility
```
**Why:** `abilities.py` may import from ship.py (for Ship type hints or component context)
**Circular Chain:** Ship -> abilities -> (potential Ship reference)
**Resolution Options:**
- A) Use TYPE_CHECKING for the ability types (isinstance won't work at runtime)
- B) Use duck typing / Protocol instead of isinstance
- C) Keep deferred (abilities are rarely needed at module load)

**Recommendation:** Option B - Use hasattr/duck typing or add `is_weapon_ability` property

---

### 2. Line 517: ModifierService in add_component()
```python
def add_component(self, component: Component, layer_type: LayerType) -> bool:
    ...
    from game.simulation.services.modifier_service import ModifierService
    ModifierService.ensure_mandatory_modifiers(component)
```
**Why:** ModifierService imports Component, which may reference Ship
**Circular Chain:** Ship -> modifier_service -> component -> Ship
**Resolution Options:**
- A) Pass ModifierService to Ship via constructor (DI)
- B) Have component apply its own modifiers
- C) Create IModifierApplicator protocol
- D) Keep deferred (only needed on component addition)

**Recommendation:** Option D - This is a reasonable deferred import; modifier application
is an edge operation, not core ship functionality.

---

### 3. Line 558: ModifierService in add_components_bulk()
```python
def add_components_bulk(self, component: Component, layer_type: LayerType, count: int) -> int:
    ...
    from game.simulation.services.modifier_service import ModifierService
    ModifierService.ensure_mandatory_modifiers(new_comp)
```
**Why:** Same as #2
**Circular Chain:** Same as #2
**Resolution:** Same as #2 - consolidated with add_component

---

### 4. Line 588: ShipStatsCalculator in recalculate_stats()
```python
def recalculate_stats(self) -> None:
    if not self.stats_calculator:
         from .ship_stats import ShipStatsCalculator
         self.stats_calculator = ShipStatsCalculator(...)
```
**Why:** ShipStatsCalculator likely imports Ship for type hints
**Circular Chain:** Ship -> ship_stats -> Ship (type hint)
**Resolution Options:**
- A) Move ShipStatsCalculator import to module level with TYPE_CHECKING guard
- B) Pass stats calculator to Ship constructor (DI)
- C) Keep deferred (lazy initialization pattern)

**Recommendation:** Option C - This is intentional lazy initialization. The import only
happens once (first recalculate_stats call), then the instance is cached. This is an
acceptable performance optimization.

**NOTE:** Line 15 already has `from .ship_stats import ShipStatsCalculator` at module level!
This deferred import at line 588 is REDUNDANT and can be removed.

---

### 5. Line 808: ShipSerializer in to_dict()
```python
def to_dict(self) -> Dict[str, Any]:
    from .ship_serialization import ShipSerializer
    return ShipSerializer.to_dict(self)
```
**Why:** ShipSerializer imports Ship for type hints and to create Ship instances
**Circular Chain:** Ship -> ship_serialization -> Ship
**Resolution Options:**
- A) Make serialization external (ShipSerializer.serialize(ship))
- B) Keep deferred (serialization is I/O operation, not performance critical)
- C) Use TYPE_CHECKING in ship_serialization.py

**Recommendation:** Option B - Serialization is inherently coupled to Ship. The deferred
import is a reasonable pattern for this bidirectional dependency.

---

### 6. Line 827: ShipSerializer in from_dict()
```python
@staticmethod
def from_dict(data: Dict[str, Any]) -> 'Ship':
    from .ship_serialization import ShipSerializer
    return ShipSerializer.from_dict(data)
```
**Why:** Same as #5
**Resolution:** Same as #5

---

## Stats.py Deferred Imports

**File:** `game/simulation/systems/stats.py`

### 1. Line 20: ResourceStorage, ResourceGeneration in calculate()
```python
def calculate(self, ship):
    from game.simulation.systems.resource_manager import ResourceStorage, ResourceGeneration
```
**Why:** resource_manager may import from stats or ship
**Circular Chain:** stats -> resource_manager -> (potential component/ship reference)
**Resolution Options:**
- A) Move to module level (if no actual circular dependency)
- B) Use duck typing instead of isinstance
- C) Keep deferred

**Recommendation:** Option A - Test if this can be moved to module level. ResourceStorage
and ResourceGeneration are data classes that shouldn't have circular dependencies.

---

### 2. Line 172-173: CombatPropulsion, ManeuveringThruster, etc. in calculate()
```python
from game.simulation.components.abilities import CombatPropulsion, ManeuveringThruster, ShieldProjection, ShieldRegeneration
from game.simulation.systems.resource_manager import ResourceConsumption
```
**Why:** abilities.py is large and may have transitive dependencies
**Circular Chain:** stats -> abilities -> (potential transitive imports)
**Resolution Options:**
- A) Move to module level if safe
- B) Use duck typing / Protocol
- C) Keep deferred

**Recommendation:** Option B - These are used for isinstance checks. The code already uses
`comp.get_abilities('CombatPropulsion')` which is ability-name-based. The isinstance
checks at lines 156, 165, 200, 360 can be replaced with duck typing.

---

### 3. Line 337: ResourceConsumption in _calculate_combat_endurance()
```python
def _calculate_combat_endurance(self, ship, component_pool):
    from game.simulation.systems.resource_manager import ResourceConsumption
```
**Why:** Already imported at line 173, this is REDUNDANT
**Resolution:** Remove this import - it's already imported in the calling function

---

### 4. Line 429: WeaponAbility in _calculate_combat_endurance()
```python
from game.simulation.components.abilities import WeaponAbility
```
**Why:** abilities.py dependency
**Circular Chain:** stats -> abilities -> (transitive)
**Resolution Options:**
- A) Use duck typing (check for reload_time and damage attributes)
- B) Keep deferred
- C) Move to module level

**Recommendation:** Option A - The code uses `c.get_abilities('WeaponAbility')` which
already handles the lookup. The isinstance check is redundant.

---

## Summary Table

| Location | Import | Recommendation | Action |
|----------|--------|----------------|--------|
| ship.py:262 | WeaponAbility, SeekerWeaponAbility | Duck typing | Refactor |
| ship.py:517 | ModifierService | Keep deferred | Document |
| ship.py:558 | ModifierService | Keep deferred | Document |
| ship.py:588 | ShipStatsCalculator | Remove (redundant) | Fix |
| ship.py:808 | ShipSerializer | Keep deferred | Document |
| ship.py:827 | ShipSerializer | Keep deferred | Document |
| stats.py:20 | ResourceStorage, ResourceGeneration | Try module level | Test |
| stats.py:172-173 | Abilities + ResourceConsumption | Duck typing | Refactor |
| stats.py:337 | ResourceConsumption | Remove (redundant) | Fix |
| stats.py:429 | WeaponAbility | Duck typing | Refactor |

---

## Recommended Actions

### Immediate Fixes (Low Risk)
1. **Remove redundant import** at ship.py:588 (ShipStatsCalculator already at module level)
2. **Remove redundant import** at stats.py:337 (ResourceConsumption already imported at 173)

### Refactoring (Medium Risk)
3. **Duck typing for abilities** - Replace isinstance checks with attribute checks
4. **Test module-level imports** - Try moving ResourceStorage/ResourceGeneration to module level

### Document as Intentional (No Change)
5. ModifierService deferred imports (edge operation)
6. ShipSerializer deferred imports (bidirectional coupling is inherent)

---

## Decision: Interface Creation

The checklist mentions creating `IModifierApplicator` interface. After analysis:

**NOT RECOMMENDED** - The ModifierService deferred import is acceptable:
- Only called during component addition (not hot path)
- The coupling is legitimate (modifiers need component context)
- Interface would add complexity without solving the root issue

Instead, document the deferred import as intentional architectural decision.
