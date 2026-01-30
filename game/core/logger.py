import logging
import os
import threading

from game.core.paths import Paths


class Logger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    cls._instance = super(Logger, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.setup()

    @classmethod
    def reset(cls):
        """Reset the singleton instance for testing purposes."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._initialized = False
                cls._instance = None

    def setup(self):
        self.enabled = True
        self.logger = logging.getLogger("StarshipBattles")
        self.logger.setLevel(logging.DEBUG)

        # Ensure logs directory exists
        os.makedirs(os.path.dirname(Paths.BATTLE_LOG), exist_ok=True)
        fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
    def log(self, msg):
        if self.enabled:
            self.logger.debug(msg)
            
    def info(self, msg):
        if self.enabled:
            self.logger.info(msg)
            
    def warning(self, msg):
        if self.enabled:
            self.logger.warning(msg)

    def error(self, msg):
        if self.enabled:
            self.logger.error(msg)

    def set_enabled(self, enabled):
        self.enabled = enabled

# Global accessor
_logger = Logger()

def log_debug(msg):
    _logger.log(msg)

def log_info(msg):
    _logger.info(msg)

def log_warning(msg):
    _logger.warning(msg)

def log_error(msg):
    _logger.error(msg)
    
def set_logging(enabled):
    _logger.set_enabled(enabled)

# Event Logging for Simulation/Tests
_event_handler = None

def set_event_handler(handler):
    """Register a callback for structured events."""
    global _event_handler
    _event_handler = handler

def log_event(event_type, **kwargs):
    """Log a structured event if a handler is registered.

    Handler exceptions are caught and logged to prevent test or simulation
    code from crashing due to event handler bugs.

    Args:
        event_type: The type of event (e.g., "damage", "movement", "turn_start")
        **kwargs: Event-specific data to pass to the handler
    """
    if _event_handler:
        try:
            _event_handler(event_type, **kwargs)
        except Exception as e:
            # Log handler errors but don't propagate - handlers shouldn't crash callers
            _logger.error(f"Event handler error for {event_type}: {e}")
