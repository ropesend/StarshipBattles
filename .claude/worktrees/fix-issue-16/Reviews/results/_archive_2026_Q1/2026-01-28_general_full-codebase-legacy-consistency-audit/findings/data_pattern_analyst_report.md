# Data Pattern Analyst Report

## Summary
- **Total issues found:** 14
- **Critical:** 3, **Major:** 6, **Minor:** 5

---

## Critical Issues

### DPA-001: Inconsistent Dictionary Access Pattern - KeyError Risk
**ID:** DPA-001
**Location:** `game/strategy/data/planet.py:192-227`, `game/strategy/data/galaxy.py:32-33,74-75,439`
**Issue:** Mixed use of direct bracket access `data['key']` and safe `.get()` access in from_dict() methods. Planet.from_dict() uses 14 direct accesses without defaults while also using `.get()` for optional fields.
**Impact:** Data corruption, deserialization failures, loss of saved game compatibility
**Recommendation:** Standardize all from_dict() methods to use `.get()` with sensible defaults for all fields.
**Effort:** Medium

---

### DPA-002: Enum String Conversion Without Error Handling
**ID:** DPA-002
**Location:** `game/strategy/data/planet.py:193`, `game/strategy/data/galaxy.py:71`
**Issue:** Enum conversion using bracket notation: `PlanetType[data['planet_type']]` will raise KeyError if the enum value name doesn't exist.
**Impact:** Complete deserialization failure if enum naming changes between versions.
**Recommendation:** Add try-catch around enum conversion with fallback to a safe default value.
**Effort:** Simple

---

### DPA-003: Incomplete Optional Field Handling with None Values
**ID:** DPA-003
**Location:** `game/strategy/data/ship_instance.py:47,62,99-106`
**Issue:** ShipInstance.from_dict() uses `data.get('serial')` which returns None for missing fields, but ShipInstance.create() logs a warning when serial is None. Dual-meaning of None creates confusion.
**Impact:** Ambiguous state - unclear if None means "not set" vs "intentionally defaulting".
**Recommendation:** Use explicit sentinel values or add a `_version` field to distinguish old saves.
**Effort:** Medium

---

## Major Issues

### DPA-004: Inconsistent Serialization Method Naming
**ID:** DPA-004
**Location:** Across 17 files with serialization methods
**Issue:** Codebase uses two different naming conventions: `to_dict()` / `from_dict()` (13 files), `to_json()` / `from_json()` (wrappers in some)
**Impact:** Developer confusion, maintainability issues
**Recommendation:** Adopt single naming convention (recommend `to_dict()`/`from_dict()`).
**Effort:** Medium

---

### DPA-005: Missing Version/Schema Information in Serialized Data
**ID:** DPA-005
**Location:** All to_dict() methods lack `_version` or `_schema_version` fields
**Issue:** No serialization format version is stored in saved data.
**Impact:** Impossible to implement safe migrations. Future format changes will silently corrupt data.
**Recommendation:** Add `_format_version` and `_schema_id` fields to all serialized data.
**Effort:** Medium

---

### DPA-006: Dataclass Field Defaults Mixed with Manual Defaults
**ID:** DPA-006
**Location:** `game/strategy/data/planet.py:20-82`, `game/strategy/data/ship_instance.py:26-63`
**Issue:** Dataclasses define field defaults via `field(default_factory=...)` but from_dict() also provides defaults via `.get()`. Redundant defaults that can diverge.
**Impact:** Subtle bugs where empty collections aren't shared as expected.
**Recommendation:** Use dataclass defaults consistently - don't repeat in from_dict().
**Effort:** Simple

---

### DPA-007: No Validation of Required Fields in from_dict()
**ID:** DPA-007
**Location:** All from_dict() implementations
**Issue:** No validation that required fields are present before use.
**Impact:** Silent data loss or corruption if save file is partially corrupted.
**Recommendation:** Add ValidationResult-based validation at start of from_dict().
**Effort:** Medium

---

### DPA-008: Circular Reference Handling is Inconsistent
**ID:** DPA-008
**Location:** `game/strategy/data/empire.py:70-94` vs `game/strategy/data/galaxy.py`
**Issue:** Empire.to_dict() explicitly avoids circular references by storing only IDs. However, other classes include full nested objects.
**Impact:** Potential stack overflow or memory bloat if circular references aren't properly broken.
**Recommendation:** Document circular reference handling strategy. Use IDs consistently for back-references.
**Effort:** Medium

---

### DPA-009: Field Type Conversions Not Always Bidirectional
**ID:** DPA-009
**Location:** `game/strategy/data/fleet.py:567`, `game/strategy/data/stars.py:100`
**Issue:** Serialization converts tuples to lists for JSON compatibility, but deserialization doesn't always convert back.
**Impact:** Type inconsistencies after round-trip serialization.
**Recommendation:** Add explicit type conversions in from_dict() to restore original types.
**Effort:** Simple

---

## Minor Issues

### DPA-010: Default Value Inconsistencies Across Instances
**Location:** `game/strategy/data/design_metadata.py:59-71`
**Issue:** Different approaches to handling missing nested objects.
**Effort:** Simple

### DPA-011: Resource Dictionary Handling Inconsistent
**Location:** `game/strategy/data/planet.py:167`
**Issue:** Assumes values are dicts; .copy() will fail if value is a scalar.
**Effort:** Simple

### DPA-012: Layer Type Enum String Conversion Missing Error Handling
**Location:** `game/simulation/battle_state.py:156`
**Issue:** Could fail if layer type names are changed.
**Effort:** Simple

### DPA-013: Optional Tuple Fields Not Fully Typed
**Location:** `game/strategy/data/stars.py:83`, `game/simulation/battle_state.py:90`
**Issue:** Tuple fields typed inconsistently.
**Effort:** Simple

### DPA-014: Backward Compatibility Partial
**Location:** `game/strategy/data/design_metadata.py:169-171`
**Issue:** Warns about old formats but doesn't actually migrate the data.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **DPA-001: Inconsistent Dictionary Access Pattern** - HIGH RISK: KeyError failures on deserialization
2. **DPA-002: Enum String Conversion Without Error Handling** - HIGH RISK: Enum changes break save loading
3. **DPA-005: Missing Version/Schema Information** - HIGH RISK: Makes all future format changes dangerous
4. **DPA-003: Incomplete Optional Field Handling** - MEDIUM RISK: Unclear semantics of None values
5. **DPA-004: Inconsistent Serialization Method Naming** - MEDIUM RISK: Maintainability issue
