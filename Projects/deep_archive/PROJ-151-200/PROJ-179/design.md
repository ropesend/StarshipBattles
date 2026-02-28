# PROJ-179: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Source: PROJ-173 Post-Refactor Audit (External Review)
An external audit reviewed the PROJ-173 God Class Decomposition and found 5 issues. Independent agent swarm verification confirmed 4 of 5 are valid (Finding #5 was incorrect).

### Verified Findings

**Finding 1: Misleading `get_system_of_object` docstring**
- Location: `game/strategy/data/galaxy_spatial_index.py:32`
- The docstring claims the method works for "Fleet, Planet, etc." but only Fleets have global coordinates. Planets have local offsets. Only 2 call sites exist, both passing Fleets.
- Severity: Low (docstring only, no runtime bug)

**Finding 2: Bypassed delegate in `Galaxy.get_zones_at_global_hex`**
- Location: `game/strategy/data/galaxy.py:297-306`
- The method directly accesses `self._global_hex_zones` instead of delegating to `self._spatial.get_zones_at_global_hex()`. This makes the spatial index method dead code.
- Severity: Medium (architectural inconsistency, dead code)
- 7 production callers all use the facade; spatial index method is never called.

**Finding 3: O(N) complexity in `get_system_at_location`**
- Location: `game/strategy/data/galaxy_spatial_index.py:116-141`
- After the O(1) fast path (direct system lookup), the fallback iterates all systems checking planets, stars, and warp points.
- Severity: Low (only called from UI validation, not per-frame; 80 systems = <1ms)
- Existing O(1) indexes can eliminate the iteration entirely.

**Finding 4: `from_dict()` encapsulation violation**
- Location: `game/strategy/data/galaxy.py:567-583`
- `from_dict()` manually rebuilds 4 private delegate indexes instead of calling delegate methods. This duplicates logic from `register_planet()`.
- Severity: Medium (logic duplication, encapsulation bypass)
- Complication: `register_planet()` assigns new IDs; deserialization must preserve existing IDs.

**Finding 5: REJECTED — Chain of responsibility return values**
- The audit claimed `StrategyInputHandler._handle_keydown_mapped` discards return values. Independent verification found the code DOES check returns at lines 124-131 with `if handler(): return` pattern. The audit was wrong.

## Swarm Findings Summary

### Architecture
The Galaxy facade/delegate pattern from PROJ-173:
- `Galaxy` (facade): Public API, unchanged for 50+ callers
- `GalaxySpatialIndex` (delegate): Spatial queries (system-at-location, fleets-in-system)
- `GalaxyEntityRegistry` (delegate): Entity lifecycle (register/unregister planets, fleets, zones)
- Both delegates hold a reference to `Galaxy` and access shared dicts through it

### Key Patterns to Reuse
- **Delegation pattern**: `return self._spatial.method(args)` — used consistently except for `get_zones_at_global_hex`
- **Index registration**: Planets registered in `_planet_to_system`, `_global_hex_planets`, `planets_by_id`
- **Zone registration**: Objects registered per occupied hex in `_global_hex_zones`

### Dependencies & Risks
1. **from_dict() ID preservation**: Must add `restore_planet()` that registers without assigning new IDs
2. **Warp point index**: No existing spatial index for warp points — needed for O(1) `get_system_at_location()`
3. **Zone-to-system reverse lookup**: No existing `_zone_to_system` map — needed for O(1) zone→system resolution

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
