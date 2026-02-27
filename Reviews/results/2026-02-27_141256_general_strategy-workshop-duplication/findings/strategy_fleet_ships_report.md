# Strategy Fleet & Ships DRY Analysis

### Summary
- Total issues found: 9
- Critical: 2, Major: 4, Minor: 3, Info: 0

### Findings

#### CRITICAL: Parallel Cargo Operation Patterns in Fleet vs Ship
**ID:** CQ-01
**Location:** `game/strategy/data/fleet_resource_aggregator.py:263-313` and `game/strategy/data/ship_cargo_manager.py:69-117`
**Issue:** Both `FleetResourceAggregator` and `ShipCargoManager` implement identical cargo loading/unloading patterns with the same business logic structure: check amount validity, calculate space available, use min() to cap at limits, update dict and return actual amount.
**Impact:** Changes to cargo transfer logic must be updated in two places, risking divergent behavior.
**Recommendation:** Create a generic `CargoTransferOperation` utility or extract a `_transfer_cargo_atomic()` method that both use.
**Effort:** Medium

#### CRITICAL: Dual Implementation of Resource Consumption Verification
**ID:** CQ-02
**Location:** `game/strategy/data/fleet_resource_aggregator.py:47-97` and `game/strategy/data/fleet_resource_aggregator.py:115-162`
**Issue:** `has_resources_for_movement()` and `has_resources_for_warp()` implement virtually identical verification loops. Same pattern repeats for `consume_movement_resources()` and `consume_warp_resources()`. Four methods are nearly identical except for which cost getter is called.
**Impact:** Four methods with near-identical logic create high maintenance burden and risk of inconsistent behavior when resource mechanics change.
**Recommendation:** Extract a generic `_verify_and_consume_resources()` method that takes a cost getter function as parameter. Reduce from 4 methods to 1 implementation + 2 thin wrappers.
**Effort:** Medium

#### MAJOR: Repeated Component Iteration Pattern in FleetCapabilityCalculator
**ID:** CQ-03
**Location:** `game/strategy/data/fleet_capability_calculator.py:65-72, 128-142, 156-170`
**Issue:** Three methods iterate over combat-capable ships and invoke component_inspector functions with the same pattern. Component registry is looked up redundantly in each iteration.
**Impact:** Adding new fleet-wide ship filters requires understanding the iteration pattern. Performance optimization opportunity missed.
**Recommendation:** Create a generic `_filter_ships_by_condition()` method that takes a predicate function.
**Effort:** Simple

#### MAJOR: Mirrored Resource Aggregation Between Fleet and Ship Layers
**ID:** CQ-04
**Location:** `game/strategy/data/fleet_resource_aggregator.py:33-45` and `game/strategy/data/ship_resource_manager.py:42-54`
**Issue:** Both expose near-identical public APIs for resource queries but at different scopes. API surface is confusing.
**Impact:** Developer unsure whether to call ship-level or fleet-level resource queries.
**Recommendation:** Clarify layering: remove redundant single-ship queries from FleetResourceAggregator, force callers to query ships directly.
**Effort:** Medium

#### MAJOR: Display/Status Methods Split Between Formatter and Instance
**ID:** CQ-05
**Location:** `game/strategy/data/ship_display_formatter.py` and `game/strategy/data/ship_instance.py:282-293, 413-459`
**Issue:** Status and display logic is split inconsistently - some goes to formatter, some stays in ShipInstance.
**Impact:** A new display feature might get added to wrong class.
**Recommendation:** Complete the extraction: move ALL display/formatting concerns to ShipDisplayFormatter. ShipInstance should be pure data/state.
**Effort:** Simple

#### MAJOR: Parallel Serialization/Deserialization Patterns
**ID:** CQ-06
**Location:** `game/strategy/data/fleet.py:367-483` and `game/strategy/data/ship_instance.py:638-715`
**Issue:** Both Fleet and ShipInstance implement `to_dict()`/`from_dict()` pairs with similar structural patterns for validation, nested types, logging, and backward compatibility.
**Impact:** Serialization bugs in one class might be replicated in the other. Adding a new field requires changes in two places.
**Recommendation:** Create a `StrategyLayerSerializer` utility with shared methods for HexCoord serialization, safe parsing, and fallback handling.
**Effort:** Medium

#### Minor: Resource Cost Accumulation Pattern Repeated
**ID:** CQ-07
**Location:** `game/strategy/data/fleet_resource_aggregator.py:40-45` and `fleet_resource_aggregator.py:108-113`
**Issue:** Same 6-line accumulation pattern is copy-pasted with only the method call changing.
**Impact:** Minor - pattern is localized.
**Recommendation:** Create `_accumulate_ship_costs(self, cost_getter_method: str)` helper.
**Effort:** Simple

#### Minor: Repeated Effectiveness Calculation for Components
**ID:** CQ-08
**Location:** `game/strategy/services/ship_stats_calculator.py:300-357` and `game/strategy/services/ship_stats_calculator.py:360-380`
**Issue:** Standard degradation and all-or-nothing warp effectiveness both follow the same retrieval pattern.
**Impact:** Minor - separation is intentional.
**Recommendation:** Consider parameterizing effectiveness calculation via a strategy object.
**Effort:** Complex

#### Minor: FleetOrder Target Serialization Complexity
**ID:** CQ-09
**Location:** `game/strategy/data/fleet.py:75-113` and `game/strategy/data/fleet.py:434-478`
**Issue:** Massive if-elif chain serializes different target types. Reverse in `from_dict()` mirrors with equal complexity.
**Impact:** Adding a new order type requires understanding both serialization directions.
**Recommendation:** Create a `FleetOrderSerializer` with registered handlers.
**Effort:** Medium

### Top 5 Priority Issues
1. **CQ-02**: Dual Resource Consumption Verification (CRITICAL) - 4 nearly-identical methods
2. **CQ-01**: Parallel Cargo Operation Patterns (CRITICAL) - Duplicate business logic
3. **CQ-06**: Serialization Pattern Duplication (MAJOR) - 100+ lines duplicated
4. **CQ-03**: Fleet Ship Iteration Pattern (MAJOR) - Blocks batch query operations
5. **CQ-04**: Resource API Confusion (MAJOR) - Unclear layer abstractions
