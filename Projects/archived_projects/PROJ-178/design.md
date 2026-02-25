# PROJ-178: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Source: PROJ-171 Post-Refactor Audit
PROJ-171 added structured deserialization validation using `validation_helpers.py` across 13 `from_dict` methods. The audit found the implementation was architecturally sound but identified consistency gaps and one previously undiscovered bug.

### Independent Code Review Findings (5 agents)

**Agent 1 - ShipInstance Review:**
- `ShipInstance.from_dict` (line 641) uses only `require_keys` for 4 fields
- No `validate_non_negative` for `current_hp`, `experience`, `kills`, `battles_survived`
- No `Raises: PersistenceException` docstring
- Significantly less thorough than Planet.from_dict

**Agent 2 - Planet Inline Deserialization:**
- `PlanetaryFacility` deserialized inline (lines 418-436) with bare `try/except (KeyError, TypeError)`
- `SpeciesPopulation` deserialized inline (lines 438-452) similarly
- No `require_keys` usage for child objects
- Other child objects (Fleet, StarSystem, Star, WarpPoint) all have their own `from_dict` methods

**Agent 3 - Docstring Gaps:**
- `Empire.from_dict` (line 173): No `Raises:` block. Has Args/Returns only.
- `Fleet.from_dict` (line 347): Minimal one-liner docstring
- `ShipInstance.from_dict` (line 641): Minimal one-liner docstring

**Agent 4 - DesignMetadata Legacy Code:**
- `_calculate_combat_power_from_ship` (lines 200-214): Uses `hasattr(comp, 'category')` — **Component has no `category` attribute at all!** Uses `type_str` and `major_classification` instead.
- This means the method **always returns 0.0** for Ship-based calculations
- `_calculate_resource_cost_from_ship` (lines 239-257): Uses `hasattr(comp, 'cost')` unnecessarily — Component always has `.cost` (defaults to 0)
- Dict-based methods log "Old layer format" warnings (lines 184, 228)
- All methods are actively called from `design_library.save_design()`

**Agent 5 - Validation Helpers Audit:**
- 12 of 13 `from_dict` methods use `require_keys`
- Only `RaceConfig.from_dict` uses zero helpers (but has separate `validate()` method)
- `validate_non_negative` used only by Planet and Spectrum
- `validate_range` never used by any from_dict method

## Swarm Findings Summary

### Architecture
The validation_helpers pattern is well-established:
- `require_keys(data, keys, context)` — structural validation
- `validate_enum(value, enum_class, field, context)` — enum membership
- `validate_positive(value, field, context)` — positive numbers
- `validate_non_negative(value, field, context)` — non-negative numbers
- `validate_range(value, min, max, field, context)` — range bounds
- `safe_from_dict(fn, data, context)` — wrapped nested deserialization

All raise `PersistenceException` with structured context dicts.

### Key Patterns to Reuse
- **Planet.from_dict** (`planet.py:363-480`): Gold standard for validation thoroughness
- **Star.from_dict** (`stars.py:146-206`): Good example of `safe_from_dict` for nested objects
- **StarSystem.from_dict** (`galaxy.py:104-147`): Good resilient degradation with broader exception catching

### Dependencies & Risks
1. **DesignMetadata fix may change saved metadata values** — combat_power and resource_cost stored in design library will differ after fix. This is acceptable since old values were always 0.0/{} for Ship-based saves.
2. **PlanetaryFacility/SpeciesPopulation from_dict extraction** — must maintain exact same resilient degradation behavior (skip bad entries, log warning)
3. **Component attribute names** — must verify exact `type_str` values used for weapons/armor in `components.json`

### Opportunities Discovered
- The `_calculate_combat_power_from_ship` bug means all saved ship designs via `from_ship()` have `combat_power=0.0` and `resource_cost={}`. Fixing this will retroactively improve the design library's filtering/sorting capabilities.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
