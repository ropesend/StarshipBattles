# Logger Analyst Report (Module Specialist)

## Summary
- Total issues found: 7
- Critical: 2, Major: 3, Minor: 2, Info: 0

## Findings

### CRITICAL: Import-Time Side Effects and File Handler Leaks
**ID:** LOG-001
**Location:** `game/core/logger.py:27-41`
**Issue:** `Logger.__init__()` calls `self.setup()` which immediately:
- Creates the logs directory on disk (`os.makedirs()` at line 36)
- Opens a `FileHandler` to `Paths.BATTLE_LOG` at line 37
- Adds the handler to Python's internal logger at line 41

This occurs on the **first import** or first call to `Logger.instance()`. In test environments:
- Unwanted file I/O during test collection
- Creation of files in output/ directories that may not exist
- Handlers are never closed → resource leaks
- Parallel tests may race on directory creation

**Impact:** Tests in headless/CI fail unexpectedly. File handles accumulate. `Paths.BATTLE_LOG` must be writable at import time.
**Recommendation:** Defer file handler creation to explicit initialization. Add cleanup on reset(). Make file logging optional.
**Effort:** Medium

---

### CRITICAL: Module-Level Global State Without Lifecycle Management
**ID:** LOG-002
**Location:** `game/core/logger.py:87-92`
**Issue:** The `_event_handler` global variable:
- Set via `set_event_handler(handler)` (lines 89-92)
- Never reset on `Logger.reset()` — requires separate cleanup
- Only reset in `conftest.py` via explicit `set_event_handler(None)` call

Dual state management: Logger singleton resets via metaclass, but global event handler must be reset independently.

**Impact:** Test pollution — handler from one test leaks into another. No guaranteed cleanup without external fixture.
**Recommendation:** Make `_event_handler` an instance variable, reset in Logger cleanup. Or document lifecycle tied to GameSession.
**Effort:** Medium

---

### MAJOR: No Resource Cleanup on Reset
**ID:** LOG-003
**Location:** `game/core/logger.py:9-41`
**Issue:** Logger has no cleanup logic. When `Logger.reset()` is called via SingletonMeta:
- FileHandler opened at line 37 is never closed
- Handler remains registered with Python's logger
- Subsequent `Logger.instance()` creates NEW instance but Python logger still has old handler
- After multiple resets, Python logger accumulates multiple FileHandlers

**Impact:** Resource leak (file handles), log duplication, memory leak, violates test isolation.
**Recommendation:** Store `fh` as instance variable. Add explicit `cleanup()` to close handler and remove from logger.
**Effort:** Simple

---

### MAJOR: File Handler Never Closed
**ID:** LOG-004
**Location:** `game/core/logger.py:37-41`
**Issue:** FileHandler is never stored as instance variable, never closed, never removed from logger. On Windows, open handles prevent file deletion.
**Impact:** File handle resource leak. Log file not flushed on crash. Descriptor exhaustion over many test runs.
**Recommendation:** Store handler as `self.fh`, add `cleanup()` method that calls `fh.close()` and `logger.removeHandler(fh)`.
**Effort:** Simple

---

### MAJOR: Event Handler Persists Across Test Boundaries
**ID:** LOG-005
**Location:** `game/core/logger.py:87-108`, `conftest.py:92-97`
**Issue:** The `_event_handler` global requires explicit cleanup in conftest.py:
```python
from game.core.logger import set_event_handler
set_event_handler(None)  # EXPLICIT CLEANUP REQUIRED
```
This flags that the pattern is broken — proper isolation would auto-reset.
**Impact:** Test interference. Fragile fixture-order-dependent cleanup.
**Recommendation:** Make event handler instance-scoped (see LOG-002).
**Effort:** Medium

---

### MINOR: Custom Logger Adds Thin Wrapper, Minimal Value Over Standard Logging
**ID:** LOG-006
**Location:** `game/core/logger.py:43-84`
**Issue:** Feature comparison:

| Feature | Custom Logger | Standard logging |
|---------|---------------|-----------------|
| Log levels | Yes (explicit check) | Yes (via setLevel) |
| File output | Yes (hardcoded) | Yes (via handler config) |
| Enable/disable | Yes (enabled flag) | Yes (setLevel/NullHandler) |
| Formatting | Yes (standard format) | Yes (via Formatter) |
| Module-level functions | Yes | No (must use getLogger) |
| Thread safety | Yes (SingletonMeta) | Yes (stdlib is thread-safe) |
| Event handler system | Yes (log_event) | No |

**Only unique feature:** Global event handler system (`log_event()`/`set_event_handler()`).
**Impact:** 114 files coupled to custom API that adds minimal value over stdlib.
**Recommendation:** Migrate to standard logging. Keep only event handler system (move to separate `game/core/event_logging.py`).
**Effort:** Info (architectural decision)

---

### MINOR: Insufficient Error Handling in Event Handler
**ID:** LOG-007
**Location:** `game/core/logger.py:104-108`
**Issue:** Event handler exception catch logs only string message, not full traceback. If Logger.instance() itself fails, can't log the handler error. Recursive failure possible.
**Impact:** Debug difficulty from lost tracebacks.
**Recommendation:** Log `traceback.format_exc()` and add stderr fallback.
**Effort:** Simple

---

## Synthesis: Value Proposition

**The custom Logger provides:**
1. Event handler system (`log_event()`/`set_event_handler()`) — UNIQUE
2. Global convenience functions (`log_info()`, etc.) — convenience only
3. Enabled/disabled toggle — standard logging can do this
4. Singleton pattern — standard logging is already global

**The custom Logger has critical flaws:**
1. Import-time side effects (creates files on disk)
2. Resource leaks (file handlers never closed)
3. Broken test isolation (global _event_handler state)
4. Unclear lifecycle (reset() doesn't reset event handler)

**Recommendation:** Migrate to standard `logging.getLogger(__name__)`. Keep ONLY the event handler system in a separate module (`game/core/event_logging.py`). The custom Logger is not justified for its 114-file coupling footprint given it adds only the event system over stdlib.
