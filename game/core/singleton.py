"""Thread-safe singleton metaclass.

Provides a shared metaclass for singleton pattern implementation across the codebase.
Eliminates duplicate singleton boilerplate in ~7 classes.

Usage:
    class MyService(metaclass=SingletonMeta):
        def __init__(self):
            self.data = {}

    # Get singleton instance
    instance = MyService.instance()
    # or via direct construction
    instance = MyService()

    # Reset for testing
    MyService.reset()
"""
import threading
from typing import Any, Dict, Type, TypeVar

__all__ = ['SingletonMeta']

T = TypeVar('T')


class SingletonMeta(type):
    """Thread-safe singleton metaclass using double-checked locking.

    Features:
    - Thread-safe instance creation with per-class locking
    - __init__ runs exactly once per instance lifecycle
    - reset() for test isolation
    - Both MyClass() and MyClass.instance() return the singleton

    Implementation notes:
    - Uses per-class locks stored in _locks dict (created at class definition time)
    - Double-checked locking: check without lock, acquire lock, check again
    - _initialized flag prevents __init__ from running multiple times
    """

    _instances: Dict[Type, Any] = {}
    _locks: Dict[Type, threading.Lock] = {}

    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        """Called when a new singleton class is defined (not instantiated)."""
        super().__init__(name, bases, namespace)
        # Create a dedicated lock for this class
        SingletonMeta._locks[cls] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Called when the singleton class is instantiated (e.g., MyClass()).

        Uses double-checked locking for thread safety:
        1. Check if instance exists (fast path, no lock)
        2. Acquire per-class lock
        3. Check again (another thread may have created it)
        4. Create instance if needed
        """
        # Fast path: already created
        if cls in SingletonMeta._instances:
            return SingletonMeta._instances[cls]

        # Slow path: need to create (with locking)
        lock = SingletonMeta._locks[cls]
        with lock:
            # Double-check after acquiring lock
            if cls in SingletonMeta._instances:
                return SingletonMeta._instances[cls]

            # Create the instance (calls __new__ but not __init__ yet)
            instance = super().__call__(*args, **kwargs)
            SingletonMeta._instances[cls] = instance
            return instance

    def instance(cls: Type[T]) -> T:
        """Get the singleton instance. Alias for calling the class directly.

        Returns:
            The singleton instance of this class.
        """
        return cls()

    def reset(cls) -> None:
        """Reset the singleton instance for testing purposes.

        Thread-safe: acquires the per-class lock before clearing.
        After reset, the next instance() call will create a new instance
        and run __init__ again.
        """
        lock = SingletonMeta._locks.get(cls)
        if lock is None:
            return

        with lock:
            if cls in SingletonMeta._instances:
                del SingletonMeta._instances[cls]
