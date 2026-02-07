# Error Handling Quick Reference

> **Full guide:** See [ERROR_HANDLING_GUIDELINES.md](ERROR_HANDLING_GUIDELINES.md) for the complete error handling guide including exception hierarchy, error codes, anti-patterns, and decision trees.

---

## Logging Level Summary

| Level | When to Use | Example |
|-------|-------------|---------|
| `log_debug()` | Development/debugging info | State changes, method params, intermediate values |
| `log_info()` | Normal operation confirmation | Initialization complete, files saved |
| `log_warning()` | Recoverable problems with fallback | Missing optional files, slow performance |
| `log_error()` | Failures preventing operation completion | Required files missing, save failed, data corrupted |

## Exception Hierarchy (`game/core/exceptions.py`)

```
GameException (base - don't raise directly)
    ├── StateException / FrozenStateException
    ├── ValidationException
    ├── ResourceException / MissingResourceException
    ├── PersistenceException
    ├── SimulationException / ComponentException / FormulaException
    └── AIException / TargetingException
```

## Core Patterns

1. **Catch specific exceptions** - Never bare `except:`, always name the type
2. **Always log exceptions** - Never silently swallow; at minimum `log_warning()`
3. **Include context** - `log_error(f"Failed to load '{design_id}' from '{path}': {e}")`
4. **Chain exceptions** - `raise DomainException(...) from e` to preserve traceback
5. **Graceful degradation** - Use fallbacks for non-critical features (e.g., placeholder images)
6. **Use custom exceptions** - Raise from `game/core/exceptions.py`, not generic `Exception`

## Error Codes (`game/core/error_codes.py`)

| Prefix | Category | Example |
|--------|----------|---------|
| V | Validation | V001 VALIDATION_FAILED, V002 INVALID_COMPONENT |
| S | State | S001 STATE_FROZEN, S002 NOT_INITIALIZED |
| R | Resource | R001 RESOURCE_NOT_FOUND |
| P | Persistence | P001 SAVE_FAILED, P002 LOAD_FAILED |
| F | Formula | F001 SYNTAX_ERROR |
| C | Component | C001 COMPONENT_NOT_FOUND |

## Reference Implementation

See `game/core/json_utils.py` for the canonical example of proper error handling patterns.
