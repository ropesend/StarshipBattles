# PROJ-185: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Registry DI Migration Status
PROJ-174 and PROJ-181 successfully migrated all production code to the DI pattern. Verified:
- All deprecated functions (`get_default_registries`, `set_default_registries`) fully removed
- Regression tests guard against reintroduction (`tests/regression/test_deprecated_code_removed.py`)
- Production code uses `get_default_registry_provider()` or constructor DI
- Only composition roots (`game/app.py`, conftest files) access `RegistryManager.instance()`

### Broader Backward Compatibility Issues
Independent audit uncovered 10+ backward compat patterns outside the registry system:
1. **Ghost code**: Stale comments/filters referencing already-removed deprecated patterns
2. **Active shims**: Code maintaining old interfaces alongside new ones (build queue single-select)
3. **Misleading comments**: Proper patterns labeled as "backward compat" (6 locations)
4. **Dead fallback paths**: O(n) fleet iteration fallback that undermines Galaxy registry authority
5. **Unused aliases**: Legacy constant names in propulsion test scenarios

## Swarm Findings Summary

### Architecture
- Registry DI architecture: Clean, no issues found
- Build queue MVVM (PROJ-172): Solid extraction, but left backward compat scaffolding
- Galaxy fleet registry: Has authoritative O(1) lookup, but game_session retains O(n) fallback
- UI utils package: Standard Python package API design (re-exports in __init__.py)

### Key Patterns to Reuse
- **Facade/delegate pattern**: Build queue Window properties delegating to ViewModel - keep as proper API
- **Package API re-exports**: UI utils __init__.py - standard Pythonic pattern, not backward compat
- **Derived convenience properties**: Window can compute `selected_index`/`selected_source` from
  `selected_indices` without needing ViewModel to maintain shim state

### Dependencies & Risks
1. **Build queue test migration** (~30 ViewModel assertions, ~50 Window assertions) - Main risk.
   Mitigation: Window keeps convenience properties as derived calculations, limiting blast radius.
2. **Propulsion alias removal** - Low risk, confirmed zero external consumers.
3. **Fleet fallback removal** - Low risk if Galaxy registry properly tracks all fleets. Tests will
   catch any gaps.

### Opportunities Discovered
- Clean-sheet build queue selection API using only `selected_indices` + `get_selected_sources()`
- Simpler ViewModel with fewer fields to maintain
- Removal of ~25 lines of shim code from ViewModel

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
