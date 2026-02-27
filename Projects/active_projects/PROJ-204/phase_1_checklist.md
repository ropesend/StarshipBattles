# Phase 1: Foundation Utilities

**Findings:** AR-02, CQ-20, CQ-21, CQ-82
**Effort:** Medium
**Goal:** Create the shared utilities that unblock consolidation in later phases

## Tasks

### 1.1 Create LayerIterator utility (AR-02, CQ-20)
- [x] Create `game/core/patterns/layer_iterator.py`
- [x] Implement `iter_components(layers)` - yields all components across all layers
- [x] Implement `iter_layers_and_components(layers)` - yields (layer_name, component) tuples
- [x] Implement `get_component_id(comp_entry)` - safe ID extraction from str or dict
- [x] Handle all format variations (list, dict, missing keys)
- [x] Write unit tests for LayerIterator (21 tests)
- [x] Replace layer iteration in `game/strategy/engine/production_engine.py`
- [x] Replace layer iteration in `game/strategy/engine/maintenance_engine.py`
- [x] Replace layer iteration in `game/strategy/engine/harvesting_engine.py` (2 locations)
- [x] Replace layer iteration in `game/strategy/engine/empire_economy_calculator.py`
- [x] Replace layer iteration in `game/strategy/data/planet.py` (2 locations)
- [x] Replace layer iteration in `game/strategy/data/design_metadata.py` (2 locations)
- [x] Replace layer iteration in `game/strategy/services/ship_stats_calculator.py`
- [x] Skipped ship_instance.py - uses index tracking incompatible with iterator
- [x] Run full test suite - verify passing

### 1.2 Create DesignCostCalculator (CQ-21, CQ-82)
- [x] Create `game/strategy/services/design_cost_calculator.py`
- [x] Implement `calculate_total_cost(design_data)` using LayerIterator
- [x] Implement `calculate_maintenance_cost(design_data, rate)`
- [x] Field naming: `resource_cost` is standard for production/maintenance; `cost` is separate for DesignMetadata display
- [x] Write unit tests for DesignCostCalculator (14 tests)
- [x] Refactor `ProductionEngine._calculate_design_cost()` to use calculator
- [x] Refactor `MaintenanceEngine.calculate_maintenance_cost()` to delegate to calculator
- [x] Skipped DesignMetadata - uses different field (`cost`) for different purpose
- [x] Run full test suite - verify passing

## Completion Checklist
- [x] All tasks above completed
- [x] Full test suite passes: 12778 passed, 1 skipped
- [x] No new warnings introduced

## Implementation Notes
- Created new `game/core/patterns/` module with `layer_iterator.py`
- Added `iter_components_with_ids()` as additional convenience function
- DesignCostCalculator exports `DEFAULT_MAINTENANCE_RATE` for consistency
- MaintenanceEngine re-exports `MAINTENANCE_RATE` for backward compatibility
- Total: 35 new tests added, 8 files refactored
