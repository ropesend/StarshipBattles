"""Focused tests for strategy fleet-operation branch logic."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.ui.screens.strategy_fleet_ops import FleetOperations


def _fleet(
    fleet_id: int = 1,
    owner_id: int = 7,
    *,
    is_building: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(id=fleet_id, owner_id=owner_id, is_building=is_building)


def _fleet_info(fleet_id: int, owner_id: int = 7) -> SimpleNamespace:
    return SimpleNamespace(fleet_id=fleet_id, owner_id=owner_id)


def _ops() -> tuple[FleetOperations, SimpleNamespace, MagicMock]:
    scene = SimpleNamespace(
        camera=MagicMock(),
        empires=[],
        hex_size=10,
    )
    scene.camera.screen_to_world.return_value = SimpleNamespace(x=100.0, y=200.0)
    facade = MagicMock()
    return FleetOperations(scene, facade), scene, facade


def test_get_fleet_at_hex_returns_first_facade_result() -> None:
    ops, _scene, facade = _ops()
    first = _fleet_info(1)
    facade.get_fleets_at_hex.return_value = [first, _fleet_info(2)]

    assert ops.get_fleet_at_hex(HexCoord(0, 0)) is first


def test_get_fleet_at_hex_returns_none_for_empty_facade_result() -> None:
    ops, _scene, facade = _ops()
    facade.get_fleets_at_hex.return_value = []

    assert ops.get_fleet_at_hex(HexCoord(0, 0)) is None


def test_handle_move_designation_returns_none_without_selected_fleet() -> None:
    ops, _scene, facade = _ops()

    assert ops.handle_move_designation(10, 20, None) is None
    facade.get_fleets_at_hex.assert_not_called()


def test_handle_move_designation_blocks_building_fleet_before_hit_testing() -> None:
    ops, scene, facade = _ops()

    result = ops.handle_move_designation(10, 20, _fleet(is_building=True))

    assert result == {
        "type": "error",
        "message": "Fleet is building - cancel BUILD order first",
    }
    scene.camera.screen_to_world.assert_not_called()
    facade.get_fleets_at_hex.assert_not_called()


def test_fleet_ops_occupied_hex_prompts_choice() -> None:
    ops, _scene, facade = _ops()
    selected = _fleet(fleet_id=1)
    target_hex = HexCoord(4, -2)
    target = _fleet_info(fleet_id=99, owner_id=3)
    facade.get_fleets_at_hex.return_value = [target]

    ops.scene.camera.hex_at_screen.return_value = target_hex
    result = ops.handle_move_designation(10, 20, selected)

    assert result == {
        "type": "choice",
        "target_fleet": target,
        "target_hex": target_hex,
    }


def test_handle_move_designation_executes_move_when_target_is_selected_fleet() -> None:
    ops, _scene, facade = _ops()
    selected = _fleet(fleet_id=1)
    target_hex = HexCoord(4, -2)
    facade.get_fleets_at_hex.return_value = [_fleet_info(fleet_id=1)]
    ops.execute_move = MagicMock(return_value={"type": "success", "fleet": selected})

    ops.scene.camera.hex_at_screen.return_value = target_hex
    result = ops.handle_move_designation(10, 20, selected)

    ops.execute_move.assert_called_once_with(selected, target_hex)
    assert result == {"type": "success", "fleet": selected}


def test_execute_move_queues_command_when_path_preview_is_available() -> None:
    ops, _scene, facade = _ops()
    fleet = _fleet(fleet_id=42)
    target_hex = HexCoord(8, 1)
    facade.get_fleet_path_preview.return_value = [HexCoord(7, 1), target_hex]
    facade.handle_command.return_value = SimpleNamespace(is_valid=True, message="ok")

    result = ops.execute_move(fleet, target_hex)

    assert result == {"type": "success", "fleet": fleet}
    cmd = facade.handle_command.call_args.args[0]
    assert cmd.fleet_id == 42
    assert cmd.target_hex == target_hex


def test_execute_move_reports_command_failure_message() -> None:
    ops, _scene, facade = _ops()
    facade.get_fleet_path_preview.return_value = [HexCoord(1, 0)]
    facade.handle_command.return_value = SimpleNamespace(is_valid=False, message="blocked")

    result = ops.execute_move(_fleet(), HexCoord(1, 0))

    assert result == {"type": "error", "message": "blocked"}


def test_execute_move_rejects_unreachable_without_issuing_command() -> None:
    ops, _scene, facade = _ops()
    facade.get_fleet_path_preview.return_value = []

    result = ops.execute_move(_fleet(), HexCoord(99, 99))

    assert result == {"type": "error", "message": "Unreachable"}
    facade.handle_command.assert_not_called()


def test_execute_intercept_reports_unknown_when_facade_returns_none() -> None:
    ops, _scene, facade = _ops()
    facade.handle_command.return_value = None

    result = ops.execute_intercept(_fleet(fleet_id=3), _fleet_info(fleet_id=4))

    assert result == {"type": "error", "message": "Unknown"}
    cmd = facade.handle_command.call_args.args[0]
    assert cmd.fleet_id == 3
    assert cmd.target_fleet_id == 4


def test_handle_join_designation_filters_to_same_owner_non_self_targets() -> None:
    ops, _scene, facade = _ops()
    selected = _fleet(fleet_id=1, owner_id=7)
    valid = _fleet_info(fleet_id=2, owner_id=7)
    facade.get_fleets_at_hex.return_value = [
        _fleet_info(fleet_id=1, owner_id=7),
        _fleet_info(fleet_id=3, owner_id=8),
        valid,
    ]
    ops.execute_join = MagicMock(return_value={"type": "success", "fleet": selected})

    ops.scene.camera.hex_at_screen.return_value = HexCoord(0, 0)
    result = ops.handle_join_designation(10, 20, selected)

    ops.execute_join.assert_called_once_with(selected, valid)
    assert result == {"type": "success", "fleet": selected}


def test_handle_join_designation_returns_choice_for_multiple_valid_targets() -> None:
    ops, _scene, facade = _ops()
    selected = _fleet(fleet_id=1, owner_id=7)
    valid_targets = [_fleet_info(fleet_id=2, owner_id=7), _fleet_info(fleet_id=3, owner_id=7)]
    facade.get_fleets_at_hex.return_value = valid_targets

    ops.scene.camera.hex_at_screen.return_value = HexCoord(0, 0)
    result = ops.handle_join_designation(10, 20, selected)

    assert result == {"type": "choice", "fleets": valid_targets}


def test_execute_join_reports_facade_failure_message() -> None:
    ops, _scene, facade = _ops()
    facade.handle_command.return_value = SimpleNamespace(is_valid=False, message="too far")

    result = ops.execute_join(_fleet(fleet_id=10), _fleet_info(fleet_id=11))

    assert result == {"type": "error", "message": "too far"}
    cmd = facade.handle_command.call_args.args[0]
    assert cmd.fleet_id == 10
    assert cmd.target_fleet_id == 11
