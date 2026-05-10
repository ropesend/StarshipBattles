from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.strategy.engine.commands import (
    ClearOrdersCommand,
    ClearPlanetOrdersCommand,
    DeleteOrderCommand,
    DeletePlanetOrderCommand,
    ReorderOrderCommand,
)
from game.ui.screens.strategy_windows.orders_window_ctrl import OrdersRegistrar


def _make_composer(*, existing_window=None) -> SimpleNamespace:
    scene = SimpleNamespace(facade=MagicMock(name="original_facade"))
    return SimpleNamespace(
        width=1200,
        height=800,
        manager=MagicMock(name="ui_manager"),
        _mapper=MagicMock(name="input_mapper"),
        scene=scene,
        fleet_orders_window=existing_window,
    )


def _open_with_mock_window(composer: SimpleNamespace, entity, entity_type: str):
    with patch("game.ui.screens.orders_window.OrdersWindow") as window_cls:
        window_cls.return_value = MagicMock(name="orders_window")
        OrdersRegistrar(composer).open(entity, entity_type=entity_type)
    return window_cls


def test_fleet_callbacks_capture_original_facade_after_scene_rebind() -> None:
    existing_window = MagicMock(name="existing_orders_window")
    composer = _make_composer(existing_window=existing_window)
    fleet = SimpleNamespace(id=7, name="7th Fleet", orders=[])

    window_cls = _open_with_mock_window(composer, fleet, "fleet")
    kwargs = window_cls.call_args.kwargs
    original_facade = composer.scene.facade
    composer.scene.facade = MagicMock(name="replacement_facade")

    kwargs["clear_orders_callback"](fleet.id)
    kwargs["delete_order_callback"](fleet.id, 2)
    kwargs["reorder_order_callback"](fleet.id, 3, -1)

    existing_window.kill.assert_called_once()
    assert composer.fleet_orders_window is window_cls.return_value
    composer.scene.facade.handle_command.assert_not_called()

    commands = [call.args[0] for call in original_facade.handle_command.call_args_list]
    assert [type(cmd) for cmd in commands] == [
        ClearOrdersCommand,
        DeleteOrderCommand,
        ReorderOrderCommand,
    ]
    assert commands[0].fleet_id == fleet.id
    assert commands[1].fleet_id == fleet.id
    assert commands[1].order_index == 2
    assert commands[2].fleet_id == fleet.id
    assert commands[2].order_index == 3
    assert commands[2].direction == -1


def test_planet_callbacks_use_planet_commands_and_do_not_reorder() -> None:
    composer = _make_composer()
    planet = SimpleNamespace(id=42, name="P2 Colony", orders=[])

    window_cls = _open_with_mock_window(composer, planet, "planet")
    kwargs = window_cls.call_args.kwargs
    original_facade = composer.scene.facade
    composer.scene.facade = MagicMock(name="replacement_facade")

    kwargs["clear_orders_callback"](planet.id)
    kwargs["delete_order_callback"](planet.id, 1)
    kwargs["reorder_order_callback"](planet.id, 1, 1)

    composer.scene.facade.handle_command.assert_not_called()
    commands = [call.args[0] for call in original_facade.handle_command.call_args_list]
    assert [type(cmd) for cmd in commands] == [
        ClearPlanetOrdersCommand,
        DeletePlanetOrderCommand,
    ]
    assert commands[0].planet_id == planet.id
    assert commands[1].planet_id == planet.id
    assert commands[1].order_index == 1


def test_edit_callback_forwards_entity_index_and_order_to_scene() -> None:
    composer = _make_composer()
    composer.scene.on_edit_order = MagicMock(name="on_edit_order")
    fleet = SimpleNamespace(id=9, name="Edit Fleet", orders=[])
    order = MagicMock(name="order")

    window_cls = _open_with_mock_window(composer, fleet, "fleet")
    edit_order_callback = window_cls.call_args.kwargs["edit_order_callback"]

    edit_order_callback(fleet.id, 4, order)

    composer.scene.on_edit_order.assert_called_once_with(fleet, 4, order)
