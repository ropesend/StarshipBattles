# Error Handling Guidelines

> **Last verified:** 2026-04-26

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
    +-- StrategyException
    |       +-- EnginePhaseError
    |
    +-- SimulationException
    |       +-- ComponentException
    |       +-- FormulaException
    |
    +-- LLMException                   (PROJ-296)
            +-- LLMConfigError         (no key / unknown provider)
            +-- LLMNetworkError        (connection / DNS / SSL / exhausted retries)
            +-- LLMResponseError       (malformed body or non-2xx other than 429)
            +-- LLMRateLimited         (429 from provider)
            +-- LLMTimeoutError        (request exceeded timeout)
            +-- LLMCancelled           (cancelled via cancel_token)
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
| **StrategyException** | Strategy-layer errors (turn processing, fleet management, empire operations) |
| **EnginePhaseError** | Sub-engine phase failed during turn tick processing — triggers rollback |
| **SimulationException** | Combat simulation engine errors (currently used as catch target and base class only -- not directly raised) |
| **ComponentException** | Component operations failures, invalid configurations (currently used as catch target and base class only -- not directly raised) |
| **FormulaException** | Formula parsing/evaluation errors |
| **LLMException** (PROJ-296) | Base class for LLM service errors -- don't raise directly |
| **LLMConfigError** | LLM not configured: no API key, unknown provider, or concurrent-call limit reached |
| **LLMNetworkError** | LLM network failure: connection, DNS, SSL, or exhausted retries on 5xx |
| **LLMResponseError** | LLM response malformed or non-2xx (other than 429) |
| **LLMRateLimited** | LLM provider returned 429 — never auto-retried |
| **LLMTimeoutError** | LLM request exceeded its configured timeout |
| **LLMCancelled** | LLM call was cancelled via `cancel_token` |

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

### Turn Processing Codes (T001-T099)

| Code | Name | Description |
|------|------|-------------|
| T001 | `PHASE_FAILED` | Sub-engine phase failed during turn processing |
| T002 | `TURN_ROLLBACK` | Turn was rolled back due to phase failure |
| T003 | `SNAPSHOT_FAILED` | Failed to create pre-turn state snapshot |

### LLM Service Codes (L001-L099) — PROJ-296

| Code | Name | Description |
|------|------|-------------|
| L001 | `LLM_CONFIG_MISSING` | No API key, unknown provider, or concurrent-call limit reached |
| L002 | `LLM_NETWORK_ERROR` | Connection / DNS / SSL failure or exhausted retries on 5xx |
| L003 | `LLM_BAD_RESPONSE` | Malformed body or non-2xx response (other than 429) |
| L004 | `LLM_RATE_LIMITED` | Provider returned 429 — never auto-retried |
| L005 | `LLM_TIMEOUT` | Request exceeded its configured timeout |
| L006 | `LLM_CANCELLED` | Request cancelled via `cancel_token` |

**Logging hygiene rule:** LLM exception `context` dicts must NEVER include
the API key, the `Authorization` header, the request body, the response
body, or message contents. Safe fields: `model`, `endpoint`, `status_code`,
`error_code`, `request_duration_ms`, `attempt`. See PROJ-296 design.md
§ "Security Model" for the full guardrails.

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

Atomic save with automatic parent directory creation. Returns `True`/`False`.
Writes to a temp file first, then replaces the original — if serialization or
writing fails the original file is untouched.

```python
from game.core.json_utils import save_json

success = save_json("output.json", data, indent=2)
```

Handles: `PermissionError` (returns `False`, logs error), `OSError` (returns `False`, logs error), `TypeError` (non-serializable data, returns `False`, logs error, cleans up temp file), `ValueError` (out-of-range floats like `inf`/`NaN`, returns `False`, logs error, cleans up temp file).

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

> **Last verified:** 2026-04-27 (PROJ-308)

Prefer narrowed exception types. When a broad `except Exception:` is genuinely necessary, it MUST carry a justification comment.

### Broad Catches

**Format:**

```python
except Exception:  # Intentional broad catch: <specific reason>
```

The justification line MUST appear on the same line as the `except` clause OR on the line immediately above it. The reason must say *what* failures are expected and *why* fire-and-forget is correct.

**Legitimate reasons:**
- Third-party callback dispatch (handler may raise anything)
- Platform-dependent init (Tkinter, audio, GPU — exception types vary by OS)
- Defensive UI updates (a failed redraw shouldn't crash the session)
- Telemetry / event emission (instrumentation must never break the host)
- Registry-provider lookups that may run before initialization (tests, CLI tools)
- Save-state / library loads where I/O + JSON + schema-validation errors all need to fall back to a safe default

**Not legitimate (don't write these):**
- "general defensive code"
- "third-party stuff"
- "legacy"
- any comment that doesn't say *what* failures are expected and *why* fire-and-forget is correct

A broad catch without a justification comment is a code-review failure. See [PROJ-308](../Projects/active_projects/PROJ-308/) for the audit that established this convention (24 sites triaged 2026-04-27).

**PROJ-251 Changes:** The turn engine's `_time_phase()` no longer swallows exceptions. It wraps them in `EnginePhaseError` and re-raises to halt the turn. The serialization chain (`Fleet.from_dict()`, `Empire.from_dict()`, `OrderSerializer.deserialize_orders()`, `Galaxy.from_dict()`) no longer silently skips corrupt entries — it raises `PersistenceException`. The `_log_empire_state()` debug logging method retains its broad catch (acceptable — logging must not crash the turn).

---

## Turn Engine Error Boundary (PROJ-251)

The turn engine uses a snapshot-and-rollback pattern to ensure game state integrity:

1. **Before turn:** `TurnStateSnapshot.capture()` serializes all empires and galaxy via `to_dict()`
2. **During turn:** 100 ticks processed normally via `_time_phase()` wrappers
3. **On phase failure:** `_time_phase()` wraps the exception in `EnginePhaseError` and re-raises
4. **In `process_turn()`:** Catches `EnginePhaseError`, restores state from snapshot, dumps crash file, re-raises
5. **In `GameSession.process_turn()`:** Catches `EnginePhaseError`, logs, re-raises for UI

```python
# Turn engine _time_phase wraps and re-raises
try:
    result = fn(*args, **kwargs)
except EnginePhaseError:
    raise  # Already wrapped
except Exception as e:
    raise EnginePhaseError(
        f"Phase '{key}' failed: {e}",
        code=ErrorCode.PHASE_FAILED.value,
        context={"phase_name": key, "tick": self._current_tick}
    ) from e
```

Sub-engines should add `_validate_tick_inputs()` methods that raise `ValidationException` with descriptive messages before mutating state. The error boundary will catch and wrap these.

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
