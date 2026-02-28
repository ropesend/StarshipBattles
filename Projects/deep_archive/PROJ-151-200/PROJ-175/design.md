# PROJ-175 Design: Logger & JSON Loading Pattern Standardization

## Logger Architecture

### Current State (game/core/logger.py, 109 lines)

```python
class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.setup()  # PROBLEM: import-time side effects

    def setup(self):
        self.enabled = True
        self.logger = logging.getLogger("StarshipBattles")
        self.logger.setLevel(logging.DEBUG)
        os.makedirs(os.path.dirname(Paths.BATTLE_LOG), exist_ok=True)  # Creates dirs!
        fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')  # Creates file!
        # ... handler never stored, never closed
```

**Problems (from consistency review):**
1. `__init__` calls `setup()` → creates file handlers on import (LOG-001)
2. FileHandler never stored → never closed, resource leak (LOG-003, LOG-004)
3. Module-level `_event_handler` global → persists across tests (LOG-002, LOG-005)
4. SingletonMeta + module globals = dual state management
5. Only unique feature: event handler system (~25 lines of value) (LOG-006)
6. 114 files coupled to thin non-standard wrapper (LC-001)

### Target State: Standard Logging + Event Module

**Delete** `game/core/logger.py` entirely.

**Create** `game/core/event_logging.py` (~40 lines):
```python
"""Event logging system for structured simulation events.

Provides structured event callbacks used by simulation and test infrastructure.
Separate from standard logging — events are typed callbacks, not log messages.

Usage:
    from game.core.event_logging import log_event, set_event_handler

    # Register handler (typically in GameSession or test fixtures)
    set_event_handler(my_handler)

    # Fire events (from simulation code)
    log_event("damage", ship_id=42, amount=100)
"""
import logging
import sys
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

_event_handler: Optional[Callable[..., Any]] = None


def set_event_handler(handler: Optional[Callable[..., Any]]) -> None:
    """Register a callback for structured events."""
    global _event_handler
    _event_handler = handler


def get_event_handler() -> Optional[Callable[..., Any]]:
    """Get the current event handler (for testing/introspection)."""
    return _event_handler


def log_event(event_type: str, **kwargs: Any) -> None:
    """Fire a structured event through the registered handler.

    Handler exceptions are caught and logged to prevent simulation code
    from crashing due to event handler bugs.
    """
    if _event_handler is None:
        return
    try:
        _event_handler(event_type, **kwargs)
    except Exception:
        logger.exception(f"Event handler error for {event_type}")
```

**Configure root logger** in `game/app.py`:
```python
import logging
import os
from game.core.paths import Paths

def configure_logging():
    """Set up application logging. Called once at app startup."""
    os.makedirs(os.path.dirname(Paths.BATTLE_LOG), exist_ok=True)

    root_logger = logging.getLogger("game")
    root_logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)
```

**Configure test logging** in `conftest.py`:
```python
import logging

@pytest.fixture(autouse=True, scope="session")
def configure_test_logging():
    """Set up logging for tests — NullHandler to suppress file I/O."""
    logging.getLogger("game").addHandler(logging.NullHandler())

@pytest.fixture(autouse=True)
def reset_event_handler():
    """Clear event handler between tests."""
    from game.core.event_logging import set_event_handler
    yield
    set_event_handler(None)
```

### Per-File Migration Pattern

Every file currently importing from `game.core.logger` gets the same mechanical transformation:

```python
# BEFORE
from game.core.logger import log_info, log_error, log_warning, log_debug

log_info("Game started")
log_error(f"Failed to load: {path}")
log_warning("Using fallback config")
log_debug(f"Cache hit for {key}")

# AFTER
import logging

logger = logging.getLogger(__name__)

logger.info("Game started")
logger.error(f"Failed to load: {path}")
logger.warning("Using fallback config")
logger.debug(f"Cache hit for {key}")
```

For files that also use event functions:
```python
# BEFORE
from game.core.logger import log_info, log_event, set_event_handler

# AFTER
import logging
from game.core.event_logging import log_event, set_event_handler

logger = logging.getLogger(__name__)
```

### Files Using `set_logging(enabled)` Pattern

Search for `set_logging` calls and replace with:
```python
# BEFORE
from game.core.logger import set_logging
set_logging(False)

# AFTER
import logging
logging.getLogger("game").setLevel(logging.CRITICAL)  # Effectively disable
```

---

## JSON Loading Architecture

### Current State

`game/core/json_utils.py` provides `load_json()`, `save_json()`, `load_json_required()` with proper error handling. **95% adoption** — only 3 file I/O calls bypass it.

### Migration Plan

| File | Current | Target | Difficulty |
|------|---------|--------|-----------|
| `game/ui/screens/formation_editor.py` | `json.dump(data, f)` / `json.load(f)` | `save_json(path, data)` / `load_json(path)` | Easy |
| `game/ui/screens/builder/stats_config.py` | `json.load(f)` | `load_json(path, default={})` | Easy |
| `game/strategy/systems/save_game_service.py` | `import json` (exception only) | `from json import JSONDecodeError` | Trivial |
| `game/strategy/systems/design_library.py` | `import json` (exception only) | `from json import JSONDecodeError` | Trivial |
| `game/ui/screens/workshop_data_loader.py` | Direct json I/O in orchestration | Migrate I/O calls to json_utils | Medium |

### json_utils Error Handling Tightening (MOD-CORE-015)

Current `IOError` catch is broad. Tighten to specific exceptions:
```python
except FileNotFoundError:
    log_debug(f"JSON file not found: {file_path}")
    return default
except PermissionError as e:
    log_error(f"Permission denied reading {file_path}: {e}")
    return default
except json.JSONDecodeError as e:
    log_error(f"Invalid JSON in {file_path}: {e}")
    return default
except OSError as e:
    log_error(f"OS error reading {file_path}: {e}")
    return default
```

Note: `json_utils.py` will be migrated to use `logging.getLogger(__name__)` in Phase 2 as part of the core module migration.

### Loader Classes (PC-015)

Per the Loader Class Analyst: 9 of 11 JSON loaders already use `json_utils`. A `BaseJSONLoader` is **not warranted** — loaders vary too much in post-processing. WorkshopDataLoader should simply use `json_utils` for its file I/O.

---

## Logging Level Guidelines

Add to `docs/ERROR_HANDLING_GUIDELINES.md`:

| Level | When to Use | Examples |
|-------|-------------|---------|
| `logger.error()` | Unrecoverable failures, data corruption | Failed to save game, missing critical data file |
| `logger.warning()` | Recoverable issues, degraded behavior | Fallback to default config, deprecated API usage |
| `logger.info()` | Normal operations worth recording | Game started, battle ended, save completed |
| `logger.debug()` | Detailed diagnostic info | File loaded, cache hit/miss, calculation details |
| `log_event()` | Structured simulation events for test/replay | Damage dealt, movement completed, turn started |

---

## Module Migration Order

| Order | Module | Files | Logger Calls | Phase |
|-------|--------|-------|-------------|-------|
| 1 | core/ | 6 | ~20 | 2 (foundation — json_utils depends on logger) |
| 2 | simulation/ | 16 | ~100 | 2 (core simulation) |
| 3 | strategy/ | 38 | ~250 | 3 (largest group) |
| 4 | ai/ | 4 | ~5 | 3 (includes dual-usage cleanup) |
| 5 | ui/ | 43 | ~400 | 3 (largest call count) |
| 6 | other (app, assets, research) | 7 | ~55 | 3 |
