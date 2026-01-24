"""
Tests for SaveGameService with turn-based saves and per-empire design folders
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.core.json_utils import load_json, save_json


class MockGameSession:
    """Mock GameSession for testing save operations."""

    def __init__(self, config=None, turn_number=1, num_empires=2):
        self.config = config or GameConfig()
        self.turn_number = turn_number
        self.save_path = None
        self.systems = [MagicMock()]  # At least one system

        # Create mock empires
        self.empires = []
        for i in range(num_empires):
            empire = MagicMock()
            empire.id = i
            empire.name = f"Empire {i}"
            self.empires.append(empire)

    def to_dict(self):
        return {
            'turn_number': self.turn_number,
            'save_path': self.save_path,
            'config': self.config.to_dict(),
            'galaxy': {'systems': {}, 'warp_lanes': [], 'radius': 4000},
            'empires': [{'id': e.id, 'name': e.name, 'color': (0, 0, 255),
                         'colony_ids': [], 'fleets': [], 'built_ship_designs': []}
                        for e in self.empires],
            'human_player_ids': [0, 1]
        }


class TestSaveGameServiceFolderStructure:
    """Tests for save folder structure creation."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_save_creates_turns_folder(self):
        """First save creates turns/ subfolder"""
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success
        turns_folder = os.path.join(save_path, "turns")
        assert os.path.exists(turns_folder), "turns/ folder should be created"

    def test_save_creates_per_empire_design_folders(self):
        """Save creates designs/empire_N/ for each empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ]
        )
        session = MockGameSession(config=config, num_empires=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success
        designs_folder = os.path.join(save_path, "designs")
        assert os.path.exists(designs_folder)

        # Check per-empire folders
        for i in range(3):
            empire_folder = os.path.join(designs_folder, f"empire_{i}")
            assert os.path.exists(empire_folder), f"designs/empire_{i}/ folder should be created"

    def test_save_writes_turn_file(self):
        """Save writes to turns/turn_N.json"""
        session = MockGameSession(turn_number=5)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success
        turn_file = os.path.join(save_path, "turns", "turn_5.json")
        assert os.path.exists(turn_file), f"Turn file should exist at turns/turn_5.json"

    def test_save_updates_metadata_latest_turn(self):
        """Metadata tracks latest_turn_number"""
        session = MockGameSession(turn_number=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert metadata['latest_turn_number'] == 3

    def test_save_increment_turn_creates_new_file(self):
        """Second save creates turn_2.json, keeps turn_1.json"""
        session = MockGameSession(turn_number=1)

        # First save
        success1, _, save_path = SaveGameService.save_game(session, "TestGame")
        assert success1

        # Increment turn and save again
        session.turn_number = 2
        session.save_path = save_path
        success2, _, _ = SaveGameService.save_game(session)

        assert success2

        # Both turn files should exist
        turn1_file = os.path.join(save_path, "turns", "turn_1.json")
        turn2_file = os.path.join(save_path, "turns", "turn_2.json")

        assert os.path.exists(turn1_file), "turn_1.json should still exist"
        assert os.path.exists(turn2_file), "turn_2.json should be created"


class TestSaveGameServiceVersion:
    """Tests for save version handling."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_save_version_is_2_0_0(self, setup_tmpdir):
        """New saves use version 2.0.0"""
        session = MockGameSession()

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        assert success
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert metadata['version'] == "2.0.0"

    def test_load_rejects_old_version(self, setup_tmpdir):
        """Loading incompatible version save returns error"""
        tmpdir = setup_tmpdir
        # Create save with valid structure but incompatible version
        save_folder = os.path.join(tmpdir, "saves", "OldSave")
        turns_folder = os.path.join(save_folder, "turns")
        os.makedirs(turns_folder)

        # Incompatible version metadata (not in MIGRATABLE_VERSIONS)
        metadata = {
            'version': '0.5.0',
            'timestamp': '2026-01-01T00:00:00',
            'player_name': 'Test',
            'turn_number': 1,
            'latest_turn_number': 1
        }
        save_json(os.path.join(save_folder, "save_metadata.json"), metadata)

        # Game state in turns folder (valid structure)
        game_state = {
            'turn_number': 1,
            'config': GameConfig().to_dict(),
            'galaxy': {'systems': {}, 'warp_lanes': [], 'radius': 4000},
            'empires': [],
            'human_player_ids': [0, 1]
        }
        save_json(os.path.join(turns_folder, "turn_1.json"), game_state)

        # Attempt to load
        result, message = SaveGameService.load_game(save_folder)

        assert result is None
        assert "version" in message.lower()


class TestSaveGameServiceLoad:
    """Tests for loading saves."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_load_defaults_to_latest_turn(self):
        """load_game() loads highest turn number by default"""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load without specifying turn
        loaded, message = SaveGameService.load_game(save_path)

        assert loaded is not None
        assert loaded.turn_number == 3

    def test_load_specific_turn(self):
        """load_game(path, turn_number=N) loads specific turn"""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load specific turn
        loaded, message = SaveGameService.load_game(save_path, turn_number=2)

        assert loaded is not None
        assert loaded.turn_number == 2

    def test_list_turns_returns_all_turns(self):
        """list_turns() returns metadata for each turn file"""
        session = MockGameSession(turn_number=1)

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # List turns
        turns = SaveGameService.list_turns(save_path)

        assert len(turns) == 3
        turn_numbers = [t['turn_number'] for t in turns]
        assert 1 in turn_numbers
        assert 2 in turn_numbers
        assert 3 in turn_numbers


class TestSaveGameServiceMetadata:
    """Tests for save metadata."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_metadata_includes_empire_count(self):
        """Metadata includes number of empires"""
        config = GameConfig(
            players=[
                PlayerConfig(name="E1", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="E2", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="E3", theme="Romulans", color=(0, 0, 255)),
            ]
        )
        session = MockGameSession(config=config, num_empires=3)

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert metadata['empire_count'] == 3

    def test_metadata_includes_empire_names(self):
        """Metadata includes list of empire names"""
        session = MockGameSession(num_empires=2)
        session.empires[0].name = "Alpha Empire"
        session.empires[1].name = "Beta Empire"

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert "Alpha Empire" in metadata['empire_names']
        assert "Beta Empire" in metadata['empire_names']


class TestSaveGameServiceNoDesignMigration:
    """Tests for BUG-29: New games should not inherit designs from temp folder."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        # Create temp designs folder with some designs (simulating previous game sessions)
        temp_designs = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs", "empire_0")
        os.makedirs(temp_designs, exist_ok=True)

        # Create a test design in temp folder
        test_design = {
            "name": "Old Design From Temp",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {}
        }
        save_json(os.path.join(temp_designs, "old_design.json"), test_design)

        yield tmpdir, temp_designs

        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)
        # Clean up temp design we created
        temp_design_file = os.path.join(temp_designs, "old_design.json")
        if os.path.exists(temp_design_file):
            os.remove(temp_design_file)

    def test_new_game_does_not_migrate_temp_designs(self, setup_tmpdir):
        """BUG-29: New game save should NOT copy designs from temp folder"""
        tmpdir, temp_designs = setup_tmpdir
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "NewGame")

        assert success

        # Check that the designs folder for empire 0 is EMPTY
        empire_designs = os.path.join(save_path, "designs", "empire_0")
        assert os.path.exists(empire_designs), "Empire designs folder should exist"

        design_files = [f for f in os.listdir(empire_designs) if f.endswith('.json')]
        assert len(design_files) == 0, f"New game should have NO designs, but found: {design_files}"


class TestSaveGameServiceErrorLogging:
    """Tests for error logging in SaveGameService (ERR-004)."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_save_error_logs_with_traceback(self, caplog):
        """Save errors should log full traceback, not print to stdout."""
        import logging

        session = MockGameSession()

        # Mock to_dict to raise an exception
        def raise_error():
            raise ValueError("Test save error")

        session.to_dict = raise_error

        with caplog.at_level(logging.ERROR):
            success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert not success
        assert "Test save error" in message

        # Should have logged an error
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on save failure"

    def test_load_error_logs_with_context(self, caplog, setup_tmpdir):
        """Load errors should log with save path context."""
        import logging
        import json

        tmpdir = setup_tmpdir

        # Create a save with valid metadata but corrupted turn file
        save_path = os.path.join(tmpdir, "saves", "BadSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)
        with open(os.path.join(save_path, "turns", "turn_1.json"), "w") as f:
            f.write("{ invalid json }")  # Corrupted JSON

        metadata = {
            "version": "2.0.0",  # Must match SaveGameService.SAVE_VERSION
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        with open(os.path.join(save_path, "save_metadata.json"), "w") as f:
            json.dump(metadata, f)

        with caplog.at_level(logging.ERROR):
            result, message = SaveGameService.load_game(save_path)

        assert result is None
        assert "corrupted" in message.lower() or "cannot read" in message.lower()
        # Should have logged an error with context
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on load failure"


class TestSaveGameServiceUserFriendlyErrors:
    """Tests for user-friendly error messages in SaveGameService (ERR-019)."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_load_error_message_is_user_friendly(self, setup_tmpdir):
        """Load error messages should be user-friendly, not expose raw exceptions (ERR-019)."""
        tmpdir = setup_tmpdir

        # Create save with valid metadata but missing required game state fields
        save_path = os.path.join(tmpdir, "saves", "IncompleteSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        metadata = {
            "version": "2.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        # Game state with missing required fields (will cause KeyError during reconstruction)
        game_state = {
            "turn_number": 1,
            # Missing: config, galaxy, empires
        }
        save_json(os.path.join(save_path, "turns", "turn_1.json"), game_state)

        result, message = SaveGameService.load_game(save_path)

        assert result is None
        # Message should be user-friendly, not raw exception
        assert "Save file" in message or "corrupted" in message.lower()
        # Should NOT expose raw Python exception class names in user message
        assert "KeyError" not in message, f"Should not expose KeyError to user: {message}"
        assert "Traceback" not in message, f"Should not expose traceback to user: {message}"

    def test_unexpected_load_error_message_is_user_friendly(self, setup_tmpdir):
        """Unexpected errors during load should have user-friendly messages (ERR-019)."""
        tmpdir = setup_tmpdir

        # Create valid-looking save
        save_path = os.path.join(tmpdir, "saves", "TestSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        metadata = {
            "version": "2.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        game_state = {
            "turn_number": 1,
            "config": GameConfig().to_dict(),
            "galaxy": {"systems": {}, "warp_lanes": [], "radius": 4000},
            "empires": [],
            "human_player_ids": [0]
        }
        save_json(os.path.join(save_path, "turns", "turn_1.json"), game_state)

        # Mock GameSession.from_dict to raise unexpected exception
        # Need to patch at module level since import happens inside function
        with patch('game.strategy.engine.game_session.GameSession.from_dict',
                   side_effect=RuntimeError("Internal processing error")):
            result, message = SaveGameService.load_game(save_path)

        assert result is None
        # Message should be user-friendly
        assert "unexpected error" in message.lower() or "failed" in message.lower() or "corrupted" in message.lower()
        # Should NOT expose raw exception details
        assert "RuntimeError" not in message, f"Should not expose exception type: {message}"
        assert "Internal processing error" not in message, f"Should not expose internal error details: {message}"
