import pytest
import os
import time
import uuid
from unittest.mock import patch
from game.core.profiling import Profiler, profile_action, profile_block, set_default_profiler
from game.core.json_utils import load_json


@pytest.fixture
def profiler_setup():
    """Set up a fresh profiler state for each test."""
    profiler = Profiler()
    profiler.active = False
    profiler.records = []
    set_default_profiler(profiler)
    test_file = f"test_profiling_history_{uuid.uuid4().hex[:8]}.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    yield test_file

    set_default_profiler(None)
    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except PermissionError:
            pass  # Win32 file locking sometimes


@pytest.fixture
def json_utils_setup():
    """Set up for JSON utils tests."""
    profiler = Profiler()
    profiler.active = False
    profiler.records = []
    set_default_profiler(profiler)
    test_file = f"test_profiling_json_utils_{uuid.uuid4().hex[:8]}.json"

    yield test_file

    set_default_profiler(None)
    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except PermissionError:
            pass


class TestProfilingJsonUtils:
    """Test that Profiler uses centralized json_utils for file operations."""

    def test_profiling_does_not_use_direct_json_calls(self, json_utils_setup):
        """Profiler.save_history should use json_utils, not direct json.dump/loads.

        PROJ-491 Task 1.2: replace brittle ``inspect.getsource`` substring
        check with a behavioral assertion at the patchpoint — if profiling
        regressed to call ``json.dump`` / ``json.loads`` directly, those would
        have to be imported into the module namespace as ``game.core.profiling.json``.
        We patch that namespace (creating the attribute if missing so the patch
        succeeds) and verify the patched callables are never invoked during a
        real save_history flow.
        """
        test_file = json_utils_setup
        from game.core.profiling import _default_profiler
        import game.core.profiling as prof_module

        profiler = _default_profiler
        profiler.start()
        profiler.record("test_action", 0.1)

        # Patch the would-be call sites in the production module's namespace.
        # ``create=True`` lets the patch attach to attributes that do not yet
        # exist; if the production code never imports ``json``, the mocks
        # naturally stay uncalled.
        with patch.object(
            prof_module, "json", create=True
        ) as mock_json:
            profiler.save_history(test_file)

            mock_json.dump.assert_not_called()
            mock_json.loads.assert_not_called()

    @patch("game.core.profiling.save_json")
    def test_save_history_uses_save_json(self, mock_save_json, json_utils_setup):
        """save_history should call save_json from json_utils."""
        test_file = json_utils_setup
        mock_save_json.return_value = True

        from game.core.profiling import _default_profiler
        profiler = _default_profiler
        profiler.start()
        profiler.record("test_action", 0.1)
        profiler.save_history(test_file)

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

        from game.core.profiling import _default_profiler
        profiler = _default_profiler
        profiler.start()
        profiler.record("test_action", 0.1)
        profiler.save_history(test_file)

        # Should have called load_json to load existing history
        mock_load.assert_called_once_with(test_file, default=[])


class TestProfiling:
    def test_independent_instances(self, profiler_setup):
        # Direct construction creates independent instances
        p1 = Profiler()
        p2 = Profiler()
        assert p1 is not p2

    def test_toggling(self, profiler_setup):
        profiler = Profiler()
        assert not profiler.is_active()
        profiler.start()
        assert profiler.is_active()
        profiler.stop()
        assert not profiler.is_active()
        profiler.toggle()
        assert profiler.is_active()

    def test_recording(self, profiler_setup):
        profiler = Profiler()
        profiler.start()
        profiler.record("test_action", 0.1)
        assert len(profiler.records) == 1
        assert profiler.records[0]['name'] == "test_action"
        assert abs(profiler.records[0]['duration_ms'] - 100.0) < 0.1

    def test_recording_inactive(self, profiler_setup):
        profiler = Profiler()
        profiler.stop()
        profiler.record("test_action", 0.1)
        assert len(profiler.records) == 0

    def test_context_manager(self, profiler_setup):
        profiler = Profiler()
        profiler.start()
        set_default_profiler(profiler)
        with profile_block("block_action"):
            time.sleep(0.02)  # 20ms sleep for more reliable timing

        assert len(profiler.records) == 1
        assert profiler.records[0]['name'] == "block_action"
        # Allow for system timer imprecision - 20ms sleep should be > 15ms
        assert profiler.records[0]['duration_ms'] > 15.0

    def test_decorator(self, profiler_setup):
        profiler = Profiler()
        profiler.start()
        set_default_profiler(profiler)

        @profile_action("func_action")
        def slow_func():
            time.sleep(0.01)

        slow_func()

        assert len(profiler.records) == 1
        assert profiler.records[0]['name'] == "func_action"

    def test_save_history(self, profiler_setup):
        test_file = profiler_setup
        profiler = Profiler()
        profiler.start()
        profiler.record("action1", 0.1)
        profiler.save_history(test_file)

        assert os.path.exists(test_file)
        data = load_json(test_file)
        assert len(data) == 1
        assert data[0]['session_id'] == profiler.session_id
        assert len(data[0]['records']) == 1

        # Test append
        profiler.records = []  # Clear memory
        # Simulate new session
        profiler.session_id = "session_2"
        profiler.record("action2", 0.2)
        profiler.save_history(test_file)

        data = load_json(test_file)
        assert len(data) == 2
        assert data[1]['session_id'] == "session_2"
