"""Tests for NewGameSetupController (PROJ-328 Phase B).

Covers the cheap pure-Python pieces of the controller: save-name
validation, ``GameConfig`` building, and the race-modal callback
state machine. The "open modal" callbacks (``on_load_race_clicked``,
``on_setup_race_clicked``) instantiate live ``pygame_gui`` modal
windows so they're exercised by the screen integration tests at
``test_new_game_setup_extended.py``, not duplicated here.
"""

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from game.core.exceptions import ValidationException
from game.strategy.engine.game_config import (
    GameConfig,
    THEME_DEFAULTS,
)
from game.ui.screens.new_game_setup_controller import NewGameSetupController
from game.ui.screens.new_game_setup_view_model import NewGameSetupViewModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_controller(
    *,
    player_count: int = 2,
    on_start_callback=None,
    on_cancel_callback=None,
):
    """Build a controller wired to a mock screen + a real view model."""
    screen = MagicMock(name="screen")
    screen.save_name_input = MagicMock(name="save_name_input")
    screen.error_label = MagicMock(name="error_label")
    screen.empire_name_inputs = [MagicMock() for _ in range(4)]
    # ``type(screen).validate_save_name`` is dispatched by the
    # controller; route to the controller's own static so tests don't
    # need to redefine it.
    type(screen).validate_save_name = NewGameSetupController.validate_save_name

    vm = NewGameSetupViewModel(player_count=player_count)
    controller = NewGameSetupController(
        screen=screen,
        view_model=vm,
        race_library=MagicMock(name="race_library"),
        on_start_callback=on_start_callback or MagicMock(name="on_start"),
        on_cancel_callback=on_cancel_callback or MagicMock(name="on_cancel"),
    )
    return controller, screen, vm


def _make_race(name="Test Race"):
    race = MagicMock()
    race.name = name
    race.faction_name = ""
    race.theme_id = "Federation"
    race.flag_id = "flag_01"
    race.portrait_id = "portrait_01"
    race.race_id = "race_01"
    race.government_type = ""
    race.society_type = ""
    return race


# ---------------------------------------------------------------------------
# validate_save_name
# ---------------------------------------------------------------------------


class TestValidateSaveName:
    def test_empty_name_invalid(self):
        ok, err = NewGameSetupController.validate_save_name("")
        assert not ok
        assert "empty" in err.lower()

    def test_whitespace_name_invalid(self):
        ok, err = NewGameSetupController.validate_save_name("   ")
        assert not ok

    @pytest.mark.parametrize("bad", ["a/b", "a\\b", "a:b", "a*b", "a?b"])
    def test_invalid_filesystem_chars_rejected(self, bad):
        ok, err = NewGameSetupController.validate_save_name(bad)
        assert not ok
        assert "invalid characters" in err.lower()

    def test_simple_name_valid(self):
        ok, err = NewGameSetupController.validate_save_name("MyGame")
        assert ok
        assert err == ""

    def test_uniqueness_check_against_existing_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "Existing"))
            ok, err = NewGameSetupController.validate_save_name(
                "Existing", saves_folder=tmpdir
            )
            assert not ok
            assert "already exists" in err.lower()

    def test_uniqueness_check_passes_for_new_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ok, err = NewGameSetupController.validate_save_name(
                "Brand New", saves_folder=tmpdir
            )
            assert ok


# ---------------------------------------------------------------------------
# build_game_config
# ---------------------------------------------------------------------------


class TestBuildGameConfig:
    def test_invalid_player_count_raises(self):
        with pytest.raises(ValidationException):
            NewGameSetupController.build_game_config(
                "Save", 0, [], None, "spiral", 10
            )

    def test_too_many_players_raises(self):
        with pytest.raises(ValidationException):
            NewGameSetupController.build_game_config(
                "Save", 5, [], None, "spiral", 10
            )

    def test_basic_config_uses_default_themes(self):
        cfg = NewGameSetupController.build_game_config(
            "Save", 2, ["A", "B"], None, "spiral", 10
        )
        assert isinstance(cfg, GameConfig)
        assert cfg.save_name == "Save"
        assert cfg.galaxy_type == "spiral"
        assert cfg.system_count == 10
        assert len(cfg.players) == 2
        assert cfg.players[0].name == "A"
        assert cfg.players[1].name == "B"
        assert cfg.players[0].theme == THEME_DEFAULTS[0][0]
        assert cfg.players[1].theme == THEME_DEFAULTS[1][0]

    def test_race_name_overrides_empire_name(self):
        race = _make_race(name="Klingon Empire")
        cfg = NewGameSetupController.build_game_config(
            "Save", 1, ["IgnoredName"], [race], "spiral", 10
        )
        assert cfg.players[0].name == "Klingon Empire"

    def test_race_theme_overrides_default(self):
        race = _make_race()
        race.theme_id = "Klingons"
        cfg = NewGameSetupController.build_game_config(
            "Save", 1, [""], [race], "spiral", 10
        )
        assert cfg.players[0].theme == "Klingons"

    def test_empty_empire_name_falls_back_to_default(self):
        cfg = NewGameSetupController.build_game_config(
            "Save", 1, [""], None, "spiral", 10
        )
        assert cfg.players[0].name == "Empire 1"


# ---------------------------------------------------------------------------
# Race-modal callbacks (state-only — no real modal construction)
# ---------------------------------------------------------------------------


class TestRaceModalCallbacks:
    def test_on_race_selected_sets_race_and_clears_modal(self):
        controller, screen, vm = _make_controller()
        modal = MagicMock(name="modal")
        vm.open_race_modal(modal, 1)
        race = _make_race()

        controller.on_race_selected(1, race)

        assert vm.get_race(1) is race
        assert vm.active_race_modal is None
        assert vm.race_modal_player_index == -1
        screen._update_race_display.assert_called_once_with(1)

    def test_on_race_created_sets_race_and_clears_modal(self):
        controller, screen, vm = _make_controller()
        race = _make_race(name="New Race")

        controller.on_race_created(0, race)

        assert vm.get_race(0) is race
        assert vm.active_race_modal is None
        screen._update_race_display.assert_called_once_with(0)

    def test_on_race_dialog_cancelled_clears_modal_only(self):
        controller, screen, vm = _make_controller()
        original_race = _make_race(name="Existing")
        vm.set_race(2, original_race)
        vm.open_race_modal(MagicMock(), 2)

        controller.on_race_dialog_cancelled()

        assert vm.active_race_modal is None
        assert vm.race_modal_player_index == -1
        # Race selection unchanged.
        assert vm.get_race(2) is original_race


# ---------------------------------------------------------------------------
# Start / Cancel flow
# ---------------------------------------------------------------------------


class TestOnStartClicked:
    def test_invalid_save_name_sets_error_no_callback(self):
        on_start = MagicMock(name="on_start")
        controller, screen, _ = _make_controller(on_start_callback=on_start)
        screen.save_name_input.get_text.return_value = ""

        controller.on_start_clicked()

        screen.error_label.set_text.assert_called()
        on_start.assert_not_called()
        screen.kill.assert_not_called()

    def test_invalid_chars_in_save_name_blocks_callback(self):
        on_start = MagicMock(name="on_start")
        controller, screen, _ = _make_controller(on_start_callback=on_start)
        screen.save_name_input.get_text.return_value = "bad/name"

        controller.on_start_clicked()

        on_start.assert_not_called()
        screen.kill.assert_not_called()

    def test_value_error_from_build_config_sets_error_label(self):
        """ValueError raised from build_game_config is surfaced to the
        error label instead of bubbling out and the start callback
        does NOT fire."""
        from unittest.mock import patch as mpatch
        on_start = MagicMock(name="on_start")
        controller, screen, _ = _make_controller(on_start_callback=on_start)
        screen.save_name_input.get_text.return_value = "ValidName"
        for inp in screen.empire_name_inputs:
            inp.get_text.return_value = "Empire"

        with mpatch.object(
            NewGameSetupController,
            "build_game_config",
            side_effect=ValueError("nope"),
        ):
            controller.on_start_clicked()

        screen.error_label.set_text.assert_called()
        on_start.assert_not_called()


    def test_PROJ466_session_init_error_keeps_window_alive_shows_error(self):
        """PROJ-466 Phase 1 Task 1.2: when the start callback raises
        SessionInitializationError (galaxy-generation failure), the window
        stays alive (NOT killed) and the error label is set, instead of the
        error propagating to the top-level crash handler."""
        from game.core.exceptions import SessionInitializationError

        def boom(_config):
            raise SessionInitializationError(
                "galaxy generation failed",
                context={"original_type": "ValidationException"},
            )

        controller, screen, vm = _make_controller(on_start_callback=boom)
        screen.save_name_input.get_text.return_value = "ValidName"
        for inp in screen.empire_name_inputs:
            inp.get_text.return_value = "Empire"

        # Must NOT raise.
        controller.on_start_clicked()

        screen.error_label.set_text.assert_called()
        screen.kill.assert_not_called()

    def test_PROJ466_real_router_callback_does_not_swallow_keeps_window_alive(
        self, monkeypatch
    ):
        """PROJ-466 Phase 4 Task 4.1: the REAL router callback
        (`ScreenRouter._on_new_game_start`) must let SessionInitializationError
        propagate so the controller — the owner of the new-game failure UX —
        keeps the window alive and shows the error. This is the composition
        the per-component Phase 1 tests missed: if the router swallows, the
        controller's catch is dead and the window is killed anyway."""
        import sys
        from types import SimpleNamespace

        from game.core.exceptions import SessionInitializationError

        class FailingGameSession:
            def __init__(self, *a, **k):
                raise SessionInitializationError("galaxy generation failed")

        monkeypatch.setitem(
            sys.modules,
            "game.strategy.engine.game_session",
            SimpleNamespace(GameSession=FailingGameSession),
        )
        monkeypatch.setitem(
            sys.modules,
            "game.ai.ai_factory",
            SimpleNamespace(AIControllerFactory=lambda: object()),
        )

        # Build a real ScreenRouter-bound callback without constructing the
        # whole router: bind the unbound method to a minimal stand-in that
        # provides only what _on_new_game_start touches before GameSession().
        from game.screen_router import ScreenRouter

        router_stub = SimpleNamespace()
        callback = ScreenRouter._on_new_game_start.__get__(router_stub, ScreenRouter)

        controller, screen, vm = _make_controller(on_start_callback=callback)
        screen.save_name_input.get_text.return_value = "ValidName"
        for inp in screen.empire_name_inputs:
            inp.get_text.return_value = "Empire"

        # Must NOT raise (controller catches the propagated error).
        controller.on_start_clicked()

        screen.error_label.set_text.assert_called()
        screen.kill.assert_not_called()


class TestOnCancelClicked:
    def test_fires_callback_and_kills(self):
        on_cancel = MagicMock(name="on_cancel")
        controller, screen, _ = _make_controller(on_cancel_callback=on_cancel)

        controller.on_cancel_clicked()

        on_cancel.assert_called_once()
        screen.kill.assert_called_once()
