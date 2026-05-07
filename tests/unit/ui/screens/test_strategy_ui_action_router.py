from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.input_actions import InputAction
from game.ui.screens.strategy_ui_action_router import UIActionRouter


def _scene() -> SimpleNamespace:
    return SimpleNamespace(
        _camera_nav=MagicMock(),
        ui=MagicMock(),
        advance_turn=MagicMock(),
        on_design_click=MagicMock(),
        on_save_game_click=MagicMock(),
        cycle_selection=MagicMock(),
    )


@pytest.mark.parametrize(
    ("action", "target", "args"),
    [
        (InputAction.STRATEGY_ZOOM_GALAXY, "_camera_nav.zoom_to_galaxy", ()),
        (InputAction.STRATEGY_ZOOM_SYSTEM, "_camera_nav.zoom_to_system", ()),
        (InputAction.STRATEGY_ZOOM_IN, "_camera_nav.zoom_in_step", ()),
        (InputAction.STRATEGY_ZOOM_OUT, "_camera_nav.zoom_out_step", ()),
        (InputAction.STRATEGY_NEXT_TURN, "advance_turn", ()),
        (InputAction.STRATEGY_OPEN_PLANETS, "ui.open_planet_list", ()),
        (InputAction.STRATEGY_OPEN_DESIGN, "on_design_click", ()),
        (InputAction.STRATEGY_OPEN_BUILD_QUEUES, "ui.open_build_queue_list", ()),
        (InputAction.STRATEGY_OPEN_EMPIRE, "ui.open_empire_panel", ()),
        (InputAction.STRATEGY_SAVE_GAME, "on_save_game_click", ()),
        (InputAction.STRATEGY_PREV_COLONY, "cycle_selection", ("colony", -1)),
        (InputAction.STRATEGY_NEXT_COLONY, "cycle_selection", ("colony", 1)),
        (InputAction.STRATEGY_PREV_FLEET, "cycle_selection", ("fleet", -1)),
        (InputAction.STRATEGY_NEXT_FLEET, "cycle_selection", ("fleet", 1)),
    ],
)
def test_ui_action_router_routes_strategy_actions(action, target, args):
    scene = _scene()
    router = UIActionRouter(SimpleNamespace(scene=scene))

    handled = router.handle_ui_action(action)

    assert handled is True
    call_target = scene
    for part in target.split("."):
        call_target = getattr(call_target, part)
    call_target.assert_called_once_with(*args)


def test_ui_action_router_returns_false_for_non_ui_action():
    scene = _scene()
    router = UIActionRouter(SimpleNamespace(scene=scene))

    handled = router.handle_ui_action(InputAction.FLEET_MOVE)

    assert handled is False
    scene._camera_nav.assert_not_called()
    scene.ui.assert_not_called()
    scene.advance_turn.assert_not_called()
    scene.on_design_click.assert_not_called()
    scene.on_save_game_click.assert_not_called()
    scene.cycle_selection.assert_not_called()
