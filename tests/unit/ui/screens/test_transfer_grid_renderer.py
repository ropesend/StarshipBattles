from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.transfer_grid_renderer import TransferGridRenderer


def _widget_factory(name: str):
    def _make(*args, **kwargs):
        widget = MagicMock(name=name)
        widget.relative_rect = kwargs.get("relative_rect", args[0] if args else None)
        widget.text = kwargs.get("text", args[1] if len(args) > 1 else None)
        widget.ui_container = kwargs.get("container", MagicMock(name="ui_container"))
        return widget

    return _make


def _make_dialog() -> SimpleNamespace:
    return SimpleNamespace(
        rect=pygame.Rect(0, 0, 900, 700),
        ui_manager=MagicMock(name="ui_manager"),
        _grid_widgets=[],
        _arrow_buttons={},
        _max_buttons={},
        _zero_buttons={},
        _pending_labels={},
    )


def test_build_chrome_constructs_dropdown_grid_and_bottom_buttons() -> None:
    renderer = TransferGridRenderer()
    dialog = _make_dialog()

    with (
        patch(
            "game.ui.screens.transfer_grid_renderer.UILabel",
            side_effect=_widget_factory("label"),
        ) as label_cls,
        patch(
            "game.ui.screens.transfer_grid_renderer.UIDropDownMenu",
            side_effect=_widget_factory("dropdown"),
        ) as dropdown_cls,
        patch(
            "game.ui.screens.transfer_grid_renderer.UIButton",
            side_effect=_widget_factory("button"),
        ) as button_cls,
        patch(
            "game.ui.screens.transfer_grid_renderer.UIScrollingContainer",
            side_effect=_widget_factory("scrolling_container"),
        ) as container_cls,
    ):
        renderer.build_chrome(dialog)

    assert label_cls.call_count == 5
    assert dropdown_cls.call_count == 2
    assert button_cls.call_count == 4
    assert container_cls.call_count == 1
    assert dropdown_cls.call_args_list[0].kwargs["options_list"] == [""]
    assert dropdown_cls.call_args_list[0].kwargs["starting_option"] == ""
    assert dropdown_cls.call_args_list[1].kwargs["options_list"] == [""]
    assert dropdown_cls.call_args_list[1].kwargs["starting_option"] == ""
    assert dialog.btn_filter.text == "Filter Empty"
    assert dialog.btn_confirm.text == "Confirm All"
    assert dialog.btn_clear_all.text == "Clear All"
    assert dialog.btn_cancel.text == "Cancel"
    assert dialog.grid_container.relative_rect == pygame.Rect(10, 75, 860, 505)
    assert dialog._grid_top_y == 75


def test_build_grid_clears_old_widgets_and_populates_row_maps() -> None:
    renderer = TransferGridRenderer()
    dialog = _make_dialog()
    dialog.grid_container = MagicMock(name="grid_container")
    dialog.grid_container.relative_rect = pygame.Rect(0, 0, 900, 300)
    old_widget = MagicMock(name="old_widget")
    dialog._grid_widgets = [old_widget]
    dialog._arrow_buttons = {1: ("stale", 1)}
    dialog._max_buttons = {2: ("stale", "load")}
    dialog._zero_buttons = {3: "stale"}
    dialog._pending_labels = {"stale": MagicMock()}
    dialog.view_model = MagicMock(name="view_model")
    dialog.view_model.visible_rows.return_value = [
        {
            "cargo_key": "metals",
            "display_name": "Metals",
            "source_amt": 12,
            "target_amt": 3,
        },
        {
            "cargo_key": "fuel",
            "display_name": "Fuel",
            "source_amt": 0,
            "target_amt": 9,
        },
    ]
    dialog.view_model.get_pending.side_effect = lambda key: {"metals": 5}.get(key, 0)
    dialog.view_model.format_pending.side_effect = lambda value: f"pending:{value}"

    with (
        patch(
            "game.ui.screens.transfer_grid_renderer.UILabel",
            side_effect=_widget_factory("label"),
        ),
        patch(
            "game.ui.screens.transfer_grid_renderer.UIButton",
            side_effect=_widget_factory("button"),
        ),
    ):
        renderer.build_grid(dialog)

    old_widget.kill.assert_called_once()
    assert len(dialog._grid_widgets) == 34
    assert len(dialog._arrow_buttons) == 20
    assert sorted(dialog._max_buttons.values()) == [
        ("fuel", "drop"),
        ("fuel", "load"),
        ("metals", "drop"),
        ("metals", "load"),
    ]
    assert sorted(dialog._zero_buttons.values()) == ["fuel", "metals"]
    assert set(dialog._pending_labels) == {"metals", "fuel"}
    assert ("metals", 100000) in dialog._arrow_buttons.values()
    assert ("metals", -100000) in dialog._arrow_buttons.values()
    dialog.grid_container.set_scrollable_area_dimensions.assert_called_once_with(
        (880, 100)
    )


def test_recreate_dropdown_kills_old_and_selects_available_fallback() -> None:
    renderer = TransferGridRenderer()
    dialog = _make_dialog()
    old_dropdown = MagicMock(name="old_dropdown")
    old_dropdown.relative_rect = pygame.Rect(1, 2, 3, 4)
    old_dropdown.ui_container = MagicMock(name="old_container")

    with patch(
        "game.ui.screens.transfer_grid_renderer.UIDropDownMenu",
        side_effect=_widget_factory("dropdown"),
    ) as dropdown_cls:
        result = renderer.recreate_dropdown(
            dialog, old_dropdown, ["Alpha", "Beta"], "Missing"
        )

    old_dropdown.kill.assert_called_once()
    assert result.relative_rect == pygame.Rect(1, 2, 3, 4)
    assert result.ui_container is old_dropdown.ui_container
    kwargs = dropdown_cls.call_args.kwargs
    assert kwargs["options_list"] == ["Alpha", "Beta"]
    assert kwargs["starting_option"] == "Alpha"
    assert kwargs["relative_rect"] == pygame.Rect(1, 2, 3, 4)
    assert kwargs["container"] is old_dropdown.ui_container


def test_recreate_dropdown_uses_blank_option_when_options_empty() -> None:
    renderer = TransferGridRenderer()
    dialog = _make_dialog()
    old_dropdown = MagicMock(name="old_dropdown")
    old_dropdown.relative_rect = pygame.Rect(1, 2, 3, 4)
    old_dropdown.ui_container = MagicMock(name="old_container")

    with patch(
        "game.ui.screens.transfer_grid_renderer.UIDropDownMenu",
        side_effect=_widget_factory("dropdown"),
    ) as dropdown_cls:
        renderer.recreate_dropdown(dialog, old_dropdown, [], "Missing")

    old_dropdown.kill.assert_called_once()
    kwargs = dropdown_cls.call_args.kwargs
    assert kwargs["options_list"] == [""]
    assert kwargs["starting_option"] == ""


def test_update_pending_label_and_filter_button_ignore_missing_widgets() -> None:
    renderer = TransferGridRenderer()
    dialog = _make_dialog()
    dialog.view_model = MagicMock(name="view_model")
    dialog.view_model.get_pending.return_value = 12
    dialog.view_model.format_pending.return_value = "Load 12"
    label = MagicMock(name="pending_label")
    dialog._pending_labels["metals"] = label
    dialog.btn_filter = MagicMock(name="filter_button")

    renderer.update_pending_label(dialog, "metals")
    renderer.update_pending_label(dialog, "fuel")
    renderer.set_filter_button_text(dialog, True)
    dialog.btn_filter = None
    renderer.set_filter_button_text(dialog, False)

    label.set_text.assert_called_once_with("Load 12")
    dialog.view_model.get_pending.assert_called_once_with("metals")


def test_extract_dropdown_value_accepts_tuple_or_plain_value() -> None:
    assert TransferGridRenderer.extract_dropdown_value(("Fleet 1", "#id")) == "Fleet 1"
    assert TransferGridRenderer.extract_dropdown_value("Fleet 2") == "Fleet 2"
