# Architecture Review Report: Strategy Domain God Classes

**Review Date:** 2026-02-27
**Scope:** Strategy domain models (Fleet, Planet, ShipInstance) and their decomposition
**Total Files Analyzed:** 33 files (~9,250 lines)
**Reviewer:** Architecture Specialist

---

## Summary

- **Total Issues Found:** 18
- **Critical:** 3
- **Major:** 8
- **Minor:** 5
- **Info:** 2

**Overall Assessment:** The facade/delegate decomposition has **partially succeeded** but reveals deeper architectural problems. While extraction reduced individual class sizes, it did not eliminate tight coupling or clarify responsibility boundaries. Services/engines exhibit **feature envy** by reaching deeply into data model internals, and the lack of true abstraction layers means changing one concept still requires shotgun surgery across multiple files.

---

## Findings

### CRITICAL: Delegates Are Tightly Coupled Pseudo-Facades

#### Critical: AR-001
**ID:** AR-001
**Location:** `game/strategy/data/fleet.py:7-9`, `game/strategy/data/fleet.py:138-144`, `game/strategy/data/fleet_resource_aggregator.py:30`, `game/strategy/data/fleet_capability_calculator.py:52`, `game/strategy/data/fleet_battle_adapter.py:36`

**Issue:** The "delegates" (FleetResourceAggregator, FleetCapabilityCalculator, FleetBattleAdapter) are not true delegation - they are **tightly coupled pseudo-facades** that still reach back into Fleet internals. Each delegate stores a reference to the parent Fleet and accesses `self._fleet.ships`, `self._fleet.orders`, `self._fleet.location` directly. This is not decoupling; it's splitting a god class into multiple pieces that still have intimate knowledge of each other.

**Impact:**
- **No reduction in coupling:** Changing Fleet's internal structure (e.g., how ships are stored) requires updating all 3 delegates
- **Circular intimacy:** Fleet knows about delegates, delegates know about Fleet internals
- **False sense of separation:** The code *looks* modular but behaves as a monolith
- **Testing complexity:** Cannot test a delegate without a fully constructed Fleet object

**Recommendation:**
1. Define **clear data contracts** (DTOs) that delegates consume instead of raw Fleet references
2. Use **dependency inversion**: delegates should depend on abstractions (interfaces/protocols), not concrete Fleet
3. Consider **Strategy Pattern** for capabilities: `fleet.capabilities.can_warp()` should not reach into `fleet._fleet.ships` - instead, pass ship collection as parameter
4. Apply **Tell, Don't Ask**: instead of delegates querying Fleet state, Fleet should tell delegates what to do with explicit data

**Example Refactor:**
```python
# BAD (current):
class FleetCapabilityCalculator:
    def __init__(self, fleet: Fleet):
        self._fleet = fleet  # Stores reference, tightly coupled

    def can_use_warp(self) -> bool:
        for ship in self._fleet.get_combat_capable_ships():  # Reaches into Fleet
            if not ShipStatsCalculator.has_warp_capability(ship):
                return False
        return True

# GOOD (proposed):
class FleetCapabilityCalculator:
    @staticmethod
    def can_use_warp(ships: List[ShipInstance]) -> bool:
        return all(ShipStatsCalculator.has_warp_capability(s) for s in ships)

# Fleet delegates WITH data, not reference:
class Fleet:
    def can_use_warp(self) -> bool:
        return FleetCapabilityCalculator.can_use_warp(self.get_combat_capable_ships())
```

**Effort:** Complex (requires redesign of all 3 fleet delegates + ship delegates)

---

#### Critical: AR-002
**ID:** AR-002
**Location:** `game/strategy/data/fleet.py:485-540`, `game/strategy/data/planet.py:405-499`, `game/strategy/data/ship_instance.py:662-715`

**Issue:** **Serialization responsibilities violate Single Responsibility Principle.** Each data model class (Fleet, Planet, ShipInstance) handles its own persistence logic with complex reference resolution (`resolve_order_references`, `from_dict` with galaxy/empire lookups). This mixes domain logic with infrastructure concerns, making classes harder to test and evolving the save format harder.

**Impact:**
- **Shotgun surgery for save format changes:** Adding a new order type requires changes in 3 places: OrderType enum, FleetOrder.to_dict(), FleetOrder.from_dict()
- **Tight coupling to persistence format:** Domain models know about dict structure, reference markers (`_fleet_ref`, `_planet_ref`)
- **Complex constructors:** `from_dict()` methods are 50-100 lines with validation, error handling, backwards compatibility
- **Cannot swap persistence:** JSON serialization is hardcoded; cannot easily move to protobuf/database

**Recommendation:**
1. Extract **Repository Pattern**: Create `FleetRepository`, `PlanetRepository`, `ShipRepository` to handle serialization
2. Use **Data Transfer Objects (DTOs)** for persistence: Separate `FleetPersistenceDTO` from domain `Fleet`
3. Apply **Adapter Pattern** for reference resolution: `ReferenceResolver` handles `_fleet_ref` → Fleet mapping
4. Consider **Memento Pattern** for save states if complex versioning needed

**Effort:** Complex (affects save/load system across all data models)

---

#### Critical: AR-003
**ID:** AR-003
**Location:** `game/strategy/engine/fleet_order_processor.py:59-648`

**Issue:** **FleetOrderProcessor is a new god class** (648 lines) that violates Command-Query Separation and has too many responsibilities:
- Order lifecycle (completion, cancellation)
- JOIN_FLEET execution
- COLONIZE validation + execution + population transfer
- TRANSFER validation + execution (fleet-to-planet, fleet-to-fleet)
- Superweapon delegation
- Founding population logic

The class mixes command execution (state changes) with complex validation and business rules, making it difficult to understand, test, and extend.

**Impact:**
- **High cyclomatic complexity:** `process_colonize()` alone is 90 lines with nested validation
- **Difficult to test:** Cannot test COLONIZE without mock Empire, Galaxy, ComponentRegistry
- **Violates Open/Closed:** Adding a new order type requires modifying this class
- **Unclear boundaries:** Why is population transfer in FleetOrderProcessor instead of PopulationEngine?

**Recommendation:**
1. Apply **Command Pattern**: Each order type gets its own command class (`ColonizeCommand`, `TransferCommand`)
2. Use **Chain of Responsibility**: Order handlers chain together, each responsible for one order type
3. Extract **validation to separate validators** (already partially done with ColonizeValidator, but execution still mixed)
4. Move **population logic to PopulationEngine** (already exists but underutilized)
5. Create **OrderExecutionContext** to pass dependencies instead of method parameters

**Example:**
```python
# Command Pattern approach:
class IOrderCommand(Protocol):
    def validate(self, context: OrderExecutionContext) -> ValidationResult: ...
    def execute(self, context: OrderExecutionContext) -> ExecutionResult: ...

class ColonizeCommand:
    def validate(self, ctx: OrderExecutionContext) -> ValidationResult:
        return ColonizeValidator.validate(ctx.galaxy, ctx.fleet, ctx.order.target, ctx.registries)

    def execute(self, ctx: OrderExecutionContext) -> ExecutionResult:
        # Focused execution logic only
        ...

# Registry maps OrderType → Command
ORDER_HANDLERS = {
    OrderType.COLONIZE: ColonizeCommand(),
    OrderType.TRANSFER: TransferCommand(),
}
```

**Effort:** Complex (requires redesign of order processing system)

---

### MAJOR: Layer Violations and Circular Dependencies

#### Major: AR-004
**ID:** AR-004
**Location:** `game/strategy/data/fleet.py:191-192`, `game/strategy/data/ship_instance.py:255-264`, `game/strategy/data/fleet_capability_calculator.py:116-125`

**Issue:** **Data classes reach into service layer** via "intentional late imports". Fleet.trigger_speed_recalculation() imports FleetSpeedCalculator, ShipInstance.get_calculated_stats() imports ShipStatsCalculator. This creates **hidden circular dependencies** where data models depend on services that depend on data models.

**Impact:**
- **Import cycles masked by late imports:** Hard to detect with static analysis
- **Violates layering:** Data layer should not know about service layer
- **Testing complexity:** Mocking becomes necessary where it shouldn't be
- **Unclear ownership:** Is speed calculation Fleet's responsibility or FleetSpeedCalculator's?

**Recommendation:**
1. **Invert the dependency:** Services should operate ON data, not be called BY data
2. Use **Dependency Injection:** Pass calculators to Fleet constructor or method calls
3. Apply **Observer Pattern:** Fleet emits "ships changed" event, external SpeedManager responds
4. Consider **Domain Events:** `ShipAddedToFleet` event triggers recalculation externally

**Example:**
```python
# BAD (current):
class Fleet:
    def trigger_speed_recalculation(self):
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        FleetSpeedCalculator.update_fleet_speed(self)  # Data calls service

# GOOD (inverted):
class Fleet:
    def add_ship(self, ship: ShipInstance):
        self.ships.append(ship)
        # Invalidate cached speed, let external code recalculate
        self._cached_speed = None

# Service layer:
fleet_speed_manager = FleetSpeedManager()
fleet.add_ship(ship)
fleet_speed_manager.update(fleet)  # Service calls data
```

**Effort:** Medium (requires changing initialization patterns)

---

#### Major: AR-005
**ID:** AR-005
**Location:** `game/strategy/engine/fleet_movement_engine.py:72-93`, `game/strategy/services/fleet_navigation_service.py:610-653`

**Issue:** **FleetMovementEngine and FleetNavigationService have unclear boundaries.** FleetMovementEngine.calculate_next_hex() immediately delegates to FleetNavigationService, making FleetMovementEngine a thin wrapper. The division of responsibility is artificial:
- FleetNavigationService: path calculation, next hex logic
- FleetMovementEngine: resource consumption, warp blocking, movement application

But both mutate Fleet state, and FleetNavigationService has a "mutation bridge" method specifically for FleetMovementEngine.

**Impact:**
- **Confused responsibility:** Which class owns movement?
- **Unnecessary indirection:** Why call MovementEngine.calculate_next_hex() which calls NavigationService.calculate_fleet_next_hex()?
- **Tight coupling:** NavigationService knows it's consumed by MovementEngine (mutation bridge comment)
- **Testing redundancy:** Both classes test similar scenarios

**Recommendation:**
1. **Merge or clarify:** Either merge into one MovementService, or clearly separate:
   - NavigationService: Pure path calculation (no mutation)
   - MovementEngine: State changes (resource consumption, location update)
2. **Remove mutation bridge:** NavigationService should return intent (next hex), not apply it
3. Use **Command/Query Separation:** Navigation = query (pure), Movement = command (mutates)

**Effort:** Medium (requires consolidation of movement logic)

---

#### Major: AR-006
**ID:** AR-006
**Location:** `game/strategy/data/planet.py:70-127`, `game/strategy/data/build_queue_source.py:80-111`

**Issue:** **PlanetaryFacility has leaky abstractions.** The `get_fuel_storage()`, `get_max_fuel_storage()`, `add_fuel()`, `withdraw_fuel()` methods directly iterate over `design_data` components and inspect ResourceStorage abilities. This violates **Information Hiding** - the facility shouldn't know the internal structure of component abilities.

Meanwhile, `build_queue_source.py` duplicates this pattern with `_get_facility_production_rates()` which also iterates component abilities. **Two different files implementing the same "iterate design_data and extract ability" pattern.**

**Impact:**
- **Code duplication:** Ability extraction logic repeated in multiple places
- **Fragile to component schema changes:** If ResourceStorage format changes, must update multiple files
- **Missing abstraction:** No ComponentAbilityExtractor service to centralize this pattern
- **Violates DRY:** Same loop structure in 5+ places across codebase

**Recommendation:**
1. Create **ComponentAbilityAggregator service** to centralize ability extraction
2. Extract to **FacilityCapabilityService**: fuel storage, production rates, shipyard detection
3. Use **Strategy Pattern** for ability queries: `ability_extractor.get_storage_capacity(facility, 'fuel')`
4. Cache results in facility to avoid repeated iteration

**Effort:** Medium (affects facility interaction patterns)

---

#### Major: AR-007
**ID:** AR-007
**Location:** `game/strategy/data/ship_instance.py:239-271`, `game/strategy/services/ship_stats_calculator.py` (not shown, but referenced)

**Issue:** **ShipInstance.get_calculated_stats() performs hidden global registry access.** Line 258-264 shows ShipInstance directly importing and calling `get_default_registry_provider()` to construct GameRegistries on the fly. This is a **Service Locator anti-pattern** that:
- Hides dependencies (can't see from signature that registries are needed)
- Makes testing harder (global state dependency)
- Violates Dependency Injection principles
- Creates tight coupling to global registry provider

**Impact:**
- **Cannot test in isolation:** Tests must set up global registry provider
- **Unclear dependencies:** Method signature doesn't reveal GameRegistries requirement
- **Tight coupling to infrastructure:** Data model knows about global registry system
- **Difficult to parallelize:** Global state prevents concurrent execution

**Recommendation:**
1. **Inject registries via constructor** or method parameter
2. **Cache registries reference** in ShipInstance (passed during creation)
3. Use **Dependency Injection Container** for wiring instead of service locator
4. Add **registries parameter** to get_calculated_stats() (with default for backward compat)

**Effort:** Medium (requires passing registries through construction chain)

---

#### Major: AR-008
**ID:** AR-008
**Location:** `game/strategy/data/fleet.py:64-113`, `game/strategy/engine/fleet_order_processor.py:443-478`

**Issue:** **FleetOrder serialization uses type markers but lacks polymorphism.** The `to_dict()` and `from_dict()` methods use discriminator dicts (`{'type': 'fleet_ref', 'id': xxx}`, `{'type': 'planet_ref', ...}`) to encode different target types. This is a **manual type system** that should be handled by proper object-oriented polymorphism.

Additionally, `from_dict()` has 7 different target resolution branches (lines 448-471 in fleet.py), making it fragile and hard to extend.

**Impact:**
- **Type safety lost:** No compile-time checking of target types
- **Shotgun surgery:** Adding new order target type requires updating 3 methods: to_dict, from_dict, resolve_order_references
- **Error-prone:** Easy to forget a case in the type discrimination chain
- **Violates Open/Closed:** Cannot add target types without modifying FleetOrder

**Recommendation:**
1. Use **polymorphic order classes:** ColonizeOrder, MoveOrder, TransferOrder instead of generic FleetOrder
2. Apply **Factory Pattern** for deserialization: OrderFactory.from_dict(data)
3. Each order class handles its own serialization/deserialization
4. Use **Visitor Pattern** if order processing needs double dispatch

**Effort:** Complex (fundamental redesign of order system)

---

#### Major: AR-009
**ID:** AR-009
**Location:** `game/strategy/data/empire.py:26-27`, `game/strategy/data/build_queue_source.py:196-227`

**Issue:** **Empire holds raw collections of Planets and Fleets instead of managed collections.** `Empire.colonies` and `Empire.fleets` are plain Python lists that other code directly appends to, removes from, and iterates over. This violates **Encapsulation** and prevents:
- Enforcement of invariants (e.g., fleet.owner_id must match empire.id)
- Notification of changes (for observers/caching)
- Consistent collection management

Additionally, `build_queue_source.py` iterates `empire.colonies` and `empire.fleets` directly (lines 216-225, 250-253), exhibiting **feature envy** - external code knowing too much about Empire's internal structure.

**Impact:**
- **Cannot enforce invariants:** Direct list manipulation bypasses add_colony/remove_colony
- **Caching invalidation broken:** No way to know when colonies/fleets change
- **Violates Tell, Don't Ask:** External code queries Empire's collections instead of asking Empire to do operations
- **Cannot change implementation:** Switching to a different collection type breaks all consumers

**Recommendation:**
1. Make `colonies` and `fleets` **private** (`_colonies`, `_fleets`)
2. Provide **read-only views**: `get_colonies() -> Sequence[Planet]` (not List)
3. Encapsulate mutations through **command methods**: `empire.add_colony(planet)` already exists, enforce its use
4. Use **Collection classes** if complex operations needed: `empire.colonies.at_hex(coord)`
5. Apply **Repository Pattern** for queries: `colony_repository.find_by_empire(empire.id)`

**Effort:** Medium (affects many callsites)

---

#### Major: AR-010
**ID:** AR-010
**Location:** `game/strategy/facade/dto/fleet_dto.py:93-179`

**Issue:** **FleetInfo.from_fleet() performs complex business logic in DTO conversion.** Lines 120-161 show order target resolution logic embedded in DTO creation:
- Checking if order.target is HexCoord, Planet, Fleet, or dict
- Formatting display strings ("Load 10 passengers")
- Handling different order types with conditional branches

This violates **Single Responsibility** - a DTO factory should transform data structure, not interpret business rules.

**Impact:**
- **Business logic in presentation layer:** Order formatting rules live in DTO instead of domain
- **Testing complexity:** Must test DTO creation with all order permutations
- **Duplication risk:** If another DTO needs order info, logic is duplicated
- **Violates separation of concerns:** UI concerns (display strings) mixed with data transfer

**Recommendation:**
1. Add **presentation methods to FleetOrder:** `order.get_display_description()`, `order.get_target_hex()`
2. Move logic to **FleetOrderFormatter service** if needed across DTOs
3. Keep DTOs as **pure data containers** - only field-to-field mapping
4. Use **Builder Pattern** if DTO construction becomes complex

**Effort:** Simple (move logic to domain/service layer)

---

#### Major: AR-011
**ID:** AR-011
**Location:** `game/strategy/services/cargo_transfer_service.py:30-53`, `game/strategy/engine/fleet_order_processor.py:359-453`

**Issue:** **CargoTransferService and FleetOrderProcessor duplicate cargo transfer logic.** CargoTransferService.resolve_colonies() handles colony lookup with fleet location fallback (lines 31-52), while FleetOrderProcessor._execute_load() and _execute_unload() implement the actual transfer mechanics (lines 359-453). These should be in the same place.

Additionally, both classes know about the internal structure of transfer order targets (`params.get('direction')`, `params.get('cargo_type')`).

**Impact:**
- **Logic split across layers:** Discovery in service, execution in processor
- **Duplication:** Both know about transfer order parameter structure
- **Hard to change:** Modifying transfer behavior requires touching 2 classes
- **Unclear ownership:** Which class owns cargo transfer?

**Recommendation:**
1. **Consolidate in one place:** Either CargoTransferService handles full transfer, or FleetOrderProcessor does
2. Extract **TransferOperation value object** to encapsulate parameters instead of raw dicts
3. Use **Command Pattern:** TransferCommand encapsulates all transfer logic
4. Consider **Transaction Script Pattern** if transfer becomes more complex

**Effort:** Medium (requires consolidation)

---

### MINOR: Design Smells and Code Quality

#### Minor: AR-012
**ID:** AR-012
**Location:** `game/strategy/data/fleet.py:299-306`, `game/strategy/data/fleet.py:207-216`

**Issue:** **Delegation methods are boilerplate proxies.** Lines 299-306 show 8 consecutive one-line methods that just delegate to `self._battle.*()` or `self._resource_agg.*()`. This is **mechanical delegation** that adds no value and clutters the interface.

**Impact:**
- **Noise in API:** 20+ delegate methods make Fleet's interface hard to navigate
- **Maintenance burden:** Every delegate method needs documentation, testing
- **False abstraction:** Delegation doesn't provide abstraction, just indirection
- **IDE autocomplete pollution:** Hard to find actual Fleet methods among delegates

**Recommendation:**
1. **Expose delegate objects directly:** `fleet.resources.get_movement_costs()` instead of `fleet.get_movement_resource_costs()`
2. Use **property access** for delegates: `fleet.resources`, `fleet.capabilities`, `fleet.battle`
3. Keep only **high-level convenience methods** on Fleet: `fleet.can_move_to(hex)` as facade
4. Document delegate access points clearly in Fleet docstring

**Effort:** Simple (change public API, add deprecation warnings)

---

#### Minor: AR-013
**ID:** AR-013
**Location:** `game/strategy/data/ship_instance.py:175-182`

**Issue:** **ShipInstance._capture_resource_levels() is unnecessarily static.** The method is marked `@staticmethod` but is only used in one place (line 220), and it operates on IPostBattleShip protocol which is ship-specific. Making it static adds no value.

**Impact:**
- **Confusing API:** Why is a private method static?
- **Hard to test:** Cannot mock instance methods in static context
- **No reusability:** Only called once, doesn't justify static status

**Recommendation:**
1. Make it an **instance method** or **module-level function**
2. If truly reusable, move to **utility module**: `ship_utils.capture_resource_levels()`
3. Consider inlining if logic is simple (it's just a 4-line dict comprehension)

**Effort:** Trivial (change method signature)

---

#### Minor: AR-014
**ID:** AR-014
**Location:** `game/strategy/data/fleet_resource_aggregator.py:33-96`, `game/strategy/data/fleet_resource_aggregator.py:55-96`

**Issue:** **Helper methods reduce readability instead of improving it.** `_accumulate_ship_costs()` and `_verify_and_consume_resources()` were extracted to reduce duplication (per PROJ-204 comments), but they use lambda callbacks and double-loop structure that makes the code harder to follow than the original duplicated version would be.

Lines 76-95 show a two-phase verify-then-consume pattern that could be clearer as inline code.

**Impact:**
- **Harder to understand:** Callback-based logic requires mental stack unwinding
- **Over-abstraction:** DRY applied where copy-paste might be clearer
- **Poor names:** "verify_and_consume_resources" has a side effect despite "verify" sounding pure

**Recommendation:**
1. **Inline the helpers** and accept slight duplication for clarity
2. If keeping abstractions, use **named classes** instead of lambdas: `MovementCostGetter`, `WarpCostGetter`
3. Split into two methods: `verify_resources()` (pure) and `consume_resources()` (mutates)
4. Add **detailed docstrings** explaining the two-phase atomic pattern

**Effort:** Simple (refactor for clarity)

---

#### Minor: AR-015
**ID:** AR-015
**Location:** `game/strategy/data/planet.py:306-335`

**Issue:** **Planet.can_build_type() duplicates logic with FleetCapabilityCalculator.can_build_type().** Both implement similar "can build X vehicle type" checks with shipyard requirements, but Planet checks `self.has_space_shipyard` while Fleet checks facilities. This is the **same business rule implemented twice** with slight variations.

**Impact:**
- **Rule duplication:** Changing build requirements requires updating 2 places
- **Inconsistency risk:** Planet and Fleet might diverge in build rules
- **Missing abstraction:** No shared BuildCapabilityService

**Recommendation:**
1. Extract **BuildCapabilityService** with shared logic
2. Define **IBuildContext protocol** that both Fleet and Planet implement
3. Service method: `can_build(context: IBuildContext, vehicle_type: str)`
4. Centralize build rules in one place

**Effort:** Simple (extract common logic)

---

#### Minor: AR-016
**ID:** AR-016
**Location:** `game/strategy/data/ship_instance.py:82-86`

**Issue:** **Delegate initialization in __post_init__ violates fail-fast principle.** Lines 82-86 create delegate instances but these could fail silently if ShipResourceManager/ShipCargoManager/ShipDisplayFormatter have construction errors. Additionally, the delegates are initialized even if never used.

**Impact:**
- **Wasted initialization:** Delegates created even if not needed (e.g., formatter for headless tests)
- **Hidden failures:** Delegate construction errors don't fail at ship creation
- **Memory overhead:** 3 delegate objects * thousands of ships = significant memory

**Recommendation:**
1. Use **lazy initialization:** Create delegates on first access via properties
2. Add **validation** in __post_init__ for critical fields (instance_id, design_id)
3. Consider **Flyweight Pattern** for formatters if they're stateless
4. Profile memory usage and optimize if delegates cause issues

**Effort:** Simple (change initialization pattern)

---

### INFO: Observations and Suggestions

#### Info: AR-017
**ID:** AR-017
**Location:** `game/strategy/engine/fleet_order_processor.py:76`, `game/strategy/services/fleet_navigation_service.py:89`

**Issue:** **Inconsistent dependency injection patterns.** FleetOrderProcessor lazy-imports SuperweaponOrderProcessor in __init__ (line 76), while FleetMovementEngine accepts optional FleetNavigationService via constructor (fleet_movement_engine.py:57-60). The codebase mixes:
- Constructor injection (preferred)
- Lazy imports (circular dependency workaround)
- Global service locators (get_default_registry_provider)

**Impact:**
- **Inconsistent patterns:** New developers don't know which approach to use
- **Hidden dependencies:** Lazy imports make dependencies unclear
- **Testing complexity:** Different classes need different mocking strategies

**Recommendation:**
1. Standardize on **constructor injection with optional defaults**
2. Use **Dependency Injection Container** for complex wiring
3. Reserve lazy imports ONLY for intentional circular dependency breaks
4. Document standard patterns in ARCHITECTURE.md

**Effort:** Info (documentation + gradual migration)

---

#### Info: AR-018
**ID:** AR-018
**Location:** `game/strategy/data/fleet.py:1-552`, `game/strategy/data/planet.py:1-500`, `game/strategy/data/ship_instance.py:1-742`

**Issue:** **Missing domain events for state changes.** Fleet, Planet, and ShipInstance mutate state (add_ship, add_colony, update_from_ship) without emitting events. This makes it hard to:
- Track changes for undo/redo
- Implement observers (e.g., UI auto-refresh)
- Audit state changes for debugging
- Implement caching invalidation

**Impact:**
- **No change notification:** External code must poll or manually track changes
- **Caching is fragile:** No way to invalidate cached stats when ships added
- **Difficult debugging:** Cannot trace how state reached current configuration
- **Missing audit trail:** No log of who changed what when

**Recommendation:**
1. Implement **Domain Events** pattern: ShipAddedToFleet, ColonyClaimed, ShipDamaged
2. Add **EventBus** for publishing/subscribing to domain events
3. Use events for **cross-aggregate communication** instead of direct method calls
4. Consider **Event Sourcing** if full history tracking needed (probably overkill)

**Effort:** Complex (architectural change, but optional enhancement)

---

## Top 5 Priority Issues

### 1. **AR-001: Delegates Are Tightly Coupled Pseudo-Facades** (Critical)
**Why it's #1:** The core decomposition strategy is flawed. Delegates don't actually decouple - they just split a god class into co-dependent pieces. Fixing this requires fundamental redesign of Fleet/Planet/ShipInstance delegation pattern and will inform all other refactorings.

**Recommended Action:** Redesign delegates to accept data parameters instead of storing parent references. Define clear DTOs for delegate consumption.

---

### 2. **AR-003: FleetOrderProcessor is a New God Class** (Critical)
**Why it's #2:** 648 lines of mixed validation + execution logic violates SRP and will continue to grow with new order types. This is a **design regression** - decomposition created a new god class instead of eliminating complexity.

**Recommended Action:** Apply Command Pattern to break apart order processing. Each order type gets its own command class with validate() + execute().

---

### 3. **AR-002: Serialization Violates SRP** (Critical)
**Why it's #3:** Mixing domain logic with persistence makes both harder to evolve. Save format changes ripple through domain models, and domain changes break saves. This blocks the ability to version save files independently.

**Recommended Action:** Extract Repository classes for Fleet/Planet/ShipInstance serialization. Use DTOs for persistence format.

---

### 4. **AR-008: FleetOrder Lacks Polymorphism** (Major)
**Why it's #4:** Manual type discrimination with string markers is error-prone and doesn't leverage the type system. Adding order types requires shotgun surgery across 3 methods. Polymorphic order classes would eliminate this fragility.

**Recommended Action:** Create order class hierarchy (ColonizeOrder, MoveOrder, TransferOrder) with polymorphic to_dict/from_dict.

---

### 5. **AR-004: Data Classes Reach Into Services** (Major)
**Why it's #5:** Late imports hide circular dependencies and violate layering. Data models should not know about services. This prevents proper dependency management and makes testing harder.

**Recommended Action:** Invert dependencies using DI. Pass calculators TO data models instead of having data models import calculators.

---

## Architectural Recommendations Summary

### Immediate Actions (Next Sprint)
1. **Define DTO contracts** for delegate consumption (AR-001)
2. **Extract order command classes** to break up FleetOrderProcessor (AR-003)
3. **Standardize DI pattern** and document in ARCHITECTURE.md (AR-017)

### Short-term (Next 2-3 Sprints)
4. **Implement Repository Pattern** for serialization (AR-002)
5. **Create polymorphic order hierarchy** (AR-008)
6. **Consolidate cargo transfer logic** (AR-011)
7. **Expose delegates as properties** instead of proxy methods (AR-012)

### Long-term (Strategic Improvements)
8. **Implement Domain Events** for change notification (AR-018)
9. **Extract ComponentAbilityAggregator** to centralize ability extraction (AR-006)
10. **Encapsulate Empire collections** with managed collection classes (AR-009)

### Architectural Principles to Adopt
- **Dependency Inversion:** High-level modules should not depend on low-level modules; both should depend on abstractions
- **Tell, Don't Ask:** Objects should tell other objects what to do, not query their state and make decisions
- **Single Responsibility:** Each class should have one reason to change
- **Command-Query Separation:** Methods either change state (command) or return data (query), not both
- **Fail Fast:** Validate early and loudly; don't allow invalid state to propagate

---

## Conclusion

The facade/delegate decomposition **reduced line counts** but **did not fix the underlying architectural problems**:

✅ **What worked:**
- Smaller individual class files (Fleet: 552 lines, down from ~1000+)
- Some separation of concerns (battle logic separate from resources)

❌ **What didn't work:**
- Delegates are still tightly coupled to parent classes
- FleetOrderProcessor became a new god class (648 lines)
- Services exhibit feature envy (reaching into data internals)
- No clear abstraction layers or protocols
- Missing polymorphism where needed (order types)

**Next Steps:**
1. Fix delegate coupling (AR-001) as foundation
2. Break apart FleetOrderProcessor (AR-003) to prevent god class reformation
3. Establish clear architectural boundaries with DTOs and protocols
4. Adopt Command Pattern for extensible order processing
5. Extract repositories to separate domain from persistence

The good news: The decomposition created **extension points** where proper abstractions can be inserted. The bad news: Without addressing coupling and missing abstractions, the codebase will continue accumulating god classes in new places.

**Overall Grade:** C+ (Partial Success)
The refactoring moved in the right direction but stopped short of true decoupling. Recommend continuing with architectural improvements outlined above.
