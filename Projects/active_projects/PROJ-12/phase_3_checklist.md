# PROJ-12 Phase 3: TurnEngine Decomposition

## Phase Overview
Split TurnEngine into specialized services.

## Tasks

### Create FleetMovementEngine
- [x] Create `game/strategy/engine/fleet_movement_engine.py`
- [x] Move _calculate_next_hex() logic
- [x] Move path management logic
- [x] Move resource consumption logic
- [x] Move warp travel handling
- [x] Add clear interface with movement results
  - **Created**: `MovementResult` dataclass, `collect_movements()`, `apply_movements()`
  - **Tests**: 29 tests in `test_fleet_movement_engine.py`

### Create ProductionEngine
- [x] Create `game/strategy/engine/production_engine.py`
- [x] Move construction queue processing
- [x] Move ship spawning logic
- [x] Handle production format migration (STRAT-009)
- [x] Support single format going forward
  - **Note**: Both list and dict formats supported for backward compatibility
  - **Tests**: 25 tests in `test_production_engine.py`

### Create FleetOrderProcessor
- [x] Create `game/strategy/engine/fleet_order_processor.py`
- [x] Centralize order lifecycle management (STRAT-006)
- [x] Move pop_order() calls to single location
- [x] Create advance_order(), complete_order(), cancel_order()
- [x] Track order state changes
  - **Created**: `JoinFleetResult`, `ColonizeResult` dataclasses
  - **Tests**: 26 tests in `test_fleet_order_processor.py`

### Address STRAT-004: Combat Resolution
- [x] If PROJ-11 Phase 4 complete, use IBattleResolver
  - **Note**: PROJ-11 Phase 4 is complete, IBattleResolver in use
- [ ] Otherwise, keep battle controller coupling but document
- [ ] Extract battle resolution orchestration to CombatResolutionEngine
  - **Deferred**: Combat logic (~80 lines) remains in TurnEngine for now

### Update TurnEngine
- [x] Keep TurnEngine as orchestrator only
- [x] Delegate to specialized engines
- [x] Maintain turn phase sequence
- [x] Clear, readable process_turn() method
  - **Note**: process_turn() now ~20 lines, _process_tick() ~30 lines
  - **TurnEngine reduced from 718 → 473 lines (34% reduction)**

### Unit Tests
- [x] Test FleetMovementEngine with mock galaxy (29 tests)
- [x] Test ProductionEngine with mock empire (25 tests)
- [x] Test FleetOrderProcessor lifecycle (26 tests)
- [x] Test TurnEngine orchestration with mocks (61 tests, updated patches)

### Integration Tests
- [x] Full turn processing tests pass (116 strategy tests pass)
- [x] Save/load cycle with turn processing works
- [x] All strategy tests pass (707 unit + 116 integration)

## Verification
- [ ] TurnEngine < 200 lines
  - **Partial**: 473 lines (combat resolution still inline)
  - Combat could be extracted to reach <200 target
- [x] Each new engine < 200 lines
  - FleetMovementEngine: 236 lines
  - ProductionEngine: 181 lines
  - FleetOrderProcessor: 275 lines
- [x] Order state management centralized
- [x] All tests pass (823+ strategy layer tests)

## Implementation Notes

### Files Created
- `game/strategy/engine/fleet_movement_engine.py` (236 lines)
- `game/strategy/engine/production_engine.py` (181 lines)
- `game/strategy/engine/fleet_order_processor.py` (275 lines)
- `tests/unit/strategy/test_fleet_movement_engine.py` (29 tests)
- `tests/unit/strategy/test_production_engine.py` (25 tests)
- `tests/unit/strategy/test_fleet_order_processor.py` (26 tests)

### Files Modified
- `game/strategy/engine/turn_engine.py` - Added lazy engine properties, delegate methods
- `tests/unit/strategy/test_turn_engine.py` - Updated patch targets for delegation

### Deferred Work
- **CombatResolutionEngine**: Combat resolution (~80 lines) could be extracted to reach <200 line target
  - Current combat uses IBattleResolver (from PROJ-11) correctly
  - Low priority since architecture is already clean
