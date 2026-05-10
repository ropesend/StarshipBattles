# Strategy Galaxy, Planets & Economy DRY Analysis

### Summary
- Total issues found: 9
- Critical: 2, Major: 3, Minor: 4, Info: 0

### Findings

#### CRITICAL: Layer Iteration Pattern Duplication
**ID:** CQ-20
**Location:** `game/strategy/engine/production_engine.py:78-83`, `game/strategy/engine/maintenance_engine.py:55-72`, `game/strategy/engine/harvesting_engine.py:150+`, `game/strategy/engine/empire_economy_calculator.py:155-162`, `game/strategy/data/planet.py:86-98`, `game/strategy/data/planet.py:144-153`
**Issue:** Nearly identical layer iteration logic appears in 6+ locations with inconsistent format handling (dict vs list).
**Impact:** Code duplication across 6+ files. Inconsistent handling of layer formats. Maintenance burden.
**Recommendation:** Extract canonical `iterate_design_layers()` / `iterate_facility_layers()` utilities into `game/strategy/services/component_inspector.py`.
**Effort:** Simple

#### CRITICAL: Resource Cost Calculation Duplication
**ID:** CQ-21
**Location:** `game/strategy/engine/maintenance_engine.py:38-78`, `game/strategy/engine/production_engine.py:61-85`, `game/strategy/engine/empire_economy_calculator.py:134-183`
**Issue:** Three independent implementations of "sum all component resource_cost values across layers". MaintenanceEngine handles both dict/list formats while ProductionEngine only handles dict.
**Impact:** Risk of economic bugs where costs differ between systems.
**Recommendation:** Create shared `DesignCostCalculator` utility with `calculate_total_design_cost()` and `calculate_maintenance_cost()`.
**Effort:** Medium

#### MAJOR: Deserialization Error Handling Pattern
**ID:** CQ-22
**Location:** `game/strategy/data/galaxy.py:108-158`, `game/strategy/data/planet.py:411-515`, `game/strategy/data/galaxy.py:570-642`
**Issue:** 11+ nearly identical error-handling loops across 3 classes for resilient deserialization with error isolation. Inconsistent exception typing and logging messages.
**Impact:** Hard to maintain consistent behavior across deserializers.
**Recommendation:** Create `deserialize_list()` utility in `game/core/json_utils.py` and replace all 11+ loops.
**Effort:** Medium

#### MAJOR: Harvester/Storage Ability Extraction Duplication
**ID:** CQ-23
**Location:** `game/strategy/engine/harvesting_engine.py:34-79`, `game/strategy/engine/empire_economy_calculator.py:164-166`, `game/strategy/data/planet.py:86-98`
**Issue:** Three different approaches to "extract ability from component definition" with different robustness levels.
**Impact:** Planet and EconomyCalculator are less robust than HarvestingEngine.
**Recommendation:** Expand ComponentInspector with `get_ability_from_component()` and `collect_ability_from_design()` utilities.
**Effort:** Medium

#### MAJOR: Planet/Facility Resource Capacity Aggregation
**ID:** CQ-24
**Location:** `game/strategy/engine/harvesting_engine.py:142-150`, `game/strategy/data/planet.py:69-98`, `game/strategy/services/ship_stats_calculator.py:~100+`
**Issue:** Multiple independent implementations of "aggregate resource capacity from facilities/ships" with inconsistent operational status checking.
**Impact:** Inconsistent handling of operational status.
**Recommendation:** Create shared facility/design scanner in `game/strategy/services/facility_scanner.py`.
**Effort:** Medium

#### Minor: Duplicate from_dict Validation Patterns
**ID:** CQ-25
**Location:** `game/strategy/data/galaxy.py:51-70`, `game/strategy/data/planet.py:44-67`, `game/strategy/data/planet.py:168-187`, `game/strategy/data/stars.py:66-98`
**Issue:** Nearly identical validation structure in all dataclass from_dict methods (require_keys, validate_enum, validate_positive).
**Impact:** Inconsistent validation approaches.
**Recommendation:** Create decorator-based validation framework or factory pattern.
**Effort:** Medium

#### Minor: Similar Zone Registration Logic
**ID:** CQ-26
**Location:** `game/strategy/data/galaxy.py:209-214`, `game/strategy/data/galaxy.py:626-637`, `game/strategy/data/galaxy_entity_registry.py:156-173`
**Issue:** Zone registration appears in 3 places with similar but slightly different logic.
**Impact:** Duplicated loop structure.
**Recommendation:** Create `register_zones_from_system()` batch registration helper.
**Effort:** Simple

#### Minor: Warp Point Index Rebuild Logic
**ID:** CQ-27
**Location:** `game/strategy/data/galaxy.py:216-218`, `game/strategy/data/galaxy.py:634-637`, `game/strategy/data/galaxy.py:548-552`
**Issue:** Nearly identical warp point index rebuild code appears 3 times.
**Impact:** Risk of divergent behavior.
**Recommendation:** Extract `_rebuild_warp_point_index(system)` helper.
**Effort:** Simple

#### Minor: Fuel Storage Ability Hardcoding
**ID:** CQ-28
**Location:** `game/strategy/data/planet.py:73-98`, `game/strategy/engine/harvesting_engine.py:34-80`
**Issue:** `get_max_fuel_storage()` is hardcoded for fuel only while HarvestingEngine has generic extraction.
**Impact:** Creates pattern of resource-specific methods rather than generic.
**Recommendation:** Refactor to generic `get_resource_storage_capacity(resource_type, registries)`.
**Effort:** Simple

### Top 5 Priority Issues
1. **CQ-20**: Layer Iteration Pattern Duplication (CRITICAL) - 6+ files, inconsistent format handling
2. **CQ-21**: Resource Cost Calculation Duplication (CRITICAL) - Risk of economic bugs
3. **CQ-22**: Deserialization Error Handling Pattern (MAJOR) - 11+ identical loops
4. **CQ-23**: Harvester/Storage Ability Extraction (MAJOR) - Three different approaches
5. **CQ-24**: Resource Capacity Aggregation (MAJOR) - Inconsistent operational status checking
