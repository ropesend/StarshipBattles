# PROJ-94: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Review audit (2026-02-10_general_resource-state-duplication-audit) found that PROJ-91 removed type-specific methods from ShipInstance but left them in the extracted managers. Eight review agents confirmed:

1. **ShipResourceManager** (252 lines) has 7 dead type-specific methods (lines 40-136) that are never called from production code. They all delegate to the generic methods below them.
2. **FleetResourceAggregator** has 5 type-specific wrapper methods that delegate to generic methods.
3. **Fleet** has 5 facade methods that delegate to the dead FleetResourceAggregator methods above.
4. **2 UI files** access private `._resources` dict directly instead of using public API.
5. **IPostBattleShip.resources** is typed as `Any` despite `IResourceReader` protocol existing.
6. **Bridge code** for capturing resource levels is duplicated between `from_ship()` and `update_from_ship()`.

## Swarm Findings Summary

### Architecture
- Strategy layer uses `ShipResourceManager` operating on `Dict[str, float]` (sparse storage)
- Simulation layer uses `ResourceRegistry` with `ResourceState` objects (always stores values)
- This dual system is architecturally justified (ShipInstance exists without simulation Ship)
- The bridge code in `from_ship()`/`update_from_ship()` converts between the two

### Key Patterns to Reuse
- **Facade/Delegate**: `ShipInstance` -> `ShipResourceManager` -> `resource_levels dict`. All public API on ShipInstance, manager handles logic.
- **Fleet delegation**: `Fleet` -> `FleetResourceAggregator`. Fleet is facade, aggregator has logic.
- **ResourceRegistry.get_resource_names()**: Already exists (added by PROJ-91, line 197-199)

### Dependencies & Risks
1. **Dead Code Hunter false positive**: `ResourceState.has_sufficient()` was flagged as dead but IS used at `game/simulation/components/abilities/resources.py:106`. Do NOT delete it.
2. **ship_stats_renderer needs ResourceState objects**: The `._resources.values()` access returns `ResourceState` objects (with `.name`, `.current_value`, `.max_value`). Simple `get_resource_names()` is insufficient. Need `get_all_resources()` method.

### Opportunities Discovered
- After PROJ-94 deletes dead methods, ShipResourceManager drops from 252 to ~155 lines
- FleetResourceAggregator drops ~35 lines
- Fleet drops ~12 lines

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
