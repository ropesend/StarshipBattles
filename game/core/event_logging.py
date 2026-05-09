"""Event logging system for structured simulation events.

Provides structured event callbacks used by simulation and test infrastructure.
Separate from standard logging — events are typed callbacks, not log messages.

This is NOT standard diagnostic logging. For diagnostic logging, use:
    import logging
    logger = logging.getLogger(__name__)

Events are typed callback invocations for simulation observers (e.g., tests,
replay systems, analytics). They carry structured data, not free-form messages.

Usage (PROJ-390): every event source takes an injected ``EventBus`` instance.
``GameSession`` constructs the bus and threads it through to engines, handlers,
and data classes that need to emit events::

    bus = EventBus(my_handler)              # owned by GameSession
    engine = SomeEngine(event_bus=bus)      # constructor injection
    engine.do_thing()                       # emits via bus.log_event(...)

Lifecycle:
    - Each ``GameSession`` creates its own ``EventBus`` (session-scoped).
    - Test fixtures create their own ``EventBus`` directly when needed.
    - Buses with no handler silently drop events.
    - Handler exceptions are caught and logged to prevent simulation crashes.

History:
    PROJ-252 introduced the session-scoped ``EventBus`` class.
    PROJ-382 migrated the bulk of producers to constructor-injected event_bus.
    PROJ-390 retired the module-level ``log_event`` / ``set_event_handler`` /
    ``get_event_handler`` compatibility shim — only the ``EventBus`` class
    remains.
"""
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class EventBus:
    """Session-scoped event bus for structured simulation events (PROJ-252).

    Each GameSession creates its own EventBus instance. Events are routed
    to the bus's handler without relying on module-level global state.
    """

    def __init__(self, handler: Optional[Callable[..., Any]] = None):
        self._handler = handler

    def set_handler(self, handler: Optional[Callable[..., Any]]) -> None:
        """Replace the handler on this bus."""
        self._handler = handler

    def log_event(self, event_type: str, **kwargs: Any) -> None:
        """Fire a structured event through this bus's handler."""
        if self._handler is None:
            return
        try:
            self._handler(event_type, **kwargs)
        except Exception:  # Intentional broad catch: third-party event handler may raise anything; instrumentation must never crash the simulation
            logger.exception(f"Event handler error for {event_type}")
