# Error Handling Guidelines

This document establishes the error handling conventions, exception hierarchy, and logging standards for the Starship Battles codebase.

> **Reference Implementation:** See `game/core/json_utils.py` for the canonical example of proper error handling patterns.

---

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [Error Codes](#error-codes)
3. [Logging Levels](#logging-levels)
4. [Patterns to Follow](#patterns-to-follow)
5. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
6. [Code Examples](#code-examples)
7. [Quick Reference](#quick-reference)

---

## Exception Hierarchy

The codebase uses a custom exception hierarchy defined in `game/core/exceptions.py`. All custom exceptions inherit from `GameException` and support error codes and context dictionaries.

### Hierarchy Diagram

```
GameException (base)
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
    |       +-- ComponentException
    |       +-- FormulaException
    |
    +-- AIException
            +-- TargetingException
```

### When to Use Each Exception Type

| Exception | Use When |
|-----------|----------|
| **GameException** | Base class only - don't raise directly |
| **StateException** | Operations attempted on objects in invalid state |
| **FrozenStateException** | Attempting to modify frozen/immutable objects (combat resolution) |
| **ValidationException** | Input validation failures, schema violations, out-of-range values |
| **ResourceException** | Resource-related errors (images, sounds, data files) |
| **MissingResourceException** | Required resource cannot be found |
| **PersistenceException** | Save/load failures, file I/O errors, data corruption |
| **SimulationException** | Combat simulation engine errors |
| **ComponentException** | Component operations failures, invalid configurations |
| **FormulaException** | Formula parsing/evaluation errors |
| **AIException** | AI decision-making errors |
| **TargetingException** | Target evaluation/selection failures |

### Exception Attributes

All exceptions support:
- `message` (str): Human-readable error description
- `code` (str, optional): Error code for programmatic handling (e.g., "V001")
- `context` (dict): Additional contextual information (defaults to `{}`)

---

## Error Codes

Error codes are defined in `game/core/error_codes.py` using the `ErrorCode` enum. Codes follow the format `X###` where X is a category letter and ### is a three-digit number.

### Code Categories

| Prefix | Category | Range | Description |
|--------|----------|-------|-------------|
| V | Validation | V001-V099 | Input validation, schema violations |
| S | State | S001-S099 | State management, transitions |
| R | Resource | R001-R099 | Resource loading, missing assets |
| P | Persistence | P001-P099 | Save/load, file I/O |
| F | Formula | F001-F099 | Formula parsing, evaluation |
| C | Component | C001-C099 | Component operations |

### Common Error Codes

| Code | Name | Description |
|------|------|-------------|
| V001 | VALIDATION_FAILED | General validation failure |
| V002 | INVALID_COMPONENT | Component configuration invalid |
| V003 | MISSING_REQUIRED | Required field missing |
| S001 | STATE_FROZEN | Object frozen, cannot modify |
| S002 | NOT_INITIALIZED | Object not properly initialized |
| R001 | RESOURCE_NOT_FOUND | Resource doesn't exist |
| P001 | SAVE_FAILED | Failed to save data |
| P002 | LOAD_FAILED | Failed to load data |
| P003 | CORRUPT_DATA | Data corrupted or malformed |
| F001 | SYNTAX_ERROR | Formula syntax error |
| C001 | COMPONENT_NOT_FOUND | Component doesn't exist |

### Using Error Codes

```python
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

# Raising with error code
raise ValidationException(
    "Invalid damage value",
    code=ErrorCode.VALIDATION_FAILED.value,
    context={"field": "damage", "value": -5}
)

# Programmatic handling
try:
    load_component(data)
except ComponentException as e:
    if e.code == ErrorCode.INVALID_COMPONENT.value:
        # Handle specific error type
        use_default_component()
```

---

## Logging Levels

Use the appropriate logging level based on severity. All production code uses Python's standard logging:

```python
import logging
logger = logging.getLogger(__name__)
```

### logger.debug()
**Detailed diagnostic information for development and debugging.**

Use for:
- State transitions: `logger.debug(f"State changed from {old} to {new}")`
- Method entry with parameters: `logger.debug(f"scan_designs: pattern={pattern}")`
- Intermediate values during complex operations
- Expected failures that don't require attention

NOT for:
- Errors or failures (use `logger.error` or `logger.warning`)
- Information users need to see (use `logger.info`)

### logger.info()
**Notable events during normal operation.**

Use for:
- Successful initialization: `logger.info(f"Loaded {count} vehicle classes.")`
- Significant operations complete: `logger.info(f"Saved game to {filepath}")`
- System state changes: `logger.info("Battle simulation started")`

NOT for:
- Debugging details (use `logger.debug`)
- Problems or failures (use `logger.warning` or `logger.error`)

### logger.warning()
**Recoverable problems where operation continues with fallback.**

Use for:
- Missing optional resources: `logger.warning(f"Portrait not found, using default")`
- Recoverable failures: `logger.warning(f"Config load failed, using defaults: {e}")`
- Validation warnings: `logger.warning(f"Modifier validation failed, loading anyway")`
- Performance issues: `logger.warning(f"Slow frame: {elapsed}ms")`

NOT for:
- Fatal errors (use `logger.error`)
- Normal operation details (use `logger.info`)

### logger.error()
**Failures that prevent operation from completing.**

Use for:
- Required file not found: `logger.error(f"Asset manifest missing: {path}")`
- Critical operations failed: `logger.error(f"Failed to save game: {e}")`
- Data corruption: `logger.error(f"Invalid JSON in {filepath}: {e}")`
- Unexpected exceptions: `logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")`

NOT for:
- Recoverable issues (use `logger.warning`)
- Debug information (use `logger.debug`)

### log_event() (Event System)
**Structured simulation events for callbacks.**

Use for:
- Simulation events: `log_event("damage", ship_id=42, amount=100)`
- Turn events: `log_event("turn_start", turn=5)`
- Combat events: `log_event("weapon_fired", weapon_id="laser", target_id=12)`

This is NOT standard logging — events are typed callbacks used by test infrastructure and game session, separate from diagnostic logging.

```python
from game.core.event_logging import log_event
log_event("damage", ship_id=42, amount=100)
```

---

## Patterns to Follow

### Pattern 1: Catch Specific Exceptions

Always catch the most specific exception type possible.

```python
# GOOD: Catches only expected exceptions
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    log_warning(f"Invalid JSON: {e}")
    return default

# GOOD: Multiple specific types when needed
try:
    value = data[key]
    result = int(value)
except KeyError:
    log_debug(f"Key '{key}' not found, using default")
    return default
except ValueError as e:
    log_warning(f"Invalid integer value for '{key}': {e}")
    return default
```

### Pattern 2: Exception Chaining with `raise from`

Preserve the original cause when re-raising exceptions.

```python
# GOOD: Chains exceptions to preserve traceback
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
# GOOD: Logs the failure for debugging
try:
    result = parse_data(data)
except ValueError as e:
    logger.warning(f"Failed to parse data, using default: {e}")
    result = default_value
```

### Pattern 4: Include Context in Error Messages

Error messages should include enough context to diagnose the problem.

```python
# GOOD: Includes identifiers and context
logger.error(f"Failed to load design '{design_id}' from '{filepath}': {e}")

# GOOD: Uses context dict for structured data
raise ValidationException(
    "Component damage value out of range",
    code=ErrorCode.OUT_OF_RANGE.value,
    context={"component_id": comp_id, "damage": damage, "max": 100}
)
```

### Pattern 5: Graceful Degradation for Non-Critical Operations

For non-critical features, prefer graceful degradation over failure.

```python
# GOOD: Uses placeholder on failure
def get_image(self, category, key):
    try:
        return self._load_image(cache_key, file_path)
    except (FileNotFoundError, pygame.error) as e:
        logger.warning(f"Failed to load image {file_path}: {e}")
        return self.get_missing_texture()
```

### Pattern 6: Use Custom Exceptions for Domain Errors

Raise custom exceptions for domain-specific errors.

```python
# GOOD: Semantic exception type
if not ship.is_valid():
    raise ValidationException(
        f"Ship '{ship.name}' has invalid configuration",
        code=ErrorCode.VALIDATION_FAILED.value,
        context={"ship_id": ship.id, "errors": ship.validation_errors}
    )
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Bare `except:` Clauses

```python
# BAD: Catches everything including SystemExit, KeyboardInterrupt
try:
    do_something()
except:
    pass
```

### Anti-Pattern 2: Catching `Exception` Without Logging

```python
# BAD: Silent failure hides bugs
try:
    result = process(data)
except Exception:
    result = None
```

### Anti-Pattern 3: Using Generic `raise Exception()`

```python
# BAD: No semantic meaning
raise Exception("Something went wrong")

# GOOD: Semantic exception with context
raise ValidationException(
    "Invalid component configuration",
    code=ErrorCode.INVALID_COMPONENT.value,
    context={"component_id": comp_id}
)
```

### Anti-Pattern 4: Missing Exception Chaining

```python
# BAD: Loses original traceback
try:
    data = json.loads(content)
except json.JSONDecodeError:
    raise ValidationException("Invalid JSON")  # Original cause lost!

# GOOD: Preserves original cause
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    raise ValidationException("Invalid JSON") from e
```

### Anti-Pattern 5: Using `traceback.print_exc()`

```python
# BAD: Prints to stdout, not to logs
except Exception:
    traceback.print_exc()

# GOOD: Captures stack trace in logs
except Exception as e:
    log_error(f"Unexpected error: {e}\n{traceback.format_exc()}")
```

### Anti-Pattern 6: Custom Logger Classes or Singletons

```python
# BAD: Custom logger wrapper (legacy pattern, now deleted)
from game.core.logger import log_info, log_error  # DON'T

# GOOD: Standard library logging
import logging
logger = logging.getLogger(__name__)
logger.info("Message here")
```

### Anti-Pattern 7: Using print() for Diagnostics

```python
# BAD: Print statements for debugging
print(f"DEBUG: processing {item}")

# GOOD: Use proper logging
logger.debug(f"Processing {item}")
```

### Anti-Pattern 8: Direct JSON File I/O

```python
# BAD: Bypasses json_utils error handling
import json
with open("file.json") as f:
    data = json.load(f)

# GOOD: Use json_utils
from game.core.json_utils import load_json
data = load_json("file.json", default={})
```

### Anti-Pattern 9: Overly Broad Exception Handling

```python
# BAD: Catches too many exception types
try:
    file_path = Path(path)
    with open(file_path) as f:
        data = json.load(f)
        validate(data)
        process(data)
except Exception as e:
    log_error(f"Failed: {e}")

# GOOD: Specific handlers for each failure mode
try:
    file_path = Path(path)
    with open(file_path) as f:
        data = json.load(f)
except FileNotFoundError:
    log_warning(f"File not found: {path}")
    return default
except json.JSONDecodeError as e:
    log_error(f"Invalid JSON in {path}: {e}")
    return default

try:
    validate(data)
except ValidationException as e:
    log_error(f"Validation failed: {e}")
    return default
```

---

## Code Examples

### Example 1: Resource Loading (Reference: json_utils.py)

```python
def load_json(filepath: Path, default=None) -> Any:
    """Load JSON with proper error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug(f"JSON file not found: {filepath}")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return default
    except IOError as e:
        logger.error(f"Error reading {filepath}: {e}")
        return default
```

### Example 2: Validation with Custom Exceptions

```python
def validate_component(component_data: dict) -> None:
    """Validate component data, raising on errors."""
    if "id" not in component_data:
        raise ValidationException(
            "Component missing required 'id' field",
            code=ErrorCode.MISSING_REQUIRED.value,
            context={"component_data": component_data}
        )

    damage = component_data.get("damage", 0)
    if damage < 0 or damage > 100:
        raise ValidationException(
            f"Component damage {damage} out of range [0, 100]",
            code=ErrorCode.OUT_OF_RANGE.value,
            context={"damage": damage, "min": 0, "max": 100}
        )
```

### Example 3: Exception Chaining in Save/Load

```python
def load_save_file(path: Path) -> GameState:
    """Load a save file with proper exception chaining."""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise PersistenceException(
            f"Save file not found: {path}",
            code=ErrorCode.RESOURCE_NOT_FOUND.value,
            context={"path": str(path)}
        ) from e
    except json.JSONDecodeError as e:
        raise PersistenceException(
            f"Save file corrupted: {path}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={"path": str(path), "error": str(e)}
        ) from e

    try:
        return GameState.from_dict(data)
    except (KeyError, TypeError) as e:
        raise PersistenceException(
            f"Invalid save file format: {path}",
            code=ErrorCode.VERSION_MISMATCH.value,
            context={"path": str(path)}
        ) from e
```

### Example 4: Graceful Degradation with Fallback

```python
def get_ship_portrait(ship_id: str) -> Surface:
    """Get ship portrait with fallback to default."""
    try:
        return asset_manager.get_image("portraits", ship_id)
    except (FileNotFoundError, pygame.error) as e:
        logger.warning(f"Portrait not found for '{ship_id}', using default: {e}")
        return asset_manager.get_default_portrait()
```

### Example 5: AI Error Handling

```python
def evaluate_target(self, target: Ship) -> float:
    """Evaluate target with proper error handling."""
    if target is None:
        raise TargetingException(
            "Cannot evaluate None target",
            code=ErrorCode.VALIDATION_FAILED.value
        )

    try:
        threat_score = self._calculate_threat(target)
        value_score = self._calculate_value(target)
        return threat_score * 0.6 + value_score * 0.4
    except AttributeError as e:
        logger.warning(f"Target evaluation failed for {target.id}: {e}")
        return 0.0  # Safe fallback score
```

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

Is it about AI decisions?
  -> TargetingException (target selection)
  -> AIException (general AI errors)
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
    # Operation that may fail
    result = risky_operation()
except SpecificException as e:
    logger.warning(f"Operation failed: {e}")
    result = fallback_value
except AnotherException as e:
    # Re-raise with more context
    raise DomainException(
        f"Failed to complete operation: {e}",
        code=ErrorCode.RELEVANT_CODE.value,
        context={"relevant": "data"}
    ) from e
```

---

## See Also

- `game/core/exceptions.py` - Exception class definitions
- `game/core/error_codes.py` - Error code enumeration
- `game/core/json_utils.py` - Reference implementation
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Quick reference for error handling
