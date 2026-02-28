# PROJ-181: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Background
PROJ-174 successfully migrated all production code from three registry access tiers:
- **TIER 3** `RegistryManager.instance()` -> only in composition roots
- **TIER 2** `get_default_registries()` -> eliminated from production
- **TIER 1** `get_default_registry_provider()` -> canonical pattern

However, PROJ-174 kept the deprecated TIER 2 functions alive with `DeprecationWarning` instead of deleting them. This violates the System Migration Policy in CLAUDE.md.

### Why Deletion Is Safe
1. **All callers are in-tree** - no external consumers
2. **`DefaultRegistryProvider` wraps `RegistryManager`** - any code using the provider already sees hydrated data
3. **Root conftest `reset_game_state`** already calls `mgr.clear()` + `mgr.hydrate()` before every test
4. **`_default_registries` module variable** was a parallel state that `DefaultRegistryProvider` never used

### Architecture After This Project
```
Composition Roots (app.py, conftest.py):
    RegistryManager.instance()  -> hydrate/clear lifecycle

Production Code:
    get_default_registry_provider() -> IRegistryProvider (reads from RegistryManager)
    Constructor DI: def __init__(self, registry: IRegistryProvider)

Tests:
    fresh_registries fixture -> function-scoped DI isolation
    minimal_registries fixture -> empty registries for unit tests
    root conftest reset_game_state -> autouse, handles clear/hydrate
```

## Swarm Findings Summary
Combined analysis from 6 independent verification agents.

### Architecture
- DI migration is complete in production code - zero deprecated callers outside composition roots
- `DefaultRegistryProvider` wraps `RegistryManager`, so removing `_default_registries` changes nothing for production code
- Root conftest already provides complete test isolation via `reset_game_state` autouse fixture

### Key Patterns to Reuse
- **`fresh_registries` fixture**: `conftest.py` - function-scoped GameRegistries with deep-copied production data
- **`minimal_registries` fixture**: `conftest.py` - empty GameRegistries for isolated unit tests
- **`@pytest.mark.use_custom_data`**: Skips production data hydration for tests needing custom registries
- **Provider pattern**: `get_default_registry_provider()` returns `DefaultRegistryProvider` singleton

### Dependencies & Risks
1. **simulation_tests have their own conftest** - doesn't use root conftest fixtures; needs separate migration approach
2. **Some tests explicitly set up registry state before `.clear()`** - removing `.clear()` is safe because root conftest does it first
3. **WorkshopContext fallback tests** - test the deprecated getter; need rewriting to test provider fallback

### Opportunities Discovered
- After this project, the `_default_registries` parallel state is gone - single source of truth via `RegistryManager` + `DefaultRegistryProvider`
- Removing `.clear()` boilerplate from 24 files reduces ~70 lines of redundant code

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
