# PROJ-95: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Three clean-sheet convention changes identified from review audit (2026-02-10_general_resource-state-duplication-audit), Findings #1, #3, #8, #10:

1. **Magic strings**: `'fuel'`, `'energy'`, `'ammo'` used as dict keys, function arguments, and conditionals across 139 production occurrences (29 files) and ~1037 test occurrences (~163 files). No `ResourceType` constant exists.
2. **Negated semantics**: Strategy layer uses `is_destroyed` (True=dead), Simulation uses `is_alive` (True=alive). Only 1 conversion point at `ship_instance.py:189`. Creates double-negation bugs.
3. **None-means-full convention**: `resource_levels` dict uses sparse storage where absent keys = full capacity. `resupply()` at line 247 actively deletes keys at max. 12 pattern instances across 4 files.

## Swarm Findings Summary

### Architecture
- `game/core/constants.py` already has `AttackType` enum, `LayerType` enum, `PLANET_RESOURCES` list -- `ResourceType` fits naturally here
- `is_destroyed` field at `ship_instance.py:60`, used in 4 prod files (13 occurrences) and 10 test files (32 occurrences)
- None-means-full pattern consistently applied: `.get(key, max_val)` in getters, `del dict[key]` in resupply, `if key not in` for "is full" check
- `PlanetaryFacility` uses DIFFERENT convention: defaults to 0.0, not max (`planet.py:36`)

### Key Patterns to Reuse
- **ResourceType as class with string constants** (not Enum): Values used extensively as dict keys; Enum adds `.value` noise everywhere. Class with string constants is cleanest.
- **ResourceType.all()**: Replaces `['fuel', 'energy', 'ammo']` list literals scattered across codebase.
- **Serialization key change**: Per CLAUDE.md "save files are disposable", use new key name `is_alive` in serialization (no backward compat).

### Dependencies & Risks
1. **PROJ-94 dependency**: Should complete first -- deletes dead methods that PROJ-95 Phase 1 would otherwise need to update with constants
2. **Test bulk replacement**: ~1037 test occurrences need careful regex replacement. Strategy: replace in production first, then bulk-replace tests, then fix any import errors.
3. **is_destroyed in tests**: Some test mocks set `is_destroyed = True/False` directly on mock objects. After rename, these become `is_alive = False/True` (inverted).
4. **resource_levels initialization**: After Phase 3, `create()` must populate resource_levels with max values. Requires calling `get_calculated_stats()` which needs `design_data` already set.

### Opportunities Discovered
- `ResourceType.all()` can replace `PLANET_RESOURCES`-style patterns for ship resources
- Eliminating None-means-full simplifies every resource getter (no more fallback logic)
- `is_alive` aligns with simulation layer, eliminating the `not ship.is_alive` conversion at line 189

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
