"""
Tests for QuickstartBuilder - Factory for creating pre-configured game sessions.

Tests cover:
- Fixture path functions (get_quickstart_fixtures_dir, get_quickstart_races_dir, get_quickstart_designs_dir)
- QuickstartBuilder.load_test_race (valid, missing, invalid JSON)
- QuickstartBuilder.build_1p_config (returns GameConfig, player count, is_human, prefix, defaults)
- QuickstartBuilder.build_2p_config (player count, both human)
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from game.strategy.quickstart_builder import (
    get_quickstart_fixtures_dir,
    get_quickstart_races_dir,
    get_quickstart_designs_dir,
    QuickstartBuilder,
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
