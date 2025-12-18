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
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        # File Handler? optional
        
    def log(self, msg):
        if self.enabled:
            self.logger.debug(msg)
            
    def info(self, msg):
        if self.enabled:
            self.logger.info(msg)
            
    def error(self, msg):
        self.logger.error(msg)
        
    def set_enabled(self, enabled):
        self.enabled = enabled

# Global accessor
_logger = Logger()

def log_debug(msg):
    _logger.log(msg)

def log_info(msg):
    _logger.info(msg)
    
def log_error(msg):
    _logger.error(msg)
    
def set_logging(enabled):
    _logger.set_enabled(enabled)
