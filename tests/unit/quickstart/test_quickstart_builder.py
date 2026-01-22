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

from game.strategy.quickstart_builder import (
    QuickstartBuilder,
    get_quickstart_fixtures_dir,
    get_quickstart_races_dir,
    get_quickstart_designs_dir,
)
from game.strategy.engine.game_config import GameConfig, PlayerConfig


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
