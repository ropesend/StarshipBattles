from game.core.logger import log_error


class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def emit(self, event_type, data=None):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    # Keep broad catch here - event handlers could raise anything
                    # but log properly with context
                    callback_name = getattr(callback, '__name__', repr(callback))
                    log_error(f"Error in event handler '{callback_name}' for {event_type}: {e}")
