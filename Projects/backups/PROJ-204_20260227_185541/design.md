# PROJ-204: Design Document

## Architecture Decisions

### Phase 1: Foundation Utilities

**LayerIterator** (`game/core/patterns/layer_iterator.py`)
- Canonical methods for iterating ship/facility layers and extracting components
- Handles all format variations (list, dict, with/without component objects)
- Methods: `iter_components(layers)`, `iter_layers_and_components(layers)`, `get_component_id(comp_entry)`
- Replaces 19+ duplicated iteration patterns across strategy, simulation, and UI

**DesignCostCalculator** (`game/strategy/services/design_cost_calculator.py`)
- Single source of truth for resource cost summation from design data
- Methods: `calculate_total_cost(design_data)`, `calculate_maintenance_cost(design_data, rate)`
- Standardizes field naming (`resource_cost` vs `cost` inconsistency)
- Used by: ProductionEngine, MaintenanceEngine, DesignMetadata

### Phase 2: Quick Wins
- `PathHelper.strip_start_hex(fleet, path)` - 3-line utility, fixes MoveCommandHandler bug
- `SpeedHelper.get_tick_interval(speed)` - 3-line utility
- `Galaxy._rebuild_warp_point_index(system)` / `register_zones_from_system(system)` - small helpers
- `FleetResourceAggregator._accumulate_ship_costs(cost_getter)` - inline helper

### Phase 3: Command Handler Consolidation
- `MissionSetupHelper.setup_mission_move(session, fleet, target_hex)` - shared for all 7 mission handlers
- `BaseCommandHandler` enhancements: `_resolve_fleet_required()`, `_resolve_planet_optional()`
- `CommandHelper.add_move_order_if_needed(fleet, target_hex)`

### Phase 4: Strategy Layer Consolidation
- `FleetResourceAggregator._verify_and_consume_resources(cost_getter, consume)` - reduces 4 methods to 1
- `deserialize_list()` utility in `game/core/json_utils.py` - replaces 11+ error-handling loops
- Expand `ComponentInspector` with ability extraction utilities

### Phase 5: Workshop UI Cleanup
- `ModifierControlRow._get_local_bounds()` - extract min/max logic
- `PanelFactory.create_titled_panel()` - eliminate bootstrap boilerplate
- `ModifierControlRow._set_controls_enabled(enabled)` - consolidate enable/disable
- `UIElementRegistry` helper with `kill_all()` method
- Consolidate event constants into unified `UIEvents` class

## Testing Strategy
- Run full test suite before and after each phase
- Each extracted utility gets dedicated unit tests
- Refactored call sites verified by existing tests
