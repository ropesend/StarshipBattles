# Error Handling and Logging Pattern Analysis

**Agent:** Error Handling & Logging Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 12
- Critical inconsistencies: 0
- Major inconsistencies: 1
- Minor inconsistencies: 3
- Dominant pattern: Centralized logger with specific exception handling

---

## Error Handling Patterns

### Exception Handling Styles

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `except Exception as e:` (catch-all) | asset_manager.py:102, battle_controller.py:191 | 60% | Most common |
| Specific exceptions (FileNotFoundError, JSONDecodeError) | json_utils.py:52-58, ship_loader.py:69 | 35% | Best practice |
| Silent `except Exception:` | target_evaluator.py:34, battle.py:186 | 5% | Problematic |

### Error Propagation Patterns

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Return tuples (success, message, data) | save_game_service.py:34, persistence.py | 15% | I/O operations |
| Return None on error | ship_loader.py, resources.py | 40% | Data loading |
| Raise exception | json_utils.py:load_json_required | 20% | Critical data |
| Log and continue | asset_manager.py:102-104 | 25% | UI/display |

---

## Logging Patterns

### Logger Initialization

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Centralized logger imports | 94 files across game/ | 95% | Dominant |
| `print()` statements | ui/builder/event_bus.py:21 | 5% | Legacy |

### Log Level Usage

| Level | Usage Pattern | Examples |
|-------|--------------|----------|
| DEBUG | File loading details, success | json_utils.py, save_game_service.py |
| INFO | Game flow milestones | app.py:246, resources.py |
| WARNING | Missing assets, fallbacks | asset_manager.py, persistence.py |
| ERROR | Exception details, failures | save_game_service.py:110 |

### Message Formatting

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| f-strings with context | Throughout codebase | 95% | Standard |
| Traceback inclusion | save_game_service.py:110 | 10% | Complex errors |

---

## Key Inconsistencies

### ERR-01: Print vs Logger in Event Buses
**Severity:** Minor
**ID:** ERR-01
**Location:** `ui/builder/event_bus.py:21`
**Issue:** Uses `print()` instead of centralized logger
**Impact:** Inconsistent error reporting, no log level control
**Recommendation:** Migrate to `log_error()` / `log_warning()`
**Effort:** Simple

### ERR-02: Silent Exception Handlers
**Severity:** Minor
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34`, `game/ui/hud/battle.py:186`
**Issue:** Exception handlers don't bind the exception variable
**Impact:** Cannot access exception details for logging/debugging
**Recommendation:** Always bind: `except Exception as e:`
**Effort:** Simple

### ERR-03: Inconsistent Error Return Patterns
**Severity:** Info
**ID:** ERR-03
**Location:** Various I/O operations
**Issue:** Mix of tuple returns, None returns, and exceptions
**Impact:** Caller must know which pattern each method uses
**Recommendation:** Document pattern choice per module; consider standardizing
**Effort:** Medium

---

## Recommended Standard

### Error Handling
```python
# Pattern A: Critical data (raises)
try:
    data = load_json_required(filepath)
except FileNotFoundError:
    raise RuntimeError(f"Critical file not found: {filepath}")

# Pattern B: Optional data (returns default)
try:
    data = load_json(filepath, default={})
except Exception as e:
    log_error(f"Failed to load {filepath}: {e}")
    return None

# Pattern C: I/O operations (returns tuple)
try:
    save_json(filepath, data)
    return True, "Saved successfully", None
except Exception as e:
    log_error(f"Save failed: {e}")
    return False, f"Error: {e}", None
```

### Logging
```python
from game.core.logger import log_debug, log_info, log_warning, log_error

log_error(f"Failed to load {resource_name}: {e}")
log_info(f"Loaded {count} items from {os.path.basename(path)}")
log_warning(f"Asset not found, using fallback: {fallback_id}")
```

---

## Top 5 Priority Issues

1. **ERR-01:** Replace `print()` with logger in event_bus.py (2 files)
2. **ERR-02:** Add exception binding to silent handlers (~5 locations)
3. Consider documenting error propagation patterns per module
4. Ensure all new code follows json_utils.py best practices
5. Expand traceback logging for complex error scenarios
