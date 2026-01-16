import logging
import sys

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.setup()
        return cls._instance
    
    def setup(self):
        self.enabled = True
        self.logger = logging.getLogger("StarshipBattles")
        self.logger.setLevel(logging.DEBUG)
        
        # File Handler (Instead of Console)
        # ch = logging.StreamHandler(sys.stdout)
        fh = logging.FileHandler('battle.log', mode='w')
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
    """Log a structured event if a handler is registered."""
    if _event_handler:
        _event_handler(event_type, **kwargs)
