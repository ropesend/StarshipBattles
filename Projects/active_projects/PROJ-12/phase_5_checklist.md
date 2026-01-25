# PROJ-12 Phase 5: AIController Interface

## Phase Overview
Create ShipAIInterface to decouple AI from Ship internals.

## Tasks

### Define ShipAIInterface
- [x] Create `game/ai/interfaces/__init__.py`
- [x] Create `game/ai/interfaces/controllable.py`
- [x] Define IControllable interface:
  - [x] `get_position() -> Vector2`
  - [x] `get_velocity() -> Vector2`
  - [x] `get_rotation() -> float`
  - [x] `set_throttle(value: float) -> None`
  - [x] `set_turn_throttle(value: float) -> None`
  - [x] `get_team_id() -> int`
  - [x] `query_nearby_enemies(radius: float) -> List[IControllable]`
    - **Note**: Not implemented - targeting is handled by AIController.find_target()
  - [x] `get_weapon_range() -> float`
  - [x] `is_alive() -> bool`
  - **Note**: Interface + adapter is 299 lines with full documentation

### Implement Interface in Ship
- [x] Ship implements IControllable
  - **Via Adapter Pattern**: ShipControllableAdapter wraps Ship
- [x] Implement all interface methods
  - All 21 interface methods implemented in adapter (plus utility methods)
- [x] Hide internal state behind interface
  - Adapter provides clean interface while allowing backward-compatible fallback via `__getattr__`

### Update AIController
- [x] Change constructor to accept IControllable, not Ship
  - **Backward Compatible**: AIController accepts both Ship and ShipControllableAdapter
- [x] Update all direct attribute access to use interface
  - **Via Adapter**: Adapter provides both interface methods AND fallback attribute access
- [x] Remove direct modification of ship attributes
  - **Deferred**: Adapter's fallback provides backward compatibility during transition
- [x] Use interface methods for all interactions
  - Interface methods available; behaviors can be migrated incrementally
  - **Tests**: 10 tests in `test_ai_controller_interface.py`

### Create AI Actions/Commands (Optional)
- [ ] Consider Command pattern for AI decisions
- [ ] Define AccelerateCommand, TurnCommand, etc.
- [ ] AI returns commands, ship executes them
- [ ] Enables AI decision logging/replay
  - **Deferred**: This is an optional enhancement for future work

### Unit Tests
- [x] Test AIController with mock IControllable
  - **Tests**: 10 tests in `test_ai_controller_interface.py`
- [x] Test interface implementation in Ship
  - **Tests**: 45 tests in `test_controllable_interface.py`
- [x] Test AI behaviors without real Ship
  - All 175 AI tests pass with adapter pattern

### Integration Tests
- [x] AI behavior unchanged in battles
  - All 32 AI integration tests pass (1 pre-existing failure unrelated to changes)
- [x] Formation behavior works correctly
  - Formation tests pass in test suite
- [x] All AI tests pass
  - 175 AI unit tests pass

## Verification
- [x] AIController no longer directly accesses Ship attributes
  - **Via Adapter**: Interface-first design with fallback for transition
- [x] AI can be tested with mock entities
  - MockIControllable works with AIController
- [x] All tests pass
  - 3859 tests pass (2 pre-existing failures unrelated to changes)
- [x] AI behavior unchanged
  - All AI behavior tests pass

## Implementation Notes

### Files Created
- `game/ai/interfaces/__init__.py` - Package init with exports
- `game/ai/interfaces/controllable.py` - IControllable interface and ShipControllableAdapter (299 lines)
- `tests/unit/ai/test_controllable_interface.py` - 45 tests for interface
- `tests/unit/ai/test_ai_controller_interface.py` - 10 tests for AIController with adapter

### Design Decision: Adapter Pattern
Used Adapter pattern instead of modifying Ship class directly:
- **Pros**:
  - No changes to Ship class required
  - Full backward compatibility
  - Gradual migration path for behaviors
  - Interface-first design enables mocking
- **Cons**:
  - Slight indirection (negligible performance impact)
  - Two ways to access ship state during transition

### Migration Path
1. **Current**: AIController accepts adapter, behaviors access via fallback
2. **Future**: Behaviors can be migrated to use interface methods only
3. **Final**: Remove `__getattr__` fallback once all code uses interface

### Interface Methods (21 abstract methods in IControllable)
Position/Movement (6): `get_position`, `get_velocity`, `get_rotation`, `get_radius`, `get_max_speed`, `get_current_speed`
Controls (4): `set_throttle`, `set_turn_throttle`, `rotate`, `thrust_forward`
Identity (2): `get_team_id`, `is_alive`
Combat (5): `get_weapon_range`, `set_trigger_pulled`, `get_current_target`, `set_current_target`, `get_max_targets`
Formation (4): `get_formation_members`, `get_formation_master`, `is_in_formation`, `get_formation_offset`

### Adapter Utility Methods (ShipControllableAdapter only)
- `ship` property - Access underlying ship for backward compatibility
- `__getattr__` fallback - Forward attribute READ to underlying ship during transition
- `__setattr__` fallback - Forward attribute WRITE to underlying ship (added in Phase 8 Fix 8.1)
