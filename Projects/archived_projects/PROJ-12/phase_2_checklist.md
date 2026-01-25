# PROJ-12 Phase 2: Ship Component Manager

## Phase Overview
Extract component and layer management from Ship class.

**Status:** Complete (Core Extraction)

## Tasks

### Create ShipComponentManager Class
- [x] Create `game/simulation/entities/ship_component_manager.py`
- [x] Define ShipComponentManager class
- [x] Move add_component() logic
- [x] Move remove_component() logic
- [x] Move get_all_components() and variants
- [x] Move layer initialization and management
- [x] Move component iteration methods

### Address SIM-02: Reduce Ship-Component Coupling
- [ ] Components should not require `component.ship` reference
- [ ] Pass context as parameter to component methods
- [ ] Create ComponentContext dataclass for required data
- [ ] Update component.recalculate_stats() to use context
**Deferred:** This is a larger refactoring effort that affects many components. Recommend separate phase or project.

### Address SIM-09: Consolidate Ability Aggregation
- [ ] Review ability_aggregator.py
- [ ] Ensure single source of truth for ability totals
- [ ] Either ship method OR calculator, not both
- [ ] Update Ship.get_total_ability_value() if needed
- [ ] Update ShipStatsCalculator to use same logic
**Deferred:** This is an optimization task that can be addressed separately without blocking the god class decomposition.

### Update Ship Class
- [x] Keep component methods as thin wrappers
- [x] Delegate to ShipComponentManager internally
- [x] Maintain backward-compatible interface

### Unit Tests
- [x] Create `tests/unit/simulation/test_ship_component_manager.py`
- [x] Test add_component() with validation
- [x] Test remove_component()
- [x] Test layer management
- [x] Test component queries

### Integration Tests
- [x] Ship builder tests pass (267 entities tests pass)
- [x] Ship validation tests pass
- [x] Stat calculation tests pass

## Verification
- [x] Ship class reduced (was ~787, now ~780 lines - delegation adds some lines)
- [x] ShipComponentManager 330 lines (contains extracted logic)
- [ ] Component coupling reduced (deferred to future phase)
- [x] All tests pass (341 combat/simulation tests, 189 integration tests)

## Implementation Notes
- Used facade pattern: Ship methods delegate to component_manager
- Lazy initialization via `component_manager` property
- `layers` dict is shared between Ship and ShipComponentManager
- Fixed `_initialize_layers()` to sync component_manager when ship class changes
- Updated test_armor_mechanics.py to use ShipCombatEngine directly (Phase 1 compat)

## Additional Test Fixes
- Fixed 27 armor mechanics tests that were incompatible with Phase 1 facade pattern
- Tests now use ShipCombatEngine directly instead of mock classes inheriting ShipCombatMixin
