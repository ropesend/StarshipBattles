# PROJ-170: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
PROJ-45 established a well-designed exception hierarchy with 10 exception classes, 19 error codes, and 563 lines of documentation. However, adoption is only ~5%:
- **63 generic raises** (46 ValueError, 4 RuntimeError, 13 TypeError DI) should use custom exceptions
- **Only 9 production files** currently use custom exceptions (28 occurrences)
- **36 except blocks** catch generic exceptions raised by game code
- **80 tests** assert generic exceptions on game code

### Review Source
Full audit conducted 2026-02-23 with 7 specialized agents. Reports at:
`Reviews/results/2026-02-23_180421_focused_exception-handling-migration-audit/`

## Gold Standard Pattern

From `game/simulation/formula_system.py` — the reference implementation:

```python
from game.core.exceptions import FormulaException
from game.core.error_codes import ErrorCode

# Raising with error code and context:
raise FormulaException(
    f"Undefined variable '{var_name}' in formula",
    code=ErrorCode.FORMULA_UNDEFINED_VAR.value,
    context={"formula": formula_str, "variable": var_name}
)

# Exception chaining (preserving cause):
try:
    result = eval(compiled, env)
except Exception as e:
    raise FormulaException(
        f"Evaluation error in formula: {formula_str}",
        code=ErrorCode.EVAL_ERROR.value,
        context={"formula": formula_str, "error": str(e)}
    ) from e
```

**Rules for every migration:**
1. Use the most specific exception class from the hierarchy
2. Always include an error code from `ErrorCode` enum
3. Always include a context dict with relevant data
4. Use `from e` when re-raising from a caught exception
5. Message should be human-readable; code + context are for programmatic handling

## Exception Class Selection Guide

| Situation | Exception Class | Common Codes |
|-----------|----------------|-------------|
| Input validation failure | `ValidationException` | V001, V002, V004 |
| Missing required DI param | `ValidationException` | C003 (MISSING_DEPENDENCY) |
| Object in wrong state | `StateException` | S002, S003 |
| Modifying frozen object | `FrozenStateException` | S001 |
| File/resource not found | `MissingResourceException` | R001 |
| Resource has bad format | `ResourceException` | R002 |
| Save/load failure | `PersistenceException` | P001-P005 |
| Combat engine error | `SimulationException` | — |
| Component config error | `ComponentException` | C001, C002, C004, C005 |
| Formula eval error | `FormulaException` | F001-F004 |

## Key Patterns to Reuse

### 1. DI Validation Pattern (13 occurrences)
```python
# BEFORE (current):
if registries is None:
    raise TypeError("registries is required for Ship initialization")

# AFTER (target):
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if registries is None:
    raise ValidationException(
        "registries is required for Ship initialization",
        code=ErrorCode.MISSING_DEPENDENCY.value,
        context={"class": "Ship", "parameter": "registries"}
    )
```

### 2. Schema Validation Pattern (18+ occurrences in loaders)
```python
# BEFORE:
raise ValueError(f"Blueprint '{name}' missing 'star_count'")

# AFTER:
raise ValidationException(
    f"Blueprint '{name}' missing required field",
    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
    context={"blueprint": name, "missing_field": "star_count"}
)
```

### 3. Range Validation Pattern
```python
# BEFORE:
raise ValueError("GameConfig requires at least 1 player")

# AFTER:
raise ValidationException(
    "Player count out of range",
    code=ErrorCode.OUT_OF_RANGE.value,
    context={"field": "player_count", "value": len(self.players), "min": 1, "max": 4}
)
```

### 4. Resource Not Found Pattern
```python
# BEFORE:
raise RuntimeError(f"Critical Error: {file_path} not found.")

# AFTER:
raise MissingResourceException(
    f"Vehicle class data file not found: {file_path}",
    code=ErrorCode.RESOURCE_NOT_FOUND.value,
    context={"file_path": str(file_path)}
)
```

## Dependencies & Risks

1. **Self-contained breaking changes (LOW risk)** — All 5 locations where raise and catch are in the same file. Change both simultaneously.

2. **Persistence tier broad catches (MEDIUM risk)** — `save_game_service.py` catches 11 exception types. Strategy: add domain exceptions to tuple, keep generic types temporarily, then remove generic types after verifying all raises migrated.

3. **Test message matching (LOW risk)** — ~15 tests use `match=` in `pytest.raises()`. Messages may change slightly. Update match patterns to work with new messages.

4. **Import ordering** — Adding `from game.core.exceptions import ...` to ~35 files. Ensure no circular imports. All exception/error_code modules are in `game/core/` with zero internal dependencies — safe.

## Opportunities Discovered

1. **9 unused error codes** (R001, R002, R003, P001, P002, P004, P005, C001) will gain their first usage during this migration
2. **Deserialization validation** could be a follow-up project (~20 from_dict methods need improved validation)
3. **Error code coverage** post-migration will jump from ~5% to ~80%+ of exception raises having codes

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
