"""
Integration tests for save/load round-trip functionality.

Tests the complete save/load cycle including:
- Save game creation
- Load game restoration
- State equality after round-trip
- Edge cases: corrupted saves, missing data, version compatibility
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.core import paths as paths_module
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship_instance(name="Test Ship", owner_id=0):
    """Create a mock ShipInstance for testing."""
    return ShipInstance(
        instance_id=f"test-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100}
        },
    )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_save_folder():
    """Create a temporary folder for saves and clean up after test."""
    temp_dir = tempfile.mkdtemp(prefix="test_saves_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def minimal_game_session():
    """Create a minimal game session for testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)


@pytest.fixture
def game_session_with_state(minimal_game_session):
    """Create a game session with some game state to preserve."""
    session = minimal_game_session

    # Add some fleets
    fleet1 = Fleet(100, 0, HexCoord(10, 10), speed=15.0)
    fleet1.ships = [make_mock_ship_instance("Scout", 0)]
    session.empires[0].add_fleet(fleet1)

    fleet2 = Fleet(200, 1, HexCoord(20, 20), speed=10.0)
    fleet2.ships = [make_mock_ship_instance("Destroyer", 1)]
    session.empires[1].add_fleet(fleet2)

    # Advance a few turns
    session.process_turn()
    session.process_turn()

    return session


# =============================================================================
# Test: Save Game Creation
# =============================================================================


class TestSaveGameCreation:
    """Tests for creating save games."""

    def test_save_creates_folder_structure(self, minimal_game_session, temp_save_folder):
        """Save creates proper folder structure."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True
        assert save_path is not None
        assert os.path.exists(save_path)

        # Check folder structure
        assert os.path.exists(os.path.join(save_path, "turns"))
        assert os.path.exists(os.path.join(save_path, "designs"))
        assert os.path.exists(os.path.join(save_path, "save_metadata.json"))

    def test_save_creates_turn_file(self, minimal_game_session, temp_save_folder):
        """Save creates turn state file."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        # Check turn file exists
        turn_file = os.path.join(save_path, "turns", f"turn_{minimal_game_session.turn_number}.json")
        assert os.path.exists(turn_file)

        # Verify content is valid JSON
        with open(turn_file, 'r') as f:
            data = json.load(f)

        assert 'turn_number' in data
        assert 'config' in data
        assert 'galaxy' in data
        assert 'empires' in data

    def test_save_creates_metadata(self, minimal_game_session, temp_save_folder):
        """Save creates metadata file with correct info."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        # Check metadata
        metadata_file = os.path.join(save_path, "save_metadata.json")
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert metadata['version'] == SaveGameService.SAVE_VERSION
        assert 'timestamp' in metadata
        assert metadata['player_name'] == "TestPlayer"
        assert metadata['empire_count'] == 2
        assert metadata['turn_number'] == minimal_game_session.turn_number

    def test_save_updates_session_path(self, minimal_game_session, temp_save_folder):
        """Save updates game session's save_path."""
        assert minimal_game_session.save_path is None

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True
        assert minimal_game_session.save_path == save_path

    def test_save_creates_per_empire_design_folders(self, minimal_game_session, temp_save_folder):
        """Save creates design folder for each empire."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        designs_folder = os.path.join(save_path, "designs")
        for empire in minimal_game_session.empires:
            empire_folder = os.path.join(designs_folder, f"empire_{empire.id}")
            assert os.path.exists(empire_folder)

    def test_save_subsequent_turns(self, minimal_game_session, temp_save_folder):
        """Saving after multiple turns creates multiple turn files."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Save turn 1
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            # Process and save turn 2
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            # Process and save turn 3
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

        # Check all turn files exist
        turns_folder = os.path.join(save_path, "turns")
        assert os.path.exists(os.path.join(turns_folder, "turn_1.json"))
        assert os.path.exists(os.path.join(turns_folder, "turn_2.json"))
        assert os.path.exists(os.path.join(turns_folder, "turn_3.json"))


# =============================================================================
# Test: Load Game Restoration
# =============================================================================


class TestLoadGameRestoration:
    """Tests for loading saved games."""

    def test_load_returns_valid_session(self, minimal_game_session, temp_save_folder):
        """Load returns a valid GameSession object."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is not None
        assert isinstance(loaded_session, GameSession)
        assert "Game loaded" in message

    def test_load_restores_turn_number(self, minimal_game_session, temp_save_folder):
        """Load restores correct turn number."""
        # Process a few turns
        minimal_game_session.process_turn()
        minimal_game_session.process_turn()
        original_turn = minimal_game_session.turn_number

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            loaded_session, _ = SaveGameService.load_game(save_path)

        assert loaded_session.turn_number == original_turn

    def test_load_restores_empires(self, game_session_with_state, temp_save_folder):
        """Load restores empire data."""
        original_empire_count = len(game_session_with_state.empires)
        original_empire_names = [e.name for e in game_session_with_state.empires]

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(game_session_with_state, save_name="test_save")
            save_path = game_session_with_state.save_path

            loaded_session, _ = SaveGameService.load_game(save_path)

        assert len(loaded_session.empires) == original_empire_count
        loaded_names = [e.name for e in loaded_session.empires]
        assert loaded_names == original_empire_names

    def test_load_restores_galaxy(self, minimal_game_session, temp_save_folder):
        """Load restores galaxy structure."""
        original_system_count = len(minimal_game_session.systems)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            loaded_session, _ = SaveGameService.load_game(save_path)

        assert len(loaded_session.systems) == original_system_count

    def test_load_specific_turn(self, minimal_game_session, temp_save_folder):
        """Load can restore a specific turn from history."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Save turn 1
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            # Process and save turn 2
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            # Process and save turn 3
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            # Load turn 2 specifically
            loaded_session, _ = SaveGameService.load_game(save_path, turn_number=2)

        assert loaded_session.turn_number == 2

    def test_load_restores_save_path(self, minimal_game_session, temp_save_folder):
        """Loaded session has correct save_path set."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            original_save_path = minimal_game_session.save_path

            loaded_session, _ = SaveGameService.load_game(original_save_path)

        assert loaded_session.save_path == original_save_path


# =============================================================================
# Test: State Equality After Round-Trip
# =============================================================================


class TestStateRoundTrip:
    """Tests for state preservation through save/load cycle."""

    def test_config_preserved(self, minimal_game_session, temp_save_folder):
        """Game config is preserved through round-trip."""
        original_radius = minimal_game_session.config.galaxy_radius
        original_players = len(minimal_game_session.config.players)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

        assert loaded_session.config.galaxy_radius == original_radius
        assert len(loaded_session.config.players) == original_players

    def test_empire_ids_preserved(self, game_session_with_state, temp_save_folder):
        """Empire IDs are preserved through round-trip."""
        original_ids = [e.id for e in game_session_with_state.empires]

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(game_session_with_state, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(game_session_with_state.save_path)

        loaded_ids = [e.id for e in loaded_session.empires]
        assert loaded_ids == original_ids

    def test_fleet_count_preserved(self, game_session_with_state, temp_save_folder):
        """Fleet counts are preserved through round-trip."""
        original_fleet_counts = [len(e.fleets) for e in game_session_with_state.empires]

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(game_session_with_state, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(game_session_with_state.save_path)

        loaded_fleet_counts = [len(e.fleets) for e in loaded_session.empires]
        assert loaded_fleet_counts == original_fleet_counts

    def test_colony_count_preserved(self, game_session_with_state, temp_save_folder):
        """Colony counts are preserved through round-trip."""
        original_colony_counts = [len(e.colonies) for e in game_session_with_state.empires]

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(game_session_with_state, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(game_session_with_state.save_path)

        loaded_colony_counts = [len(e.colonies) for e in loaded_session.empires]
        assert loaded_colony_counts == original_colony_counts

    def test_planet_ids_preserved(self, game_session_with_state, temp_save_folder):
        """Planet IDs in galaxy are preserved through round-trip."""
        original_planet_ids = set()
        for system in game_session_with_state.systems:
            for planet in system.planets:
                original_planet_ids.add(planet.id)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(game_session_with_state, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(game_session_with_state.save_path)

        loaded_planet_ids = set()
        for system in loaded_session.systems:
            for planet in system.planets:
                loaded_planet_ids.add(planet.id)

        assert loaded_planet_ids == original_planet_ids

    def test_human_player_ids_preserved(self, minimal_game_session, temp_save_folder):
        """Human player IDs are preserved through round-trip."""
        original_human_ids = minimal_game_session.human_player_ids.copy()

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

        assert loaded_session.human_player_ids == original_human_ids


# =============================================================================
# Test: Edge Cases - Corrupted Saves
# =============================================================================


class TestCorruptedSaves:
    """Tests for handling corrupted save files."""

    def test_load_missing_metadata(self, temp_save_folder):
        """Load fails gracefully when metadata is missing."""
        # Create incomplete save folder
        save_path = os.path.join(temp_save_folder, "broken_save")
        os.makedirs(os.path.join(save_path, "turns"))

        # No metadata file

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "Missing save_metadata.json" in message or "Invalid save" in message

    def test_load_missing_turns_folder(self, temp_save_folder):
        """Load fails gracefully when turns folder is missing."""
        # Create incomplete save folder
        save_path = os.path.join(temp_save_folder, "broken_save")
        os.makedirs(save_path)

        # Create metadata but no turns folder
        metadata = {"version": "2.0.0", "timestamp": "2026-01-23", "player_name": "Test"}
        with open(os.path.join(save_path, "save_metadata.json"), 'w') as f:
            json.dump(metadata, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "turns folder" in message.lower() or "invalid" in message.lower()

    def test_load_invalid_json_turn_file(self, minimal_game_session, temp_save_folder):
        """Load fails gracefully with corrupted turn JSON."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

        # Corrupt the turn file
        turn_file = os.path.join(save_path, "turns", "turn_1.json")
        with open(turn_file, 'w') as f:
            f.write("{ invalid json }")

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "corrupted" in message.lower() or "cannot read" in message.lower()

    def test_load_missing_required_fields(self, minimal_game_session, temp_save_folder):
        """Load fails gracefully when required fields are missing."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

        # Remove required field from turn file
        turn_file = os.path.join(save_path, "turns", "turn_1.json")
        with open(turn_file, 'r') as f:
            data = json.load(f)
        del data['galaxy']  # Remove required field
        with open(turn_file, 'w') as f:
            json.dump(data, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "missing" in message.lower() or "corrupted" in message.lower()

    def test_load_nonexistent_save(self, temp_save_folder):
        """Load fails gracefully for nonexistent save."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game("nonexistent_save")

        assert loaded_session is None
        assert "not found" in message.lower() or "invalid" in message.lower()


# =============================================================================
# Test: Version Compatibility
# =============================================================================


class TestVersionCompatibility:
    """Tests for save version handling."""

    def test_current_version_loads(self, minimal_game_session, temp_save_folder):
        """Current version saves load correctly."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, message = SaveGameService.load_game(minimal_game_session.save_path)

        assert loaded_session is not None

    def test_incompatible_version_rejected(self, temp_save_folder):
        """Incompatible versions are rejected."""
        # Create save with incompatible version
        save_path = os.path.join(temp_save_folder, "old_save")
        os.makedirs(os.path.join(save_path, "turns"))

        # Create metadata with unknown version
        metadata = {
            "version": "0.0.1",  # Incompatible version
            "timestamp": "2026-01-23",
            "player_name": "Test",
            "turn_number": 1
        }
        with open(os.path.join(save_path, "save_metadata.json"), 'w') as f:
            json.dump(metadata, f)

        # Create minimal turn file
        turn_data = {
            "turn_number": 1,
            "config": {},
            "galaxy": {},
            "empires": []
        }
        with open(os.path.join(save_path, "turns", "turn_1.json"), 'w') as f:
            json.dump(turn_data, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "incompatible" in message.lower() or "version" in message.lower()

    def test_migratable_version_loads(self, temp_save_folder):
        """Migratable older versions are accepted."""
        # This test verifies the migratable version list
        migratable = SaveGameService.MIGRATABLE_VERSIONS

        for version in migratable:
            is_compatible = SaveGameService._is_compatible_version(version)
            assert is_compatible, f"Version {version} should be compatible (migratable)"


# =============================================================================
# Test: Save Management
# =============================================================================


class TestSaveManagement:
    """Tests for save listing and deletion."""

    def test_list_saves(self, minimal_game_session, temp_save_folder):
        """List saves returns saved games."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Create multiple saves
            SaveGameService.save_game(minimal_game_session, save_name="save_1")
            minimal_game_session.save_path = None  # Reset for new save
            SaveGameService.save_game(minimal_game_session, save_name="save_2")

            saves = SaveGameService.list_saves()

        assert len(saves) >= 2
        save_names = [s['save_name'] for s in saves]
        assert "save_1" in save_names
        assert "save_2" in save_names

    def test_list_turns(self, minimal_game_session, temp_save_folder):
        """List turns returns available turn history."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Save multiple turns
            SaveGameService.save_game(minimal_game_session, save_name="test_save")

            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            turns = SaveGameService.list_turns(minimal_game_session.save_path)

        assert len(turns) == 3
        turn_numbers = [t['turn_number'] for t in turns]
        assert 1 in turn_numbers
        assert 2 in turn_numbers
        assert 3 in turn_numbers

    def test_delete_save(self, minimal_game_session, temp_save_folder):
        """Delete save removes save folder."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="to_delete")
            save_path = minimal_game_session.save_path

            assert os.path.exists(save_path)

            success, message = SaveGameService.delete_save(save_path)

        assert success is True
        assert not os.path.exists(save_path)

    def test_delete_nonexistent_save(self, temp_save_folder):
        """Delete nonexistent save fails gracefully."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message = SaveGameService.delete_save("nonexistent")

        assert success is False
        assert "not found" in message.lower()

    def test_get_save_info(self, minimal_game_session, temp_save_folder):
        """Get save info returns metadata."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="info_test")

            info = SaveGameService.get_save_info(minimal_game_session.save_path)

        assert info is not None
        assert info['player_name'] == "TestPlayer"
        assert 'version' in info
        assert 'timestamp' in info


# =============================================================================
# Test: Game Continuity
# =============================================================================


class TestGameContinuity:
    """Tests for continuing gameplay after load."""

    def test_can_process_turn_after_load(self, minimal_game_session, temp_save_folder):
        """Loaded game can process turns."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

        initial_turn = loaded_session.turn_number

        # Process turn should work
        loaded_session.process_turn()

        assert loaded_session.turn_number == initial_turn + 1

    def test_can_save_after_load(self, minimal_game_session, temp_save_folder):
        """Loaded game can be saved again."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

            loaded_session.process_turn()

            # Save should work
            success, message, _ = SaveGameService.save_game(loaded_session)

        assert success is True

    def test_multiple_save_load_cycles(self, minimal_game_session, temp_save_folder):
        """Multiple save/load cycles preserve state."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Cycle 1
            SaveGameService.save_game(minimal_game_session, save_name="cycle_test")
            session, _ = SaveGameService.load_game(minimal_game_session.save_path)

            # Cycle 2
            session.process_turn()
            SaveGameService.save_game(session)
            session, _ = SaveGameService.load_game(session.save_path)

            # Cycle 3
            session.process_turn()
            SaveGameService.save_game(session)
            session, _ = SaveGameService.load_game(session.save_path)

        # Should be at turn 3
        assert session.turn_number == 3
