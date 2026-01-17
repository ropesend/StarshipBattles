import time
import uuid
import threading
from functools import wraps
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

from game.core.json_utils import load_json, save_json
from game.core.logger import log_error, log_info


class Profiler:
    """
    Singleton profiler for performance measurement.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        profiler = Profiler.instance()
        profiler.start()
        with profile_block("my_operation"):
            do_something()

    Testing:
        - Use reset() to destroy instance completely
        - Use clear() to reset records but preserve instance
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if Profiler._instance is not None:
            raise Exception("Profiler is a singleton. Use Profiler.instance()")
        self.active = False
        self.session_id = str(uuid.uuid4())
        self.records: List[Dict] = []
        self.start_time = None
        log_info(f"Profiler initialized with session ID: {self.session_id}")

    @classmethod
    def instance(cls) -> 'Profiler':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton Profiler instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def clear(self):
        """Reset all records. Used for test isolation."""
        self.records = []
        self.session_id = str(uuid.uuid4())

    def start(self):
        """Enable profiling."""
        self.active = True
        self.start_time = time.time()
        log_info("Profiling started")

    def stop(self):
        """Disable profiling."""
        self.active = False
        log_info("Profiling stopped")

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
        # logger.debug(f"Profiled {name}: {duration*1000:.2f}ms")

    def save_history(self, filename: str = "profiling_history.json"):
        """Save current session to history file."""
        if not self.records:
            log_info("No records to save.")
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
            log_info(f"Saved {len(self.records)} records to {filename}")
        else:
            log_error(f"Failed to save profiling history to {filename}")

# Global accessor for backwards compatibility (lazy, not module-level instantiation)
class _ProfilerProxy:
    """Proxy that delegates to Profiler.instance() for lazy initialization."""

    def __getattr__(self, name):
        return getattr(Profiler.instance(), name)

    def __setattr__(self, name, value):
        setattr(Profiler.instance(), name, value)


PROFILER = _ProfilerProxy()


def profile_action(name: str):
    """Decorator to profile a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not PROFILER.is_active():
                return func(*args, **kwargs)
            
            t0 = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            finally:
                t1 = time.perf_counter()
                PROFILER.record(name, t1 - t0)
            return result
        return wrapper
    return decorator

@contextmanager
def profile_block(name: str):
    """Context manager to profile a block of code."""
    if not PROFILER.is_active():
        yield
        return
        
    t0 = time.perf_counter()
    try:
        yield
    finally:
        t1 = time.perf_counter()
        PROFILER.record(name, t1 - t0)
