# Cross-Layer Duplication Analysis

### Summary
- Total issues found: 8
- Critical: 2, Major: 3, Minor: 2, Info: 1

### Findings

#### CRITICAL: Design Metadata Calculations Duplicated Across Layers
**ID:** CQ-80
**Location:** `game/strategy/data/design_metadata.py:168-224` and `game/simulation/entities/ship.py:608-614`
**Issue:** DesignMetadata contains two separate implementations for calculating combat power and resource costs - one working on raw design dict, one on Ship object. Builder UI implicitly depends on these.
**Impact:** If calculations change, design library metadata may diverge from actual ship stats.
**Recommendation:** Document DesignMetadata as canonical source. Add contract comments.
**Effort:** Simple

#### CRITICAL: Design Data Loading Split Between Layers
**ID:** CQ-81
**Location:** `game/strategy/systems/design_library.py:190-221` and `game/ui/services/design_loader_adapter.py:52-75`
**Issue:** Two separate code paths load designs. Strategy returns raw dict, UI creates Ship object from dict. Both use SimulationDesignLoader internally but with different assumptions.
**Impact:** Workshop save/load cycle may not be symmetric if paths diverge. UI adapter duplicates strategy layer's responsibility.
**Recommendation:** Make DesignLibrary the single source of truth for design I/O. Have UI adapter delegate to DesignLibrary.
**Effort:** Medium

#### MAJOR: Resource Cost Calculation Duplicated Across Three Engines
**ID:** CQ-82
**Location:** `game/strategy/engine/production_engine.py:61-85`, `game/strategy/engine/maintenance_engine.py:257-280`, `game/strategy/data/design_metadata.py:227-268`
**Issue:** Multiple independent implementations sum component resource_cost fields. Note field name difference: `resource_cost` vs `cost` - latent bug.
**Impact:** Three places to fix if cost model changes. Field name inconsistency could cause silent data loss.
**Recommendation:** Create shared `DesignCostCalculator` utility. Standardize field naming.
**Effort:** Medium

#### MAJOR: Ship Display Formatting Located in Wrong Layer
**ID:** CQ-83
**Location:** `game/strategy/data/ship_display_formatter.py` vs `game/ui/screens/build_queue_helpers.py`
**Issue:** ShipDisplayFormatter in strategy layer handles presentation concerns. Strategy layer has UI-specific concerns (status text, display IDs).
**Impact:** Presentation logic scattered across layers.
**Recommendation:** DEFER - requires IShipInstance Protocol work (PROJ-193). Remove from strategy, have UI format via dedicated formatters.
**Effort:** Complex

#### MAJOR: Design Library Filtering Logic Partially Duplicated in UI
**ID:** CQ-84
**Location:** `game/strategy/systems/design_library.py:303-357` vs `game/ui/screens/design_selector_window.py:241-277`
**Issue:** Both layers implement filtering logic. UI manages filter UI state while DesignLibrary manages filter business logic. Coordination overhead.
**Impact:** Adding new filters requires changes in both layers.
**Recommendation:** Extract `DesignFilterManager` class in strategy layer with mutable state for current filters.
**Effort:** Medium

#### Minor: Metadata Loading with Embedded Metadata Pattern
**ID:** CQ-85
**Location:** `game/strategy/systems/design_library.py:149-156` vs `game/strategy/data/design_metadata.py:119-135`
**Issue:** Both places extract metadata from the same `_metadata` location but with different field selections.
**Impact:** Easy to forget to preserve metadata fields.
**Recommendation:** Consolidate metadata handling. Move preservation logic to DesignMetadata.
**Effort:** Simple

#### Minor: Ship Stats Calculator Imports From Simulation
**ID:** CQ-86
**Location:** `game/strategy/services/ship_stats_calculator.py:1-37`
**Issue:** Imports from simulation layer documented as intentional. No action needed.
**Recommendation:** No action needed.
**Effort:** N/A

#### Info: Multiple Validation Paths for Ships
**ID:** CQ-87
**Location:** `game/simulation/entities/ship.py:608-614`, `game/ui/panels/design_stats_panel.py:373-415`
**Issue:** Ship provides validation methods, UI independently formats results. This is appropriate separation.
**Recommendation:** No action needed.
**Effort:** N/A

### Top 5 Priority Issues
1. **CQ-82**: Resource Cost Calculation (CRITICAL) - Field name inconsistency, 3 implementations
2. **CQ-81**: Design Data Loading (CRITICAL) - Split responsibility
3. **CQ-80**: Design Metadata (MEDIUM) - Undocumented contract
4. **CQ-84**: Design Library Filtering (MAJOR) - Scattered filter logic
5. **CQ-85**: Metadata Preservation (MINOR) - Split across classes
