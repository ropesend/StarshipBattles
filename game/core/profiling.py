import logging
import time
import uuid
from functools import wraps
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

from game.core.json_utils import load_json, save_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)

# Module-level Profiler reference (PROJ-258)
_default_profiler: Optional['Profiler'] = None


class Profiler:
    """Profiler for performance measurement.

    PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext.

    Usage:
        profiler = ctx.profiler  # Via ApplicationContext
        profiler.start()
        with profile_block("my_operation"):
            do_something()
    """

    def __init__(self):
        self.active = False
        self.session_id = str(uuid.uuid4())
        self.records: List[Dict] = []
        self.start_time = None
        logger.info(f"Profiler initialized with session ID: {self.session_id}")

    @classmethod
    def instance(cls) -> 'Profiler':
        """PROJ-258 compatibility shim — returns module-level Profiler."""
        global _default_profiler
        if _default_profiler is None:
            _default_profiler = cls()
        return _default_profiler

    @classmethod
    def reset(cls) -> None:
        """PROJ-258 compatibility shim — replaces module-level Profiler."""
        global _default_profiler
        _default_profiler = cls()

    def clear(self):
        """Reset all records. Used for test isolation."""
        self.records = []
        self.session_id = str(uuid.uuid4())

    def start(self):
        """Enable profiling."""
        self.active = True
        self.start_time = time.time()
        logger.info("Profiling started")

    def stop(self):
        """Disable profiling."""
        self.active = False
        logger.info("Profiling stopped")

    def toggle(self):
        """Toggle profiling state."""
        if self.active:
            self.stop()
        else:
            self.start()
        return self.active
    
    def is_active(self):
        return self.active

    def record(self, name: str, duration: float, metadata: Optional[Dict] = None):
        """Record a profiled action."""
        if not self.active:
            return

        entry = {
            "name": name,
            "duration_ms": duration * 1000.0,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.records.append(entry)

    def save_history(self, filename: str = None):
        """Save current session to history file."""
        if filename is None:
            filename = Paths.PROFILING_HISTORY
        if not self.records:
            logger.info("No records to save.")
            return

        # Load existing history using json_utils
        history = load_json(filename, default=[])

        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "records": self.records
        }

        history.append(session_data)

        # Save using json_utils
        if save_json(filename, history):
            logger.info(f"Saved {len(self.records)} records to {filename}")
        else:
            logger.error(f"Failed to save profiling history to {filename}")

# Module-level decorators and context managers for convenient profiling
def profile_action(name: str):
    """Decorator to profile a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = Profiler.instance()
            if not profiler.is_active():
                return func(*args, **kwargs)

            t0 = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            finally:
                t1 = time.perf_counter()
                profiler.record(name, t1 - t0)
            return result
        return wrapper
    return decorator


@contextmanager
def profile_block(name: str):
    """Context manager to profile a block of code."""
    profiler = Profiler.instance()
    if not profiler.is_active():
        yield
        return

    t0 = time.perf_counter()
    try:
        yield
    finally:
        t1 = time.perf_counter()
        profiler.record(name, t1 - t0)
