import unittest
import os
import json
import time
import uuid
from profiling import Profiler, profile_action, profile_block, PROFILER

class TestProfiling(unittest.TestCase):
    def setUp(self):
        # Reset singleton state for testing
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
        p1 = Profiler()
        p2 = Profiler()
        self.assertIs(p1, p2)
        self.assertIs(p1, PROFILER)

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
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['session_id'], PROFILER.session_id)
            self.assertEqual(len(data[0]['records']), 1)
            
        # Test append
        PROFILER.records = [] # Clear memory
        # Simulate new session
        PROFILER.session_id = "session_2" 
        PROFILER.record("action2", 0.2)
        PROFILER.save_history(self.test_file)
        
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[1]['session_id'], "session_2")

if __name__ == '__main__':
    unittest.main()
