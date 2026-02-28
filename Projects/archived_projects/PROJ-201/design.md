# PROJ-201: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Target Function
`FleetDataSource._get_column_value` (CC=29, 104 lines, lines 130-233)

This method is a dispatch function that formats ship attributes as display strings for 19 different column types in the fleet report table.

### Current Structure

The function uses a 14-branch if-elif chain to handle different column types. The complexity comes from:

1. **Multi-condition branches** - `status` has 4 nested conditions
2. **Loop iteration** - `resources` iterates over resource types
3. **Late imports** - 4 branches require lazy imports to avoid circular dependencies
4. **Varying logic depth** - Some branches are 1 line, others are 10+ lines

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

| Aspect | Finding | Source |
|--------|---------|--------|
| Control flow | 14 branches, 2 with nested logic | Structure Analysis |
| Dependencies | Single internal caller, pure function | Dependency Analysis |
| Test coverage | 30 tests cover all 19 column types | Safety Analysis |
| Risk level | Low-Medium (strong test coverage) | Safety Analysis |
| Recommendation | REFACTOR | Safety Analysis |

### Key Patterns to Reuse

- **Late import pattern**: `speed`, `warp`, `spaceyard`, `capability` branches - must preserve imports inside handlers
- **SPECIAL_CAPABILITY_COLUMNS dict**: `lines 46-52` - maps column IDs to ability names, reuse for consolidated handler

### Dependencies & Risks

1. **Late imports for circular dependency avoidance** - Keep imports inside handler methods
2. **Status priority order** - Must preserve: DESTROYED > DERELICT > DAMAGED > OK
3. **Format strings** - Must preserve exact formatting (e.g., `"{mass:,.0f}"` for tonnage)

### Opportunities Discovered

- Consolidate 5 capability columns into single handler using existing SPECIAL_CAPABILITY_COLUMNS mapping
- Service-call handlers (warp, spaceyard) can share Yes/No formatting pattern

## Target Architecture

```
_get_column_value(ship, col_id)
    |
    +-- Guard: image columns return ""
    |
    +-- Dispatch via _COLUMN_HANDLERS dict
    |       |
    |       +-- _format_serial(ship) -> str
    |       +-- _format_design(ship) -> str
    |       +-- _format_name(ship) -> str
    |       +-- _format_hp_pct(ship) -> str
    |       +-- _format_status(ship) -> str
    |       +-- _format_speed(ship) -> str
    |       +-- _format_tonnage(ship) -> str
    |       +-- _format_warp(ship) -> str
    |       +-- _format_spaceyard(ship) -> str
    |       +-- _format_transport(ship) -> str
    |       +-- _format_resources(ship) -> str
    |       +-- _format_cargo(ship) -> str
    |       +-- _format_capability(ship, col_id) -> str
    |
    +-- Default: return ""
```

### Handler Groupings

| Group | Handlers | Shared Pattern |
|-------|----------|----------------|
| Simple | serial, design, name, hp_pct, tonnage | Direct attribute access |
| Complex | status, resources | Multi-line logic |
| Service | speed, warp, spaceyard | Late import + service call |
| Capability | 5 can_* columns | Unified capability checker |

## Invariants to Preserve

1. Return type is always `str`
2. Image columns (`portrait`, `topdown`) return `""`
3. Unknown columns return `""`
4. Status priority: DESTROYED > DERELICT > DAMAGED > OK
5. Late imports must stay inside handler methods
6. Format strings must be exact (e.g., `"{mass:,.0f}"` for tonnage)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
