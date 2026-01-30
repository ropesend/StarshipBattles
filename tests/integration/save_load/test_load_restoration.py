"""Tests for load game restoration and state round-trip preservation."""
import pytest
from unittest.mock import patch

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_session import GameSession
from game.core import paths as paths_module


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
