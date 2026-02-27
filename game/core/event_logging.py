"""Event logging system for structured simulation events.

Provides structured event callbacks used by simulation and test infrastructure.
Separate from standard logging — events are typed callbacks, not log messages.

This is NOT standard diagnostic logging. For diagnostic logging, use:
    import logging
    logger = logging.getLogger(__name__)

Events are typed callback invocations for simulation observers (e.g., tests,
replay systems, analytics). They carry structured data, not free-form messages.

Usage:
    from game.core.event_logging import log_event, set_event_handler

    # Register handler (typically in GameSession or test fixtures)
    set_event_handler(my_handler)

    # Fire events (from simulation code)
    log_event("damage", ship_id=42, amount=100)

Lifecycle:
    - Handler is set by GameSession during game startup
    - Handler is cleared (set to None) in test fixtures via conftest.py
    - When no handler is registered, log_event() is a no-op
    - Handler exceptions are caught and logged to prevent simulation crashes
"""
import logging
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
