"""Event bus for decoupled communication between UI components.

PROJ-382 Phase 2 (Pattern #10 / Pattern #6 naming hygiene): the workshop /
build-queue UI bus is named ``WorkshopEventBus`` to avoid colliding with
the canonical strategy-layer ``EventBus`` (``game/core/event_logging.py``).
The two buses serve different scopes; sharing the name made imports
ambiguous at code-review time.
"""
from __future__ import annotations

import logging

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)


class WorkshopEventBus:
    """Simple publish/subscribe event bus with proper error handling.

    Used by workshop / build-queue UI to coordinate between viewmodels,
    panels, and sidebars without hardcoded references between widgets.
    """

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback) -> None:
        """Register a callback for an event type.

        Args:
            event_type: String identifier for the event
            callback: Function to call when event is emitted (receives data arg)

        Raises:
            ValidationException: If callback is not callable
        """
        if not callable(callback):
            raise ValidationException(
                f"Callback must be callable, got {type(callback).__name__}",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"expected": "callable", "actual_type": type(callback).__name__}
            )
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback) -> None:
        """Remove a callback from an event type.

        Args:
            event_type: String identifier for the event
            callback: The callback function to remove
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def emit(self, event_type, data=None) -> None:
        """Emit an event to all subscribers.

        Args:
            event_type: String identifier for the event
            data: Optional data to pass to callbacks

        Note:
            Uses a defensive copy of the subscriber list to allow
            safe subscribe/unsubscribe during event handling.
        """
        if event_type in self._subscribers:
            # Defensive copy - allows handlers to modify subscriptions safely
            handlers = list(self._subscribers[event_type])
            for callback in handlers:
                try:
                    callback(data)
                except Exception as e:  # Intentional broad catch: event handler isolation prevents handler bugs from crashing callers
                    logger.error(f"Error in event handler for {event_type}: {e}")
