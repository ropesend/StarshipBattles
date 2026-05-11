"""Issue #19 AC2: superweapon error results must reach a visible UI surface.

The shared chokepoint is `_handle_superweapon_click` in
`game/ui/screens/strategy_click_dispatcher.py`. Any
`{'type': 'error', 'message': ...}` returned by a superweapon designation
handler must be routed to `scene.ui.show_error_message(message)`.

The fix is generic across all five superweapon-target modes:
- IMPLODE_PLANET_TARGET
- STELLERATE_STAR_TARGET
- OPEN_WARP_TARGET
- CLOSE_WARP_TARGET
- DYSON_SPHERE_TARGET
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def dispatcher():
    """Build a ClickModeDispatcher with mocked handler/scene/ui."""
    from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher

    handler = MagicMock()
    handler.input_mode = 'SELECT'
    scene = MagicMock()
    scene.ui = MagicMock()
    scene.ui.show_error_message = MagicMock()
    scene._superweapons = MagicMock()
    scene.selected_fleet = MagicMock()
    handler.scene = scene
    # input_mode setter writes back to handler.input_mode
    type(handler).input_mode = property(
        lambda self: self.__dict__['input_mode'],
        lambda self, v: self.__dict__.__setitem__('input_mode', v),
    )
    dispatcher = ClickModeDispatcher(handler)
    return dispatcher, handler, scene


_SUPERWEAPON_MODES = [
    pytest.param('IMPLODE_PLANET_TARGET', 'handle_implode_planet_designation', id="implode"),
    pytest.param('STELLERATE_STAR_TARGET', 'handle_stellerate_star_designation', id="stellerate"),
    pytest.param('OPEN_WARP_TARGET', 'handle_open_warp_designation', id="open_warp"),
    pytest.param('CLOSE_WARP_TARGET', 'handle_close_warp_designation', id="close_warp"),
    pytest.param('DYSON_SPHERE_TARGET', 'handle_dyson_sphere_designation', id="dyson"),
]


@pytest.mark.parametrize("mode,designation_method", _SUPERWEAPON_MODES)
def test_error_result_is_surfaced_to_user(dispatcher, mode, designation_method):
    """An {'type': 'error', ...} return must invoke scene.ui.show_error_message."""
    disp, handler, scene = dispatcher
    handler.input_mode = mode
    error_message = "Fleet has no Quantum Tunneling Inducer component"
    designation = MagicMock(return_value={'type': 'error', 'message': error_message})
    setattr(scene._superweapons, designation_method, designation)

    result = disp.dispatch_click(100, 200, 1)

    assert result is True
    scene.ui.show_error_message.assert_called_once_with(error_message)
    # After error, input_mode resets to SELECT (caller can pick a new fleet)
    assert handler.input_mode == 'SELECT'


@pytest.mark.parametrize("mode,designation_method", _SUPERWEAPON_MODES)
def test_success_result_does_not_show_error(dispatcher, mode, designation_method):
    """A non-error result (success/prompt) must NOT call show_error_message."""
    disp, handler, scene = dispatcher
    handler.input_mode = mode
    designation = MagicMock(return_value={'type': 'success'})
    setattr(scene._superweapons, designation_method, designation)

    result = disp.dispatch_click(100, 200, 1)

    assert result is True
    scene.ui.show_error_message.assert_not_called()
    assert handler.input_mode == 'SELECT'


@pytest.mark.parametrize("mode,designation_method", _SUPERWEAPON_MODES)
def test_prompt_result_does_not_show_error(dispatcher, mode, designation_method):
    """A 'prompt' result (e.g. system picker) must NOT call show_error_message."""
    disp, handler, scene = dispatcher
    handler.input_mode = mode
    designation = MagicMock(return_value={'type': 'prompt'})
    setattr(scene._superweapons, designation_method, designation)

    result = disp.dispatch_click(100, 200, 1)

    assert result is True
    scene.ui.show_error_message.assert_not_called()


def test_show_error_message_delegates_to_window_manager():
    """StrategyUI.show_error_message routes to window_manager.show_message_dialog."""
    from game.ui.screens.strategy_ui import StrategyUI

    instance = StrategyUI.__new__(StrategyUI)
    instance.window_manager = MagicMock()

    instance.show_error_message("boom")

    instance.window_manager.show_message_dialog.assert_called_once()
    args, _ = instance.window_manager.show_message_dialog.call_args
    # The dialog is invoked with a title and the message
    assert "boom" in args
