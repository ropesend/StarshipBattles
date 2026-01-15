"""
Combat Lab Logging Configuration

Provides centralized logging configuration for the Combat Lab test framework.
Uses Python's standard logging module with dual output:
- Console: INFO and above (user-facing messages)
- File: DEBUG and above (full diagnostic log)

Usage:
    from simulation_tests.logging_config import setup_combat_lab_logging, get_logger

    # Setup logging (call once at startup)
    setup_combat_lab_logging()

    # Get a module-specific logger
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message", exc_info=True)
"""

import logging
import sys
from pathlib import Path

# Track whether logging has been initialized
_logging_initialized = False


def setup_combat_lab_logging(log_file="combat_lab.log", console_level=logging.INFO):
    """
    Configure logging for Combat Lab test framework.

    Creates a logger with dual output:
    - Console handler: INFO and above (user-facing)
    - File handler: DEBUG and above (full diagnostics)

    Args:
        log_file: Path to log file (default: "combat_lab.log" in current directory)
        console_level: Minimum level for console output (default: logging.INFO)

    Returns:
        logging.Logger: The configured Combat Lab logger

    Note:
        This function is idempotent - calling it multiple times will not
        create duplicate handlers.
    """
    global _logging_initialized

    # Get or create the CombatLab logger
    logger = logging.getLogger("CombatLab")

    # If already initialized, return existing logger
    if _logging_initialized and logger.handlers:
        return logger

    # Set base level to DEBUG to capture everything
    logger.setLevel(logging.DEBUG)

    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False

    # Clear any existing handlers (in case of re-initialization)
    logger.handlers.clear()

    # Console handler (INFO and above by default)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    _logging_initialized = True

    logger.debug("Combat Lab logging initialized")
    logger.debug(f"Log file: {Path(log_file).absolute()}")
    logger.debug(f"Console level: {logging.getLevelName(console_level)}")

    return logger


def get_logger(name):
    """
    Get a module-specific logger under the CombatLab namespace.

    Args:
        name: Module name (typically __name__)

    Returns:
        logging.Logger: A logger instance for the specified module

    Example:
        logger = get_logger(__name__)
        logger.info("Module initialized")
    """
    # Ensure logging is initialized
    if not _logging_initialized:
        setup_combat_lab_logging()

    # Create hierarchical logger name
    # e.g., "CombatLab.test_framework.runner"
    if name.startswith("CombatLab."):
        logger_name = name
    else:
        logger_name = f"CombatLab.{name}"

    return logging.getLogger(logger_name)


def set_console_level(level):
    """
    Change the console output level for Combat Lab logger.

    Args:
        level: logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING)

    Example:
        # Enable verbose console output
        set_console_level(logging.DEBUG)

        # Quiet console output (warnings/errors only)
        set_console_level(logging.WARNING)
    """
    logger = logging.getLogger("CombatLab")
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(level)
            logger.debug(f"Console level changed to {logging.getLevelName(level)}")
            break


def set_module_level(module_name, level):
    """
    Set the log level for a specific module.

    Args:
        module_name: Module name (e.g., "test_framework.runner")
        level: logging level (e.g., logging.DEBUG, logging.WARNING)

    Example:
        # Suppress debug messages from runner module
        set_module_level("test_framework.runner", logging.INFO)
    """
    logger_name = f"CombatLab.{module_name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
