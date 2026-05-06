"""Pure tests for WorkshopShipOps business logic."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.constants import LayerType
from game.core.exceptions import ValidationException
from game.ui.colors import VEHICLE_DEFAULT
from game.ui.screens.workshop_viewmodel_ship_ops import WorkshopShipOps


def _result(
    *,
    success: bool = True,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    ship: object | None = None,
    removed_component: object | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        success=success,
        errors=errors or [],
        warnings=warnings or [],
        ship=ship,
        removed_component=removed_component,
    )


class FakeShip:
    def __init__(self) -> None:
        self.name = "Old Ship"
        self.theme_id = "Federation"
        self.movement_policy = "old_move"
        self.targeting_policy = "old_target"
        self.design_role = "old_role"
        self.clear_non_hull_components = MagicMock()


class FakeViewModel:
    def __init__(self, ship: FakeShip | None) -> None:
        self.screen_width = 800
        self.screen_height = 600
        self._ship = ship
        self._last_result = None
        self.required_actions: list[str] = []
        self.cleared_selection = 0
        self.notify_count = 0
        self.emit_count = 0

    @property
    def ship(self) -> FakeShip | None:
        return self._ship

    @ship.setter
    def ship(self, value: FakeShip | None) -> None:
        self._ship = value
        self._emit_ship_updated()

    def _require_ship(self, action: str) -> bool:
        self.required_actions.append(action)
        return self._ship is not None

    def _with_ship(self, action: str, service_call, on_success, on_failure):
        if not self._require_ship(action):
            return on_failure
        result = service_call(self._ship)
        self._last_result = result
        if result.success:
            self.notify_ship_changed()
            return on_success(result)
        return on_failure

    def clear_selection(self) -> None:
        self.cleared_selection += 1

    def notify_ship_changed(self) -> None:
        self.notify_count += 1

    def _emit_ship_updated(self) -> None:
        self.emit_count += 1

    def remove_component(self, layer: LayerType, index: int):
        return self._ship_service.remove_component(self._ship, layer, index).removed_component


class FakeShipService:
    def __init__(self) -> None:
        self.create_result = _result(success=False, errors=["not configured"])
        self.add_result = _result()
        self.add_instance_result = _result()
        self.bulk_result = _result()
        self.remove_result = _result(removed_component=object())
        self.change_result = _result()
        self.validate_result = object()
        self.available_components = ["laser"]
        self.ship_summary = {"mass": 50}
        self.create_calls: list[dict[str, object]] = []
        self.add_calls: list[tuple[object, str, LayerType]] = []
        self.add_instance_calls: list[tuple[object, object, LayerType]] = []
        self.bulk_calls: list[tuple[object, str, LayerType, int]] = []
        self.remove_calls: list[tuple[object, LayerType, int]] = []
        self.change_calls: list[tuple[object, str, bool]] = []

    def create_ship(self, **kwargs):
        self.create_calls.append(kwargs)
        return self.create_result

    def add_component(self, ship: object, component_id: str, layer: LayerType):
        self.add_calls.append((ship, component_id, layer))
        return self.add_result

    def add_component_instance(self, ship: object, component: object, layer: LayerType):
        self.add_instance_calls.append((ship, component, layer))
        return self.add_instance_result

    def add_component_bulk(
        self,
        ship: object,
        component_id: str,
        layer: LayerType,
        count: int,
    ):
        self.bulk_calls.append((ship, component_id, layer, count))
        return self.bulk_result

    def remove_component(self, ship: object, layer: LayerType, index: int):
        self.remove_calls.append((ship, layer, index))
        return self.remove_result

    def change_class(self, ship: object, new_class: str, *, migrate_components: bool):
        self.change_calls.append((ship, new_class, migrate_components))
        return self.change_result

    def validate_design(self, ship: object):
        return (ship, self.validate_result)

    def get_available_components(self, ship: object, layer: LayerType):
        return [ship, layer, *self.available_components]

    def get_ship_summary(self, ship: object):
        return {"ship": ship, **self.ship_summary}


def _ops(
    ship: FakeShip | None = None,
    service: FakeShipService | None = None,
) -> tuple[WorkshopShipOps, FakeViewModel, FakeShipService]:
    viewmodel = FakeViewModel(ship)
    ship_service = service or FakeShipService()
    viewmodel._ship_service = ship_service
    return WorkshopShipOps(viewmodel, ship_service), viewmodel, ship_service


def test_create_default_ship_uses_service_result_and_screen_center() -> None:
    created_ship = FakeShip()
    service = FakeShipService()
    service.create_result = _result(ship=created_ship)
    ops, viewmodel, _service = _ops(service=service)

    result = ops.create_default_ship("Cruiser")

    assert result is created_ship
    assert viewmodel.ship is created_ship
    assert viewmodel._last_result is service.create_result
    assert service.create_calls == [
        {
            "name": "Custom Ship",
            "ship_class": "Cruiser",
            "x": 400,
            "y": 300,
            "color": VEHICLE_DEFAULT,
        }
    ]
    assert viewmodel.emit_count == 1


def test_create_default_ship_raises_validation_exception_on_service_failure() -> None:
    service = FakeShipService()
    service.create_result = _result(success=False, errors=["bad class"])
    ops, viewmodel, _service = _ops(service=service)

    with pytest.raises(ValidationException) as exc_info:
        ops.create_default_ship("Unknown")

    assert "bad class" in str(exc_info.value)
    assert viewmodel._last_result is service.create_result
    assert viewmodel.ship is None


def test_component_operations_delegate_through_standard_with_ship_path() -> None:
    ship = FakeShip()
    component = object()
    removed = object()
    service = FakeShipService()
    service.remove_result = _result(removed_component=removed)
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.add_component("laser", LayerType.CORE) is True
    assert ops.add_component_instance(component, LayerType.INNER) is True
    assert ops.remove_component(LayerType.OUTER, 2) is removed

    assert service.add_calls == [(ship, "laser", LayerType.CORE)]
    assert service.add_instance_calls == [(ship, component, LayerType.INNER)]
    assert service.remove_calls == [(ship, LayerType.OUTER, 2)]
    assert viewmodel.notify_count == 3


def test_pick_up_component_clears_selection_after_successful_removal() -> None:
    ship = FakeShip()
    removed = object()
    service = FakeShipService()
    service.remove_result = _result(removed_component=removed)
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.pick_up_component(LayerType.CORE, 0) is removed

    assert service.remove_calls == [(ship, LayerType.CORE, 0)]
    assert viewmodel.cleared_selection == 1


def test_pick_up_component_keeps_selection_when_removal_fails() -> None:
    ship = FakeShip()
    service = FakeShipService()
    service.remove_result = _result(success=False, removed_component=None)
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.pick_up_component(LayerType.CORE, 0) is None

    assert viewmodel.cleared_selection == 0


def test_add_component_bulk_returns_zero_without_ship_and_skips_service() -> None:
    service = FakeShipService()
    ops, _viewmodel, _service = _ops(None, service)

    assert ops.add_component_bulk("laser", LayerType.CORE, 3) == 0
    assert service.bulk_calls == []


@pytest.mark.parametrize(
    ("warnings", "expected_count"),
    [
        ([], 3),
        (["only two slots free"], 2),
    ],
)
def test_add_component_bulk_success_returns_count_adjusted_for_warning(
    warnings: list[str],
    expected_count: int,
) -> None:
    ship = FakeShip()
    service = FakeShipService()
    service.bulk_result = _result(warnings=warnings)
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.add_component_bulk("laser", LayerType.CORE, 3) == expected_count

    assert service.bulk_calls == [(ship, "laser", LayerType.CORE, 3)]
    assert viewmodel._last_result is service.bulk_result
    assert viewmodel.notify_count == 1


def test_add_component_bulk_failure_stores_result_without_notification() -> None:
    ship = FakeShip()
    service = FakeShipService()
    service.bulk_result = _result(success=False, errors=["full"])
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.add_component_bulk("laser", LayerType.CORE, 3) == 0

    assert viewmodel._last_result is service.bulk_result
    assert viewmodel.notify_count == 0


def test_change_ship_class_success_clears_selection_and_notifies() -> None:
    ship = FakeShip()
    service = FakeShipService()
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.change_ship_class("Destroyer", migrate_components=False) is True

    assert service.change_calls == [(ship, "Destroyer", False)]
    assert viewmodel._last_result is service.change_result
    assert viewmodel.cleared_selection == 1
    assert viewmodel.notify_count == 1


def test_change_ship_class_failure_returns_false_without_ui_side_effects() -> None:
    ship = FakeShip()
    service = FakeShipService()
    service.change_result = _result(success=False, errors=["too heavy"])
    ops, viewmodel, _service = _ops(ship, service)

    assert ops.change_ship_class("Destroyer") is False

    assert viewmodel._last_result is service.change_result
    assert viewmodel.cleared_selection == 0
    assert viewmodel.notify_count == 0


def test_lookup_helpers_return_empty_without_ship_and_delegate_with_ship() -> None:
    no_ship_ops, _no_ship_vm, no_ship_service = _ops(None)

    assert no_ship_ops.validate_design() is None
    assert no_ship_ops.get_available_components_for_layer(LayerType.CORE) == []
    assert no_ship_ops.get_ship_summary() == {}
    assert no_ship_service.change_calls == []

    ship = FakeShip()
    ops, _viewmodel, service = _ops(ship)

    assert ops.validate_design() == (ship, service.validate_result)
    assert ops.get_available_components_for_layer(LayerType.OUTER) == [
        ship,
        LayerType.OUTER,
        "laser",
    ]
    assert ops.get_ship_summary() == {"ship": ship, "mass": 50}


def test_clear_design_resets_ship_defaults_and_notifies() -> None:
    ship = FakeShip()
    ops, viewmodel, _service = _ops(ship)

    ops.clear_design()

    ship.clear_non_hull_components.assert_called_once_with()
    assert ship.movement_policy == "kite_max"
    assert ship.targeting_policy == "standard"
    assert ship.name == "Custom Ship"
    assert viewmodel.cleared_selection == 1
    assert viewmodel.notify_count == 1


def test_clear_design_returns_without_ship() -> None:
    ops, viewmodel, _service = _ops(None)

    ops.clear_design()

    assert viewmodel.required_actions == ["clear design"]
    assert viewmodel.cleared_selection == 0
    assert viewmodel.notify_count == 0


@pytest.mark.parametrize(
    ("method_name", "attribute", "new_value"),
    [
        ("set_ship_name", "name", "Updated"),
        ("set_ship_theme", "theme_id", "Klingon"),
        ("set_ship_movement_policy", "movement_policy", "brawl_close"),
        ("set_ship_targeting_policy", "targeting_policy", "sniper"),
        ("set_ship_design_role", "design_role", "carrier"),
    ],
)
def test_attribute_setters_emit_only_when_value_changes(
    method_name: str,
    attribute: str,
    new_value: str,
) -> None:
    ship = FakeShip()
    ops, viewmodel, _service = _ops(ship)

    getattr(ops, method_name)(getattr(ship, attribute))
    assert viewmodel.emit_count == 0

    getattr(ops, method_name)(new_value)

    assert getattr(ship, attribute) == new_value
    assert viewmodel.emit_count == 1


@pytest.mark.parametrize(
    ("method_name", "expected_action"),
    [
        ("set_ship_name", "set ship name"),
        ("set_ship_theme", "set ship theme"),
        ("set_ship_movement_policy", "set movement policy"),
        ("set_ship_targeting_policy", "set targeting policy"),
        ("set_ship_design_role", "set design role"),
    ],
)
def test_attribute_setters_return_without_ship(
    method_name: str,
    expected_action: str,
) -> None:
    ops, viewmodel, _service = _ops(None)

    getattr(ops, method_name)("new")

    assert viewmodel.emit_count == 0
    assert viewmodel.required_actions == [expected_action]
