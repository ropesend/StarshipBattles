import pytest
import os
import time
import uuid
from unittest.mock import patch
from game.core.profiling import Profiler, profile_action, profile_block, PROFILER
from game.core.json_utils import load_json


@pytest.fixture
def profiler_setup():
    """Set up a fresh profiler state for each test."""
    Profiler.reset()
    PROFILER.active = False
    PROFILER.records = []
    test_file = f"test_profiling_history_{uuid.uuid4().hex[:8]}.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    yield test_file

    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except PermissionError:
            pass  # Win32 file locking sometimes


@pytest.fixture
def json_utils_setup():
    """Set up for JSON utils tests."""
    Profiler.reset()
    PROFILER.active = False
    PROFILER.records = []
    test_file = f"test_profiling_json_utils_{uuid.uuid4().hex[:8]}.json"

    yield test_file

    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except PermissionError:
            pass


class TestProfilingJsonUtils:
    """Test that Profiler uses centralized json_utils for file operations."""

    def test_profiling_does_not_use_direct_json_calls(self, json_utils_setup):
        """Profiler.save_history should use json_utils, not direct json.dump/loads."""
        import game.core.profiling as prof_module
        import inspect
        source = inspect.getsource(prof_module)

        # The file should use load_json/save_json from json_utils
        assert "json.dump(" not in source, "Should use save_json from game.core.json_utils"
        assert "json.loads(" not in source, "Should use load_json from game.core.json_utils"

    @patch("game.core.profiling.save_json")
    def test_save_history_uses_save_json(self, mock_save_json, json_utils_setup):
        """save_history should call save_json from json_utils."""
        test_file = json_utils_setup
        mock_save_json.return_value = True

        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        PROFILER.save_history(test_file)

        mock_save_json.assert_called_once()
        # Verify the filename was passed
        call_args = mock_save_json.call_args
        assert call_args[0][0] == test_file

    @patch("game.core.profiling.load_json")
    @patch("game.core.profiling.save_json")
    def test_save_history_loads_existing_with_load_json(self, mock_save, mock_load, json_utils_setup):
        """save_history should use load_json to read existing history."""
        test_file = json_utils_setup
        mock_load.return_value = [{"session_id": "old", "records": []}]
        mock_save.return_value = True

        # Create a file so the code path tries to load it
        with open(test_file, 'w') as f:
            f.write('[{"session_id": "old", "records": []}]')

        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        PROFILER.save_history(test_file)

        # Should have called load_json to load existing history
        mock_load.assert_called_once_with(test_file, default=[])


class TestProfiling:
    def test_singleton(self, profiler_setup):
        # Use instance() for singleton access
        p1 = Profiler.instance()
        p2 = Profiler.instance()
        assert p1 is p2
        # PROFILER proxy delegates to same instance
        assert p1 is Profiler.instance()

    def test_toggling(self, profiler_setup):
        assert not PROFILER.is_active()
        PROFILER.start()
        assert PROFILER.is_active()
        PROFILER.stop()
        assert not PROFILER.is_active()
        PROFILER.toggle()
        assert PROFILER.is_active()

    def test_recording(self, profiler_setup):
        PROFILER.start()
        PROFILER.record("test_action", 0.1)
        assert len(PROFILER.records) == 1
        assert PROFILER.records[0]['name'] == "test_action"
        assert abs(PROFILER.records[0]['duration_ms'] - 100.0) < 0.1

    def test_recording_inactive(self, profiler_setup):
        PROFILER.stop()
        PROFILER.record("test_action", 0.1)
        assert len(PROFILER.records) == 0

    def test_context_manager(self, profiler_setup):
        PROFILER.start()
        with profile_block("block_action"):
            time.sleep(0.02)  # 20ms sleep for more reliable timing

        assert len(PROFILER.records) == 1
        assert PROFILER.records[0]['name'] == "block_action"
        # Allow for system timer imprecision - 20ms sleep should be > 15ms
        assert PROFILER.records[0]['duration_ms'] > 15.0

    def test_decorator(self, profiler_setup):
        PROFILER.start()

        @profile_action("func_action")
        def slow_func():
            time.sleep(0.01)

        slow_func()

        assert len(PROFILER.records) == 1
        assert PROFILER.records[0]['name'] == "func_action"

    def test_save_history(self, profiler_setup):
        test_file = profiler_setup
        PROFILER.start()
        PROFILER.record("action1", 0.1)
        PROFILER.save_history(test_file)

        assert os.path.exists(test_file)
        data = load_json(test_file)
        assert len(data) == 1
        assert data[0]['session_id'] == PROFILER.session_id
        assert len(data[0]['records']) == 1

        # Test append
        PROFILER.records = []  # Clear memory
        # Simulate new session
        PROFILER.session_id = "session_2"
        PROFILER.record("action2", 0.2)
        PROFILER.save_history(test_file)

        data = load_json(test_file)
        assert len(data) == 2
        assert data[1]['session_id'] == "session_2"
