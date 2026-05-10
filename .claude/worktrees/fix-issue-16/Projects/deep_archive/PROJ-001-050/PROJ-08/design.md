# PROJ-08: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
The strategy layer is well-organized with clean separation between services and data. Key findings:
- `ShipStatsService` is stateless and isolated (only imports from `game.core.registry`)
- `ShipInstance.resource_levels` is already a generic `Dict[str, float]`
- Fleet operations use atomic check-then-consume patterns
- TurnEngine has 4-phase tick processing with clear extension points

## Swarm Findings Summary

### Architecture
- **Clean boundaries:** ShipStatsService only imports from `game.core.registry`
- **Data flow:** Fleet → ShipInstance → ShipStatsService → Component Registry
- **Caching:** ShipInstance uses `_cached_stats` with explicit invalidation
- **Coupling issue:** TurnEngine imports from simulation layer for battle resolution (acceptable, out of scope)

### Key Patterns to Reuse
- **RegistryManager pattern** (`game/core/registry.py:4-185`): Singleton with in-place dict updates
- **Ability Registry pattern** (`game/simulation/components/abilities/__init__.py:52-97`): Factory with class map
- **Multi-format handling** (`game/simulation/components/abilities/resources.py:30-40`): Dict or primitive input
- **Stat binding pattern** (`game/simulation/components/abilities/stat_keys.py:100-136`): Declarative bindings

### Dependencies & Risks
1. **CRITICAL BUG:** `ship_stats_service.py` had uninitialized variables - fixed by refactoring to generic dicts
2. **Backward compatibility:** Old saves missing `component_toggles` field - mitigated by defaulting to `{}`
3. **Cache invalidation:** Component toggle must invalidate `_cached_stats`
4. **Atomic operations:** Partial consumption risk if exception mid-loop - mitigated by two-phase pattern

### Dependency Map
- **31 files** in dependency chain for resource handling
- **Zero circular dependencies** (safe architecture)
- **4 locations** with hardcoded resource strings (all in core files)
- **Modification order:** ship_stats_service → ship_instance → fleet → turn_engine → tests
