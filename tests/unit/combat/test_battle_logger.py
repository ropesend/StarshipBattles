"""Unit tests for BattleLogger resource management."""
import pytest
import os
import warnings

from game.core.paths import Paths
from game.simulation.systems.battle_engine import BattleLogger


@pytest.fixture
def test_file():
    """Provide test file path and clean up after test."""
    file_path = os.path.join(Paths.LOGS_DIR, "test_battle_log.txt")
    yield file_path
    # Clean up test files
    if os.path.exists(file_path):
        os.remove(file_path)


class TestBattleLogger:
    """Tests for BattleLogger file resource management."""

    def test_context_manager_opens_and_closes(self, test_file):
        """BattleLogger should support context manager protocol."""
        with BattleLogger(test_file, enabled=True) as logger:
            assert logger.file is not None
            logger.log("Test message")
        # File should be closed after with block
        assert logger.file is None

    def test_destructor_closes_file(self, test_file):
        """BattleLogger destructor should close file without ResourceWarning."""
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            logger = BattleLogger(test_file, enabled=True)
            logger.start_session()
            assert logger.file is not None
            del logger
            # Filter for ResourceWarning about unclosed file
            resource_warnings = [x for x in w if issubclass(x.category, ResourceWarning)]
            assert len(resource_warnings) == 0, \
                "BattleLogger should not leave unclosed file on deletion"

    def test_close_sets_file_to_none(self, test_file):
        """close() should set file to None."""
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        assert logger.file is not None
        logger.close()
        assert logger.file is None

    def test_double_close_is_safe(self, test_file):
        """Calling close() twice should not raise errors."""
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.close()
        logger.close()  # Should not raise
        assert logger.file is None

    def test_disabled_logger_does_not_open_file(self, test_file):
        """Disabled logger should not open any file."""
        logger = BattleLogger(test_file, enabled=False)
        logger.start_session()
        assert logger.file is None
        assert not os.path.exists(test_file)
