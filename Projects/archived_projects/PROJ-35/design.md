# PROJ-35: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The "Split Brain" Problem
Three modules handle fleet movement with overlapping but different logic:

1. **FleetMovementSimulator** (`game/strategy/engine/fleet_movement.py`, 309 lines)
   - Uses immutable `FleetState` snapshots
   - Claims to be "single source of truth" but is NOT used by TurnEngine
   - Used only for UI path projection via `pathfinding.py`

2. **FleetMovementEngine** (`game/strategy/engine/fleet_movement_engine.py`, 237 lines)
   - Mutates Fleet objects directly
   - Actually used by TurnEngine for game state updates
   - Has its own movement logic that duplicates Simulator's

3. **pathfinding.py** (`game/strategy/data/pathfinding.py`, 372 lines)
   - Contains core algorithms used by both
   - `project_fleet_path()` delegates to FleetMovementSimulator
   - `calculate_intercept_point()` called by both systems

### Risk Assessment
| Risk | Severity | Description |
|------|----------|-------------|
| UI/Execution Mismatch | HIGH | UI shows one path, TurnEngine executes different |
| Ghost Fleets | MEDIUM | Fleet appears at position UI didn't predict |
| Invalid Intercepts | MEDIUM | MOVE_TO_FLEET calculates wrong intercept point |
| State Mutation Bugs | MEDIUM | Immutable vs mutable patterns cause subtle bugs |

## Swarm Findings Summary

### Architecture Analysis

**Call Flow - UI Projection:**
```
GameSession.get_fleet_path_projection()
  → pathfinding.project_fleet_path()
    → FleetMovementSimulator.project_path_as_dicts()
      → Uses immutable FleetState
      → Calls find_hybrid_path()
      → Returns PathSegment list
```

**Call Flow - Turn Execution:**
```
TurnEngine._process_tick()
  → FleetMovementEngine.collect_movements()
    → FleetMovementEngine.calculate_next_hex()
      → Mutates fleet.path directly
      → Calls find_hybrid_path()
  → FleetMovementEngine.apply_movements()
    → Mutates fleet.location
    → Consumes resources
```

### Key Patterns to Reuse

- **Immutable State Pattern**: `FleetState.from_fleet()` creates snapshots - keep this
- **Lazy Import Pattern**: Both modules use lazy imports to avoid circular deps
- **Speed-Based Tick Calculation**: `interval = 100 // fleet.speed` - preserve exactly
- **Path Normalization**: Remove start hex if equals current location - consolidate

### Dependencies & Risks

1. **Immutability vs Mutability Clash**
   - Simulator: Pure functions with immutable state
   - Engine: Direct mutation of Fleet objects
   - **Mitigation**: Service provides both pure methods and a mutation bridge

2. **Resource Consumption Coupling**
   - Engine consumes resources; Simulator doesn't
   - **Mitigation**: Keep resource consumption in FleetMovementEngine only

3. **Intercept Fake Fleet Object**
   - FleetMovementSimulator line 83 creates fake fleet with `id=-1`
   - **Mitigation**: Update `calculate_intercept_point` to accept NavigationState

4. **Path Removal Logic Differs**
   - Simulator: `path = path[1:]` (returns new list)
   - Engine: `fleet.path.pop(0)` (mutates in-place)
   - **Mitigation**: Unified service handles both patterns

### Opportunities Discovered

1. **True Single Source of Truth**: Unify all navigation logic
2. **Cleaner Testing**: Pure functions are easier to test
3. **Better Type Safety**: NavigationState with `can_warp` pre-computed
4. **Reduced Code Duplication**: ~100 lines of duplicate logic consolidated

## Design Decisions

### Decision 1: Full Unification (Option A)
**Choice**: Create single `FleetNavigationService` rather than shared core with facades
**Rationale**: True single source of truth, cleaner architecture, worth the larger refactor

### Decision 2: Fix Fake Fleet in Intercept
**Choice**: Update `calculate_intercept_point` to accept `NavigationState`
**Rationale**: Eliminates hack, enables proper warp capability checking

### Decision 3: NavigationState with can_warp
**Choice**: Pre-compute `can_warp` in NavigationState factory
**Rationale**: Eliminates need for Fleet object in pure navigation functions

### Decision 4: Mutation Bridge Pattern
**Choice**: `calculate_fleet_next_hex()` wraps pure function + applies mutations
**Rationale**: FleetMovementEngine continues to work with mutable Fleet objects

See [decisions.md](decisions.md) for the full log with rationale.

## Test Impact

### Tests Requiring Modification
| Test File | Count | Impact |
|-----------|-------|--------|
| `test_fleet_movement_engine.py` | 26 | Update to use delegated navigation |
| `test_pathfinding.py` | 35+ | Verify unchanged behavior |
| `test_turn_engine_strategy.py` | 3 | Verify timing preserved |
| `test_path_projection.py` | 2 | Update to use new service |

### New Tests Required
- `test_fleet_navigation_service.py` - Unit tests for new service
- `test_fleet_navigation_consistency.py` - Verify projection = execution

## Project Completion Notes (2026-01-27)

### Final Architecture
```
FleetNavigationService (single source of truth)
├── Core (stateless, pure functions):
│   ├── get_destination(state, order, galaxy) → HexCoord?
│   ├── compute_path(state, destination, galaxy) → [HexCoord]
│   └── compute_next_step(state, galaxy) → NavigationStep
├── Projection (for UI):
│   ├── project_path(fleet, galaxy, max_turns) → [PathSegment]
│   └── project_path_as_dicts(fleet, galaxy) → [dict]
└── Execution (for TurnEngine):
    └── calculate_fleet_next_hex(fleet, galaxy) → HexCoord?
        (mutation bridge: applies state changes to mutable Fleet)

FleetMovementEngine (simplified - delegates navigation)
├── collect_movements(empires, galaxy, tick) → [(Fleet, HexCoord)]
├── apply_movement(fleet, next_hex, galaxy) → MovementResult
└── apply_movements(queue, galaxy) → [MovementResult]
    (retains ALL resource consumption logic)

pathfinding.py (updated)
├── project_fleet_path() → delegates to FleetNavigationService
└── calculate_intercept_point() → accepts Union[Fleet, NavigationState]

FleetMovementSimulator (DEPRECATED)
└── Retained for backward compatibility with DeprecationWarning
```

### Key Changes Made
1. **FleetNavigationService created** (468 lines) - Single source of truth
2. **FleetMovementEngine updated** - Delegates navigation to service
3. **calculate_intercept_point updated** - Accepts NavigationState (no more fake fleet)
4. **project_fleet_path updated** - Uses FleetNavigationService instead of FleetMovementSimulator
5. **FleetMovementSimulator deprecated** - Warning added, code kept for compatibility

### Tests Added
- `test_fleet_navigation_service.py` - 36 unit tests
- `test_fleet_navigation_consistency.py` - 10 consistency tests verifying projection = execution

### Critical Bugs Fixed During Implementation
1. Non-movement orders being incorrectly popped (COLONIZE, JOIN_FLEET)
2. Double order-pop in apply_movement() causing chained orders to fail
3. Invalid MOVE_TO_FLEET targets not being handled gracefully
