from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.strategy.data.race_config import RaceConfig
from game.ui.screens.race_setup.controller import RaceSetupController
from game.ui.screens.race_setup.view_model import RaceSetupViewModel


def _valid_config(**overrides) -> RaceConfig:
    data = {
        "race_id": "race-1",
        "name": "Rossarian",
        "race_name": "Rossarian",
        "flag_id": "flag_a",
        "portrait_id": "portrait_a",
        "theme_id": "Federation",
    }
    data.update(overrides)
    return RaceConfig(**data)


def _screen_stub(race_config: RaceConfig) -> SimpleNamespace:
    return SimpleNamespace(
        race_config=race_config,
        is_editing=False,
        ui_manager=MagicMock(name="ui_manager"),
        error_label=MagicMock(name="error_label"),
        btn_save=MagicMock(name="btn_save"),
        race_browser=None,
        kill=MagicMock(name="kill"),
        get_abs_rect=MagicMock(return_value=pygame.Rect(100, 50, 1000, 800)),
        _identity_panel=None,
        _flag_gallery=None,
        _portrait_gallery=None,
        _theme_gallery=None,
        _environment_panel=None,
        _aptitudes_panel=None,
        _description_panel=None,
        _summary_panel=None,
    )


def _controller(
    race_config: RaceConfig | None = None,
    *,
    screen: SimpleNamespace | None = None,
) -> tuple[RaceSetupController, SimpleNamespace, RaceSetupViewModel, MagicMock]:
    config = race_config or _valid_config()
    screen = screen or _screen_stub(config)
    view_model = RaceSetupViewModel(is_editing=screen.is_editing)
    renderer = MagicMock(name="renderer")
    race_library = MagicMock(name="race_library")
    controller = RaceSetupController(
        screen=screen,
        view_model=view_model,
        renderer=renderer,
        race_config=config,
        race_library=race_library,
        race_registry=MagicMock(name="race_registry"),
        on_complete_callback=MagicMock(name="on_complete_callback"),
        on_cancel_callback=MagicMock(name="on_cancel_callback"),
    )
    return controller, screen, view_model, renderer


def test_description_controller_change_updates_panel_state() -> None:
    controller, screen, _, _ = _controller()
    description_panel = MagicMock(name="description_panel")
    description_controller = MagicMock(name="description_controller")
    screen._description_panel = description_panel

    controller.attach_description_controller(description_controller)
    controller.on_description_controller_change()

    description_panel.set_state.assert_called_once_with(description_controller)


def test_on_theme_selected_updates_config_and_refreshes_preview() -> None:
    controller, _, _, renderer = _controller()

    controller.on_theme_selected("Klingons")

    assert controller.race_config.theme_id == "Klingons"
    renderer.refresh_ship_preview.assert_called_once_with("Klingons")


def test_validate_for_save_syncs_identity_name_before_validator() -> None:
    controller, screen, _, _ = _controller()
    screen._identity_panel = MagicMock(name="identity_panel")

    def update_identity() -> None:
        controller.race_config.race_name = "Updated Species"

    screen._identity_panel.update_config.side_effect = update_identity

    with patch("game.ui.screens.race_setup.controller.RaceValidator") as validator:
        validator.return_value.validate.return_value = SimpleNamespace(
            is_valid=True,
            message="",
        )
        is_valid, message = controller.validate_for_save()

    assert is_valid is True
    assert message == ""
    assert controller.race_config.name == "Updated Species"
    validator.return_value.validate.assert_called_once_with(controller.race_config)


def test_validate_for_save_returns_aptitude_budget_error() -> None:
    controller, screen, _, _ = _controller()
    screen._aptitudes_panel = MagicMock(name="aptitudes_panel")

    with (
        patch("game.strategy.data.race_point_budget.RacePointBudget") as budget_cls,
        patch("game.ui.screens.race_setup.controller.RaceValidator") as validator,
    ):
        budget = budget_cls.return_value
        budget.is_within_budget.return_value = False
        budget.get_remaining_points.return_value = -7
        is_valid, message = controller.validate_for_save()

    assert is_valid is False
    assert message == "Over budget by 7 points (Aptitudes tab)"
    screen._aptitudes_panel.update_config.assert_called_once()
    validator.return_value.validate.assert_not_called()


def test_on_load_race_opens_centered_browser_dialog() -> None:
    controller, screen, _, _ = _controller()

    with patch(
        "game.ui.screens.race_setup.controller.RaceBrowserDialog"
    ) as dialog_cls:
        controller.on_load_race()

    rect = dialog_cls.call_args.kwargs["rect"]
    assert rect.topleft == (300, 200)
    assert rect.size == (600, 500)
    assert dialog_cls.call_args.kwargs["manager"] is screen.ui_manager
    assert dialog_cls.call_args.kwargs["race_library"] is controller.race_library
    assert dialog_cls.call_args.kwargs["on_select_callback"] == controller.on_race_selected
    assert screen.race_browser is dialog_cls.return_value


def test_on_race_selected_mirrors_config_and_refreshes_all_panels() -> None:
    controller, screen, view_model, _ = _controller()
    panels = [
        "_identity_panel",
        "_flag_gallery",
        "_portrait_gallery",
        "_theme_gallery",
        "_environment_panel",
        "_aptitudes_panel",
        "_description_panel",
        "_summary_panel",
    ]
    for attr in panels:
        setattr(screen, attr, MagicMock(name=attr))
    description_controller = MagicMock(name="description_controller")
    controller.attach_description_controller(description_controller)
    loaded = _valid_config(name="Loaded", race_name="Loaded")

    controller.on_race_selected(loaded)

    assert controller.race_config is loaded
    assert screen.race_config is loaded
    assert view_model.is_editing is True
    assert screen.is_editing is True
    for attr in panels:
        assert getattr(screen, attr).race_config is loaded
    description_controller.set_race_config.assert_called_once_with(loaded)
    screen._identity_panel.set_from_config.assert_called_once()
    screen._flag_gallery.set_from_config.assert_called_once()
    screen._portrait_gallery.set_from_config.assert_called_once()
    screen._theme_gallery.set_from_config.assert_called_once()
    screen._environment_panel.set_from_config.assert_called_once()
    screen._aptitudes_panel.set_from_config.assert_called_once()
    screen._description_panel.set_from_config.assert_called_once()
    screen._summary_panel.refresh.assert_called_once()
    screen.btn_save.set_text.assert_called_once_with("Update")


def test_on_save_invalid_config_shows_error_without_saving() -> None:
    controller, screen, _, _ = _controller()
    controller.validate_for_save = MagicMock(return_value=(False, "bad config"))

    controller.on_save()

    screen.error_label.set_text.assert_called_once_with("bad config")
    controller.race_library.save_race.assert_not_called()


def test_on_save_editing_existing_race_prompts_update_dialog() -> None:
    controller, _, view_model, renderer = _controller()
    view_model.is_editing = True
    controller.race_config.race_id = "existing"
    controller.validate_for_save = MagicMock(return_value=(True, ""))
    controller.race_config.validate = MagicMock(
        return_value=SimpleNamespace(is_valid=True, message="")
    )

    controller.on_save()

    renderer.show_save_update_dialog.assert_called_once()
    controller.race_library.save_race.assert_not_called()


def test_do_save_success_invalidates_registry_completes_and_kills() -> None:
    controller, screen, _, _ = _controller()
    controller.race_library.save_race.return_value = (True, "saved")

    controller.do_save()

    controller.race_registry.invalidate.assert_called_once_with("race-1")
    controller.on_complete_callback.assert_called_once_with(controller.race_config)
    screen.kill.assert_called_once()


def test_do_save_failure_displays_library_message() -> None:
    controller, screen, _, _ = _controller()
    controller.race_library.save_race.return_value = (False, "disk full")

    controller.do_save()

    screen.error_label.set_text.assert_called_once_with("disk full")
    controller.on_complete_callback.assert_not_called()
    screen.kill.assert_not_called()


def test_on_save_as_new_clears_id_and_editing_before_save() -> None:
    controller, screen, view_model, renderer = _controller()
    view_model.is_editing = True
    screen.is_editing = True
    controller.race_config.race_id = "existing"
    controller.do_save = MagicMock(name="do_save")

    controller.on_save_as_new()

    renderer.close_save_update_dialog.assert_called_once()
    assert controller.race_config.race_id is None
    assert view_model.is_editing is False
    assert screen.is_editing is False
    screen.btn_save.set_text.assert_called_once_with("Save")
    controller.do_save.assert_called_once()


def test_on_cancel_invokes_callback_and_kills_screen() -> None:
    controller, screen, _, _ = _controller()

    controller.on_cancel()

    controller.on_cancel_callback.assert_called_once()
    screen.kill.assert_called_once()


def test_description_panel_update_helpers_delegate_when_present() -> None:
    controller, screen, _, _ = _controller()
    screen._description_panel = MagicMock(name="description_panel")

    controller.update_description_char_counts()
    controller.update_descriptions_from_text()

    screen._description_panel.update_char_counts.assert_called_once()
    screen._description_panel.update_config.assert_called_once()
