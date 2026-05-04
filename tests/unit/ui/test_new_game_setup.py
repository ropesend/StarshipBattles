"""
Tests for NewGameSetupScreen - new game configuration UI.
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch
import re

from game.core.exceptions import ValidationException


class TestNewGameSetupValidation:
    """Tests for save name validation logic."""

    def test_save_name_not_empty_validation(self):
        """Empty save name rejected with error."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        # Test the static validation method
        is_valid, error = NewGameSetupScreen.validate_save_name("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_save_name_whitespace_only_rejected(self):
        """Whitespace-only save name rejected."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        is_valid, error = NewGameSetupScreen.validate_save_name("   ")
        assert not is_valid
        assert "empty" in error.lower()

    def test_save_name_valid_characters(self):
        """Valid save names with alphanumeric and spaces accepted."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        valid_names = ["MyGame", "Game 1", "Test_Game", "Campaign-2026"]
        for name in valid_names:
            is_valid, error = NewGameSetupScreen.validate_save_name(name)
            assert is_valid, f"'{name}' should be valid: {error}"

    def test_save_name_invalid_characters_rejected(self):
        """Special characters in save name rejected."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        invalid_names = ["Game/1", "Test\\Game", "My:Game", "Game?Name", "Test*Game", "Game<>"]
        for name in invalid_names:
            is_valid, error = NewGameSetupScreen.validate_save_name(name)
            assert not is_valid, f"'{name}' should be invalid"


class TestNewGameSetupValidationUniqueness:
    """Tests for save name uniqueness checking."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

        # Create saves folder with existing save
        self.saves_folder = os.path.join(self.tmpdir, "saves")
        os.makedirs(self.saves_folder)
        os.makedirs(os.path.join(self.saves_folder, "ExistingGame"))

    def teardown_method(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_save_name_unique_accepted(self):
        """Unique save name accepted."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        is_valid, error = NewGameSetupScreen.validate_save_name("NewUniqueName", self.saves_folder)
        assert is_valid

    def test_save_name_duplicate_rejected(self):
        """Duplicate save name rejected."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        is_valid, error = NewGameSetupScreen.validate_save_name("ExistingGame", self.saves_folder)
        assert not is_valid
        assert "exists" in error.lower()


class TestNewGameSetupSystemCountDefault:
    """FEAT-27: default system_count is 2, sourced from GameConfig dataclass."""

    def test_build_game_config_default_system_count_is_2(self):
        """build_game_config uses 2 as the default system_count."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        config = NewGameSetupScreen.build_game_config(
            save_name="DefaultSysCount",
            player_count=1,
            empire_names=["Solo"]
        )

        assert config.system_count == 2

    def test_build_game_config_default_matches_dataclass_constant(self):
        """The default system_count produced by build_game_config matches
        the DEFAULT_SYSTEM_COUNT constant from game_config.

        FEAT-27 single-source-of-truth contract: the UI must NOT hardcode
        the default; it imports DEFAULT_SYSTEM_COUNT so changing one
        place updates both. PROJ-322 Task 5.25 (S08-CAT5-... / APC-002-F09):
        rewritten as a behavioural test (call build_game_config with no
        system_count and observe the resulting GameConfig) instead of
        signature/getsource source-inspection.
        """
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
        from game.strategy.engine.game_config import DEFAULT_SYSTEM_COUNT

        config = NewGameSetupScreen.build_game_config(
            save_name="DefaultSig",
            player_count=1,
            empire_names=["Solo"],
        )
        assert config.system_count == DEFAULT_SYSTEM_COUNT
        assert DEFAULT_SYSTEM_COUNT == 2


class TestSystemCountSliderCurve:
    """FEAT-27: continuous quadratic mapping for the galaxy-size slider.

    Internal slider value t ∈ [0, 1000] maps to game `system_count` ∈ [1, 150]
    via `value = max(1, min(150, int(round(1 + 149 * (t/1000) ** 2))))`.

    The curve is fine-grained at the low end (each thumb-pixel produces a
    1-step change near 1) and coarser at the high end (a thumb-pixel near
    100% drags through ~5–10 systems).
    """

    def test_curve_at_t_zero_returns_1(self):
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        assert system_count_slider_curve(0) == 1

    def test_curve_at_t_max_returns_150(self):
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        assert system_count_slider_curve(1000) == 150

    def test_curve_clamps_below_zero(self):
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        assert system_count_slider_curve(-50) == 1

    def test_curve_clamps_above_max(self):
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        assert system_count_slider_curve(2000) == 150

    def test_curve_low_end_fine_grained(self):
        """Adjacent t values near 0 must yield single-system increments."""
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        prev = system_count_slider_curve(0)
        max_jump = 0
        for t in range(0, 100):
            v = system_count_slider_curve(t)
            max_jump = max(max_jump, v - prev)
            prev = v
        assert max_jump <= 1, (
            f"Low-end curve must give 1-system increments; saw a {max_jump}-system jump"
        )

    def test_curve_high_end_traverses_more_systems_than_low_end(self):
        """Equal slider-travel deltas should cover more systems at the high
        end than at the low end. Concretely, the last 10% of slider travel
        must cover strictly more `system_count` ground than the first 10%.
        This is the user's "fine at low, coarse at high" contract."""
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        low_span = system_count_slider_curve(100) - system_count_slider_curve(0)
        high_span = system_count_slider_curve(1000) - system_count_slider_curve(900)
        assert high_span > low_span, (
            f"High-end must cover more systems than low-end per equal travel; "
            f"low_span={low_span}, high_span={high_span}"
        )
        # Concrete sanity check: the top 10% should cover at least 10x as
        # many systems as the bottom 10% (quadratic gives ~28x in practice).
        assert high_span >= 10 * max(1, low_span), (
            f"High-end span {high_span} should be at least 10x low-end span {low_span}"
        )

    def test_curve_is_monotonic_non_decreasing(self):
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        prev = system_count_slider_curve(0)
        for t in range(1, 1001):
            v = system_count_slider_curve(t)
            assert v >= prev, f"curve regressed at t={t}: {prev} -> {v}"
            prev = v

    def test_curve_landings_cover_full_range(self):
        """Every system_count in [1, 150] must be reachable by some t."""
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        landings = {system_count_slider_curve(t) for t in range(0, 1001)}
        assert 1 in landings and 150 in landings
        assert len(landings) >= 100, (
            f"Curve must produce broad coverage; only {len(landings)} distinct values"
        )

    def test_default_system_count_2_is_reachable(self):
        """The default value 2 must be reachable by some slider position."""
        from game.ui.screens.new_game_setup_screen import system_count_slider_curve
        landings = {system_count_slider_curve(t) for t in range(0, 1001)}
        assert 2 in landings


class TestNewGameSetupConfigBuilding:
    """Tests for GameConfig construction from setup screen."""

    def test_setup_builds_correct_config_1_player(self):
        """Setup produces valid GameConfig for 1 player."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
        from game.strategy.engine.game_config import GameConfig

        config = NewGameSetupScreen.build_game_config(
            save_name="TestGame",
            player_count=1,
            empire_names=["Solo Empire"]
        )

        assert isinstance(config, GameConfig)
        assert config.save_name == "TestGame"
        assert len(config.players) == 1
        assert config.players[0].name == "Solo Empire"

    def test_setup_builds_correct_config_4_players(self):
        """Setup produces valid GameConfig for 4 players."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        # FEAT-27: 4 players require system_count >= 4 at N>=2.
        config = NewGameSetupScreen.build_game_config(
            save_name="BigGame",
            player_count=4,
            empire_names=["Empire A", "Empire B", "Empire C", "Empire D"],
            system_count=4,
        )

        assert len(config.players) == 4
        assert config.players[0].name == "Empire A"
        assert config.players[3].name == "Empire D"

    def test_setup_auto_assigns_themes(self):
        """Themes assigned based on player number."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
        from game.strategy.engine.game_config import THEME_DEFAULTS

        # FEAT-27: 4 players require system_count >= 4 at N>=2.
        config = NewGameSetupScreen.build_game_config(
            save_name="ThemeTest",
            player_count=4,
            empire_names=["E1", "E2", "E3", "E4"],
            system_count=4,
        )

        # Verify themes match THEME_DEFAULTS
        assert config.players[0].theme == THEME_DEFAULTS[0][0]  # Federation
        assert config.players[1].theme == THEME_DEFAULTS[1][0]  # Atlantians
        assert config.players[2].theme == THEME_DEFAULTS[2][0]  # Romulans
        assert config.players[3].theme == THEME_DEFAULTS[3][0]  # Klingons

    def test_setup_auto_assigns_colors(self):
        """Colors assigned based on player number."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
        from game.strategy.engine.game_config import THEME_DEFAULTS

        config = NewGameSetupScreen.build_game_config(
            save_name="ColorTest",
            player_count=2,
            empire_names=["Red", "Green"]
        )

        # Verify colors match THEME_DEFAULTS
        assert config.players[0].color == THEME_DEFAULTS[0][1]
        assert config.players[1].color == THEME_DEFAULTS[1][1]

    def test_setup_uses_default_names_if_empty(self):
        """Default empire names used if not provided."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        config = NewGameSetupScreen.build_game_config(
            save_name="DefaultTest",
            player_count=2,
            empire_names=["", ""]  # Empty names
        )

        # Should use default names
        assert len(config.players[0].name) > 0
        assert len(config.players[1].name) > 0


class TestNewGameSetupRaceConfig:
    """Tests for race_config propagation to PlayerConfig."""

    def test_build_config_passes_race_config(self):
        """Race config should be passed through to PlayerConfig."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
        from game.strategy.data.race_config import RaceConfig

        race = RaceConfig(race_id="test_species", name="Test Species")
        config = NewGameSetupScreen.build_game_config(
            save_name="RaceTest",
            player_count=1,
            empire_names=["Test Empire"],
            race_configs=[race]
        )

        assert config.players[0].race_config is not None, \
            "race_config should be passed to PlayerConfig"
        assert config.players[0].race_config.race_id == "test_species"

    def test_build_config_none_race_config_when_no_race(self):
        """PlayerConfig should have None race_config when no race provided."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        config = NewGameSetupScreen.build_game_config(
            save_name="NoRaceTest",
            player_count=1,
            empire_names=["Test Empire"],
            race_configs=None
        )

        assert config.players[0].race_config is None


class TestNewGameSetupDefaultSaveName:
    """Tests for auto-generated default save name."""

    def test_default_save_name_starts_with_save_game(self):
        """Default save name starts with 'save game'."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        name = NewGameSetupScreen.generate_default_save_name()
        assert name.startswith("save game ")

    def test_default_save_name_contains_timestamp(self):
        """Default save name contains a date-time timestamp."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        name = NewGameSetupScreen.generate_default_save_name()
        # Should match pattern: "save game YYYY-MM-DD HHMM"
        assert re.match(r"save game \d{4}-\d{2}-\d{2} \d{4}$", name), \
            f"Expected 'save game YYYY-MM-DD HHMM' pattern, got: '{name}'"

    def test_default_save_name_passes_validation(self):
        """Default save name passes save name validation."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        name = NewGameSetupScreen.generate_default_save_name()
        is_valid, error = NewGameSetupScreen.validate_save_name(name)
        assert is_valid, f"Default save name '{name}' failed validation: {error}"


class TestNewGameSetupPlayerCount:
    """Tests for player count handling."""

    def test_player_count_options_1_to_4(self):
        """Player count options available: 1, 2, 3, 4."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        options = NewGameSetupScreen.get_player_count_options()

        assert options == [1, 2, 3, 4]

    def test_build_config_rejects_invalid_count(self):
        """Building config with invalid player count raises error."""
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        with pytest.raises(ValidationException):
            NewGameSetupScreen.build_game_config(
                save_name="Test",
                player_count=5,  # Invalid
                empire_names=["E1", "E2", "E3", "E4", "E5"]
            )

        with pytest.raises(ValidationException):
            NewGameSetupScreen.build_game_config(
                save_name="Test",
                player_count=0,  # Invalid
                empire_names=[]
            )


class TestSetupRacePassesLoadedData:
    """BUG-92: Verify Setup Species passes loaded race data to RaceSetupScreen."""

    def _make_screen(self):
        """PROJ-328 Phase B: build via real two-stage construction."""
        import pygame
        from tests.fixtures.ui_widget_factory import bypass_init, make_ui_widget
        from tests.fixtures.new_game_setup_ui_builder import (
            MockNewGameSetupUiBuilder,
        )
        from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

        ui_manager = MagicMock(name="ui_manager")
        ui_manager.window_resolution = (1920, 1080)

        with bypass_init(NewGameSetupScreen):
            screen = make_ui_widget(
                NewGameSetupScreen,
                rect=pygame.Rect(0, 0, 650, 600),
                manager=ui_manager,
                on_start_callback=MagicMock(),
                on_cancel_callback=MagicMock(),
                ui_builder=MockNewGameSetupUiBuilder(),
            )
        # ``ui_manager`` defaults to a MagicMock with no
        # ``window_resolution``; replace with the configured one.
        screen.ui_manager = ui_manager
        return screen

    def test_setup_race_passes_loaded_race(self):
        """When a race is already loaded, Setup Species should pass it as race_to_edit."""
        from game.strategy.data.race_config import RaceConfig

        loaded_race = RaceConfig(race_id="loaded_species", name="Loaded Species")

        screen = self._make_screen()
        screen.player_races[0] = loaded_race

        with patch('game.ui.screens.race_setup_screen.RaceSetupScreen') as MockRaceSetup:
            screen._on_setup_race_clicked(0)

            MockRaceSetup.assert_called_once()
            call_kwargs = MockRaceSetup.call_args
            # race_to_edit should be the loaded race, not None
            assert call_kwargs.kwargs.get('race_to_edit') is loaded_race or \
                   (len(call_kwargs.args) > 4 and call_kwargs.args[4] is loaded_race), \
                "race_to_edit should be the loaded race config"

    def test_setup_race_no_loaded_race_passes_none(self):
        """When no race is loaded, Setup Species should pass None as race_to_edit."""
        screen = self._make_screen()
        # All player_races already default to None from the view model.

        with patch('game.ui.screens.race_setup_screen.RaceSetupScreen') as MockRaceSetup:
            screen._on_setup_race_clicked(0)

            MockRaceSetup.assert_called_once()
            call_kwargs = MockRaceSetup.call_args
            # race_to_edit should be None
            race_to_edit = call_kwargs.kwargs.get('race_to_edit')
            assert race_to_edit is None, \
                "race_to_edit should be None when no race is loaded"
