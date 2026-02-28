# Phase 7: Strategy Deferred Import Analysis

## Overview

This document analyzes deferred imports (imports inside function bodies) in the strategy data layer.
These imports exist to avoid circular dependencies but indicate architectural coupling issues.

---

## Fleet.py Deferred Imports

**File:** `game/strategy/data/fleet.py`

### 1. Line 88: FleetMobilityService in _trigger_speed_recalculation()
```python
def _trigger_speed_recalculation(self):
    from game.strategy.services.fleet_mobility_service import FleetMobilityService
    FleetMobilityService.recalculate_fleet_speed(self)
```
**Why:** FleetMobilityService may have transitive imports back to Fleet
**Circular Chain:** Fleet -> fleet_mobility_service -> (potential Fleet reference)
**Resolution Options:**
- A) Accept service as parameter instead of importing
- B) Keep deferred (speed recalculation is an edge operation)
- C) Dependency injection via constructor

**Recommendation:** Option B - Keep deferred import. This is called only when ships
are added/removed from the fleet, which is an edge operation. The coupling is legitimate
(fleet speed depends on ship composition).

---

### 2. Line 110: ShipStatsService in can_use_warp()
```python
def can_use_warp(self) -> bool:
    from game.strategy.services.ship_stats_service import ShipStatsService
    ...
    if not ShipStatsService.has_warp_capability(ship):
```
**Why:** ShipStatsService may have transitive imports through component handling
**Circular Chain:** Fleet -> ship_stats_service -> (potential component/ship dependencies)
**Resolution Options:**
- A) Accept service as parameter
- B) Keep deferred (warp check is a query operation)
- C) Move logic to ShipInstance

**Recommendation:** Option B - Keep deferred import. The method is a query and the
service encapsulates warp capability logic that requires component inspection.

---

### 3. Line 128: ShipStatsService in get_warp_limiting_ship()
```python
def get_warp_limiting_ship(self) -> Optional['ShipInstance']:
    from game.strategy.services.ship_stats_service import ShipStatsService
    ...
    if not ShipStatsService.has_warp_capability(ship):
```
**Why:** Same as #2
**Circular Chain:** Same as #2
**Resolution:** Same as #2 - consolidate with can_use_warp

---

### 4. Line 573: ShipInstance in from_dict()
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Fleet':
    from game.strategy.data.ship_instance import ShipInstance
    ...
    fleet.ships.append(ShipInstance.from_dict(ship_data))
```
**Why:** ShipInstance is in same package, potential circular type hints
**Circular Chain:** Fleet -> ship_instance -> (Fleet reference in type hints)
**Resolution Options:**
- A) Keep deferred (serialization is special case)
- B) Move to module level (already have TYPE_CHECKING import)
- C) Extract deserialization to separate module

**Recommendation:** Option B - Move to module level. ShipInstance is already imported
with TYPE_CHECKING for type hints, so the circular dependency is already handled.
The runtime import can safely be at module level since ship_instance.py doesn't
import Fleet at module level.

---

## ShipInstance.py Deferred Imports

**File:** `game/strategy/data/ship_instance.py`

### 1. Line 125: ShipSerializer in from_ship()
```python
@classmethod
def from_ship(cls, ship: 'Ship', owner_id: int) -> 'ShipInstance':
    from game.simulation.entities.ship_serialization import ShipSerializer
    design_data = ShipSerializer.to_dict(ship)
```
**Why:** Cross-layer import (strategy -> simulation)
**Circular Chain:** ship_instance -> ship_serialization -> ship -> (potential ship_instance ref)
**Resolution Options:**
- A) Keep deferred (cross-layer boundary import)
- B) Accept serializer as parameter
- C) Extract to factory function

**Recommendation:** Option A - Keep deferred import. This is a cross-layer boundary
import (strategy importing from simulation). The import is legitimate and the
deferred pattern avoids any potential circular issues at module load time.

---

### 2. Line 189: ShipStatsService in get_calculated_stats()
```python
def get_calculated_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
    if self._cached_stats is None or force_refresh:
        from game.strategy.services.ship_stats_service import ShipStatsService
        self._cached_stats = ShipStatsService.calculate_stats(...)
```
**Why:** ShipStatsService imports from ship_instance or has transitive dependencies
**Circular Chain:** ship_instance -> ship_stats_service -> (potential circular)
**Resolution Options:**
- A) Keep deferred (stats calculation is lazy)
- B) Inject service at construction
- C) Move stats calculation to ShipInstance

**Recommendation:** Option A - Keep deferred import. The import is inside a lazy
initialization pattern (cached stats). The service encapsulates complex stats
calculation that shouldn't be in ShipInstance directly.

---

### 3. Lines 597-598: ShipSerializer and log_debug in to_ship()
```python
def to_ship(self, position: Tuple[float, float], team_id: int) -> 'Ship':
    from game.simulation.entities.ship_serialization import ShipSerializer
    from game.core.logger import log_debug
    ship = ShipSerializer.from_dict(self.design_data)
```
**Why:** Cross-layer import (strategy -> simulation)
**Circular Chain:** Same as #1
**Resolution Options:**
- A) Keep deferred (cross-layer boundary import)
- B) log_debug can move to module level (no circular risk)

**Recommendation:**
- ShipSerializer: Option A - Keep deferred (cross-layer)
- log_debug: Option B - Move to module level (log_debug is already imported at line 19)

**Note:** Actually, log_warning is imported at module level (line 19), and log_debug
is from the same module. This can be consolidated.

---

## Summary Table

| Location | Import | Recommendation | Action |
|----------|--------|----------------|--------|
| fleet.py:88 | FleetMobilityService | Keep deferred | Document |
| fleet.py:110 | ShipStatsService | Keep deferred | Document |
| fleet.py:128 | ShipStatsService | Keep deferred | Document |
| fleet.py:573 | ShipInstance | Move to module level | Refactor |
| ship_instance.py:125 | ShipSerializer | Keep deferred | Document |
| ship_instance.py:189 | ShipStatsService | Keep deferred | Document |
| ship_instance.py:597 | ShipSerializer | Keep deferred | Document |
| ship_instance.py:598 | log_debug | Move to module level | Refactor |

---

## Recommended Actions

### Immediate Fixes (Low Risk)
1. **Move log_debug to module level** in ship_instance.py (consolidate with log_warning)
2. **Move ShipInstance import to module level** in fleet.py (no actual circular)

### Document as Intentional (No Change)
3. FleetMobilityService deferred imports (edge operations)
4. ShipStatsService deferred imports (lazy calculation, encapsulation)
5. ShipSerializer deferred imports (cross-layer boundary)

---

## Decision: FleetHelperService

The checklist mentions creating `FleetHelperService` to wrap service calls.

**NOT RECOMMENDED** - After analysis:
- The service deferred imports in Fleet are acceptable (edge operations, queries)
- Creating a wrapper service adds complexity without solving the root issue
- The coupling is legitimate (fleet operations need service capabilities)
- Service calls are already class methods, not instance methods requiring DI

Instead, document the deferred imports as intentional architectural decisions.

---

## Key Observations

1. **Fleet.py has minimal deferred imports** - Only 4 deferred imports, all reasonable:
   - 2 for FleetMobilityService/ShipStatsService (service queries)
   - 1 for ShipInstance (can be fixed)

2. **ShipInstance.py deferred imports are cross-layer** - Most imports are from
   simulation layer, which is appropriate to keep deferred to maintain layer separation.

3. **No deep circular chains** - Unlike Phase 6 findings, these imports don't create
   deep dependency chains. They're mostly service lookups or cross-layer boundaries.

4. **TYPE_CHECKING already used** - Both files use TYPE_CHECKING for type hints,
   showing the pattern is already established.
