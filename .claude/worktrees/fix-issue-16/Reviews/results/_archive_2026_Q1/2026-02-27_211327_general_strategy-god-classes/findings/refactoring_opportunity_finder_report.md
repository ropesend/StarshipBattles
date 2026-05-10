# Refactoring Opportunity Finder Report
## Strategy God Classes - Fleet, Planet, ShipInstance

**Review Date:** 2026-02-27
**Reviewer:** Code Review Agent (Refactoring Opportunities)
**Scope:** Strategy data tier god classes (~9,250 lines across 33 files)

---

## Summary

- **Total issues found:** 14
- **Critical:** 3 (god class bloat, serialization complexity, embedded classes)
- **Major:** 6 (order management, resource tracking, facility management)
- **Minor:** 3 (property facades, helper consolidation)
- **Info:** 2 (delegate patterns assessment)

**Key Findings:**
1. **FleetOrder serialization** is a 40-line conditional mess that should be extracted
2. **Planet embeds 3 separate concerns** (facilities, populations, grid topology) in one file
3. **Fleet order queue** management duplicates list operations and lacks encapsulation
4. **Construction queue** appears on both Fleet and Planet with identical structure but no shared abstraction
5. **Existing delegates are excellent** — FleetResourceAggregator, FleetCapabilityCalculator, and ShipResourceManager all follow clean patterns

---

## Findings

### CRITICAL: FleetOrder Serialization God Method
**ID:** ROF-001
**Location:** `game/strategy/data/fleet.py:75-113` (FleetOrder.to_dict)
**Issue:** 40-line method with 7 different target format branches (transfer, planet_ref, ship_id_list, warp_params, HexCoord, Fleet, raw). This violates SRP and makes the order class responsible for understanding all possible target types.

**Impact:**
- Every new order type adds another conditional branch
- Circular import risks (late import of Planet at runtime)
- from_dict (lines 389-483) has matching complexity with 7 format handlers
- Difficult to test all serialization paths
- Violates Tell Don't Ask (inspecting target types)

**Recommendation:**
Extract **OrderSerializer** service with strategy pattern:
```python
# game/strategy/services/order_serializer.py
class OrderSerializer:
    def __init__(self):
        self._serializers = {
            OrderType.TRANSFER: self._serialize_transfer,
            OrderType.IMPLODE_PLANET: self._serialize_planet_ref,
            OrderType.SELF_DESTRUCT: self._serialize_ship_list,
            # etc.
        }

    def serialize_order(self, order: FleetOrder) -> Dict[str, Any]:
        serializer = self._serializers.get(order.type, self._serialize_default)
        target_data = serializer(order.target)
        return {'type': order.type.name, 'target': target_data, ...}

    def deserialize_order(self, data: Dict) -> FleetOrder:
        # Mirror logic with deserializer registry
```

Benefits:
- Each order type has isolated serialization logic
- Easy to add new order types (register new handler)
- No circular imports (service can import Planet safely)
- Testable per order type

**Effort:** Medium (2-3 hours)
- Create OrderSerializer service
- Extract 7 format handlers
- Update Fleet.to_dict/from_dict to delegate
- Write tests for each format

---

### CRITICAL: Planet Embeds Multiple Classes
**ID:** ROF-002
**Location:** `game/strategy/data/planet.py:35-149` (PlanetaryFacility + SpeciesPopulation)
**Issue:** Planet.py contains 3 separate classes in one 500-line file:
1. **PlanetaryFacility** (lines 35-149) — 114 lines, 7 methods, separate lifecycle
2. **SpeciesPopulation** (lines 151-183) — 32 lines, dataclass
3. **Planet** (lines 185-500) — 315 lines, main class

Additionally, Planet mixes 4 distinct concerns:
- Physical properties (mass, radius, atmosphere)
- Economic/resource tracking (resources dict, facilities list)
- Multi-hex zone topology (occupied_hexes, diameter_hexes)
- Construction queue management (construction_queue, can_build_type)

**Impact:**
- Planet is at risk of god class bloat (already 315 lines)
- PlanetaryFacility is a domain entity that deserves its own file
- SpeciesPopulation is reusable but buried in planet.py
- Difficult to understand which methods belong to which concern

**Recommendation:**
**Phase 1:** Extract embedded classes (Simple extraction)
- Move **PlanetaryFacility** → `game/strategy/data/planetary_facility.py`
- Move **SpeciesPopulation** → `game/strategy/data/species_population.py`
- Update imports in planet.py

**Phase 2:** Extract Planet delegates (Facade/delegate pattern)
- Create **PlanetFacilityManager** delegate (lines 306-335)
  - `has_space_shipyard` property
  - `can_build_type()` method
  - Facility fuel storage aggregation
- Create **PlanetResourceManager** delegate
  - `resources` dict management
  - Resource tracking (add_fuel methods on PlanetaryFacility)
- Create **PlanetTopologyManager** delegate
  - `occupied_hexes` calculation
  - Multi-hex zone support (diameter_hexes)

Benefits:
- Planet becomes coordinator instead of god class
- Each delegate has single responsibility
- Facility and population become reusable domain objects
- Easier to test each concern in isolation

**Effort:** Complex (6-8 hours)
- Phase 1: 2 hours (file moves, import updates)
- Phase 2: 4-6 hours (3 delegates + facade methods)

---

### CRITICAL: Construction Queue Duplication
**ID:** ROF-003
**Location:** `game/strategy/data/fleet.py:135` + `game/strategy/data/planet.py:228`
**Issue:** Both Fleet and Planet have identical `construction_queue: List[Dict[str, Any]]` with identical structure but no shared abstraction. PlanetaryFacility also has its own construction_queue (planet.py:42).

Queue item structure (from ProductionEngine):
```python
{
    'design_id': str,
    'type': str,  # "ship", "fighter", "satellite", "complex"
    'turns_remaining': int,
    # Optional PROJ-75 fields:
    'total_cost': Dict[str, float],
    'cost_per_tick': Dict[str, float],
    'resources_consumed': Dict[str, float],
    'ticks_in_current_turn': int,
}
```

**Impact:**
- Duplicated validation logic (3 places check queue structure)
- No type safety (raw dicts passed everywhere)
- BuildQueueSource wraps these queues but doesn't encapsulate the items
- ProductionEngine has to handle 3 different queue sources with identical logic

**Recommendation:**
Extract **ConstructionQueueItem** value object and **ConstructionQueue** collection:

```python
# game/strategy/data/construction_queue.py
@dataclass
class ConstructionQueueItem:
    design_id: str
    vehicle_type: str  # "ship", "fighter", "satellite", "complex"
    turns_remaining: int
    total_cost: Dict[str, float] = field(default_factory=dict)
    cost_per_tick: Dict[str, float] = field(default_factory=dict)
    resources_consumed: Dict[str, float] = field(default_factory=dict)
    ticks_in_current_turn: int = 0

    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConstructionQueueItem': ...

class ConstructionQueue:
    def __init__(self):
        self._items: List[ConstructionQueueItem] = []

    def add_item(self, item: ConstructionQueueItem): ...
    def peek(self) -> Optional[ConstructionQueueItem]: ...
    def pop_completed(self) -> Optional[ConstructionQueueItem]: ...
    def is_empty(self) -> bool: ...
    def to_dict(self) -> List[Dict]: ...
```

Then replace:
- `fleet.construction_queue: List[Dict]` → `fleet.construction_queue: ConstructionQueue`
- `planet.construction_queue: List[Dict]` → `planet.construction_queue: ConstructionQueue`
- `facility.construction_queue: List[Dict]` → `facility.construction_queue: ConstructionQueue`

Benefits:
- Type safety for queue items
- Centralized validation
- Queue operations encapsulated (no raw list manipulation)
- BuildQueueSource can wrap ConstructionQueue instead of raw list

**Effort:** Medium (4-5 hours)
- Create value object + collection (2 hours)
- Update Fleet, Planet, PlanetaryFacility (1 hour)
- Update ProductionEngine + BuildQueueSource (1.5 hours)
- Tests (30 min)

---

### MAJOR: Fleet Order Queue Management Scattered
**ID:** ROF-004
**Location:** `game/strategy/data/fleet.py:323-347` (order queue methods)
**Issue:** Fleet directly manipulates its `orders: List[FleetOrder]` with raw list operations:
- `add_order()` — direct append/insert
- `clear_orders()` — direct clear + path reset
- `get_current_order()` — direct index access
- `pop_order()` — direct pop + path reset

This violates encapsulation and spreads order lifecycle knowledge across Fleet and FleetOrderProcessor.

**Impact:**
- Path management coupled to order lifecycle (path reset in 2 places)
- FleetOrderProcessor calls Fleet.get_current_order(), checks type, then calls Fleet.pop_order() (Tell Don't Ask violation)
- No validation when adding orders (can add None, duplicates, invalid orders)
- Difficult to add order queue features (priorities, dependencies, validation)

**Recommendation:**
Extract **FleetOrderQueue** value object:

```python
# game/strategy/data/fleet_order_queue.py
class FleetOrderQueue:
    def __init__(self):
        self._orders: List[FleetOrder] = []
        self._current_path: List[HexCoord] = []

    def add(self, order: FleetOrder, index: Optional[int] = None):
        """Add order with validation."""
        if order is None:
            raise ValueError("Cannot add None order")
        # Validation logic here
        if index is None:
            self._orders.append(order)
        else:
            self._orders.insert(index, order)

    def peek(self) -> Optional[FleetOrder]:
        """Get current order without removing."""
        return self._orders[0] if self._orders else None

    def complete_current(self) -> Optional[FleetOrder]:
        """Remove and return current order, clear path."""
        if self._orders:
            finished = self._orders.pop(0)
            self._current_path = []
            return finished
        return None

    def clear_all(self):
        """Clear all orders and path."""
        self._orders.clear()
        self._current_path = []

    def get_path(self) -> List[HexCoord]:
        return list(self._current_path)

    def set_path(self, path: List[HexCoord]):
        self._current_path = list(path)
```

Replace Fleet attributes:
- `fleet.orders` → `fleet.order_queue`
- `fleet.path` → managed by `fleet.order_queue`

Benefits:
- Path lifecycle tied to order lifecycle (single responsibility)
- Validation at order addition
- Encapsulated queue operations
- Easier to add queue features (undo, reorder, dependencies)

**Effort:** Medium (3-4 hours)
- Create FleetOrderQueue class (1.5 hours)
- Refactor Fleet to use queue (1 hour)
- Update FleetOrderProcessor, FleetNavigationService (1 hour)
- Tests (30 min)

---

### MAJOR: Planet Resource/Facility Methods Scattered
**ID:** ROF-005
**Location:** `game/strategy/data/planet.py:337-350` + embedded in PlanetaryFacility
**Issue:** Resource and facility management methods are scattered:
- `planet.add_production()` (lines 337-350) — construction queue manipulation
- `planet.can_build_type()` (lines 315-335) — capability query
- `planet.has_space_shipyard` (lines 306-308) — delegates to facility scan
- `facility.add_fuel()` (lines 98-113) — resource management
- `facility.withdraw_fuel()` (lines 115-127) — resource management
- `facility.get_max_fuel_storage()` (lines 74-96) — scans components

Planet is a coordinator but also implements production logic directly.

**Impact:**
- Planet has mixed abstraction levels (physical properties + game mechanics)
- Resource methods on PlanetaryFacility scan components (should be cached)
- No centralized facility query service
- Difficult to add colony-wide resource aggregation

**Recommendation:**
Extract **PlanetProductionManager** delegate:

```python
# game/strategy/data/planet_production_manager.py
class PlanetProductionManager:
    def __init__(self, planet: Planet):
        self._planet = planet

    def can_build_type(self, vehicle_type: str) -> bool:
        """Check if planet can build vehicle type."""
        if vehicle_type.lower() == "complex":
            return True
        if vehicle_type.lower() in ("ship", "fighter", "satellite"):
            return self.has_space_shipyard
        return False

    @property
    def has_space_shipyard(self) -> bool:
        return any(f.is_shipyard for f in self._planet.facilities)

    def add_to_queue(self, design_id: str, turns: int, vehicle_type: str = "ship"):
        """Add item to construction queue."""
        # Validation + queue item creation
        self._planet.construction_queue.add_item(...)
```

Extract **PlanetFacilityManager** delegate:

```python
# game/strategy/data/planet_facility_manager.py
class PlanetFacilityManager:
    def __init__(self, planet: Planet):
        self._planet = planet

    def get_total_fuel_storage(self, registries) -> float:
        """Aggregate fuel storage across all facilities."""
        return sum(f.get_max_fuel_storage(registries) for f in self._planet.facilities)

    def add_fuel_to_storage(self, amount: float, registries) -> float:
        """Distribute fuel to facilities, return overflow."""
        # Distribution logic

    def get_shipyards(self) -> List[PlanetaryFacility]:
        return [f for f in self._planet.facilities if f.is_shipyard]
```

Benefits:
- Planet becomes pure data + delegates
- Production logic centralized
- Facility management encapsulated
- Easier to add colony-wide queries

**Effort:** Medium (3-4 hours)
- Create 2 delegate classes (2 hours)
- Refactor Planet to use delegates (1 hour)
- Update callers (1 hour)

---

### MAJOR: Fleet Resource Delegation Incomplete
**ID:** ROF-006
**Location:** `game/strategy/data/fleet.py:239-279` (pass-through methods)
**Issue:** Fleet has excellent delegates (FleetResourceAggregator, FleetCapabilityCalculator) but still exposes 15+ pass-through methods that just call the delegate. This is facade bloat.

Example (lines 241-251):
```python
def get_movement_resource_costs(self) -> Dict[str, float]:
    return self._resource_agg.get_movement_resource_costs()

def has_resources_for_movement(self) -> bool:
    return self._resource_agg.has_resources_for_movement()
```

**Impact:**
- Fleet class is 552 lines, ~100 lines are just delegate pass-throughs
- Violates "minimize pass-through with direct delegation" principle
- API surface bloat (40+ methods on Fleet)
- Callers have to know which methods are on Fleet vs delegates

**Recommendation:**
**Option 1: Direct Delegation (Preferred)**
Remove pass-through methods, expose delegates as public properties:
```python
# Before:
fleet.get_movement_resource_costs()
fleet.has_resources_for_movement()
fleet.fuel_endurance()

# After:
fleet.resources.get_movement_costs()
fleet.resources.has_movement_resources()
fleet.resources.fuel_endurance()
```

**Option 2: Keep High-Value Facades Only**
Keep only the most common operations as facades:
- `fleet.speed` (property, frequently accessed)
- `fleet.has_space_shipyard` (common capability check)
- Remove the rest (14 methods)

Benefits:
- Fleet class shrinks by ~20%
- Clear separation between Fleet API and delegate APIs
- Follows existing delegate pattern (FleetBattleAdapter already exposed as property)

**Effort:** Simple (1-2 hours)
- Remove pass-through methods (30 min)
- Update callers to use `fleet.resources.*` and `fleet.capabilities.*` (1 hour)
- Update tests (30 min)

---

### MAJOR: FleetOrder Execution Progress Tracking Mixed
**ID:** ROF-007
**Location:** `game/strategy/data/fleet.py:68` (FleetOrder.execution_progress)
**Issue:** FleetOrder has `execution_progress: int` field (PROJ-187) tracked at order level, but order completion/progress management is split between:
- FleetOrder (stores progress)
- FleetOrderProcessor (increments progress, checks completion)
- ActionExecutionEngine (calls processor)

This creates temporal coupling and unclear ownership.

**Impact:**
- Order state mutation spread across 3 classes
- Difficult to add progress callbacks/events
- Progress increment logic duplicated (tick += 1 in multiple places)
- No validation (progress can exceed required ticks)

**Recommendation:**
Extract **OrderExecutionTracker** as part of FleetOrderQueue (ROF-004):

```python
class FleetOrderQueue:
    def tick_current_order(self) -> bool:
        """
        Increment execution progress on current order.
        Returns True if order completed this tick.
        """
        order = self.peek()
        if not order:
            return False

        order.execution_progress += 1
        # Check completion condition (delegated to order type handler)
        if self._is_order_complete(order):
            self.complete_current()
            return True
        return False
```

Benefits:
- Order lifecycle fully encapsulated in queue
- Progress tracking + completion in single location
- Easier to add progress events/validation

**Effort:** Simple (1-2 hours) — combine with ROF-004

---

### MAJOR: Planet Topology Logic Scattered
**ID:** ROF-008
**Location:** `game/strategy/data/planet.py:264-279` (occupied_hexes property)
**Issue:** Planet has `diameter_hexes` field for multi-hex zones (PROJ-139) and calculates occupied hexes with inline hex math. This mixes zone topology with planet data.

```python
@property
def occupied_hexes(self) -> FrozenSet[HexCoord]:
    if self.diameter_hexes > 0:
        radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
        return hex_circle_filled(self.location, radius)
    return frozenset({self.location})
```

**Impact:**
- Planet responsible for hex geometry calculations
- Dyson Sphere creation logic elsewhere has to set diameter_hexes (coupling)
- No validation (diameter_hexes could be negative, non-integer)
- Violates SRP (physical planet + zone topology)

**Recommendation:**
Extract **ZoneOccupant** protocol and **PlanetZone** value object:

```python
# game/core/protocols.py (extend IZoneOccupant)
class IZoneOccupant(Protocol):
    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]: ...
    @property
    def center_hex(self) -> HexCoord: ...

# game/strategy/data/planet_zone.py
@dataclass(frozen=True)
class PlanetZone:
    center: HexCoord
    diameter_hexes: float

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        if self.diameter_hexes > 0:
            radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
            return hex_circle_filled(self.center, radius)
        return frozenset({self.center})

    @property
    def is_multi_hex(self) -> bool:
        return self.diameter_hexes > 0
```

Planet becomes:
```python
class Planet:
    # Remove: diameter_hexes field
    # Add: zone field
    zone: PlanetZone = field(default_factory=lambda: PlanetZone(...))

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        return self.zone.occupied_hexes
```

Benefits:
- Zone topology encapsulated
- Reusable for other multi-hex objects (stations, anomalies)
- Validation in PlanetZone constructor
- Planet becomes pure data + zone reference

**Effort:** Medium (2-3 hours)
- Create PlanetZone value object (1 hour)
- Refactor Planet to use zone (30 min)
- Update serialization (30 min)
- Update Dyson Sphere creation (30 min)

---

### MINOR: ShipInstance Already Well-Decomposed
**ID:** ROF-009
**Location:** `game/strategy/data/ship_instance.py:1-742`
**Issue:** ShipInstance is 741 lines but already has 3 excellent delegates:
- ShipResourceManager (lines 78-86)
- ShipCargoManager (lines 79-86)
- ShipDisplayFormatter (lines 80-86)

Most methods are thin facades over delegates. Only concern is the 100-line `to_ship()` method (lines 514-570).

**Impact:** Minimal — ShipInstance is well-architected.

**Recommendation:**
Extract **ShipBattleAdapter** for symmetry with FleetBattleAdapter:

```python
# game/strategy/data/ship_battle_adapter.py
class ShipBattleAdapter:
    def __init__(self, ship_instance: ShipInstance):
        self._ship = ship_instance

    def to_battle_ship(self, position: Tuple[float, float], team_id: int,
                      registries: Optional[GameRegistries] = None) -> Ship:
        """Create simulation Ship from this instance."""
        # Move lines 514-570 here

    def apply_damage_state(self, ship: Ship):
        """Apply HP and component damage to simulation ship."""
        # Move damage application logic (lines 543-560)

    def apply_resource_state(self, ship: Ship):
        """Apply resource levels to simulation ship."""
        # Move resource application (lines 563-565)
```

Benefits:
- Symmetry with FleetBattleAdapter
- ShipInstance shrinks to ~640 lines
- Battle conversion logic centralized

**Effort:** Simple (1-2 hours) — mostly code movement

---

### MINOR: Fleet.name Property Duplicates Logic
**ID:** ROF-010
**Location:** `game/strategy/data/fleet.py:146-159`
**Issue:** Fleet.name is a @property that generates display names dynamically based on ship count. This is presentation logic in a data class.

```python
@property
def name(self) -> str:
    ship_count = len(self.ships)
    if ship_count == 0:
        return f"Empty Fleet {self.id}"
    elif ship_count == 1:
        return f"Fleet {self.id}: {self.ships[0].name}"
    else:
        return f"Fleet {self.id} ({ship_count} ships)"
```

**Impact:**
- Name changes dynamically (breaks equals/hash if used as key)
- Presentation logic in data layer
- String formatting repeated across codebase

**Recommendation:**
**Option 1:** Extract to FleetDisplayFormatter (like ShipDisplayFormatter)
```python
class FleetDisplayFormatter:
    def get_display_name(self, fleet: Fleet) -> str: ...
```

**Option 2:** Add explicit `display_name` field, generate once on fleet creation/ship change

Benefits:
- Stable identity (name doesn't change after creation)
- Presentation logic centralized
- Easier to customize per faction/empire

**Effort:** Simple (1 hour)

---

### MINOR: Planet Helper Modules Underutilized
**ID:** ROF-011
**Location:** `game/strategy/data/planet_physics.py`, `planet_atmosphere.py`, `planet_naming.py`
**Issue:** These helper modules exist but Planet class still has direct physical property fields (mass, radius, atmosphere dict). No clear separation between "Planet as data" vs "Planet as physical simulation".

**Impact:** Minimal — helpers are used during generation, Planet is just storage.

**Recommendation:**
Consider extracting **PlanetPhysics** value object if physics calculations are needed at runtime:

```python
@dataclass(frozen=True)
class PlanetPhysics:
    mass: float
    radius: float
    density: float
    surface_gravity: float
    escape_velocity: float  # Calculated, not stored

    @property
    def escape_velocity(self) -> float:
        from game.strategy.data.planet_physics import calculate_escape_velocity
        return calculate_escape_velocity(self.mass, self.radius)
```

But current design is fine for now — only act if physics queries become common.

**Effort:** N/A (informational)

---

### INFO: Existing Delegates Are Excellent Examples
**ID:** ROF-012
**Location:** Multiple delegate files
**Issue:** N/A — this is a positive assessment.

**Assessment:**
The existing delegates follow excellent patterns:

1. **FleetResourceAggregator** (334 lines)
   - ✅ Clear single responsibility (resource aggregation)
   - ✅ Helper method consolidation (_accumulate_ship_costs, _verify_and_consume_resources)
   - ✅ Data-driven design (no hardcoded resource types)
   - ✅ Well-documented (PROJ-204 consolidation notes)

2. **FleetCapabilityCalculator** (187 lines)
   - ✅ Stateless queries (can_build_type, has_space_shipyard)
   - ✅ Late imports for service dependencies
   - ✅ Static helper methods for reuse

3. **ShipResourceManager** (142 lines)
   - ✅ Encapsulates resource_levels dict access
   - ✅ Generic resource methods (no fuel/energy hardcoding)
   - ✅ Validation (negative amount checks)

4. **ShipCargoManager** (118 lines)
   - ✅ Simple, focused API
   - ✅ Proper capacity validation

**What Worked:**
- Facade pattern (Fleet/ShipInstance keep delegates private, expose via properties or facades)
- Delegate constructors take parent as parameter, store as `_fleet` or `_ship`
- No circular dependencies (delegates import TYPE_CHECKING parent)

**What Didn't:**
- ROF-006: Too many pass-through facades on Fleet (diminishing returns)

**Recommendation:** Use these as templates for new delegates (PlanetProductionManager, PlanetFacilityManager, OrderSerializer).

**Effort:** N/A (informational)

---

### INFO: Fleet.resolve_order_references Is Post-Load Fixup
**ID:** ROF-013
**Location:** `game/strategy/data/fleet.py:485-540`
**Issue:** N/A — this is correct design for save/load.

**Assessment:**
Fleet.from_dict() stores order targets as `{'_fleet_ref': id}` or `{'_planet_ref': id}` because the referenced objects don't exist yet during deserialization. Then `resolve_order_references()` is called after all entities are loaded.

This is the **two-phase deserialization pattern** and is correct for cyclic references.

**Recommendation:** No change needed. Document this pattern in ARCHITECTURE.md as the standard approach for entity references in save files.

**Effort:** N/A (informational)

---

### MAJOR: PlanetaryFacility Resource Methods Duplicate Ship Patterns
**ID:** ROF-014
**Location:** `game/strategy/data/planet.py:70-127` (PlanetaryFacility fuel methods)
**Issue:** PlanetaryFacility has resource_levels dict and fuel methods identical to ShipInstance:
- `get_fuel_storage()` — reads from resource_levels dict
- `get_max_fuel_storage(registries)` — scans components for ResourceStorage ability
- `add_fuel()` — adds to resource_levels, returns overflow
- `withdraw_fuel()` — removes from resource_levels

This is the SAME pattern as ShipResourceManager.

**Impact:**
- Code duplication (same pattern in 2 places)
- No reuse of ShipResourceManager logic
- PlanetaryFacility scans components every time (no caching)

**Recommendation:**
Create generic **VehicleResourceManager** that works with any object with `design_data` and `resource_levels`:

```python
# game/strategy/data/vehicle_resource_manager.py
class VehicleResourceManager:
    """Generic resource manager for any entity with design_data and resource_levels."""

    def __init__(self, vehicle: Any, registries):
        """
        Args:
            vehicle: Object with design_data dict and resource_levels dict
            registries: GameRegistries for component lookups
        """
        self._vehicle = vehicle
        self._registries = registries
        self._cached_capacities: Optional[Dict[str, float]] = None

    def get_capacity(self, resource_type: str) -> float:
        if self._cached_capacities is None:
            self._cached_capacities = self._scan_capacities()
        return self._cached_capacities.get(resource_type, 0.0)

    def _scan_capacities(self) -> Dict[str, float]:
        """Scan design_data components for ResourceStorage abilities."""
        # Reuse component scanning logic
```

Then:
- **ShipResourceManager** extends VehicleResourceManager (remove duplication)
- **PlanetaryFacility** uses VehicleResourceManager instance
- Cache capacities instead of rescanning on every call

Benefits:
- DRY (single implementation)
- Cached capacities (performance)
- Reusable for future vehicle types (satellites, complexes)

**Effort:** Medium (3-4 hours)
- Create VehicleResourceManager base (2 hours)
- Refactor ShipResourceManager to extend base (1 hour)
- Refactor PlanetaryFacility to use manager (1 hour)

---

## Top 5 Priority Issues

Ranked by **value/cost ratio** (impact ÷ effort):

### 1. ROF-003: Construction Queue Duplication (CRITICAL)
**Value:** 9/10 (eliminates duplication, adds type safety, affects 3 entities)
**Cost:** 4-5 hours
**Ratio:** 1.8-2.25

**Why First:**
- Affects Fleet, Planet, AND PlanetaryFacility
- Eliminates raw dict manipulation (big quality win)
- Enables future queue features (undo, priorities)
- Unblocks BuildQueueSource simplification

---

### 2. ROF-001: FleetOrder Serialization Extraction (CRITICAL)
**Value:** 8/10 (eliminates god method, removes circular imports, extensibility)
**Cost:** 2-3 hours
**Ratio:** 2.67-4.0

**Why Second:**
- Highest ratio (best bang for buck)
- 7 serialization branches consolidated
- Easy to add new order types after
- Removes late import hack

---

### 3. ROF-004: Fleet Order Queue Encapsulation (MAJOR)
**Value:** 7/10 (encapsulation, path lifecycle coupling fixed)
**Cost:** 3-4 hours (combine with ROF-007)
**Ratio:** 1.75-2.33

**Why Third:**
- Pairs well with ROF-001 (order system overhaul)
- Fixes Tell Don't Ask violation (FleetOrderProcessor)
- Enables queue features (validation, undo)
- Path management finally correct

---

### 4. ROF-002: Planet Embedded Classes Extraction (CRITICAL)
**Value:** 8/10 (major god class reduction, reusability)
**Cost:** 6-8 hours (Phase 1 + Phase 2)
**Ratio:** 1.0-1.33

**Why Fourth:**
- Largest god class reduction (Planet shrinks by 40%)
- Phase 1 is simple (just file moves)
- Phase 2 creates reusable delegates
- Unblocks colony-wide resource aggregation

---

### 5. ROF-014: Generic Vehicle Resource Manager (MAJOR)
**Value:** 6/10 (DRY, performance, reusability)
**Cost:** 3-4 hours
**Ratio:** 1.5-2.0

**Why Fifth:**
- Eliminates Ship/Facility duplication
- Performance win (cached capacities)
- Reusable for future vehicle types
- Pairs well with ROF-002 (facility extraction)

---

## Recommended Execution Order

**Sprint 1: Order System Overhaul** (5-7 hours)
1. ROF-001: Extract OrderSerializer
2. ROF-004 + ROF-007: Extract FleetOrderQueue

**Sprint 2: Construction Queue Standardization** (4-5 hours)
3. ROF-003: Extract ConstructionQueue value object

**Sprint 3: Planet God Class Decomposition** (6-8 hours)
4. ROF-002 Phase 1: Extract PlanetaryFacility, SpeciesPopulation
5. ROF-002 Phase 2: Extract Planet delegates

**Sprint 4: Resource Management Consolidation** (3-4 hours)
6. ROF-014: Generic VehicleResourceManager
7. ROF-005: PlanetProductionManager delegate

**Sprint 5: Polish** (3-5 hours)
8. ROF-006: Remove Fleet pass-through facades
9. ROF-008: Extract PlanetZone value object
10. ROF-009: Extract ShipBattleAdapter (optional)

**Total Effort:** 21-29 hours (~3-4 weeks at 8 hours/week)

---

## End of Report
