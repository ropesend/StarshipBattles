from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pygame
import pytest

from game.ui.screens.test_lab.screen_input_handler import TestLabInputHandler as InputHandler


def _event(event_type: int, **attrs: object) -> pygame.event.Event:
    return pygame.event.Event(event_type, attrs)


def _panel(name: str, consumed: bool) -> MagicMock:
    panel = MagicMock(name=name)
    panel.handle_event.return_value = consumed
    return panel


@pytest.fixture
def handler_context():
    ui_state = MagicMock()
    ui_state.get_selected_category.return_value = None
    controller = SimpleNamespace(ui_state=ui_state)
    callbacks = {
        "continue_batch": MagicMock(),
        "on_run": MagicMock(),
        "on_run_headless": MagicMock(),
        "on_run_visual_baseline": MagicMock(),
        "on_run_all": MagicMock(),
        "create_ship_panels": MagicMock(),
        "create_results_panel": MagicMock(),
        "prompt_custom_seed": MagicMock(),
    }
    viewmodel = SimpleNamespace(
        confirmation_dialog=None,
        json_popup=None,
        tabbed_ship_panel=None,
        ship_panels=[],
        component_panels=[],
        results_panel=None,
        test_details_panel=None,
        group_header_rects={},
        category_rects={},
        tag_filter_rects={},
        tag_clear_rect=None,
        run_all_tests_btn_rect=None,
        run_test_btn_rect=None,
        run_headless_btn_rect=None,
        run_baseline_btn_rect=None,
        seed_mode_rects={},
        seed_input_rect=None,
        test_list_panel_rect=None,
        scroll_offset=0,
        scroll=MagicMock(),
        close_confirmation_dialog=MagicMock(),
        close_json_popup=MagicMock(),
    )
    handler = InputHandler(viewmodel, controller, registry=MagicMock(), callbacks=callbacks)
    executor = SimpleNamespace(batch_running=False)
    return SimpleNamespace(
        handler=handler,
        viewmodel=viewmodel,
        ui_state=ui_state,
        callbacks=callbacks,
        executor=executor,
    )


def _handle(ctx, event: pygame.event.Event, scenarios: dict[str, object] | None = None) -> bool:
    return ctx.handler.handle_event(event, scenarios or {}, [], ctx.executor)


def test_timer_event_continues_batch_and_consumes(handler_context) -> None:
    ctx = handler_context

    consumed = _handle(ctx, _event(pygame.USEREVENT + 1))

    assert consumed is True
    ctx.callbacks["continue_batch"].assert_called_once_with()


def test_confirmation_dialog_blocks_panels_and_closes_when_dialog_closes(handler_context) -> None:
    ctx = handler_context
    dialog = MagicMock()
    dialog.is_open = True
    dialog.handle_event.side_effect = lambda event: setattr(dialog, "is_open", False)
    ctx.viewmodel.confirmation_dialog = dialog
    ctx.viewmodel.json_popup = MagicMock(is_open=True)
    ctx.viewmodel.results_panel = _panel("results", True)

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(1, 1), button=1))

    assert consumed is True
    dialog.handle_event.assert_called_once()
    ctx.viewmodel.close_confirmation_dialog.assert_called_once_with()
    ctx.viewmodel.close_json_popup.assert_not_called()
    ctx.viewmodel.results_panel.handle_event.assert_not_called()


def test_json_popup_handles_events_when_no_confirmation_dialog(handler_context) -> None:
    ctx = handler_context
    popup = MagicMock()
    popup.is_open = True
    popup.handle_event.side_effect = lambda event: setattr(popup, "is_open", False)
    ctx.viewmodel.json_popup = popup

    consumed = _handle(ctx, _event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

    assert consumed is True
    popup.handle_event.assert_called_once()
    ctx.viewmodel.close_json_popup.assert_called_once_with()


@pytest.mark.parametrize(
    "consuming_slot",
    ["tabbed", "ship", "component", "results", "details"],
)
def test_panel_dispatch_stops_at_first_consuming_panel(handler_context, consuming_slot: str) -> None:
    ctx = handler_context
    panels = {
        "tabbed": _panel("tabbed", consuming_slot == "tabbed"),
        "ship": _panel("ship", consuming_slot == "ship"),
        "component": _panel("component", consuming_slot == "component"),
        "results": _panel("results", consuming_slot == "results"),
        "details": _panel("details", consuming_slot == "details"),
    }
    ctx.viewmodel.tabbed_ship_panel = panels["tabbed"]
    ctx.viewmodel.ship_panels = [panels["ship"]]
    ctx.viewmodel.component_panels = [panels["component"]]
    ctx.viewmodel.results_panel = panels["results"]
    ctx.viewmodel.test_details_panel = panels["details"]

    consumed = _handle(ctx, _event(pygame.KEYUP, key=pygame.K_SPACE))

    assert consumed is True
    panels[consuming_slot].handle_event.assert_called_once()
    ordered_slots = ["tabbed", "ship", "component", "results", "details"]
    for later_slot in ordered_slots[ordered_slots.index(consuming_slot) + 1:]:
        panels[later_slot].handle_event.assert_not_called()


def test_mousewheel_inside_test_list_scrolls(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.test_list_panel_rect = pygame.Rect(260, 120, 420, 200)

    with patch("game.ui.screens.test_lab.screen_input_handler.pygame.mouse.get_pos", return_value=(300, 140)):
        consumed = _handle(ctx, _event(pygame.MOUSEWHEEL, y=2))

    assert consumed is True
    ctx.viewmodel.scroll.assert_called_once_with(-80)


def test_mousewheel_outside_test_list_does_not_scroll(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.test_list_panel_rect = pygame.Rect(260, 120, 420, 200)

    with patch("game.ui.screens.test_lab.screen_input_handler.pygame.mouse.get_pos", return_value=(20, 20)):
        consumed = _handle(ctx, _event(pygame.MOUSEWHEEL, y=1))

    assert consumed is False
    ctx.viewmodel.scroll.assert_not_called()


def test_mousemotion_sets_all_tests_hover_without_consuming(handler_context) -> None:
    ctx = handler_context

    consumed = _handle(ctx, _event(pygame.MOUSEMOTION, pos=(25, 145)))

    assert consumed is False
    ctx.ui_state.set_category_hover.assert_has_calls([call(None), call("ALL")])
    ctx.ui_state.set_test_hover.assert_called_once_with(None)


def test_mousemotion_sets_group_header_hover(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.group_header_rects = {"Weapons": pygame.Rect(20, 200, 200, 30)}

    _handle(ctx, _event(pygame.MOUSEMOTION, pos=(25, 205)))

    ctx.ui_state.set_category_hover.assert_has_calls([call(None), call("GROUP:Weapons")])


def test_mousemotion_sets_visible_test_hover_with_scroll_offset(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.test_list_panel_rect = pygame.Rect(260, 120, 420, 200)
    ctx.viewmodel.scroll_offset = 55

    consumed = _handle(
        ctx,
        _event(pygame.MOUSEMOTION, pos=(265, 145)),
        scenarios={"B": object(), "A": object()},
    )

    assert consumed is False
    ctx.ui_state.set_test_hover.assert_has_calls([call(None), call("B")])


def test_left_click_all_tests_clears_selection(handler_context) -> None:
    ctx = handler_context

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(25, 145), button=1))

    assert consumed is True
    ctx.ui_state.select_category.assert_called_once_with(None)
    ctx.ui_state.select_group.assert_called_once_with(None)
    ctx.ui_state.select_test.assert_called_once_with(None)


def test_group_header_click_toggles_and_selects_group(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.group_header_rects = {"Propulsion": pygame.Rect(20, 190, 200, 30)}

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(30, 195), button=1))

    assert consumed is True
    ctx.ui_state.toggle_group.assert_called_once_with("Propulsion")
    ctx.ui_state.select_group.assert_called_once_with("Propulsion")
    ctx.ui_state.select_test.assert_called_once_with(None)


def test_category_click_toggles_selected_category_off(handler_context) -> None:
    ctx = handler_context
    ctx.ui_state.get_selected_category.return_value = "Weapons"
    ctx.viewmodel.category_rects = {"Weapons": pygame.Rect(35, 240, 180, 30)}

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(40, 245), button=1))

    assert consumed is True
    ctx.ui_state.select_category.assert_called_once_with(None)
    ctx.ui_state.select_test.assert_called_once_with(None)


def test_tag_filter_click_cycles_state(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.tag_filter_rects = {"smoke": pygame.Rect(700, 40, 80, 28)}

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(710, 45), button=1))

    assert consumed is True
    ctx.ui_state.cycle_tag_state.assert_called_once_with("smoke")


def test_run_all_click_is_consumed_but_suppressed_while_batch_running(handler_context) -> None:
    ctx = handler_context
    ctx.executor.batch_running = True
    ctx.viewmodel.run_all_tests_btn_rect = pygame.Rect(300, 80, 120, 32)

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(310, 90), button=1))

    assert consumed is True
    ctx.callbacks["on_run_all"].assert_not_called()


def test_test_item_click_selects_test_and_rebuilds_panels(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.test_list_panel_rect = pygame.Rect(260, 120, 420, 200)

    consumed = _handle(
        ctx,
        _event(pygame.MOUSEBUTTONDOWN, pos=(265, 145), button=1),
        scenarios={"B": object(), "A": object()},
    )

    assert consumed is True
    ctx.ui_state.select_test.assert_called_once_with("A")
    ctx.callbacks["create_ship_panels"].assert_called_once_with("A")
    ctx.callbacks["create_results_panel"].assert_called_once_with("A")


@pytest.mark.parametrize(
    ("rect_attr", "callback_name"),
    [
        ("run_test_btn_rect", "on_run"),
        ("run_headless_btn_rect", "on_run_headless"),
        ("run_baseline_btn_rect", "on_run_visual_baseline"),
    ],
)
def test_action_button_clicks_call_callbacks(handler_context, rect_attr: str, callback_name: str) -> None:
    ctx = handler_context
    setattr(ctx.viewmodel, rect_attr, pygame.Rect(800, 300, 140, 32))

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(810, 310), button=1))

    assert consumed is True
    ctx.callbacks[callback_name].assert_called_once_with()


def test_seed_mode_click_sets_mode(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.seed_mode_rects = {"fixed": pygame.Rect(500, 400, 80, 30)}

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(510, 410), button=1))

    assert consumed is True
    ctx.ui_state.set_seed_mode.assert_called_once_with("fixed")


def test_seed_input_click_prompts_custom_seed(handler_context) -> None:
    ctx = handler_context
    ctx.viewmodel.seed_input_rect = pygame.Rect(590, 400, 120, 30)

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(600, 410), button=1))

    assert consumed is True
    ctx.callbacks["prompt_custom_seed"].assert_called_once_with()


def test_right_click_does_not_consume_even_on_clickable_area(handler_context) -> None:
    ctx = handler_context

    consumed = _handle(ctx, _event(pygame.MOUSEBUTTONDOWN, pos=(25, 145), button=3))

    assert consumed is False
    ctx.ui_state.select_test.assert_not_called()
