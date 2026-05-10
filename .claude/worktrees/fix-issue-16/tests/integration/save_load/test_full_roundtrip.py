"""Full GameSession end-to-end round-trip tests (PROJ-223 Phase 5).

These are the ultimate integration tests — if they pass, the entire
serialization chain (GameSession → SaveGameService → disk → load → verify) works.
"""

import json
import os
import pytest
import tempfile
import shutil

from game.strategy.engine.game_session import GameSession
from game.strategy.systems.save_game_service import SaveGameService
from tests.infrastructure.deep_compare import deep_compare


@pytest.fixture
def rich_game_session():
    """Create a game session with diverse state for comprehensive testing."""
    from game.strategy.engine.game_config import GameConfig, PlayerConfig

    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 3
    config.galaxy_seed = 42
    config.players = [
        PlayerConfig(name="Federation", is_human=True, color=(0, 100, 255), theme="Federation"),
        PlayerConfig(name="Klingons", is_human=False, color=(255, 50, 50), theme="Klingons"),
    ]
    session = GameSession(config=config)

    # Process a couple turns to build up state
    session.process_turn()
    session.process_turn()

    return session


@pytest.fixture
def temp_save_dir():
    """Temporary directory for save/load tests."""
    d = tempfile.mkdtemp(prefix="test_full_roundtrip_")
    yield d
    if os.path.exists(d):
        shutil.rmtree(d)


class TestComprehensiveGameSessionRoundTrip:
    """Task 5.1: Comprehensive end-to-end round-trip."""

    def test_to_dict_from_dict_round_trip(self, rich_game_session):
        """GameSession.to_dict → from_dict preserves all state."""
        session = rich_game_session
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        # Core fields
        assert restored.turn_number == session.turn_number
        assert len(restored.empires) == len(session.empires)
        assert len(restored.systems) == len(session.systems)

        # Galaxy
        assert restored.galaxy.radius == session.galaxy.radius
        assert len(restored.galaxy.systems) == len(session.galaxy.systems)

    def test_save_load_via_service(self, rich_game_session, temp_save_dir):
        """Full save/load through SaveGameService."""
        session = rich_game_session
        session.save_path = os.path.join(temp_save_dir, "test_save")

        success, msg, save_path = SaveGameService.save_game(session)
        assert success, f"Save failed: {msg}"

        loaded, msg = SaveGameService.load_game(save_path)
        assert loaded is not None, f"Load failed: {msg}"

        assert loaded.turn_number == session.turn_number
        assert len(loaded.empires) == len(session.empires)

    def test_deep_compare_after_round_trip(self, rich_game_session):
        """Field-level comparison of to_dict before and after round-trip."""
        session = rich_game_session
        original_dict = session.to_dict()

        restored = GameSession.from_dict(original_dict)
        restored_dict = restored.to_dict()

        # Ignore fields that are non-deterministic (frozenset ordering in storms)
        ignore = set()
        # Collect storm hex_offset paths dynamically
        for i, sys_entry in enumerate(original_dict.get('galaxy', {}).get('systems', [])):
            system = sys_entry.get('system', {})
            for j, _ in enumerate(system.get('storms', [])):
                ignore.add(f"galaxy.systems[{i}].system.storms[{j}].hex_offsets")

        diffs = deep_compare(original_dict, restored_dict, ignore_fields=ignore)
        if diffs:
            diff_report = "\n".join(f"  {d.path}: {d.message}" for d in diffs[:20])
            pytest.fail(f"Round-trip produced {len(diffs)} differences:\n{diff_report}")

    def test_process_turn_works_after_load(self, rich_game_session):
        """Turn processing should work on a loaded session."""
        session = rich_game_session
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        original_turn = restored.turn_number
        restored.process_turn()
        assert restored.turn_number == original_turn + 1

    def test_re_save_succeeds(self, rich_game_session, temp_save_dir):
        """After load, a re-save should succeed."""
        session = rich_game_session
        session.save_path = os.path.join(temp_save_dir, "test_save")

        success1, _, save_path = SaveGameService.save_game(session)
        assert success1

        loaded, _ = SaveGameService.load_game(save_path)
        assert loaded is not None

        # Re-save
        loaded.save_path = os.path.join(temp_save_dir, "test_resave")
        success2, msg, _ = SaveGameService.save_game(loaded)
        assert success2, f"Re-save failed: {msg}"


class TestMultiCycleSaveLoadPlay:
    """Task 5.2: Save → Load → Play → Save → Load → Verify."""

    def test_multi_cycle(self, rich_game_session, temp_save_dir):
        session = rich_game_session
        session.save_path = os.path.join(temp_save_dir, "cycle_test")

        # Cycle 1: Save
        success, _, save_path = SaveGameService.save_game(session)
        assert success

        # Cycle 1: Load
        loaded, _ = SaveGameService.load_game(save_path)
        assert loaded is not None

        # Play 3 turns
        for _ in range(3):
            loaded.process_turn()

        turn_after_play = loaded.turn_number

        # Cycle 2: Save again
        loaded.save_path = os.path.join(temp_save_dir, "cycle_test_2")
        success2, _, save_path2 = SaveGameService.save_game(loaded)
        assert success2

        # Cycle 2: Load again
        final, _ = SaveGameService.load_game(save_path2)
        assert final is not None
        assert final.turn_number == turn_after_play

    def test_turn_number_increments(self, rich_game_session):
        session = rich_game_session
        original_turn = session.turn_number

        d = session.to_dict()
        restored = GameSession.from_dict(d)
        assert restored.turn_number == original_turn

        restored.process_turn()
        assert restored.turn_number == original_turn + 1

    def test_events_accumulate(self, rich_game_session):
        session = rich_game_session
        d = session.to_dict()
        restored = GameSession.from_dict(d)

        events_before = len(restored._event_log.get_all_events())
        restored.process_turn()
        events_after = len(restored._event_log.get_all_events())
        # Events should not decrease (may or may not increase depending on game state)
        assert events_after >= events_before


class TestJsonFormatStability:
    """Task 5.3: JSON format stability verification."""

    def test_to_dict_is_json_serializable(self, rich_game_session):
        d = rich_game_session.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0

    def test_all_dict_keys_are_strings(self, rich_game_session):
        d = rich_game_session.to_dict()
        _check_keys_are_strings(d, "root")

    def test_no_non_serializable_objects(self, rich_game_session):
        """Verify no HexCoord, datetime, enum objects leak into to_dict."""
        d = rich_game_session.to_dict()
        _check_serializable(d, "root")


def _check_keys_are_strings(obj, path):
    """Recursively verify all dict keys are strings."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert isinstance(key, str), f"Non-string key at {path}: {key!r} (type={type(key).__name__})"
            _check_keys_are_strings(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _check_keys_are_strings(item, f"{path}[{i}]")


def _check_serializable(obj, path):
    """Recursively verify all values are JSON-serializable types."""
    allowed = (str, int, float, bool, type(None))
    if isinstance(obj, dict):
        for key, value in obj.items():
            _check_serializable(value, f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        # JSON serializes both list and tuple as arrays
        for i, item in enumerate(obj):
            _check_serializable(item, f"{path}[{i}]")
    elif isinstance(obj, allowed):
        pass
    else:
        raise AssertionError(f"Non-serializable value at {path}: {obj!r} (type={type(obj).__name__})")
