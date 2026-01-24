# PROJ-12 Phase 2: Ship Component Manager

## Phase Overview
Extract component and layer management from Ship class.

## Tasks

### Create ShipComponentManager Class
- [ ] Create `game/simulation/entities/ship_component_manager.py`
- [ ] Define ShipComponentManager class
- [ ] Move add_component() logic
- [ ] Move remove_component() logic
- [ ] Move get_all_components() and variants
- [ ] Move layer initialization and management
- [ ] Move component iteration methods

### Address SIM-02: Reduce Ship-Component Coupling
- [ ] Components should not require `component.ship` reference
- [ ] Pass context as parameter to component methods
- [ ] Create ComponentContext dataclass for required data
- [ ] Update component.recalculate_stats() to use context

### Address SIM-09: Consolidate Ability Aggregation
- [ ] Review ability_aggregator.py
- [ ] Ensure single source of truth for ability totals
- [ ] Either ship method OR calculator, not both
- [ ] Update Ship.get_total_ability_value() if needed
- [ ] Update ShipStatsCalculator to use same logic

### Update Ship Class
- [ ] Keep component methods as thin wrappers
- [ ] Delegate to ShipComponentManager internally
- [ ] Maintain backward-compatible interface

### Unit Tests
- [ ] Create `tests/unit/simulation/test_ship_component_manager.py`
- [ ] Test add_component() with validation
- [ ] Test remove_component()
- [ ] Test layer management
- [ ] Test component queries

### Integration Tests
- [ ] Ship builder tests pass
- [ ] Ship validation tests pass
- [ ] Stat calculation tests pass

## Verification
- [ ] Ship class reduced by another ~150 lines
- [ ] ShipComponentManager < 200 lines
- [ ] Component coupling reduced
- [ ] All tests pass
