# DRY-CROSS: Cross-Layer Duplication Patterns Report

## Summary
- **Total cross-layer duplication findings:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

## Findings

### CRITICAL: Numeric Type Checking Pattern (30+ occurrences, 15+ files, 3 layers)
**ID:** XL-001
**Layers Affected:** simulation, strategy, ui
**Location:** 15+ files across abilities, validators, UI config panels, AI controller
**Issue:** `isinstance(value, (int, float))` appears 30+ times. Also the compound pattern `data if isinstance(data, (int, float)) else data.get('value', default)` repeated extensively.
**Impact:** Numeric coercion logic scattered with no single source of truth.
**Recommendation:** Create `game/core/numeric_utils.py` with `is_numeric()` and `coerce_numeric()`.
**Effort:** Simple

### CRITICAL: Resource Calculation Logic Across Layers
**ID:** XL-002
**Layers Affected:** simulation, strategy
**Location:** `resource_manager.py`, `ship_resource_manager.py`, `component_resource_manager.py`, `ship_stats_calculator.py`
**Issue:** Three parallel resource management systems with nearly identical get/consume/set patterns.
**Impact:** Resource behavior inconsistencies between combat and strategy layers.
**Recommendation:** Create abstract `IResourceManager` protocol in `game/core/resource_contracts.py`.
**Effort:** Medium

### MAJOR: Design Component Iteration Patterns
**ID:** XL-003
**Layers Affected:** simulation, strategy
**Location:** `ship.py` (get_all_components), `component_inspector.py` (iterate_design_components), `ship_validator.py`
**Issue:** Two different patterns: runtime Component iteration vs design-time JSON/dict iteration. Partially addressed by ComponentInspector but simulation layer still has own pattern.
**Recommendation:** Extend ComponentInspector with unified `iterate_component_abilities()`.
**Effort:** Simple

### MAJOR: Stat Calculation Duplication
**ID:** XL-005
**Layers Affected:** simulation, strategy
**Location:** `ship_stat_querier.py`, `ship_stats.py`, `ship_stats_calculator.py` (strategy), `component_stats_calculator.py`
**Issue:** Multiple layers of stat calculation with overlapping responsibility and stack_group rules.
**Impact:** If stack_group rules change, both layers need updating.
**Recommendation:** Extract core `AbilityAggregator` with stack_group logic to `game/core/ability_aggregation.py`.
**Effort:** Complex

### MAJOR: Serialization Pattern Duplication
**ID:** XL-006
**Layers Affected:** simulation, strategy
**Location:** ship_serialization.py, ship_instance.py, fleet.py, battle_state.py, research_tracker.py, galaxy.py
**Issue:** Every major class implements to_dict/from_dict independently. No shared base or mixin.
**Impact:** 500+ lines of serialization boilerplate across 20+ classes.
**Recommendation:** Create `game/core/serializable.py` with `Serializable` base class and auto-serialization.
**Effort:** Medium

### MAJOR: Damage/Health Management
**ID:** XL-007
**Layers Affected:** simulation, strategy
**Location:** `component_health_manager.py`, `ship_instance.py:252,387-422`
**Issue:** Strategy layer reimplements damage summary methods that simulation already calculates.
**Recommendation:** Create `game/core/health_utils.py` with shared damage analysis functions.
**Effort:** Simple

### Minor: Cost Calculation Patterns
**ID:** XL-008
**Layers Affected:** simulation, strategy, ui
**Issue:** Cost calculation scattered with inconsistent terminology (base_cost, modified_cost, calculated_cost).
**Recommendation:** Standardize terminology; create `game/core/cost_utils.py`.
**Effort:** Simple

### Minor: Type Checking/Coercion Patterns
**ID:** XL-009
**Layers Affected:** core, simulation, strategy, ui
**Issue:** Type validation patterns like `isinstance(param, type)` repeated without shared utilities.
**Recommendation:** Create `game/core/type_utils.py` with assertion utilities.
**Effort:** Simple

### Minor: Validation Result Consolidation (Already Done Well!)
**ID:** XL-004
**Layers Affected:** all
**Issue:** POSITIVE FINDING - ValidationResult was previously duplicated but has been consolidated. Good pattern.
**Recommendation:** Document as exemplary pattern.
**Effort:** Complete

### Minor: Formula System (Good Cross-Layer Usage)
**ID:** XL-011
**Issue:** POSITIVE - Formula system correctly centralized in simulation, properly imported by strategy.
**Effort:** N/A

### Info: Event/Observer Pattern
**ID:** XL-010
**Issue:** Only UI layer implements observer pattern. Other layers use direct calls. Acceptable for now.
**Effort:** N/A

### Info: Logging Pattern
**ID:** XL-012
**Issue:** POSITIVE - Logging consistently centralized in core/logger.py. Good design.
**Effort:** N/A

## Top 5 Cross-Layer Consolidation Opportunities
1. **XL-001**: Numeric utilities - 30+ occurrences, 15 files, Simple, Highest frequency
2. **XL-006**: Serializable base class - 20+ classes, 500+ lines, Medium, High ROI
3. **XL-002**: Resource manager interface - 4 managers, Medium, Prevents inconsistency
4. **XL-003**: Component ability iteration - 20+ files, Simple, Single source of truth
5. **XL-009**: Type utilities - 10+ files, Simple, Consistent error messages
