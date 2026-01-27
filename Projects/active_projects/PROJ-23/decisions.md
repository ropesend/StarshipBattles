# PROJ-23: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for ShipStatsService Modifier Application Bug |
| 2026-01-27 | Option C selected: Shared modifier logic | User selected after reviewing pros/cons. Best long-term maintainability, no code duplication, O(n*m) performance without object instantiation overhead. |
| 2026-01-27 | Add functions to existing modifiers.py | Rather than creating new file, extend existing `game/simulation/components/modifiers.py` to keep related functionality together |
| 2026-01-27 | Refactor Component to use shared function | Ensures single source of truth - Component and ShipStatsService will use identical calculation logic |
| 2026-01-27 | Apply multipliers to: mass, HP, capacity, strategic movement, consumption | These are the stats affected by design modifiers that ShipStatsService currently ignores |

## Approach Options Considered

### Option A: Calculate Multipliers in ShipStatsService (Rejected)
- **Pros**: Simple, fast to implement
- **Cons**: Duplicates logic, maintenance burden, risk of drift
- **Decision**: Rejected - creates tech debt

### Option B: Instantiate Full Component Objects (Rejected)
- **Pros**: Single source of truth, handles all edge cases
- **Cons**: Performance overhead (20,000 instantiations for 1000 ships), memory usage
- **Decision**: Rejected - performance concerns for large fleets

### Option C: Extract Shared Modifier Logic (Selected)
- **Pros**: No duplication, efficient, maintainable, testable
- **Cons**: Requires refactoring Component (medium effort)
- **Decision**: **Selected** - best balance of maintainability and performance
