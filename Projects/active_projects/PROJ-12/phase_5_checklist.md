# PROJ-12 Phase 5: AIController Interface

## Phase Overview
Create ShipAIInterface to decouple AI from Ship internals.

## Tasks

### Define ShipAIInterface
- [ ] Create `game/ai/interfaces/__init__.py`
- [ ] Create `game/ai/interfaces/controllable.py`
- [ ] Define IControllable interface:
  - [ ] `get_position() -> Vector2`
  - [ ] `get_velocity() -> Vector2`
  - [ ] `get_rotation() -> float`
  - [ ] `set_throttle(value: float) -> None`
  - [ ] `set_turn_throttle(value: float) -> None`
  - [ ] `get_team_id() -> int`
  - [ ] `query_nearby_enemies(radius: float) -> List[IControllable]`
  - [ ] `get_weapon_range() -> float`
  - [ ] `is_alive() -> bool`

### Implement Interface in Ship
- [ ] Ship implements IControllable
- [ ] Implement all interface methods
- [ ] Hide internal state behind interface

### Update AIController
- [ ] Change constructor to accept IControllable, not Ship
- [ ] Update all direct attribute access to use interface
- [ ] Remove direct modification of ship attributes
- [ ] Use interface methods for all interactions

### Create AI Actions/Commands (Optional)
- [ ] Consider Command pattern for AI decisions
- [ ] Define AccelerateCommand, TurnCommand, etc.
- [ ] AI returns commands, ship executes them
- [ ] Enables AI decision logging/replay

### Unit Tests
- [ ] Test AIController with mock IControllable
- [ ] Test interface implementation in Ship
- [ ] Test AI behaviors without real Ship

### Integration Tests
- [ ] AI behavior unchanged in battles
- [ ] Formation behavior works correctly
- [ ] All AI tests pass

## Verification
- [ ] AIController no longer directly accesses Ship attributes
- [ ] AI can be tested with mock entities
- [ ] All tests pass
- [ ] AI behavior unchanged
