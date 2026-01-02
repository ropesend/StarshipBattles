"""
Simulation-based component tests.

This package contains infrastructure for running full simulation tests
that validate component behavior through log-based verification.

Note: This is NOT a unittest module. Run simulation tests using:
    python tests/simulation/run_component_tests.py
"""
# Only export the non-importing modules
from .test_logger import (
    ComponentTestLogger,
    TestEventType,
    enable_test_logging,
    set_test_log_dir,
    TEST_LOGGING_ENABLED,
    TEST_LOG_DIR,
)
from .test_log_parser import TestLogParser, LogEvent

# The run_component_tests module should be imported directly when needed
# to avoid side-effect imports during unittest discovery

