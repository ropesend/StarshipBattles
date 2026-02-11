import logging
import os
from typing import Any, Callable, Optional

from game.core.paths import Paths
from game.core.singleton import SingletonMeta


class Logger(metaclass=SingletonMeta):
    """Singleton logger for the game.

    Thread Safety:
        - Instance creation is thread-safe via SingletonMeta

    Usage:
        logger = Logger.instance()
        logger.info("message")

        # Or via convenience functions:
        from game.core.logger import log_info
        log_info("message")

    Testing:
        - Use reset() to destroy instance completely
    """

    def __init__(self):
        self.setup()

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
        
    def log(self, msg: str) -> None:
        if self.enabled:
            self.logger.debug(msg)

    def info(self, msg: str) -> None:
        if self.enabled:
            self.logger.info(msg)

    def warning(self, msg: str) -> None:
        if self.enabled:
            self.logger.warning(msg)

    def error(self, msg: str) -> None:
        if self.enabled:
            self.logger.error(msg)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

def log_debug(msg: str) -> None:
    """Log a debug message."""
    Logger.instance().log(msg)


def log_info(msg: str) -> None:
    """Log an info message."""
    Logger.instance().info(msg)


def log_warning(msg: str) -> None:
    """Log a warning message."""
    Logger.instance().warning(msg)


def log_error(msg: str) -> None:
    """Log an error message."""
    Logger.instance().error(msg)


def set_logging(enabled: bool) -> None:
    """Enable or disable logging."""
    Logger.instance().set_enabled(enabled)

# Event Logging for Simulation/Tests
_event_handler = None

def set_event_handler(handler: Optional[Callable[..., Any]]) -> None:
    """Register a callback for structured events."""
    global _event_handler
    _event_handler = handler

def log_event(event_type: str, **kwargs: Any) -> None:
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
        except Exception as e:  # Intentional broad catch: event handler isolation prevents handler bugs from crashing callers
            Logger.instance().error(f"Event handler error for {event_type}: {e}")
