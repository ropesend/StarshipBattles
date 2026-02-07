# Error Handling Guidelines

This document establishes the error handling conventions and logging standards for the Starship Battles codebase.

> **See Also:** [ERROR_HANDLING_GUIDELINES.md](ERROR_HANDLING_GUIDELINES.md) for the comprehensive guide including:
> - Custom exception hierarchy (`game/core/exceptions.py`)
> - Error codes (`game/core/error_codes.py`)
> - Code examples and anti-patterns

## Logging Levels

### log_debug()
Use for information useful during development and debugging that is not needed in normal operation.

**Appropriate uses:**
- State transitions: `log_debug(f"State changed from {old} to {new}")`
- Method entry with parameters: `log_debug(f"scan_designs: Scanning pattern: {pattern}")`
- Intermediate values during complex operations
- UI interactions during testing: `log_debug("Design button clicked")`

**Not appropriate for:**
- Errors or failures (use log_error or log_warning)
- Information users need to see (use log_info)
- Normal operation confirmations (use log_info)

### log_info()
Use for notable events during normal operation that confirm the system is working correctly.

**Appropriate uses:**
- Successful initialization: `log_info(f"Loaded {len(classes)} vehicle classes.")`
- Significant operations complete: `log_info(f"Saved JSON to {filepath}")`
- System state changes: `log_info("Research tree layout complete")`

**Not appropriate for:**
- Debugging details (use log_debug)
- Problems or failures (use log_warning or log_error)

### log_warning()
Use for recoverable problems where operation continues but with degraded functionality or fallback behavior.

**Appropriate uses:**
- Missing optional resources: `log_warning(f"Resources file not found at {filepath}, using defaults")`
- Recoverable failures with fallback: `log_warning(f"Failed to load portrait, using placeholder: {e}")`
- Validation warnings: `log_warning(f"Modifier '{mod_id}' failed schema validation, loading anyway")`
- Performance issues: `log_warning(f"Slow Frame: {ticks} ticks took {elapsed}ms")`

**Not appropriate for:**
- Fatal errors (use log_error)
- Normal operation details (use log_info or log_debug)

### log_error()
Use for failures that prevent an operation from completing successfully.

**Appropriate uses:**
- Required file not found: `log_error(f"Asset Manifest not found: {path}")`
- Critical operations failed: `log_error(f"Failed to save game: {e}")`
- Data corruption: `log_error(f"Invalid JSON in {filepath}: {e}")`
- Unexpected exceptions: `log_error(f"Unexpected error: {e}\n{traceback.format_exc()}")`

**Not appropriate for:**
- Recoverable issues with fallback (use log_warning)
- Debug information (use log_debug)

## Exception Handling Patterns

### Pattern 1: Catch Specific Exceptions
Always catch the most specific exception type possible.

```python
# Bad - catches everything including SystemExit and KeyboardInterrupt
try:
    do_something()
except:
    pass

# Good - catches only expected exceptions
try:
    do_something()
except (ValueError, KeyError) as e:
    log_warning(f"Operation failed: {e}")
```

### Pattern 2: Always Log Exceptions
Never silently swallow exceptions. At minimum, log a warning.

```python
# Bad - silent failure hides bugs
try:
    result = parse_data(data)
except Exception:
    result = default_value

# Good - logs the failure for debugging
try:
    result = parse_data(data)
except Exception as e:
    log_warning(f"Failed to parse data, using default: {e}")
    result = default_value
```

### Pattern 3: Include Context in Error Messages
Error messages should include enough context to diagnose the problem without debugging.

```python
# Bad - no context for debugging
log_error("Failed to load design")

# Good - includes identifiers and paths
log_error(f"Failed to load design '{design_id}' from '{filepath}': {e}")
```

### Pattern 4: Use traceback.format_exc() for Stack Traces
Never use `traceback.print_exc()` in production code. Always use the logger.

```python
# Bad - prints to stdout, not to logs
except Exception:
    traceback.print_exc()

# Good - captures stack trace in logs
except Exception as e:
    import traceback
    log_error(f"Unexpected error: {e}\n{traceback.format_exc()}")
```

### Pattern 5: Use Exception Variable or Remove It
If you catch an exception, either log it or use `except ExceptionType:` without the variable.

```python
# Bad - captures exception but ignores it
except Exception as e:
    return None

# Good - logs the exception
except Exception as e:
    log_warning(f"Operation failed: {e}")
    return None

# Also good - doesn't capture unused variable
except Exception:
    return None
```

### Pattern 6: User-Friendly Error Messages
External-facing error messages should be helpful without exposing internal details.

```python
# Bad - exposes internal exception details
return None, f"KeyError: 'config' not found in game_state"

# Good - user-friendly message, log has details
log_error(f"Failed to reconstruct game session: {e}")
return None, "Save file corrupted: Failed to reconstruct game state"
```

## Breadcrumb Logging for Complex Operations

For multi-step operations, log breadcrumbs before each step to aid debugging:

```python
def complex_operation(self, data):
    log_debug(f"complex_operation: starting with {len(data)} items")

    log_debug("Step 1: Validating data...")
    if not self._validate(data):
        log_warning("Validation failed, aborting")
        return None

    log_debug("Step 2: Processing items...")
    processed = self._process(data)

    log_debug("Step 3: Saving results...")
    self._save(processed)

    log_info(f"complex_operation: completed successfully ({len(processed)} items)")
    return processed
```

## Exception Documentation

Document exceptions in docstrings for public methods:

```python
def load_design(self, design_id: str) -> Optional[Ship]:
    """Load a ship design from disk.

    Args:
        design_id: The unique identifier for the design

    Returns:
        The loaded Ship, or None if loading fails

    Raises:
        ValueError: If design_id is empty or invalid
        FileNotFoundError: If design file doesn't exist
    """
```

## Graceful Degradation

For non-critical features, prefer graceful degradation over failure:

```python
# Asset loading - use placeholder if asset missing
def get_image(self, category, key):
    try:
        return self._load_image(cache_key, file_path)
    except Exception as e:
        log_warning(f"Failed to load image {file_path}: {e}")
        return self.get_missing_texture()  # Returns placeholder
```

## Summary Table

| Level | When to Use | Examples |
|-------|-------------|----------|
| DEBUG | Development/debugging info | State changes, method params, intermediate values |
| INFO | Normal operation confirmation | Initialization complete, files saved |
| WARNING | Recoverable problems | Missing optional files, fallback used, slow performance |
| ERROR | Operation failures | Required files missing, save failed, data corrupted |
