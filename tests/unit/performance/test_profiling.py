import unittest
import os
import time
import uuid
from unittest.mock import patch
from game.core.profiling import Profiler, profile_action, profile_block, PROFILER
from game.core.json_utils import load_json


class TestProfilingJsonUtils(unittest.TestCase):
    """Test that Profiler uses centralized json_utils for file operations."""

    def setUp(self):
        Profiler.reset()
        PROFILER.active = False
        PROFILER.records = []
        self.test_file = f"test_profiling_json_utils_{uuid.uuid4().hex[:8]}.json"

    def tearDown(self):
        if os.path.exists(self.test_file):
            try:
                os.remove(self.test_file)
            except PermissionError:
                pass

    def test_profiling_does_not_use_direct_json_calls(self):
        """Profiler.save_history should use json_utils, not direct json.dump/loads."""
        import game.core.profiling as prof_module
        import inspect
        source = inspect.getsource(prof_module)

        # The file should use load_json/save_json from json_utils
        assert "json.dump(" not in source, "Should use save_json from game.core.json_utils"
        assert "json.loads(" not in source, "Should use load_json from game.core.json_utils"

    @patch("game.core.profiling.save_json")
    def test_save_history_uses_save_json(self, mock_save_json):
        """save_history should call save_json from json_utils."""
        mock_save_json.return_value = True

        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        PROFILER.save_history(self.test_file)

        mock_save_json.assert_called_once()
        # Verify the filename was passed
        call_args = mock_save_json.call_args
        self.assertEqual(call_args[0][0], self.test_file)

    @patch("game.core.profiling.load_json")
    @patch("game.core.profiling.save_json")
    def test_save_history_loads_existing_with_load_json(self, mock_save, mock_load):
        """save_history should use load_json to read existing history."""
        mock_load.return_value = [{"session_id": "old", "records": []}]
        mock_save.return_value = True

        # Create a file so the code path tries to load it
        with open(self.test_file, 'w') as f:
            f.write('[{"session_id": "old", "records": []}]')

        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        PROFILER.save_history(self.test_file)

        # Should have called load_json to load existing history
        mock_load.assert_called_once_with(self.test_file, default=[])


class TestProfiling(unittest.TestCase):
    def setUp(self):
        # Reset singleton state for testing
        Profiler.reset()
        # Ensure fresh instance
        PROFILER.active = False
        PROFILER.records = []
        # Use unique file name to prevent parallel test conflicts
        self.test_file = f"test_profiling_history_{uuid.uuid4().hex[:8]}.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            try:
                os.remove(self.test_file)
            except PermissionError:
                pass # Win32 file locking sometimes

    def test_singleton(self):
        # Use instance() for singleton access
        p1 = Profiler.instance()
        p2 = Profiler.instance()
        self.assertIs(p1, p2)
        # PROFILER proxy delegates to same instance
        self.assertIs(p1, Profiler.instance())

    def test_toggling(self):
        self.assertFalse(PROFILER.is_active())
        PROFILER.start()
        self.assertTrue(PROFILER.is_active())
        PROFILER.stop()
        self.assertFalse(PROFILER.is_active())
        PROFILER.toggle()
        self.assertTrue(PROFILER.is_active())

    def test_recording(self):
        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        self.assertEqual(len(PROFILER.records), 1)
        self.assertEqual(PROFILER.records[0]['name'], "test_action")
        self.assertAlmostEqual(PROFILER.records[0]['duration_ms'], 100.0, delta=0.1)

    def test_recording_inactive(self):
        PROFILER.stop()
        PROFILER.record("test_action", 0.1)
        self.assertEqual(len(PROFILER.records), 0)

    def test_context_manager(self):
        PROFILER.start()
        with profile_block("block_action"):
            time.sleep(0.01)
        
        self.assertEqual(len(PROFILER.records), 1)
        self.assertEqual(PROFILER.records[0]['name'], "block_action")
        self.assertGreater(PROFILER.records[0]['duration_ms'], 9.0)

    def test_decorator(self):
        PROFILER.start()
        
        @profile_action("func_action")
        def slow_func():
            time.sleep(0.01)
            
        slow_func()
        
        self.assertEqual(len(PROFILER.records), 1)
        self.assertEqual(PROFILER.records[0]['name'], "func_action")

    def test_save_history(self):
        PROFILER.start()
        PROFILER.record("action1", 0.1)
        PROFILER.save_history(self.test_file)
        
        self.assertTrue(os.path.exists(self.test_file))
        data = load_json(self.test_file)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['session_id'], PROFILER.session_id)
        self.assertEqual(len(data[0]['records']), 1)
            
        # Test append
        PROFILER.records = [] # Clear memory
        # Simulate new session
        PROFILER.session_id = "session_2" 
        PROFILER.record("action2", 0.2)
        PROFILER.save_history(self.test_file)

        data = load_json(self.test_file)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]['session_id'], "session_2")

if __name__ == '__main__':
    unittest.main()
