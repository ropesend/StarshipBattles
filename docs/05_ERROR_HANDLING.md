# Error Handling Guidelines

Error handling conventions, exception hierarchy, logging standards, and reference patterns for the Starship Battles codebase.

> **Reference Implementation:** `game/core/json_utils.py` demonstrates all patterns described here.

---

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [Error Codes](#error-codes)
3. [Logging Levels](#logging-levels)
4. [JSON Utilities](#json-utilities)
5. [Patterns to Follow](#patterns-to-follow)
6. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
7. [Quick Reference](#quick-reference)

---

## Exception Hierarchy

All custom exceptions are defined in `game/core/exceptions.py`. They inherit from `GameException` and support error codes and context dictionaries.

### Hierarchy Diagram

```
GameException (base - don't raise directly)
    |
    +-- StateException
    |       +-- FrozenStateException
    |
    +-- ValidationException
    |
    +-- ResourceException
    |       +-- MissingResourceException
    |
    +-- PersistenceException
    |
    +-- SimulationException
            +-- ComponentException
            +-- FormulaException
```

### When to Use Each Exception Type

| Exception | Use When |
|-----------|----------|
| **GameException** | Base class only -- don't raise directly |
| **StateException** | Operations attempted on objects in invalid state |
| **FrozenStateException** | Attempting to modify frozen/immutable objects (combat resolution) |
| **ValidationException** | Input validation failures, schema violations, out-of-range values |
| **ResourceException** | Resource-related errors (images, sounds, data files) |
| **MissingResourceException** | Required resource cannot be found |
| **PersistenceException** | Save/load failures, file I/O errors, data corruption |
| **SimulationException** | Combat simulation engine errors (currently used as catch target and base class only -- not directly raised) |
| **ComponentException** | Component operations failures, invalid configurations (currently used as catch target and base class only -- not directly raised) |
| **FormulaException** | Formula parsing/evaluation errors |

### Exception Attributes

All exceptions support:
- `message` (str): Human-readable error description
- `code` (str, optional): Error code for programmatic handling (e.g., "V001")
- `context` (dict): Additional contextual information (defaults to `{}`)

---

## Error Codes

Error codes are defined in `game/core/error_codes.py` using the `ErrorCode` enum. Codes follow the format `X###` where X is a category letter and ### is a three-digit number.

### Validation Codes (V001-V099)

| Code | Name | Description |
|------|------|-------------|
| V001 | `VALIDATION_FAILED` | General validation failure |
| V002 | `SCHEMA_VALIDATION_ERROR` | Schema or structural validation error (missing fields, invalid data structure) |
| V003 | `MISSING_ENTITY` | Referenced entity does not exist |
| V004 | `OUT_OF_RANGE` | Value is outside allowed range |

### State Codes (S001-S099)

| Code | Name | Description |
|------|------|-------------|
| S001 | `STATE_FROZEN` | Object frozen, cannot modify |
| S002 | `NOT_INITIALIZED` | Object not properly initialized |
| S003 | `INVALID_STATE` | Object is in an invalid or unexpected state |

### Resource Codes (R001-R099)

| Code | Name | Description |
|------|------|-------------|
| R001 | `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| R002 | `INVALID_FORMAT` | Resource has invalid or unsupported format |
| R003 | `RESOURCE_LOAD_FAILED` | Failed to load resource |

### Persistence Codes (P001-P099)

| Code | Name | Description |
|------|------|-------------|
| P001 | `SAVE_FAILED` | Failed to save data |
| P002 | `LOAD_FAILED` | Failed to load data |
| P003 | `CORRUPT_DATA` | Data corrupted or malformed |
| P004 | `VERSION_MISMATCH` | Save file version is incompatible |
| P005 | `IO_ERROR` | File system I/O error occurred |

### Formula Codes (F001-F099)

| Code | Name | Description |
|------|------|-------------|
| F001 | `FORMULA_SYNTAX_ERROR` | Formula syntax error |
| F002 | `FORMULA_UNDEFINED_VAR` | Undefined variable in formula |
| F003 | `EVAL_ERROR` | Formula runtime evaluation error |
| F004 | `FORMULA_GENERAL_ERROR` | General formula evaluation failure |

### Component Codes (C001-C099)

| Code | Name | Description |
|------|------|-------------|
| C001 | `COMPONENT_NOT_FOUND` | Component doesn't exist |
| C002 | `COMPONENT_INVALID` | Component configuration is invalid |
| C003 | `MISSING_DEPENDENCY` | Required dependency injection parameter not provided |
| C004 | `SLOT_OCCUPIED` | Component slot is already occupied |
| C005 | `INCOMPATIBLE_COMPONENT` | Component is not compatible with target |

### Using Error Codes

```python
from game.core.exceptions import ValidationException, ComponentException
from game.core.error_codes import ErrorCode

# V001 - General validation failure
raise ValidationException(
    "Invalid damage value",
    code=ErrorCode.VALIDATION_FAILED.value,
    context={"field": "damage", "value": -5}
)

# V002 - Schema validation error
raise ValidationException(
    "Missing required fields in ship data",
    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
    context={"missing_fields": ["hull_id", "components"]}
)

# C003 - Missing dependency injection parameter
raise ComponentException(
    "Required 'registry_provider' parameter not provided",
    code=ErrorCode.MISSING_DEPENDENCY.value,
    context={"expected": "registry_provider", "caller": "ShipLoader"}
)

# Programmatic handling
try:
    load_component(data)
except ComponentException as e:
    if e.code == ErrorCode.COMPONENT_INVALID.value:
        use_default_component()
```

---

## Logging Levels

All production code uses Python's standard logging module:

```python
import logging
logger = logging.getLogger(__name__)
```

### logger.debug()
**Detailed diagnostic information for development and debugging.**

Use for: state transitions, method parameters, intermediate values, expected failures.

```python
logger.debug(f"State changed from {old} to {new}")
logger.debug(f"scan_designs: pattern={pattern}")
```

### logger.info()
**Notable events during normal operation.**

Use for: successful initialization, significant operations complete, system state changes.

```python
logger.info(f"Loaded {count} vehicle classes.")
logger.info(f"Saved game to {filepath}")
```

### logger.warning()
**Recoverable problems where operation continues with fallback.**

Use for: missing optional resources, recoverable failures, validation warnings, performance issues.

```python
logger.warning(f"Portrait not found, using default")
logger.warning(f"Config load failed, using defaults: {e}")
```

### logger.error()
**Failures that prevent operation from completing.**

Use for: required files not found, critical operations failed, data corruption, unexpected exceptions.

```python
logger.error(f"Asset manifest missing: {path}")
logger.error(f"Failed to save game: {e}")
logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
```

### log_event() (Event System)
**Structured simulation events for callbacks -- NOT standard logging.**

Defined in `game/core/event_logging.py`. Events are typed callback invocations for simulation observers (tests, replay systems, analytics). When no handler is registered, `log_event()` is a no-op.

```python
from game.core.event_logging import log_event, set_event_handler

# Register handler (in GameSession or test fixtures)
set_event_handler(my_handler)

# Fire events (from simulation code)
log_event("damage", ship_id=42, amount=100)
log_event("weapon_fired", weapon_id="laser", target_id=12)
```

Handler lifecycle:
- Set by `GameSession` during game startup
- Cleared (set to `None`) in test fixtures via `conftest.py`
- Handler exceptions are caught and logged to prevent simulation crashes

---

## JSON Utilities

`game/core/json_utils.py` is the canonical location for all file-based JSON operations. Do NOT use `json.load`/`json.dump` directly for file operations in `game/`.

### load_json()

Safe loading with default return on failure. Never raises exceptions.

```python
from game.core.json_utils import load_json

data = load_json("config.json", default={})
```

Handles: `FileNotFoundError` (returns default, logs debug), `json.JSONDecodeError` (returns default, logs error), `PermissionError` (returns default, logs error), `OSError` (returns default, logs error).

### load_json_required()

Strict loading for critical files. Raises exceptions on failure.

```python
from game.core.json_utils import load_json_required

data = load_json_required("critical_config.json")
# Raises FileNotFoundError if file doesn't exist
# Raises json.JSONDecodeError if JSON is invalid
```

### save_json()

Save with automatic parent directory creation. Returns `True`/`False`.

```python
from game.core.json_utils import save_json

success = save_json("output.json", data, indent=2)
```

### deserialize_list()

Resilient list deserialization that skips invalid items with a warning log. Ensures partial save files can still be loaded.

```python
from game.core.json_utils import deserialize_list

planets = deserialize_list(
    data.get('planets', []),
    Planet.from_dict,
    entity_name='planet',
    parent_name=f"StarSystem '{system.name}'"
)
# Invalid items are skipped with logger.warning(), not raised
```

Catches: `PersistenceException`, `KeyError`, `TypeError`, `ValueError`.

---

## Patterns to Follow

### Pattern 1: Catch Specific Exceptions

Always catch the most specific exception type possible.

```python
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.warning(f"Invalid JSON: {e}")
    return default
```

### Pattern 2: Exception Chaining with `raise from`

Preserve the original cause when re-raising exceptions.

```python
try:
    data = load_json(path)
except json.JSONDecodeError as e:
    raise PersistenceException(
        f"Failed to parse save file: {path}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={"path": str(path)}
    ) from e
```

### Pattern 3: Always Log Exceptions

Never silently swallow exceptions. At minimum, log a warning.

```python
try:
    result = parse_data(data)
except ValueError as e:
    logger.warning(f"Failed to parse data, using default: {e}")
    result = default_value
```

### Pattern 4: Include Context in Error Messages

Error messages should include enough context to diagnose the problem.

```python
logger.error(f"Failed to load design '{design_id}' from '{filepath}': {e}")

raise ValidationException(
    "Component damage value out of range",
    code=ErrorCode.OUT_OF_RANGE.value,
    context={"component_id": comp_id, "damage": damage, "max": 100}
)
```

### Pattern 5: Graceful Degradation for Non-Critical Operations

For non-critical features, prefer graceful degradation over failure.

```python
def get_image(self, category, key):
    try:
        return self._load_image(cache_key, file_path)
    except (FileNotFoundError, pygame.error) as e:
        logger.warning(f"Failed to load image {file_path}: {e}")
        return self.get_missing_texture()
```

### Pattern 6: Use Custom Exceptions for Domain Errors

```python
if not ship.is_valid():
    raise ValidationException(
        f"Ship '{ship.name}' has invalid configuration",
        code=ErrorCode.VALIDATION_FAILED.value,
        context={"ship_id": ship.id, "errors": ship.validation_errors}
    )
```

---

## Anti-Patterns to Avoid

### 1. Bare `except:` Clauses

```python
# BAD: Catches SystemExit, KeyboardInterrupt
try:
    do_something()
except:
    pass
```

### 2. Catching `Exception` Without Logging

```python
# BAD: Silent failure hides bugs
try:
    result = process(data)
except Exception:
    result = None
```

### 3. Using Generic `raise Exception()`

```python
# BAD
raise Exception("Something went wrong")

# GOOD
raise ValidationException(
    "Invalid component configuration",
    code=ErrorCode.COMPONENT_INVALID.value,
    context={"component_id": comp_id}
)
```

### 4. Missing Exception Chaining

```python
# BAD: Loses original traceback
except json.JSONDecodeError:
    raise ValidationException("Invalid JSON")

# GOOD: Preserves original cause
except json.JSONDecodeError as e:
    raise ValidationException("Invalid JSON") from e
```

### 5. Custom Logger Wrappers

```python
# BAD: Legacy pattern (deleted)
from game.core.logger import log_info, log_error

# GOOD: Standard library logging
import logging
logger = logging.getLogger(__name__)
logger.info("Message here")
```

### 6. Direct JSON File I/O

```python
# BAD: Bypasses json_utils error handling
import json
with open("file.json") as f:
    data = json.load(f)

# GOOD: Use json_utils
from game.core.json_utils import load_json
data = load_json("file.json", default={})
```

### 7. Using print() for Diagnostics

```python
# BAD
print(f"DEBUG: processing {item}")

# GOOD
logger.debug(f"Processing {item}")
```

### 8. Using traceback.print_exc()

```python
# BAD: Prints to stdout, not to logs
except Exception:
    traceback.print_exc()

# GOOD: Captures stack trace in logs
except Exception as e:
    logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
```

---

## Intentional Broad Catch Convention

In some cases, catching `Exception` broadly is justified -- for example, in crash handlers, platform-dependent code, and event handler isolation where an unexpected exception must not propagate and crash the application. The codebase convention is to annotate these with an inline comment:

```python
# Intentional broad catch: <reason>
except Exception as e:
    logger.error(f"Unexpected error in event handler: {e}")
```

This annotation signals to reviewers (and to automated audits) that the broad catch was deliberate, not accidental. Always include a brief reason explaining why a broad catch is appropriate at that call site.

---

## Quick Reference

### Decision Tree: Which Exception to Use?

```
Is it a validation/input error?
  -> ValidationException

Is it about loading/saving data?
  -> PersistenceException

Is it about missing files/assets?
  -> MissingResourceException (if file missing)
  -> ResourceException (general resource errors)

Is it about object state?
  -> FrozenStateException (if object is immutable)
  -> StateException (general state errors)

Is it about combat simulation?
  -> ComponentException (component-related)
  -> FormulaException (formula-related)
  -> SimulationException (general simulation)
```

### Logging Decision Tree

```
Is it a fatal error preventing operation?
  -> logger.error()

Is it a problem with automatic recovery/fallback?
  -> logger.warning()

Is it normal successful operation?
  -> logger.info()

Is it diagnostic/debugging information?
  -> logger.debug()

Is it a structured simulation event (damage, movement, etc.)?
  -> log_event()  # from game.core.event_logging
```

### Exception Handler Template

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.warning(f"Operation failed: {e}")
    result = fallback_value
except AnotherException as e:
    raise DomainException(
        f"Failed to complete operation: {e}",
        code=ErrorCode.RELEVANT_CODE.value,
        context={"relevant": "data"}
    ) from e
```

---

## See Also

- `game/core/exceptions.py` -- Exception class definitions
- `game/core/error_codes.py` -- Error code enumeration
- `game/core/json_utils.py` -- Reference implementation
- `game/core/event_logging.py` -- Event logging system

*Last Updated: March 2026*
