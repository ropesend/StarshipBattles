"""
Tests for QuickstartBuilder - Factory for creating pre-configured game sessions.

Tests cover:
- Fixture path functions (get_quickstart_fixtures_dir, get_quickstart_races_dir, get_quickstart_designs_dir)
- QuickstartBuilder.load_test_race (valid, missing, invalid JSON)
- QuickstartBuilder.build_1p_config (returns GameConfig, player count, is_human, prefix, defaults)
- QuickstartBuilder.build_2p_config (player count, both human)
- QuickstartBuilder.copy_quickstart_designs (success, missing dir, copy errors)
- QuickstartBuilder.spawn_initial_complexes (success, no colonies, missing designs)
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from game.strategy.quickstart_builder import (
    get_quickstart_fixtures_dir,
    get_quickstart_races_dir,
    get_quickstart_designs_dir,
    QuickstartBuilder,
    INITIAL_COMPLEXES,
)
from game.strategy.engine.game_config import GameConfig
from game.strategy.data.race_config import RaceConfig


class TestFixturePathFunctions:
    """Tests for fixture directory path functions."""

    def test_get_quickstart_fixtures_dir_returns_path(self):
        """get_quickstart_fixtures_dir returns a Path object."""
        result = get_quickstart_fixtures_dir()

        assert isinstance(result, Path)

    def test_get_quickstart_races_dir_under_fixtures(self):
        """get_quickstart_races_dir returns a subdir of fixtures."""
        fixtures_dir = get_quickstart_fixtures_dir()
        races_dir = get_quickstart_races_dir()

        assert races_dir.parent == fixtures_dir
        assert races_dir.name == "races"

    def test_get_quickstart_designs_dir_under_fixtures(self):
        """get_quickstart_designs_dir returns a subdir of fixtures."""
        fixtures_dir = get_quickstart_fixtures_dir()
        designs_dir = get_quickstart_designs_dir()

        assert designs_dir.parent == fixtures_dir
        assert designs_dir.name == "designs"


class TestQuickstartBuilderLoadTestRace:
    """Tests for QuickstartBuilder.load_test_race method."""

    def test_load_test_race_valid_file(self):
        """load_test_race returns RaceConfig when file exists and is valid."""
        # Use the actual test fixture
        result = QuickstartBuilder.load_test_race("test_emp1.json")

        assert result is not None
        assert isinstance(result, RaceConfig)
        assert result.race_id == "test_emp1"
        assert result.name == "TestEmp1"

    def test_load_test_race_missing_file(self):
        """load_test_race returns None when file doesn't exist."""
        result = QuickstartBuilder.load_test_race("nonexistent_race.json")

        assert result is None

    def test_load_test_race_invalid_json(self):
        """load_test_race returns None on parse failure."""
        # Mock load_json to simulate a JSON parse error (returns None)
        with patch("game.strategy.quickstart_builder.load_json", return_value=None):
            # Need a file that "exists" but has invalid JSON
            with patch.object(Path, "exists", return_value=True):
                result = QuickstartBuilder.load_test_race("invalid.json")

        assert result is None


class TestQuickstartBuilderBuild1PConfig:
    """Tests for QuickstartBuilder.build_1p_config method."""

    def test_build_1p_returns_game_config(self):
        """build_1p_config returns a GameConfig instance."""
        result = QuickstartBuilder.build_1p_config()

        assert isinstance(result, GameConfig)

    def test_build_1p_single_player(self):
        """build_1p_config creates exactly 1 player."""
        result = QuickstartBuilder.build_1p_config()

        assert len(result.players) == 1

    def test_build_1p_player_is_human(self):
        """build_1p_config player has is_human=True."""
        result = QuickstartBuilder.build_1p_config()

        assert result.players[0].is_human is True

    def test_build_1p_custom_prefix(self):
        """build_1p_config save_name starts with custom prefix."""
        custom_prefix = "MyCustomGame"
        result = QuickstartBuilder.build_1p_config(save_name_prefix=custom_prefix)

        assert result.save_name.startswith(custom_prefix)

    def test_build_1p_default_parameters(self):
        """build_1p_config uses default galaxy_radius=8000 and system_count=100."""
        result = QuickstartBuilder.build_1p_config()

        assert result.galaxy_radius == 8000
        assert result.system_count == 100
        assert result.galaxy_type == "spiral"


class TestQuickstartBuilderBuild2PConfig:
    """Tests for QuickstartBuilder.build_2p_config method."""

    def test_build_2p_has_two_players(self):
        """build_2p_config creates exactly 2 players."""
        result = QuickstartBuilder.build_2p_config()

        assert len(result.players) == 2

    def test_build_2p_both_human(self):
        """build_2p_config both players have is_human=True."""
        result = QuickstartBuilder.build_2p_config()

        assert result.players[0].is_human is True
        assert result.players[1].is_human is True


class TestQuickstartBuilderCopyDesigns:
    """Tests for QuickstartBuilder.copy_quickstart_designs method."""

    def test_copy_quickstart_designs_missing_source_dir(self):
        """copy_quickstart_designs returns False when source dir missing."""
        with patch.object(Path, "exists", return_value=False):
            result = QuickstartBuilder.copy_quickstart_designs("/fake/path", [1, 2])

        assert result is False

    def test_copy_quickstart_designs_no_design_files(self, tmp_path):
        """copy_quickstart_designs returns False when no design files exist."""
        # Create empty source dir
        source_dir = tmp_path / "designs"
        source_dir.mkdir()

        with patch(
            "game.strategy.quickstart_builder.get_quickstart_designs_dir",
            return_value=source_dir
        ):
            result = QuickstartBuilder.copy_quickstart_designs(str(tmp_path / "save"), [1])

        assert result is False

    def test_copy_quickstart_designs_creates_empire_folders(self, tmp_path):
        """copy_quickstart_designs creates empire_{id}/designs folders."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test_design.json").write_text('{"name": "test"}')

        save_path = tmp_path / "save"
        save_path.mkdir()

        with patch(
            "game.strategy.quickstart_builder.get_quickstart_designs_dir",
            return_value=source_dir
        ):
            result = QuickstartBuilder.copy_quickstart_designs(str(save_path), [1, 2])

        assert result is True
        assert (save_path / "designs" / "empire_1").exists()
        assert (save_path / "designs" / "empire_2").exists()

    def test_copy_quickstart_designs_copies_all_design_files(self, tmp_path):
        """copy_quickstart_designs copies all JSON files to each empire."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "design_a.json").write_text('{"name": "A"}')
        (source_dir / "design_b.json").write_text('{"name": "B"}')

        save_path = tmp_path / "save"
        save_path.mkdir()

        with patch(
            "game.strategy.quickstart_builder.get_quickstart_designs_dir",
            return_value=source_dir
        ):
            result = QuickstartBuilder.copy_quickstart_designs(str(save_path), [1])

        assert result is True
        empire_designs = save_path / "designs" / "empire_1"
        assert (empire_designs / "design_a.json").exists()
        assert (empire_designs / "design_b.json").exists()

    def test_copy_quickstart_designs_handles_copy_error(self, tmp_path):
        """copy_quickstart_designs returns False on copy errors."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test_design.json").write_text('{"name": "test"}')

        save_path = tmp_path / "save"
        save_path.mkdir()

        with patch(
            "game.strategy.quickstart_builder.get_quickstart_designs_dir",
            return_value=source_dir
        ):
            with patch("shutil.copy2", side_effect=OSError("Permission denied")):
                result = QuickstartBuilder.copy_quickstart_designs(str(save_path), [1])

        assert result is False


class TestQuickstartBuilderSpawnComplexes:
    """Tests for QuickstartBuilder.spawn_initial_complexes method."""

    def test_spawn_initial_complexes_no_empires(self, tmp_path):
        """spawn_initial_complexes returns True with no empires."""
        session = MagicMock()
        session.empires = []

        result = QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        assert result is True

    def test_spawn_initial_complexes_empire_no_colonies(self, tmp_path):
        """spawn_initial_complexes skips empires with no colonies."""
        empire = MagicMock()
        empire.id = 1
        empire.colonies = []

        session = MagicMock()
        session.empires = [empire]

        result = QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # Returns True, just skips that empire
        assert result is True

    def test_spawn_initial_complexes_uses_first_colony_as_home(self, tmp_path):
        """spawn_initial_complexes adds facilities to first colony."""
        home_planet = MagicMock()
        home_planet.name = "Home World"
        home_planet.facilities = []

        empire = MagicMock()
        empire.id = 1
        empire.colonies = [home_planet]

        session = MagicMock()
        session.empires = [empire]

        # Mock DesignLibrary to return valid design data
        mock_design_data = {"name": "Test Complex", "components": []}
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = mock_design_data
            MockLibrary.return_value = mock_lib

            result = QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # Should have added facilities to home_planet
        assert len(home_planet.facilities) == len(INITIAL_COMPLEXES)

    def test_spawn_initial_complexes_missing_design_returns_partial_success(self, tmp_path):
        """spawn_initial_complexes returns False when design missing."""
        home_planet = MagicMock()
        home_planet.name = "Home World"
        home_planet.facilities = []

        empire = MagicMock()
        empire.id = 1
        empire.colonies = [home_planet]

        session = MagicMock()
        session.empires = [empire]

        # Mock DesignLibrary to return None (design not found)
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = None
            MockLibrary.return_value = mock_lib

            result = QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # Returns False because designs couldn't be loaded
        assert result is False

    def test_spawn_initial_complexes_creates_planetary_facility(self, tmp_path):
        """spawn_initial_complexes creates PlanetaryFacility instances."""
        from game.strategy.data.planet import PlanetaryFacility

        home_planet = MagicMock()
        home_planet.name = "Home World"
        home_planet.facilities = []

        empire = MagicMock()
        empire.id = 1
        empire.colonies = [home_planet]

        session = MagicMock()
        session.empires = [empire]

        mock_design_data = {"name": "Test Complex", "components": []}
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = mock_design_data
            MockLibrary.return_value = mock_lib

            QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # All facilities should be PlanetaryFacility instances
        assert all(
            isinstance(f, PlanetaryFacility)
            for f in home_planet.facilities
        )

    def test_spawn_initial_complexes_facilities_are_operational(self, tmp_path):
        """spawn_initial_complexes creates operational facilities."""
        home_planet = MagicMock()
        home_planet.name = "Home World"
        home_planet.facilities = []

        empire = MagicMock()
        empire.id = 1
        empire.colonies = [home_planet]

        session = MagicMock()
        session.empires = [empire]

        mock_design_data = {"name": "Test Complex", "components": []}
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = mock_design_data
            MockLibrary.return_value = mock_lib

            QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # All facilities should be operational
        assert all(f.is_operational for f in home_planet.facilities)

    def test_spawn_initial_complexes_multiple_empires(self, tmp_path):
        """spawn_initial_complexes handles multiple empires."""
        home1 = MagicMock()
        home1.name = "Home 1"
        home1.facilities = []

        home2 = MagicMock()
        home2.name = "Home 2"
        home2.facilities = []

        empire1 = MagicMock()
        empire1.id = 1
        empire1.colonies = [home1]

        empire2 = MagicMock()
        empire2.id = 2
        empire2.colonies = [home2]

        session = MagicMock()
        session.empires = [empire1, empire2]

        mock_design_data = {"name": "Test Complex", "components": []}
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = mock_design_data
            MockLibrary.return_value = mock_lib

            result = QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        assert result is True
        assert len(home1.facilities) == len(INITIAL_COMPLEXES)
        assert len(home2.facilities) == len(INITIAL_COMPLEXES)

    def test_spawn_initial_complexes_unique_instance_ids(self, tmp_path):
        """spawn_initial_complexes creates unique instance IDs."""
        home_planet = MagicMock()
        home_planet.name = "Home World"
        home_planet.facilities = []

        empire = MagicMock()
        empire.id = 1
        empire.colonies = [home_planet]

        session = MagicMock()
        session.empires = [empire]

        mock_design_data = {"name": "Test Complex", "components": []}
        with patch(
            "game.strategy.quickstart_builder.DesignLibrary"
        ) as MockLibrary:
            mock_lib = MagicMock()
            mock_lib.load_design_data.return_value = mock_design_data
            MockLibrary.return_value = mock_lib

            QuickstartBuilder.spawn_initial_complexes(str(tmp_path), session)

        # All instance_ids should be unique
        instance_ids = [f.instance_id for f in home_planet.facilities]
        assert len(instance_ids) == len(set(instance_ids))
