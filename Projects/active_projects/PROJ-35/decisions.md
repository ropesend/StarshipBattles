# PROJ-35: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for Unify Fleet Movement Logic |
| 2026-01-27 | **Architecture: Option A (Full Unification)** | Create single FleetNavigationService rather than shared core with facades. True single source of truth worth the larger refactor. |
| 2026-01-27 | **Fix Fake Fleet in Intercept** | Update calculate_intercept_point to accept NavigationState, eliminating the `id=-1` hack and enabling proper warp capability checking. |
| 2026-01-27 | **NavigationState with can_warp** | Pre-compute `can_warp` in NavigationState factory to eliminate need for Fleet object in pure navigation functions. |
| 2026-01-27 | **Mutation Bridge Pattern** | `calculate_fleet_next_hex()` wraps pure function and applies mutations so FleetMovementEngine continues to work with mutable Fleet objects. |
| 2026-01-27 | **Keep Resource Logic in Engine** | FleetMovementEngine retains all resource consumption logic (`apply_movement`). Service only handles navigation. |

## Decision Details

### Architecture: Option A (Full Unification)
**Context**: Two options were considered:
- Option A: Full unification into single FleetNavigationService
- Option B: Extract shared core, keep both FleetMovementSimulator and FleetMovementEngine as facades

**Decision**: Option A

**Consequences**:
- Larger initial refactor
- True single source of truth achieved
- FleetMovementSimulator can be deprecated and eventually removed
- All navigation logic in one place

### Fix Fake Fleet in Intercept
**Context**: FleetMovementSimulator.calculate_destination() creates a fake fleet object:
```python
type('Fleet', (), {'location': state.location, 'speed': state.speed, 'id': -1})()
```
This is passed to `calculate_intercept_point()` which expects a Fleet.

**Decision**: Update `calculate_intercept_point` to accept `Union[Fleet, NavigationState]`

**Consequences**:
- Cleaner code, no fake objects
- Proper warp capability checking in intercept calculations
- Slight signature change requiring type checking at function start
