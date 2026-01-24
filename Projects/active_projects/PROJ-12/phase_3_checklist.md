# PROJ-12 Phase 3: TurnEngine Decomposition

## Phase Overview
Split TurnEngine into specialized services.

## Tasks

### Create FleetMovementEngine
- [ ] Create `game/strategy/engine/fleet_movement_engine.py`
- [ ] Move _calculate_next_hex() logic
- [ ] Move path management logic
- [ ] Move resource consumption logic
- [ ] Move warp travel handling
- [ ] Add clear interface with movement results

### Create ProductionEngine
- [ ] Create `game/strategy/engine/production_engine.py`
- [ ] Move construction queue processing
- [ ] Move ship spawning logic
- [ ] Handle production format migration (STRAT-009)
- [ ] Support single format going forward

### Create FleetOrderProcessor
- [ ] Create `game/strategy/engine/fleet_order_processor.py`
- [ ] Centralize order lifecycle management (STRAT-006)
- [ ] Move pop_order() calls to single location
- [ ] Create advance_order(), complete_order(), cancel_order()
- [ ] Track order state changes

### Address STRAT-004: Combat Resolution
- [ ] If PROJ-11 Phase 4 complete, use IBattleResolver
- [ ] Otherwise, keep battle controller coupling but document
- [ ] Extract battle resolution orchestration to CombatResolutionEngine

### Update TurnEngine
- [ ] Keep TurnEngine as orchestrator only
- [ ] Delegate to specialized engines
- [ ] Maintain turn phase sequence
- [ ] Clear, readable process_turn() method

### Unit Tests
- [ ] Test FleetMovementEngine with mock galaxy
- [ ] Test ProductionEngine with mock empire
- [ ] Test FleetOrderProcessor lifecycle
- [ ] Test TurnEngine orchestration with mocks

### Integration Tests
- [ ] Full turn processing tests pass
- [ ] Save/load cycle with turn processing works
- [ ] All strategy tests pass

## Verification
- [ ] TurnEngine < 200 lines
- [ ] Each new engine < 200 lines
- [ ] Order state management centralized
- [ ] All tests pass
