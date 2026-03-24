"""
Tests for QuickstartBuilder module.

Tests that the builder creates valid game configurations and
correctly loads race fixtures.
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import MagicMock

from game.strategy.quickstart_builder import (
    QuickstartBuilder,
    get_quickstart_fixtures_dir,
    get_quickstart_races_dir,
    get_quickstart_designs_dir,
    INITIAL_COMPLEXES,
)
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.data.planet import PlanetaryFacility


class TestQuickstartBuilderPaths:
    """Test that fixture paths resolve correctly."""

    def test_fixtures_dir_exists(self):
        """Quickstart fixtures directory should exist."""
        fixtures_dir = get_quickstart_fixtures_dir()
        assert fixtures_dir.exists(), f"Fixtures dir not found: {fixtures_dir}"

    def test_races_dir_exists(self):
        """Quickstart races directory should exist."""
        races_dir = get_quickstart_races_dir()
        assert races_dir.exists(), f"Races dir not found: {races_dir}"

    def test_designs_dir_exists(self):
        """Quickstart designs directory should exist."""
        designs_dir = get_quickstart_designs_dir()
        assert designs_dir.exists(), f"Designs dir not found: {designs_dir}"


class TestQuickstartBuilderRaceLoading:
    """Test race fixture loading."""

    def test_load_test_emp1(self):
        """Should load test_emp1 race."""
        race = QuickstartBuilder.load_test_race("test_emp1.json")
        assert race is not None
        assert race.name == "TestEmp1"
        assert race.theme_id == "Federation"

    def test_load_test_emp2(self):
        """Should load test_emp2 race."""
        race = QuickstartBuilder.load_test_race("test_emp2.json")
        assert race is not None
        assert race.name == "TestEmp2"
        assert race.theme_id == "Atlantians"

    def test_load_nonexistent_race_returns_none(self):
        """Loading nonexistent race should return None."""
        race = QuickstartBuilder.load_test_race("nonexistent.json")
        assert race is None


class TestQuickstartBuilder1PConfig:
    """Tests for 1-player quickstart configuration."""

    def test_build_1p_config_returns_game_config(self):
        """build_1p_config should return a GameConfig."""
        config = QuickstartBuilder.build_1p_config()
        assert isinstance(config, GameConfig)

    def test_build_1p_config_has_one_player(self):
        """1P config should have exactly 1 player."""
        config = QuickstartBuilder.build_1p_config()
        assert len(config.players) == 1

    def test_build_1p_config_player_is_human(self):
        """1P config player should be human."""
        config = QuickstartBuilder.build_1p_config()
        assert config.players[0].is_human is True

    def test_build_1p_config_save_name_has_timestamp(self):
        """Save name should include timestamp."""
        config = QuickstartBuilder.build_1p_config()
        # Format: Quickstart_1P_YYYYMMDD_HHMMSS
        assert config.save_name.startswith("Quickstart_1P_")
        assert len(config.save_name) > len("Quickstart_1P_")

    def test_build_1p_config_custom_prefix(self):
        """Should support custom save name prefix."""
        config = QuickstartBuilder.build_1p_config(save_name_prefix="Test1P")
        assert config.save_name.startswith("Test1P_")

    def test_build_1p_config_loads_race_data(self):
        """Should load race data from fixture."""
        config = QuickstartBuilder.build_1p_config()
        player = config.players[0]
        # If fixture loaded correctly, should have race data
        assert player.name == "TestEmp1"
        assert player.flag_id != ""
        assert player.portrait_id != ""

    def test_build_1p_config_custom_galaxy_params(self):
        """Should support custom galaxy parameters."""
        config = QuickstartBuilder.build_1p_config(
            galaxy_radius=5000,
            system_count=30
        )
        assert config.galaxy_radius == 5000
        assert config.system_count == 30


class TestQuickstartBuilder2PConfig:
    """Tests for 2-player quickstart configuration."""

    def test_build_2p_config_returns_game_config(self):
        """build_2p_config should return a GameConfig."""
        config = QuickstartBuilder.build_2p_config()
        assert isinstance(config, GameConfig)

    def test_build_2p_config_has_two_players(self):
        """2P config should have exactly 2 players."""
        config = QuickstartBuilder.build_2p_config()
        assert len(config.players) == 2

    def test_build_2p_config_both_players_human(self):
        """Both players should be human."""
        config = QuickstartBuilder.build_2p_config()
        assert config.players[0].is_human is True
        assert config.players[1].is_human is True

    def test_build_2p_config_players_have_different_themes(self):
        """Players should have different themes."""
        config = QuickstartBuilder.build_2p_config()
        assert config.players[0].theme != config.players[1].theme

    def test_build_2p_config_players_have_different_colors(self):
        """Players should have different colors."""
        config = QuickstartBuilder.build_2p_config()
        assert config.players[0].color != config.players[1].color

    def test_build_2p_config_save_name_has_timestamp(self):
        """Save name should include timestamp."""
        config = QuickstartBuilder.build_2p_config()
        assert config.save_name.startswith("Quickstart_2P_")


class TestQuickstartBuilderDesignCopying:
    """Tests for design file copying."""

    @pytest.fixture
    def temp_save_folder(self):
        """Create a temporary save folder."""
        folder = tempfile.mkdtemp()
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_copy_designs_creates_folders(self, temp_save_folder):
        """Should create empire design folders."""
        result = QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        assert result is True

        empire_folder = Path(temp_save_folder) / "designs" / "empire_0"
        assert empire_folder.exists()

    def test_copy_designs_copies_files(self, temp_save_folder):
        """Should copy design JSON files."""
        result = QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        assert result is True

        empire_folder = Path(temp_save_folder) / "designs" / "empire_0"
        design_files = list(empire_folder.glob("*.json"))
        assert len(design_files) >= 2  # At least qs_escort and qs_complex

    def test_copy_designs_multiple_empires(self, temp_save_folder):
        """Should copy to multiple empire folders."""
        result = QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0, 1])
        assert result is True

        for empire_id in [0, 1]:
            empire_folder = Path(temp_save_folder) / "designs" / f"empire_{empire_id}"
            assert empire_folder.exists()
            design_files = list(empire_folder.glob("*.json"))
            assert len(design_files) >= 2


    def test_copy_designs_applies_empire_themes(self, temp_save_folder):
        """BUG-102: Copied designs should have theme_id updated to match each empire's theme."""
        import json

        empire_themes = {0: "Federation", 1: "Klingons"}
        result = QuickstartBuilder.copy_quickstart_designs(
            temp_save_folder, [0, 1], empire_themes=empire_themes
        )
        assert result is True

        # Check empire 0 designs have Federation theme
        empire_0_folder = Path(temp_save_folder) / "designs" / "empire_0"
        for design_file in empire_0_folder.glob("*.json"):
            with open(design_file) as f:
                data = json.load(f)
            if "theme_id" in data:
                assert data["theme_id"] == "Federation", (
                    f"{design_file.name}: expected Federation, got {data['theme_id']}"
                )

        # Check empire 1 designs have Klingons theme
        empire_1_folder = Path(temp_save_folder) / "designs" / "empire_1"
        for design_file in empire_1_folder.glob("*.json"):
            with open(design_file) as f:
                data = json.load(f)
            if "theme_id" in data:
                assert data["theme_id"] == "Klingons", (
                    f"{design_file.name}: expected Klingons, got {data['theme_id']}"
                )

    def test_copy_designs_without_themes_preserves_original(self, temp_save_folder):
        """Backward compat: without empire_themes, designs keep original theme_id."""
        import json

        result = QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        assert result is True

        empire_folder = Path(temp_save_folder) / "designs" / "empire_0"
        for design_file in empire_folder.glob("*.json"):
            with open(design_file) as f:
                data = json.load(f)
            # Original template theme should be preserved (Federation)
            if "theme_id" in data:
                assert data["theme_id"] == "Federation"


class TestInitialComplexesConstant:
    """Tests for the INITIAL_COMPLEXES constant."""

    def test_initial_complexes_has_seven_entries(self):
        """Should have exactly 7 complex design IDs."""
        assert len(INITIAL_COMPLEXES) == 7

    def test_initial_complexes_includes_shipyard(self):
        """Should include the existing qs_complex shipyard."""
        assert 'qs_complex' in INITIAL_COMPLEXES

    def test_initial_complexes_includes_all_resource_types(self):
        """Should include complexes for all 5 resource types."""
        assert 'qs_metals_complex' in INITIAL_COMPLEXES
        assert 'qs_organics_complex' in INITIAL_COMPLEXES
        assert 'qs_vapors_complex' in INITIAL_COMPLEXES
        assert 'qs_radioactives_complex' in INITIAL_COMPLEXES
        assert 'qs_exotics_complex' in INITIAL_COMPLEXES

    def test_initial_complexes_includes_resupply_depot(self):
        """Should include the resupply depot."""
        assert 'qs_resupply_depot' in INITIAL_COMPLEXES

    def test_initial_complexes_are_strings(self):
        """All entries should be strings."""
        for design_id in INITIAL_COMPLEXES:
            assert isinstance(design_id, str)


class TestSpawnInitialComplexes:
    """Tests for QuickstartBuilder.spawn_initial_complexes()."""

    @pytest.fixture
    def temp_save_folder(self):
        """Create a temporary save folder with designs copied."""
        folder = tempfile.mkdtemp()
        # Copy quickstart designs for empire 0
        QuickstartBuilder.copy_quickstart_designs(folder, [0])
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    @pytest.fixture
    def temp_save_folder_2p(self):
        """Create a temporary save folder with designs for 2 empires."""
        folder = tempfile.mkdtemp()
        QuickstartBuilder.copy_quickstart_designs(folder, [0, 1])
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def _make_mock_planet(name="Home Planet"):
        """Create a mock planet with facilities list."""
        planet = MagicMock()
        planet.name = name
        planet.facilities = []
        return planet

    @staticmethod
    def _make_mock_empire(empire_id=0, colonies=None):
        """Create a mock empire with colonies."""
        empire = MagicMock()
        empire.id = empire_id
        empire.colonies = colonies if colonies is not None else []
        return empire

    @staticmethod
    def _make_mock_session(empires=None):
        """Create a mock game session."""
        session = MagicMock()
        session.empires = empires if empires is not None else []
        return session

    def test_spawns_seven_complexes_on_home_planet(self, temp_save_folder):
        """Should spawn all 7 complexes on the home planet."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        assert result is True
        assert len(planet.facilities) == 7

    def test_spawned_facilities_are_planetary_facility(self, temp_save_folder):
        """Each spawned facility should be a PlanetaryFacility instance."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        for facility in planet.facilities:
            assert isinstance(facility, PlanetaryFacility)

    def test_spawned_facilities_are_operational(self, temp_save_folder):
        """All spawned facilities should be operational."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        for facility in planet.facilities:
            assert facility.is_operational is True

    def test_spawned_facilities_have_unique_ids(self, temp_save_folder):
        """Each facility should have a unique instance_id."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        instance_ids = [f.instance_id for f in planet.facilities]
        assert len(instance_ids) == len(set(instance_ids)), "Instance IDs must be unique"

    def test_spawned_facilities_have_design_data(self, temp_save_folder):
        """Each facility should have populated design_data."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        for facility in planet.facilities:
            assert isinstance(facility.design_data, dict)
            assert len(facility.design_data) > 0, f"design_data empty for {facility.design_id}"

    def test_spawned_facilities_have_correct_design_ids(self, temp_save_folder):
        """Spawned facility design_ids should match INITIAL_COMPLEXES."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        spawned_ids = {f.design_id for f in planet.facilities}
        expected_ids = set(INITIAL_COMPLEXES)
        assert spawned_ids == expected_ids

    def test_spawned_facilities_have_names(self, temp_save_folder):
        """Each facility should have a non-empty name from design data."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        for facility in planet.facilities:
            assert facility.name, f"Facility {facility.design_id} has no name"

    def test_two_empires_both_get_complexes(self, temp_save_folder_2p):
        """Both empires should get all 7 complexes on their home planets."""
        planet1 = self._make_mock_planet("Home 1")
        planet2 = self._make_mock_planet("Home 2")
        empire1 = self._make_mock_empire(0, colonies=[planet1])
        empire2 = self._make_mock_empire(1, colonies=[planet2])
        session = self._make_mock_session(empires=[empire1, empire2])

        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder_2p, session)

        assert result is True
        assert len(planet1.facilities) == 7
        assert len(planet2.facilities) == 7

    def test_empire_with_no_colonies_skipped(self, temp_save_folder):
        """Empire with no colonies should be skipped gracefully."""
        empire = self._make_mock_empire(0, colonies=[])
        session = self._make_mock_session(empires=[empire])

        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        # Still returns True overall - just warns and skips
        assert result is True

    def test_returns_true_on_success(self, temp_save_folder):
        """Should return True when all complexes spawn successfully."""
        planet = self._make_mock_planet()
        empire = self._make_mock_empire(0, colonies=[planet])
        session = self._make_mock_session(empires=[empire])

        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        assert result is True

    def test_empty_empires_returns_true(self, temp_save_folder):
        """No empires should return True (nothing to do, no failure)."""
        session = self._make_mock_session(empires=[])

        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        assert result is True

    def test_uses_first_colony_as_home_planet(self, temp_save_folder):
        """Should spawn complexes on first colony only."""
        home = self._make_mock_planet("Home")
        second = self._make_mock_planet("Second Colony")
        empire = self._make_mock_empire(0, colonies=[home, second])
        session = self._make_mock_session(empires=[empire])

        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        assert len(home.facilities) == 7
        assert len(second.facilities) == 0
