# PROJ-171: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem
20 `from_dict` deserialization methods were audited. Only 3 validate well; **4 have no validation at all** and **11 have partial validation**. Corrupt save data produces cryptic `KeyError` or `TypeError` crashes with no indication of which field is wrong or which object failed to load.

### Current State of Deserialization
| Validation Level | Count | Methods |
|-----------------|-------|---------|
| VALIDATES_WELL | 3 | RaceConfig, EventLog, LayerData |
| PARTIAL_VALIDATION | 11 | ShipSerializer, Fleet, StarSystem, Empire, Planet, Star, ShipInstance, ComponentState, ShipState, TechTree, DesignMetadata |
| NO_VALIDATION | 4 | Galaxy, WarpPoint, Spectrum, Event |

### Unsafe Patterns Found
1. **Direct dict access** (`data["key"]`) without `.get()` — 14+ methods, 80+ unsafe accesses
2. **Enum conversions** (`PlanetType[value]`, `StarType[value]`, `OrderType[value]`) without try/except — 4 methods
3. **Cascading nested from_dict** — inner failure produces opaque error without context about outer object
4. **No range checks** on physics properties (mass, radius, temperature can be negative or zero)

### Defensive Patterns Found (model these)
1. **RaceConfig.from_dict()** — ALL fields use `.get()` with sensible defaults. Never crashes.
2. **ShipSerializer.from_dict()** — `isinstance(c_entry, dict)` check, graceful skip of missing components
3. **TechTree.load_from_json()** — Skips malformed entries, counts loaded/skipped

## Key Patterns to Reuse

### Pattern: Validation Helper Functions
**File:** `game/core/validation_helpers.py` (NEW — Phase 1)
```python
require_keys(data, ['id', 'name'], 'Fleet')           # Required field check
validate_enum(value, StarType, 'star_type', 'Star')    # Safe enum conversion
validate_positive(mass, 'mass', 'Planet')              # Range check
safe_from_dict(Star.from_dict, star_data, 'Star')      # Wrapped from_dict call
```

### Pattern: Resilient Collection Deserialization
For nested collections (stars in system, ships in fleet, planets in system):
```python
stars = []
for i, star_data in enumerate(data.get('stars', [])):
    try:
        stars.append(Star.from_dict(star_data))
    except PersistenceException:
        logger.warning(f"Skipping corrupt star {i} in system '{name}'")
```

### Pattern: Error Context Enrichment
Each from_dict wraps internal errors with class context:
```python
try:
    # ... deserialization logic ...
except (KeyError, TypeError) as e:
    raise PersistenceException(
        f"Failed to deserialize Fleet '{data.get('id', '?')}': {e}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={"class": "Fleet", "error": str(e), "data_keys": list(data.keys())}
    ) from e
```

## Dependencies & Risks

1. **PROJ-170 (Exception Migration)** — Soft dependency. PROJ-170 migrates existing generic raises to domain exceptions. PROJ-171 adds NEW validation raises. Can proceed independently.
   - **Mitigation:** Use PersistenceException directly — no dependency on PROJ-170's changes.

2. **Existing round-trip tests** — 5 test files with ~1700 lines of serialization tests. Adding validation to from_dict could break tests that pass minimal data.
   - **Mitigation:** Run existing tests after every change. Most tests use valid data. Any test using intentionally minimal data may need a field added.

3. **Save file backwards compatibility** — Old saves may have different field sets.
   - **Mitigation:** Use `.get()` with defaults for fields added after the original format. Only `require_keys()` for fields that have ALWAYS existed.

4. **Performance** — Validation on deserialization paths.
   - **Mitigation:** O(n) key checks — trivial compared to object construction and I/O.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
