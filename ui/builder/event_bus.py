"""Event bus for decoupled communication between UI components."""
from game.core.logger import log_error


class EventBus:
    """Simple publish/subscribe event bus with proper error handling."""

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        """Register a callback for an event type.

        Args:
            event_type: String identifier for the event
            callback: Function to call when event is emitted (receives data arg)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        """Remove a callback from an event type.

        Args:
            event_type: String identifier for the event
            callback: The callback function to remove
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def emit(self, event_type, data=None):
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
                except Exception as e:
                    log_error(f"Error in event handler for {event_type}: {e}")
