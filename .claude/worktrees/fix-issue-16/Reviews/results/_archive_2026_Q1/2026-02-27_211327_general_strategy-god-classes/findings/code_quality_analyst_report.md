# Code Quality Analyst Report
**Review Date:** 2026-02-27
**Scope:** Strategy domain models - God class patterns, pass-through proxies, and code complexity
**Files Reviewed:** 33 files (~9,250 lines) in `game/strategy/`

---

## Summary
- **Total issues found:** 18
- **Critical:** 3
- **Major:** 8
- **Minor:** 5
- **Info:** 2

### Key Findings
The strategy domain models show **moderate god class accumulation** with **extensive pass-through facade bloat**. While delegation has been attempted (PROJ-87 Phase 3-4), the pattern used creates **zero-value proxy methods** that simply forward calls without adding abstraction. The delegates themselves are well-designed, but the parent classes retain bloated APIs.

**Good news:** No significant DRY violations or magic numbers. Code is generally well-named and documented.

**Bad news:** Pass-through facades create maintenance burden without architectural benefit. Serialization methods are extremely complex (80-95 lines).

---

## Critical Issues

### CQ-01: Fleet Class Pass-Through Facade Bloat
**ID:** CQ-01
**Severity:** CRITICAL
**Location:** `game/strategy/data/fleet.py:203-322` (120 lines of pure delegation)
**Issue:** Fleet has **28 pass-through methods** that add zero value over direct delegate access. Every method is a 1-line `return self._delegate.method()` call.

**Examples:**
```python
# Line 208-210: Pure pass-through
@property
def has_space_shipyard(self) -> bool:
    return self._capabilities.has_space_shipyard

# Line 241-243: Pure pass-through
def get_movement_resource_costs(self) -> Dict[str, float]:
    return self._resource_agg.get_movement_resource_costs()

# Line 283-285: Pure pass-through
def get_fleet_cargo_capacity(self, cargo_type: str) -> int:
    return self._resource_agg.get_fleet_cargo_capacity(cargo_type)
```

**Methods affected:**
- Resource aggregation: 13 methods (lines 241-298)
- Capability queries: 8 methods (lines 208-238)
- Battle conversion: 3 methods (lines 299-321)
- Cargo operations: 4 methods (lines 283-298)

**Impact:**
- **120 lines of maintenance burden** for zero abstraction value
- Violates **Single Responsibility Principle** - Fleet now has 4+ distinct concerns
- Public API is **4x larger** than it needs to be
- Every delegate method change requires updating Fleet interface
- Unclear which methods are "real" Fleet logic vs forwarding

**Recommendation:**
1. **Make delegates public** via properties only (`fleet.resources`, `fleet.capabilities`, `fleet.battle`)
2. **Remove all pass-through methods** - callers use `fleet.resources.get_movement_costs()` instead
3. **Keep only methods that add Fleet-specific logic** (e.g., `add_ship`, `remove_ship`, `merge_with`)
4. This reduces Fleet from **47 public methods to ~15-20**

**Effort:** Medium (requires updating ~50-100 call sites, but mechanically simple)

---

### CQ-02: ShipInstance Class Pass-Through Facade Bloat
**ID:** CQ-02
**Severity:** CRITICAL
**Location:** `game/strategy/data/ship_instance.py:291-458` (168 lines of pure delegation)
**Issue:** ShipInstance has **30+ pass-through methods** across 3 delegates with identical pattern to Fleet (CQ-01).

**Delegate breakdown:**
- **ShipResourceManager** (`_resource_mgr`): 11 methods (lines 297-383)
- **ShipCargoManager** (`_cargo_mgr`): 6 methods (lines 355-373)
- **ShipDisplayFormatter** (`_display_fmt`): 6 methods (lines 291-458)

**Examples:**
```python
# Line 297-307: Pure pass-through to _resource_mgr
def get_resource_capacity(self, resource_type: str) -> float:
    return self._resource_mgr.get_resource_capacity(resource_type)

# Line 355-357: Pure pass-through to _cargo_mgr
def get_cargo_capacity(self, cargo_type: str) -> int:
    return self._cargo_mgr.get_cargo_capacity(cargo_type)

# Line 448-450: Pure pass-through to _display_fmt
def get_status_text(self) -> str:
    return self._display_fmt.get_status_text()
```

**Impact:**
- **168 lines** of zero-value forwarding code
- **59 public methods** on ShipInstance (should be ~20-25)
- Same maintenance burden as CQ-01
- Delegates are already well-designed with clear separation

**Recommendation:**
1. Expose delegates as public properties: `ship.resources`, `ship.cargo`, `ship.display`
2. Remove all pass-through methods
3. Update callers to use `ship.resources.get_capacity('fuel')`
4. Keep only core ShipInstance logic: `to_ship()`, `update_from_ship()`, `create()`, `from_dict()`, etc.

**Effort:** Medium-Complex (more call sites than Fleet, ~100-200 updates)

---

### CQ-03: Deserialization Methods Exceed Complexity Threshold
**ID:** CQ-03
**Severity:** CRITICAL
**Location:**
- `game/strategy/data/fleet.py:389-483` (95 lines)
- `game/strategy/data/planet.py:406-499` (94 lines)
- `game/strategy/data/ship_instance.py:663-705` (43 lines, plus complex `to_ship` 57 lines)

**Issue:** `from_dict()` methods are **extremely long and complex** with deep nesting, multiple format handling, and mixed concerns (validation + construction + error handling).

**Fleet.from_dict() complexity:**
- **95 lines** in single method
- **7 different order target formats** (lines 435-472)
- Nested try-catch loops for resilient deserialization
- Mixed validation, transformation, and construction logic
- **Nesting depth: 4 levels** (violates "max 3" guideline)

**Planet.from_dict() complexity:**
- **94 lines** in single method
- **14 required field validations** (lines 424-443)
- Separate validation functions for positive/non-negative values
- Error context building with custom exceptions
- **Nesting depth: 3-4 levels**

**Impact:**
- Methods are **hard to test** comprehensively (too many branches)
- **Hard to modify** without introducing bugs
- Violates **Single Responsibility** (validate + deserialize + error recovery)
- **Cognitive load** too high for code review

**Recommendation:**
1. **Extract validation** to separate `_validate_fleet_data(data)` method
2. **Extract order deserialization** to `_deserialize_orders(order_data_list)` helper
3. **Extract ship/facility deserialization** to dedicated methods
4. Break `from_dict()` into **3-5 smaller methods** (<30 lines each)
5. Consider **Builder pattern** for complex construction

**Example refactor:**
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Fleet':
    """Deserialize from save game."""
    cls._validate_required_keys(data)
    location = cls._parse_location(data.get('location'))

    fleet = cls(
        fleet_id=data['id'],
        owner_id=data['owner_id'],
        location=location,
        speed=data.get('speed', 5.0),
    )

    fleet.ships = cls._deserialize_ships(data.get('ships', []))
    fleet.path = cls._deserialize_path(data.get('path', []))
    fleet.orders = cls._deserialize_orders(data.get('orders', []))
    fleet.construction_queue = data.get('construction_queue', [])

    return fleet
```

**Effort:** Medium (refactoring deserialization logic, high test coverage exists)

---

## Major Issues

### CQ-04: FleetOrder.to_dict() Has 7 Target Format Branches
**ID:** CQ-04
**Severity:** MAJOR
**Location:** `game/strategy/data/fleet.py:75-113` (39 lines)
**Issue:** Single serialization method handles **7 different target types** with brittle isinstance checks and magic string keys.

**Target formats:**
1. TRANSFER order dict (`{'type': 'transfer', 'value': ...}`)
2. Planet reference (`{'type': 'planet_ref', 'id': ...}`)
3. Ship ID list (`{'type': 'ship_id_list', 'value': ...}`)
4. Warp params (`{'type': 'warp_params', 'value': ...}`)
5. HexCoord (`{'q': x, 'r': y}`)
6. Fleet reference (`{'type': 'fleet_ref', 'id': ...}`)
7. Raw fallback (`{'type': 'raw', 'value': str}`)

**Impact:**
- **High coupling** to specific order types
- **Brittle** - adding new order type requires updating 2 places (to_dict + from_dict)
- **No polymorphism** - all logic centralized instead of distributed
- Hard to test all branches comprehensively

**Recommendation:**
1. Use **polymorphic serialization** - each OrderType has its own serializer
2. Create `OrderTargetSerializer` registry: `OrderType.TRANSFER -> TransferTargetSerializer`
3. Refactor to: `target_data = OrderTargetSerializer.serialize(order.type, order.target)`
4. Eliminates isinstance cascade and centralizes format knowledge

**Effort:** Medium (architectural change, but clear pattern)

---

### CQ-05: Planet Class Has 5 Distinct Responsibilities
**ID:** CQ-05
**Severity:** MAJOR
**Location:** `game/strategy/data/planet.py:186-499` (313 lines for Planet class)
**Issue:** Planet dataclass manages **5 unrelated concerns** in single class:
1. **Physical properties** (mass, radius, gravity, temperature, atmosphere)
2. **Facilities management** (facilities list, construction queue)
3. **Population tracking** (multi-species populations, happiness)
4. **Resource management** (resource dict with quality/quantity)
5. **Build capabilities** (shipyard checks, vehicle type validation)

**Evidence:**
- **15 physical property fields** (lines 192-217)
- **4 gameplay state fields** (facilities, populations, resources, construction_queue)
- **3 display fields** (image_id, image_rotation, diameter_hexes)
- **10 public methods** mixing physics calculations with gameplay logic

**Impact:**
- Violates **Single Responsibility Principle**
- **High coupling** between physics and gameplay
- Changes to facility system affect planet physics
- Hard to reuse physics model independently

**Recommendation:**
1. **Extract PlanetPhysics** dataclass (mass, radius, gravity, atmosphere, etc.)
2. **Extract PlanetEconomy** manager (facilities, resources, build queue)
3. **Extract PlanetDemographics** (populations, happiness calculations)
4. Planet becomes **composition** of these 3 components
5. Each component has focused responsibility and can be tested independently

**Effort:** Medium-Complex (requires careful dependency analysis)

---

### CQ-06: FleetNavigationService Method Length Violations
**ID:** CQ-06
**Severity:** MAJOR
**Location:** `game/strategy/services/fleet_navigation_service.py`
**Issue:** Service has **multiple methods >50 lines** violating code guideline:
- `project_path()`: **124 lines** (lines 413-562) - exceeds threshold by 2.5x
- `compute_next_step()`: **107 lines** (lines 305-411) - exceeds threshold by 2x
- `from_dict()` (Fleet): **95 lines** - covered in CQ-03

**project_path() complexity:**
- Simulates multi-turn movement with speed/turn accounting
- Handles action order tick consumption (PROJ-187)
- Tracks first-order execution progress
- Safety limits for infinite loop prevention
- **7 state variables** tracked across iterations
- **Nesting depth: 4 levels**

**Impact:**
- **Hard to understand** - too much logic in one place
- **Hard to test** - many edge cases and state transitions
- **Hard to modify** - change ripples are unpredictable
- **Difficult code review** - cognitive overload

**Recommendation:**
1. Extract **ProjectionContext** dataclass to hold iteration state
2. Extract `_advance_to_next_order()` helper (action time consumption logic)
3. Extract `_execute_movement_step()` helper (path following logic)
4. Break into 4-5 methods <30 lines each
5. Main loop becomes readable: `while ctx.can_continue(): ctx.step()`

**Effort:** Medium (well-tested code, refactor requires careful validation)

---

### CQ-07: Duplicate Ship Iteration Pattern in FleetResourceAggregator
**ID:** CQ-07
**Severity:** MAJOR
**Location:** `game/strategy/data/fleet_resource_aggregator.py:100-182`
**Issue:** Three methods use **identical ship iteration pattern** with different cost getters:
- `get_movement_resource_costs()` (lines 100-107)
- `get_warp_resource_costs()` (lines 144-151)
- Fuel/warp endurance calculations (lines 186-232)

**Pattern duplication:**
```python
# Repeated 3 times with different lambda
def get_X_costs(self) -> Dict[str, float]:
    return self._accumulate_ship_costs(lambda ship: ship.get_X_costs())
```

**Impact:**
- **UPDATE:** Actually this is NOT a DRY violation - PROJ-204 already fixed this
- Helper methods `_accumulate_ship_costs()` and `_verify_and_consume_resources()` exist (lines 34-96)
- These are **good abstractions** that eliminate duplication
- The lambda pattern is **intentional** - passes different cost getter to shared helper

**Recommendation:**
- **No action needed** - this is good design
- Mark as **Info** severity instead of Major
- Document the pattern as best practice for other aggregators

**Effort:** None (already solved correctly)

---

### CQ-08: ShipInstance.to_ship() Nested Loop Complexity
**ID:** CQ-08
**Severity:** MAJOR
**Location:** `game/strategy/data/ship_instance.py:514-570` (57 lines)
**Issue:** Triple-nested loop to apply component damage:

```python
# Lines 553-560: Nesting depth = 3
for comp_id, target_hp in self.component_damage.items():
    for layer_type, layer_data in ship.layers.items():
        for comp in layer_data.components:
            if comp.id == comp_id:
                damage = comp.current_hp - target_hp
                if damage > 0:
                    comp.take_damage(damage)
```

**Impact:**
- **O(n × m × k)** complexity where n=damage entries, m=layers, k=components per layer
- Inefficient for ships with many damaged components
- **Nesting depth: 4 levels** with the if statement
- No early break after finding match

**Recommendation:**
1. **Build component lookup dict** first: `comp_by_id = {c.id: c for layer in ship.layers for c in layer.components}`
2. **Single loop**: `for comp_id, target_hp in self.component_damage.items(): comp_by_id[comp_id].set_hp(target_hp)`
3. Reduces complexity to **O(m × k) + O(n)** - much better for damaged ships
4. Extract to helper: `_apply_component_damage(ship, self.component_damage)`

**Effort:** Simple (clear optimization, well-tested)

---

### CQ-09: Planet.from_dict() Has 14 Sequential Validation Calls
**ID:** CQ-09
**Severity:** MAJOR
**Location:** `game/strategy/data/planet.py:424-443` (20 lines of pure validation)
**Issue:** Sequential validation of 14 fields with repetitive pattern:

```python
require_keys(data, ['name', 'location', ...14 fields...], 'Planet')
planet_type = validate_enum(data['planet_type'], PlanetType, 'planet_type', 'Planet')
validate_positive(data['mass'], 'mass', 'Planet')
validate_positive(data['radius'], 'radius', 'Planet')
# ... 10 more validate_* calls
```

**Impact:**
- **Boilerplate heavy** - 40% of method is validation calls
- **Poor error messages** - doesn't tell user ALL invalid fields, only first failure
- **Hard to maintain** - adding field requires 3 updates (field list, validation, construction)
- Validation logic **scattered** across validation_helpers module

**Recommendation:**
1. Use **schema validation library** (e.g., Pydantic, marshmallow, or custom)
2. Define `PlanetSchema` with field constraints in one place
3. Single call: `validated_data = PlanetSchema.validate(data)`
4. Gets all validation errors at once, better UX
5. OR: Extract to `_validate_planet_fields(data)` helper that returns validated dict

**Effort:** Medium (depends on schema library choice vs custom validation)

---

### CQ-10: Fleet.resolve_order_references() Has Side Effects Without Return Value
**ID:** CQ-10
**Severity:** MAJOR
**Location:** `game/strategy/data/fleet.py:485-540` (56 lines)
**Issue:** Method mutates fleet.orders by removing invalid references, but:
- **No return value** to indicate what happened
- **Silent failures** except logger.warning()
- Caller doesn't know if orders were removed
- Mixed concerns: validation + resolution + mutation + logging

**Current behavior:**
```python
fleet.resolve_order_references(galaxy, empires)
# Did it remove orders? How many? Which ones? Unknown.
```

**Impact:**
- **Hard to test** - no observable return value
- **Hard to debug** - state changes are invisible to caller
- **No error recovery** - caller can't react to removed orders
- Violates **Command-Query Separation** principle

**Recommendation:**
1. **Return removed order count**: `removed_count = fleet.resolve_order_references(...)`
2. OR: **Return removed orders**: `removed = fleet.resolve_order_references(...)`
3. OR: **Make pure function**: `new_orders = resolve_order_references(fleet.orders, galaxy, empires)`
4. Caller can then log/alert: "Removed 3 invalid orders from fleet X"

**Effort:** Simple (add return value, update call sites)

---

### CQ-11: PlanetaryFacility.get_max_fuel_storage() Duplicates Component Iteration
**ID:** CQ-11
**Severity:** MAJOR
**Location:** `game/strategy/data/planet.py:74-96` (23 lines)
**Issue:** Manual component iteration pattern duplicated across codebase:

```python
# Pattern appears in:
# - PlanetaryFacility.get_max_fuel_storage()
# - PlanetaryFacility.is_shipyard (lines 130-148)
# - Likely other places checking for abilities

for comp in iter_components(self.design_data):
    comp_id = get_component_id(comp)
    comp_def = registries.components.get(comp_id)
    if not comp_def:
        continue
    abilities = get_component_abilities(comp_def)
    for storage in (abilities.get('ResourceStorage') or []):
        # ... check storage.resource == target
```

**Impact:**
- **DRY violation** - same iteration logic in 3+ places
- **High coupling** to component structure
- Changes to ability lookup require updating multiple sites
- `component_inspector` service exists but not consistently used

**Recommendation:**
1. **Use existing service**: `from game.strategy.services.component_inspector import get_resource_storage`
2. Create service method: `ComponentInspector.get_total_storage(design_data, resource_type, registries)`
3. Reduces to: `return ComponentInspector.get_total_storage(self.design_data, 'fuel', registries)`
4. Centralize component iteration logic in one place

**Effort:** Simple (service already exists, just needs new method)

---

## Minor Issues

### CQ-12: Magic Number: Fleet Formation Spacing
**ID:** CQ-12
**Severity:** MINOR
**Location:** `game/strategy/data/fleet_battle_adapter.py:86-91`
**Issue:** Hardcoded formation constants without named constants:

```python
base_x = 20000 if team_id == 0 else 80000  # Magic numbers
base_y = 50000
spacing = 2000
```

**Impact:** Minor - clear from context, but violates "no magic numbers" guideline

**Recommendation:**
```python
TEAM_0_START_X = 20000
TEAM_1_START_X = 80000
FORMATION_CENTER_Y = 50000
SHIP_SPACING = 2000
```

**Effort:** Trivial (5 minutes)

---

### CQ-13: Inconsistent Delegate Privacy (Fleet vs ShipInstance)
**ID:** CQ-13
**Severity:** MINOR
**Location:**
- `game/strategy/data/fleet.py:138-144` (private `_resource_agg`, `_capabilities`, `_battle`)
- `game/strategy/data/ship_instance.py:78-80` (private `_resource_mgr`, `_cargo_mgr`, `_display_fmt`)

**Issue:** All delegates are **private** (`_delegate`) but have **public pass-through facades**. This is inconsistent with delegation pattern best practices.

**Impact:**
- Users can't access delegates directly (would be cleaner than facades)
- Naming suggests internal implementation, but API forces going through parent
- Inconsistent with CQ-01/CQ-02 recommendation to expose delegates

**Recommendation:**
- Make delegates **public** properties: `self.resources`, `self.capabilities`, `self.battle`
- Remove pass-through methods
- Clearly documents delegation intent
- OR: Keep private and document why (currently undocumented)

**Effort:** Trivial (part of fixing CQ-01/CQ-02)

---

### CQ-14: ShipInstance Clone Method Doesn't Copy Serial Number
**ID:** CQ-14
**Severity:** MINOR
**Location:** `game/strategy/data/ship_instance.py:717-736` (20 lines)
**Issue:** `clone()` method creates deep copy but **omits serial number** from copied instance:

```python
def clone(self) -> 'ShipInstance':
    return ShipInstance(
        instance_id=str(uuid.uuid4()),  # New ID for clone
        # ... copies all fields EXCEPT serial
        # serial is not set, defaults to None
    )
```

**Impact:**
- **Inconsistent identity** - clone loses serial number tracking
- Unclear if intentional or bug
- No docstring explaining serial number behavior
- May break fleet tracking if serial is used for identification

**Recommendation:**
1. **Document intent** - is this a "new ship of same design" or "exact copy"?
2. If "new ship", serial should come from empire: `clone(self, empire: Empire)`
3. If "exact copy", preserve serial: `serial=self.serial`
4. Current behavior is ambiguous

**Effort:** Trivial (document or fix serial handling)

---

### CQ-15: Fleet.merge_with() Lacks Validation
**ID:** CQ-15
**Severity:** MINOR
**Location:** `game/strategy/data/fleet.py:349-365` (17 lines)
**Issue:** Merge operation has minimal validation:

```python
def merge_with(self, other_fleet: 'Fleet') -> None:
    if not isinstance(other_fleet, Fleet):
        return  # Silent failure

    # No checks for:
    # - Same owner_id?
    # - Same location?
    # - Fleet compatibility?
```

**Impact:**
- Can merge enemy fleets (owner_id mismatch)
- Can merge fleets at different locations
- Silent failure instead of raising exception
- No documentation of merge constraints

**Recommendation:**
1. Add validation: `if self.owner_id != other_fleet.owner_id: raise ValueError(...)`
2. Check location proximity: `if hex_distance(self.location, other) > 0: raise ValueError(...)`
3. OR: Document that validation happens elsewhere (caller responsibility)
4. Replace silent return with exception

**Effort:** Simple (add validation checks)

---

### CQ-16: Planet.to_dict() Manual Field Copying
**ID:** CQ-16
**Severity:** MINOR
**Location:** `game/strategy/data/planet.py:352-403` (52 lines)
**Issue:** Manual copying of all 20+ fields instead of using dataclass utilities:

```python
return {
    'id': self.id,
    'name': self.name,
    'location': hex_to_dict(self.location),
    # ... 20 more fields manually copied
}
```

**Impact:**
- **Boilerplate heavy** - manual field listing
- **Easy to forget fields** when adding new ones
- Python `dataclasses.asdict()` exists but not used
- Maintenance burden

**Recommendation:**
1. Use `dataclasses.asdict(self)` as baseline
2. Override special fields (HexCoord, facilities) after
3. Reduces from 52 lines to ~15 lines
4. OR: Document why manual is preferred (e.g., control over serialization format)

**Effort:** Simple (but test carefully - serialization is critical)

---

### CQ-17: Inconsistent Error Handling in Deserialization
**ID:** CQ-17
**Severity:** MINOR
**Location:** Multiple `from_dict()` methods
**Issue:** Inconsistent error handling strategies:
- **Fleet.from_dict()**: Catches broad `Exception`, logs warning, skips invalid items (resilient)
- **Planet.from_dict()**: Raises `PersistenceException` with detailed context (strict)
- **ShipInstance.from_dict()**: Validates but doesn't catch deserialization errors (mixed)

**Examples:**
```python
# Fleet: resilient
try:
    fleet.ships.append(ShipInstance.from_dict(ship_data))
except Exception as e:
    logger.warning(f"skipping corrupt ship: {e}")

# Planet: strict
if condition:
    raise PersistenceException("invalid data", context={...})
```

**Impact:**
- **Unpredictable behavior** - same corruption handled differently
- **Hard to document** - when does deserialization fail vs skip?
- Users don't know which classes are resilient vs strict

**Recommendation:**
1. **Choose strategy**: Resilient (skip corrupt) OR Strict (fail fast)
2. **Document in ARCHITECTURE.md** which strategy applies to each class
3. **Consistent exception types** - all use PersistenceException
4. OR: Add `strict: bool = True` parameter to control behavior

**Effort:** Simple (document existing behavior, or standardize)

---

## Info Issues

### CQ-18: FleetNavigationService Safety Limit Could Be Configurable
**ID:** CQ-18
**Severity:** INFO
**Location:** `game/strategy/services/fleet_navigation_service.py:456`
**Issue:** Hardcoded safety limit for infinite loop prevention:

```python
max_steps = max_turns * moves_per_turn + 100
```

**Impact:** None currently - works fine

**Recommendation:** Consider making configurable for testing edge cases:
```python
max_steps = max_turns * moves_per_turn + self.safety_margin  # default 100
```

**Effort:** Trivial

---

## Top 5 Priority Issues

1. **CQ-01 + CQ-02: Pass-Through Facade Bloat (Fleet + ShipInstance)** - CRITICAL
   - **Impact:** 288 lines of zero-value code, bloated APIs (4x larger than needed)
   - **Fix:** Remove pass-throughs, expose delegates as public properties
   - **Benefit:** Cleaner APIs, less maintenance, clearer responsibility separation
   - **Effort:** Medium (100-200 call site updates)

2. **CQ-03: Deserialization Method Complexity** - CRITICAL
   - **Impact:** 95-line methods exceed threshold by 3x, hard to test/modify
   - **Fix:** Extract validation, parsing, and construction into separate methods
   - **Benefit:** Readable code, easier testing, reduced cognitive load
   - **Effort:** Medium (requires careful refactoring, good test coverage exists)

3. **CQ-05: Planet God Class (5 Responsibilities)** - MAJOR
   - **Impact:** Physics + Facilities + Population + Resources + Build all in one class
   - **Fix:** Extract PlanetPhysics, PlanetEconomy, PlanetDemographics
   - **Benefit:** True separation of concerns, reusable components
   - **Effort:** Medium-Complex (requires dependency analysis)

4. **CQ-06: FleetNavigationService Method Length (124 lines)** - MAJOR
   - **Impact:** project_path() is 2.5x too long, hard to understand/modify
   - **Fix:** Extract ProjectionContext and helper methods
   - **Benefit:** Readable simulation logic, easier to extend
   - **Effort:** Medium (well-tested, refactor carefully)

5. **CQ-08: ShipInstance.to_ship() Triple-Nested Loop** - MAJOR
   - **Impact:** O(n×m×k) complexity, inefficient for damaged ships
   - **Fix:** Build component lookup dict, single-pass damage application
   - **Benefit:** Better performance, cleaner code (nesting depth 1 instead of 4)
   - **Effort:** Simple (clear optimization path)

---

## Positive Observations

**What's working well:**
1. **No significant DRY violations** - PROJ-204 already fixed resource aggregation duplication
2. **Good naming** - methods are well-named, intent is clear
3. **Comprehensive docstrings** - most methods document args/returns/behavior
4. **Type hints** - consistent use throughout
5. **Delegates are well-designed** - FleetResourceAggregator, ShipResourceManager are excellent
6. **Test coverage** - 7353 tests passing indicates good test discipline

**Architectural wins:**
- FleetResourceAggregator's `_accumulate_ship_costs()` and `_verify_and_consume_resources()` are exemplary helper methods
- NavigationState as immutable snapshot is good functional design
- Use of protocols (IPostBattleShip) for layer boundaries is clean

---

## Conclusion

The strategy domain shows **moderate god class accumulation** but with a specific pattern: **delegation has been implemented, but facades haven't been removed**. This creates bloat without architectural benefit.

**Primary recommendation:** Complete the delegation refactor by removing pass-through methods and exposing delegates as public properties. This will reduce API surface by 60-70% while maintaining all functionality.

**Secondary focus:** Break up complex serialization methods and extract Planet responsibilities into separate components.

**Overall assessment:** Code quality is GOOD with targeted improvements needed. The foundation is solid - just needs facade cleanup and complexity reduction in a few hot spots.
