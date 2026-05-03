# Error Code Gap Analysis Report

## Current Code Usage Audit

Comprehensive audit of all `ErrorCode` enum values, their current usage in production code, and status.

| Code | Name | Used In | Usage Count | Status |
|------|------|---------|-------------|--------|
| V001 | VALIDATION_FAILED | `projectile.py`, `formula_system.py`, `modifier_effects.py`, `registry.py` | 4 | Active |
| V004 | OUT_OF_RANGE | `projectile.py` | 1 | Active |
| S001 | STATE_FROZEN | `registry.py`, `ship.py` | 3 | Active |
| S002 | NOT_INITIALIZED | `registry.py` | 1 | Active |
| S003 | INVALID_STATE | `battle_controller.py` | 1 | Active |
| R001 | RESOURCE_NOT_FOUND | (none found in production) | 0 | **UNUSED** |
| R002 | INVALID_FORMAT | (none found in production) | 0 | **UNUSED** |
| R003 | RESOURCE_LOAD_FAILED | (none found in production) | 0 | **UNUSED** |
| P001 | SAVE_FAILED | (none found) | 0 | **UNUSED** |
| P002 | LOAD_FAILED | (none found) | 0 | **UNUSED** |
| P003 | CORRUPT_DATA | `game_session.py` | 1 | Active |
| P004 | VERSION_MISMATCH | (none found) | 0 | **UNUSED** |
| P005 | IO_ERROR | (none found) | 0 | **UNUSED** |
| F001 | FORMULA_SYNTAX_ERROR | `formula_system.py` | 2 | Active |
| F002 | FORMULA_UNDEFINED_VAR | `formula_system.py` | 1 | Active |
| F003 | EVAL_ERROR | `formula_system.py`, `modifier_effects.py` | 2 | Active |
| F004 | FORMULA_GENERAL_ERROR | `formula_system.py` | 1 | Active |
| C001 | COMPONENT_NOT_FOUND | (none found) | 0 | **UNUSED** |
| C002 | COMPONENT_INVALID | `component.py` | 2 | Active |
| C004 | SLOT_OCCUPIED | `component.py` | 1 | Active |
| C005 | INCOMPATIBLE_COMPONENT | `component.py` | 2 | Active |

### Summary

- **10 codes** actively used in production
- **9 codes** currently UNUSED but defined in the enum
- The unused codes (R-series, P001/P002/P004/P005, C001) were defined proactively and will be needed during the exception migration

---

## Proposed New Error Codes

### V002 — SCHEMA_VALIDATION_ERROR

**Purpose:** Missing required fields, invalid structure in configuration JSON validation.

**Maps from:** 18+ `ValueError` raises in loader files including:
- Blueprint loaders (missing required sections, invalid structure)
- Astrophysics config loaders (invalid parameter structures)
- Galaxy layout validators (missing required layout fields)
- Component schema validators (invalid component definitions)

**Example usage:**
```python
raise ValidationException(
    "Missing required section in blueprint config",
    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
    context={"section": name, "file": filepath}
)
```

**Distinguishes from V001 (VALIDATION_FAILED):** V001 is for runtime value validation (e.g., "damage cannot be negative"). V002 is for structural/schema validation (e.g., "config file missing required 'weapons' section").

---

### V003 — MISSING_ENTITY

**Purpose:** Referenced entity or resource does not exist by name or ID.

**Maps from:** `KeyError` raises for:
- Unknown blueprint name lookups
- Mass distribution key not found
- Orbit zone name not in configuration
- Named entity lookups that fail (ship class, component type, ability name)

**Example usage:**
```python
raise ValidationException(
    "Unknown blueprint referenced",
    code=ErrorCode.MISSING_ENTITY.value,
    context={"name": name, "available": list(registry.keys())}
)
```

**Distinguishes from R001 (RESOURCE_NOT_FOUND):** R001 is for file-system resources (files, directories). V003 is for logical entities within the data model (a named blueprint, a ship class, etc.).

---

### C003 — MISSING_DEPENDENCY

**Purpose:** Required dependency injection parameter not provided.

**Maps from:** 13 `TypeError` raises for missing DI parameters including:
- Missing `registries` parameter in component constructors
- Missing `registry_provider` in service initialization
- Missing required service dependencies in factory methods

**Example usage:**
```python
raise ComponentException(
    "Required dependency 'registries' not provided",
    code=ErrorCode.MISSING_DEPENDENCY.value,
    context={"class": cls.__name__, "param": "registries"}
)
```

**Design note:** This code fills the gap in the C-series (C001, C002, ___, C004, C005). It was placed here because the majority of DI violations occur in component and simulation code. An alternative placement would be V005 (general validation) or S004 (state/initialization), but C003 best represents the primary use case.

---

## Missing Exception Classes Analysis

The existing exception hierarchy is **sufficient** for all identified migration needs. No new exception classes are required.

| Exception Class | Covers |
|----------------|--------|
| `ValidationException` | Schema validation, range checks, type validation, config validation, missing entities |
| `StateException` | Initialization failures, invalid state transitions, frozen state violations |
| `ResourceException` / `MissingResourceException` | File not found, invalid file format, resource load failures |
| `PersistenceException` | Save/load failures, corrupt data, version mismatches |
| `ComponentException` | Component config errors, DI violations in component code, slot conflicts |
| `SimulationException` | Battle/simulation-level errors (parent of ComponentException) |
| `FormulaException` | Formula parsing, evaluation, and variable errors |

### Why no new classes are needed

1. The existing hierarchy already covers all semantic domains in the codebase
2. The error code system provides fine-grained distinction within each class
3. Adding new exception classes would fragment the catch hierarchy unnecessarily
4. Callers can distinguish specific error types via `error.code` when needed

---

## Complete Proposed Error Code Table (Post-Migration)

| Code | Name | Category | Description | Status |
|------|------|----------|-------------|--------|
| V001 | VALIDATION_FAILED | Validation | General validation failure | Existing |
| V002 | SCHEMA_VALIDATION_ERROR | Validation | Schema/config structure invalid | **NEW** |
| V003 | MISSING_ENTITY | Validation | Referenced entity not found by name/ID | **NEW** |
| V004 | OUT_OF_RANGE | Validation | Value outside allowed range | Existing |
| S001 | STATE_FROZEN | State | Object is frozen/immutable | Existing |
| S002 | NOT_INITIALIZED | State | Object not yet initialized | Existing |
| S003 | INVALID_STATE | State | Object in invalid state for operation | Existing |
| R001 | RESOURCE_NOT_FOUND | Resource | Resource file not found on disk | Existing (unused) |
| R002 | INVALID_FORMAT | Resource | Resource file has invalid format | Existing (unused) |
| R003 | RESOURCE_LOAD_FAILED | Resource | Failed to load resource from disk | Existing (unused) |
| P001 | SAVE_FAILED | Persistence | Save operation failed | Existing (unused) |
| P002 | LOAD_FAILED | Persistence | Load operation failed | Existing (unused) |
| P003 | CORRUPT_DATA | Persistence | Data corrupted or malformed | Existing |
| P004 | VERSION_MISMATCH | Persistence | Incompatible save version | Existing (unused) |
| P005 | IO_ERROR | Persistence | File I/O error | Existing (unused) |
| F001 | FORMULA_SYNTAX_ERROR | Formula | Formula has syntax error | Existing |
| F002 | FORMULA_UNDEFINED_VAR | Formula | Undefined variable in formula | Existing |
| F003 | EVAL_ERROR | Formula | Formula evaluation failed | Existing |
| F004 | FORMULA_GENERAL_ERROR | Formula | General formula failure | Existing |
| C001 | COMPONENT_NOT_FOUND | Component | Component doesn't exist in registry | Existing (unused) |
| C002 | COMPONENT_INVALID | Component | Invalid component configuration | Existing |
| C003 | MISSING_DEPENDENCY | Component | Required DI parameter not provided | **NEW** |
| C004 | SLOT_OCCUPIED | Component | Component slot already occupied | Existing |
| C005 | INCOMPATIBLE_COMPONENT | Component | Component incompatible with target | Existing |

### Totals

| Metric | Count |
|--------|-------|
| Existing codes (active) | 10 |
| Existing codes (unused, reserved for migration) | 9 |
| New codes proposed | 3 |
| **Total post-migration** | **22** |

---

## Migration Impact Summary

### Codes that will see significant new usage during migration

| Code | Current Uses | Expected Post-Migration Uses | Primary New Sources |
|------|-------------|------------------------------|---------------------|
| V001 | 4 | 15-20 | General validation in loaders, constructors |
| V002 | 0 (new) | 18+ | Config/schema validation across all loaders |
| V003 | 0 (new) | 10-15 | Entity lookup failures in registries |
| C002 | 2 | 8-12 | Component construction validation |
| C003 | 0 (new) | 13+ | DI parameter validation |
| P003 | 1 | 5-8 | Save/load data validation |
| R001 | 0 | 3-5 | File-based resource loading |
| R002 | 0 | 3-5 | Resource format validation |

### Codes that may remain unused post-migration

| Code | Reason |
|------|--------|
| P004 (VERSION_MISMATCH) | Save migration policy is "discard old saves" — version checks may not be needed |
| P005 (IO_ERROR) | Most I/O errors are caught as OSError at stdlib level, not wrapped in domain exceptions |
| R003 (RESOURCE_LOAD_FAILED) | May overlap with R001 + R002 in practice |

These codes should be retained in the enum for future use but are not expected to see immediate adoption.
