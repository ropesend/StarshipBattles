"""Pure tests for WorkshopLayerOps helper behavior."""
from __future__ import annotations

from types import SimpleNamespace

from game.core.constants import LayerType
from game.ui.screens.workshop_viewmodel_layer_ops import WorkshopLayerOps


class FakeLayer:
    def __init__(self, components: list[object] | None = None) -> None:
        self.components = components or []


class FakeShip:
    def __init__(self, components: list[object] | None = None) -> None:
        self.layers = {
            LayerType.HULL: FakeLayer(),
            LayerType.CORE: FakeLayer(components),
            LayerType.INNER: FakeLayer(),
            LayerType.OUTER: FakeLayer(),
            LayerType.ARMOR: FakeLayer(),
        }


class FakeViewModel:
    def __init__(self, ship: FakeShip | None) -> None:
        self._ship = ship
        self.required_actions: list[str] = []
        self.changed = False

    def _require_ship(self, action: str) -> bool:
        self.required_actions.append(action)
        return self._ship is not None

    def _with_ship(self, _action, operation, mapper, default):
        if self._ship is None:
            return default
        return mapper(operation(self._ship))

    def notify_ship_changed(self) -> None:
        self.changed = True


class FakeShipService:
    def __init__(self) -> None:
        self.move_calls: list[tuple[object, LayerType, int, LayerType]] = []

    def move_component(
        self,
        ship: object,
        source_layer: LayerType,
        index: int,
        target_layer: LayerType,
    ) -> bool:
        self.move_calls.append((ship, source_layer, index, target_layer))
        return True


class FakeRestrictionRule:
    def validate(self, _ship, component, layer: LayerType):
        return SimpleNamespace(is_valid=layer in component.valid_layers)


def _patch_restriction_rule(monkeypatch) -> None:
    import game.simulation.validation.ship_validator as ship_validator

    monkeypatch.setattr(
        ship_validator,
        "LayerRestrictionDefinitionRule",
        lambda: FakeRestrictionRule(),
    )


def _ops(viewmodel: FakeViewModel, service: FakeShipService | None = None) -> WorkshopLayerOps:
    return WorkshopLayerOps(viewmodel, service or FakeShipService(), registries=object())


def test_resolve_target_layer_returns_none_without_ship(monkeypatch) -> None:
    _patch_restriction_rule(monkeypatch)
    component = SimpleNamespace(valid_layers={LayerType.CORE})

    assert _ops(FakeViewModel(None)).resolve_target_layer(component) is None


def test_resolve_target_layer_prefers_selected_valid_layer(monkeypatch) -> None:
    _patch_restriction_rule(monkeypatch)
    component = SimpleNamespace(valid_layers={LayerType.CORE, LayerType.OUTER})
    ops = _ops(FakeViewModel(FakeShip()))

    assert ops.resolve_target_layer(component, selected_layer=LayerType.OUTER) == LayerType.OUTER


def test_resolve_target_layer_prefers_inner_layer_on_nearest_tie(monkeypatch) -> None:
    _patch_restriction_rule(monkeypatch)
    component = SimpleNamespace(valid_layers={LayerType.CORE, LayerType.OUTER})
    ops = _ops(FakeViewModel(FakeShip()))

    assert ops.resolve_target_layer(component, selected_layer=LayerType.INNER) == LayerType.CORE


def test_resolve_target_layer_excludes_hull(monkeypatch) -> None:
    _patch_restriction_rule(monkeypatch)
    component = SimpleNamespace(valid_layers={LayerType.HULL})
    ops = _ops(FakeViewModel(FakeShip()))

    assert ops.resolve_target_layer(component, selected_layer=LayerType.HULL) is None


def test_resolve_move_target_searches_next_valid_layer_by_direction(monkeypatch) -> None:
    _patch_restriction_rule(monkeypatch)
    component = SimpleNamespace(valid_layers={LayerType.CORE, LayerType.ARMOR})
    ops = _ops(FakeViewModel(FakeShip()))

    assert ops.resolve_move_target(component, LayerType.INNER, "up") == LayerType.CORE
    assert ops.resolve_move_target(component, LayerType.INNER, "down") == LayerType.ARMOR


def test_move_component_delegates_through_service() -> None:
    ship = FakeShip()
    viewmodel = FakeViewModel(ship)
    service = FakeShipService()

    result = _ops(viewmodel, service).move_component(
        LayerType.CORE, 1, LayerType.OUTER
    )

    assert result is True
    assert service.move_calls == [(ship, LayerType.CORE, 1, LayerType.OUTER)]


def test_move_component_group_moves_matching_indices_in_reverse(monkeypatch) -> None:
    import game.ui.screens.builder.grouping_strategies as grouping_strategies

    monkeypatch.setattr(grouping_strategies, "get_component_group_key", lambda c: c.group)
    matching_a = SimpleNamespace(group="engine")
    other = SimpleNamespace(group="weapon")
    matching_b = SimpleNamespace(group="engine")
    ship = FakeShip(components=[matching_a, other, matching_b])
    viewmodel = FakeViewModel(ship)
    service = FakeShipService()

    result = _ops(viewmodel, service).move_component_group(
        "engine", LayerType.CORE, LayerType.OUTER
    )

    assert result is True
    assert [
        (source, index, target)
        for _ship, source, index, target in service.move_calls
    ] == [
        (LayerType.CORE, 2, LayerType.OUTER),
        (LayerType.CORE, 0, LayerType.OUTER),
    ]
    assert viewmodel.changed is True
