"""
Tests for SaveGameService save and load operations.

Covers:
- Folder structure creation
- Save versioning
- Loading saves
- Metadata handling
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import patch

from unittest.mock import MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.core.json_utils import load_json, save_json
from game.core import paths as paths_module


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
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_save_creates_turns_folder(self):
        """First save creates turns/ subfolder"""
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success, f"Save failed: {message}"
        turns_folder = os.path.join(save_path, "turns")
        assert os.path.exists(turns_folder), "turns/ folder should be created"

    def test_save_creates_per_empire_design_folders(self):
        """Save creates designs/empire_N/ for each empire"""
        # FEAT-27: pin system_count >= num players to satisfy the N>=2
        # distinct-system invariant.
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=3,
        )
        session = MockGameSession(config=config, num_empires=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success, f"Save failed: {message}"
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

        assert success, f"Save failed: {message}"
        turn_file = os.path.join(save_path, "turns", "turn_5.json")
        assert os.path.exists(turn_file), f"Turn file should exist at turns/turn_5.json"

    def test_save_updates_metadata_latest_turn(self):
        """Metadata tracks latest_turn_number"""
        session = MockGameSession(turn_number=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success, f"Save failed: {message}"
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
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_save_version_is_3_0_0(self, setup_tmpdir):
        """New saves use version 3.0.0 (PROJ-276 Phase 5 bump)"""
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert success, f"Save failed: {message}"
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert metadata['version'] == "3.0.0"

    def test_load_rejects_old_version(self, setup_tmpdir):
        """Loading incompatible version save returns error"""
        tmpdir = setup_tmpdir
        # Create save with valid structure but incompatible version
        save_folder = os.path.join(tmpdir, "saves", "OldSave")
        turns_folder = os.path.join(save_folder, "turns")
        os.makedirs(turns_folder)

        # Incompatible version metadata (only current version accepted)
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
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
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
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_metadata_includes_empire_count(self):
        """Metadata includes number of empires"""
        # FEAT-27: pin system_count >= num players to satisfy the N>=2
        # distinct-system invariant.
        config = GameConfig(
            players=[
                PlayerConfig(name="E1", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="E2", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="E3", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=3,
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


# ---------------------------------------------------------------------------
# PROJ-427 Phase 0: characterization — pin current module-global replay-store
# ownership in save_game_service. Phase 5 will convert this to instance-owned
# wiring; these tests pin today's behavior so the conversion is observably
# diff-able.
# ---------------------------------------------------------------------------


class TestProj427Phase0ReplayStoreModuleGlobal:
    """Pin the present-day `_replay_store` module-global contract."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_set_get_replay_store_round_trip(self):
        """Phase 0 characterization: set_replay_store registers via the
        module-global; get_replay_store returns the same instance.
        Phase 5 removes both functions in favor of constructor injection."""
        from game.strategy.systems import save_game_service as sgs_mod

        sentinel = MagicMock()
        try:
            sgs_mod.set_replay_store(sentinel)
            assert sgs_mod.get_replay_store() is sentinel
            assert sgs_mod._replay_store is sentinel
        finally:
            sgs_mod.set_replay_store(None)

    def test_save_notifies_module_global_replay_store(self):
        """Phase 0 characterization: SaveGameService.save_game notifies
        the registered module-global replay store via set_save_root.
        Phase 5 replaces this with an instance field on SaveGameService."""
        from game.strategy.systems import save_game_service as sgs_mod

        spy = MagicMock()
        try:
            sgs_mod.set_replay_store(spy)
            session = MockGameSession()
            success, _, save_path = SaveGameService.save_game(
                session, "Proj427CharSave"
            )
            assert success
            spy.set_save_root.assert_called()
        finally:
            sgs_mod.set_replay_store(None)

    def test_delete_notifies_module_global_replay_store_clear(self):
        """Phase 0 characterization: SaveGameService.delete_save notifies
        the registered module-global replay store via clear_save_root."""
        from game.strategy.systems import save_game_service as sgs_mod

        session = MockGameSession()
        success, _, save_path = SaveGameService.save_game(
            session, "Proj427CharDelete"
        )
        assert success

        spy = MagicMock()
        try:
            sgs_mod.set_replay_store(spy)
            # The current API exposes delete_save on SaveGameService.
            if hasattr(SaveGameService, "delete_save"):
                SaveGameService.delete_save(save_path)
                spy.clear_save_root.assert_called()
            else:
                # If delete API not surfaced, at minimum prove
                # _notify_replay_store_save_deleted notifies the global.
                sgs_mod._notify_replay_store_save_deleted()
                spy.clear_save_root.assert_called()
        finally:
            sgs_mod.set_replay_store(None)
