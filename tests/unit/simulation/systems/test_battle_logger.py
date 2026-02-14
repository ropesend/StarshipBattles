"""Unit tests for BattleLogger.

BattleLogger is a toggleable logger that writes battle events to file.
It lives in game/simulation/systems/battle_engine.py.
"""
import pytest
import os
import warnings
from unittest.mock import patch, MagicMock

from game.core.paths import Paths
from game.simulation.systems.battle_engine import BattleLogger


class TestBattleLoggerInit:
    """Tests for BattleLogger initialization."""

    def test_init_defaults(self):
        """BattleLogger should use default filename and enabled=True."""
        logger = BattleLogger()
        expected_path = os.path.join(Paths.LOGS_DIR, "battle_log.txt")
        assert logger.filename == expected_path
        assert logger.enabled is True
        assert logger.file is None

    def test_init_custom_filename(self, tmp_path):
        """BattleLogger should accept custom filename."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(filename=test_file)
        assert logger.filename == test_file
        assert logger.enabled is True

    def test_init_disabled(self, tmp_path):
        """BattleLogger should accept enabled=False."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(filename=test_file, enabled=False)
        assert logger.enabled is False

    def test_init_filename_none_uses_default(self):
        """BattleLogger with filename=None should use default path."""
        logger = BattleLogger(filename=None)
        expected_path = os.path.join(Paths.LOGS_DIR, "battle_log.txt")
        assert logger.filename == expected_path


class TestBattleLoggerContextManager:
    """Tests for BattleLogger context manager protocol."""

    def test_context_manager_opens_and_closes(self, tmp_path):
        """BattleLogger should support context manager protocol."""
        test_file = str(tmp_path / "test.txt")
        with BattleLogger(test_file, enabled=True) as logger:
            assert logger.file is not None
            logger.log("Test message")
        # File should be closed after with block
        assert logger.file is None

    def test_context_manager_returns_self(self, tmp_path):
        """__enter__ should return the logger instance."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        result = logger.__enter__()
        assert result is logger
        logger.close()

    def test_context_manager_exit_returns_false(self, tmp_path):
        """__exit__ should return False to not suppress exceptions."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        result = logger.__exit__(None, None, None)
        assert result is False

    def test_context_manager_closes_on_exception(self, tmp_path):
        """File should be closed even if exception raised in context."""
        test_file = str(tmp_path / "test.txt")
        try:
            with BattleLogger(test_file, enabled=True) as logger:
                assert logger.file is not None
                raise ValueError("Test exception")
        except ValueError:
            pass
        assert logger.file is None


class TestBattleLoggerStartSession:
    """Tests for BattleLogger.start_session()."""

    def test_start_session_opens_file(self, tmp_path):
        """start_session should open file for enabled logger."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        assert logger.file is None
        logger.start_session()
        assert logger.file is not None
        logger.close()

    def test_start_session_creates_directory(self, tmp_path):
        """start_session should create log directory if needed."""
        nested_dir = tmp_path / "nested" / "logs"
        log_file = str(nested_dir / "test.txt")
        logger = BattleLogger(log_file, enabled=True)
        logger.start_session()
        assert nested_dir.exists()
        logger.close()

    def test_start_session_writes_header(self, tmp_path):
        """start_session should write battle log header."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.close()
        with open(test_file, 'r') as f:
            content = f.read()
        assert "=== BATTLE LOG STARTED ===" in content

    def test_start_session_closes_existing_file(self, tmp_path):
        """start_session should close any existing file first."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        first_file = logger.file
        logger.start_session()  # Start new session
        assert logger.file is not None
        assert logger.file is not first_file  # New file opened
        logger.close()

    def test_start_session_disabled_does_nothing(self, tmp_path):
        """start_session should not open file when disabled."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=False)
        logger.start_session()
        assert logger.file is None
        assert not os.path.exists(test_file)

    def test_start_session_io_error_disables_logger(self, tmp_path):
        """start_session should disable logger on IOError."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            logger.start_session()
        assert logger.enabled is False
        assert logger.file is None


class TestBattleLoggerLog:
    """Tests for BattleLogger.log()."""

    def test_log_writes_message(self, tmp_path):
        """log should write message to file."""
        test_file = str(tmp_path / "test.txt")
        with BattleLogger(test_file, enabled=True) as logger:
            logger.log("Test message 1")
            logger.log("Test message 2")
        with open(test_file, 'r') as f:
            content = f.read()
        assert "Test message 1" in content
        assert "Test message 2" in content

    def test_log_appends_newline(self, tmp_path):
        """log should append newline to each message."""
        test_file = str(tmp_path / "test.txt")
        with BattleLogger(test_file, enabled=True) as logger:
            logger.log("Line1")
            logger.log("Line2")
        with open(test_file, 'r') as f:
            lines = f.readlines()
        # Should have header, Line1\n, Line2\n, footer
        line1_found = any("Line1\n" in line for line in lines)
        line2_found = any("Line2\n" in line for line in lines)
        assert line1_found
        assert line2_found

    def test_log_disabled_does_nothing(self, tmp_path):
        """log should do nothing when logger is disabled."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=False)
        logger.start_session()
        logger.log("Should not appear")
        assert not os.path.exists(test_file)

    def test_log_no_file_does_nothing(self, tmp_path):
        """log should do nothing if file not opened."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        # Don't call start_session
        logger.log("Should not crash")  # Should not raise

    def test_log_io_error_handles_gracefully(self, tmp_path):
        """log should handle IOError gracefully."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.file.write = MagicMock(side_effect=IOError("Disk full"))
        # Should not raise
        logger.log("Test")
        logger.close()


class TestBattleLoggerClose:
    """Tests for BattleLogger.close()."""

    def test_close_sets_file_to_none(self, tmp_path):
        """close() should set file to None."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        assert logger.file is not None
        logger.close()
        assert logger.file is None

    def test_close_writes_footer(self, tmp_path):
        """close() should write battle log footer."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.close()
        with open(test_file, 'r') as f:
            content = f.read()
        assert "=== BATTLE LOG ENDED ===" in content

    def test_double_close_is_safe(self, tmp_path):
        """Calling close() twice should not raise errors."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.close()
        logger.close()  # Should not raise
        assert logger.file is None

    def test_close_no_file_is_safe(self, tmp_path):
        """close() with no open file should not raise."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        # Don't start session
        logger.close()  # Should not raise

    def test_close_io_error_handles_gracefully(self, tmp_path):
        """close() should handle IOError gracefully."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)
        logger.start_session()
        logger.file.close = MagicMock(side_effect=IOError("Device error"))
        # Should not raise, should still set file to None
        logger.close()
        assert logger.file is None


class TestBattleLoggerDestructor:
    """Tests for BattleLogger destructor behavior."""

    def test_destructor_closes_file(self, tmp_path):
        """BattleLogger destructor should close file without ResourceWarning."""
        test_file = str(tmp_path / "test.txt")
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


class TestBattleLoggerIntegration:
    """Integration tests for BattleLogger."""

    def test_full_logging_session(self, tmp_path):
        """Test complete logging session flow."""
        test_file = str(tmp_path / "test.txt")
        with BattleLogger(test_file, enabled=True) as logger:
            logger.log("Ship A fires at Ship B")
            logger.log("Damage: 50")
            logger.log("Ship B shields down")

        with open(test_file, 'r') as f:
            content = f.read()

        assert "=== BATTLE LOG STARTED ===" in content
        assert "Ship A fires at Ship B" in content
        assert "Damage: 50" in content
        assert "Ship B shields down" in content
        assert "=== BATTLE LOG ENDED ===" in content

    def test_multiple_sessions(self, tmp_path):
        """Multiple sessions should overwrite previous log."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=True)

        logger.start_session()
        logger.log("Session 1")
        logger.close()

        logger.start_session()
        logger.log("Session 2")
        logger.close()

        with open(test_file, 'r') as f:
            content = f.read()

        # Only session 2 content should remain (file overwritten)
        assert "Session 1" not in content
        assert "Session 2" in content

    def test_disabled_logger_does_not_open_file(self, tmp_path):
        """Disabled logger should not open any file."""
        test_file = str(tmp_path / "test.txt")
        logger = BattleLogger(test_file, enabled=False)
        logger.start_session()
        assert logger.file is None
        assert not os.path.exists(test_file)
