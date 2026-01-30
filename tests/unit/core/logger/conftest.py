"""Shared fixtures for logger tests."""
import pytest


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger state before and after each test."""
    from game.core.logger import Logger, set_logging, set_event_handler

    # Reset to clean state
    Logger.reset()
    set_logging(True)
    set_event_handler(None)

    yield

    # Cleanup after test
    Logger.reset()
    set_logging(True)
    set_event_handler(None)


@pytest.fixture
def fresh_logger():
    """Get a freshly initialized logger instance."""
    from game.core.logger import Logger
    Logger.reset()
    return Logger()
