"""Unit tests for BattleLogger resource management."""
import unittest
import os
import sys
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.systems.battle_engine import BattleLogger


class TestBattleLogger(unittest.TestCase):
    """Tests for BattleLogger file resource management."""
    
    def setUp(self):
        self.test_file = "test_battle_log.txt"
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_context_manager_opens_and_closes(self):
        """BattleLogger should support context manager protocol."""
        with BattleLogger(self.test_file, enabled=True) as logger:
            self.assertIsNotNone(logger.file)
            logger.log("Test message")
        # File should be closed after with block
        self.assertIsNone(logger.file)
    
    def test_destructor_closes_file(self):
        """BattleLogger destructor should close file without ResourceWarning."""
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            logger = BattleLogger(self.test_file, enabled=True)
            logger.start_session()
            self.assertIsNotNone(logger.file)
            del logger
            # Filter for ResourceWarning about unclosed file
            resource_warnings = [x for x in w if issubclass(x.category, ResourceWarning)]
            self.assertEqual(len(resource_warnings), 0, 
                "BattleLogger should not leave unclosed file on deletion")
    
    def test_close_sets_file_to_none(self):
        """close() should set file to None."""
        logger = BattleLogger(self.test_file, enabled=True)
        logger.start_session()
        self.assertIsNotNone(logger.file)
        logger.close()
        self.assertIsNone(logger.file)
    
    def test_double_close_is_safe(self):
        """Calling close() twice should not raise errors."""
        logger = BattleLogger(self.test_file, enabled=True)
        logger.start_session()
        logger.close()
        logger.close()  # Should not raise
        self.assertIsNone(logger.file)
    
    def test_disabled_logger_does_not_open_file(self):
        """Disabled logger should not open any file."""
        logger = BattleLogger(self.test_file, enabled=False)
        logger.start_session()
        self.assertIsNone(logger.file)
        self.assertFalse(os.path.exists(self.test_file))


if __name__ == '__main__':
    unittest.main()
