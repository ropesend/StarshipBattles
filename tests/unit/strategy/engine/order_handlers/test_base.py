"""Tests for `order_handlers.base` (PROJ-368).

Covers the registry contract, Protocol conformance, the unified result
dataclass defaults, and the BaseOrderHandler event-bus null-check.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    IOrderHandler,
    OrderExecutionResult,
    OrderHandlerRegistry,
)


def _make_handler_for(order_type: OrderType) -> IOrderHandler:
    handler = MagicMock(spec=IOrderHandler)
    handler.supported_order_types = (order_type,)
    return handler


def test_registry_register_and_get():
    registry = OrderHandlerRegistry()
    handler = _make_handler_for(OrderType.JOIN_FLEET)
    registry.register(OrderType.JOIN_FLEET, handler)
    assert registry.get(OrderType.JOIN_FLEET) is handler


def test_registry_get_unknown_returns_none():
    registry = OrderHandlerRegistry()
    assert registry.get(OrderType.MOVE) is None


def test_registry_register_duplicate_raises():
    registry = OrderHandlerRegistry()
    registry.register(OrderType.JOIN_FLEET, _make_handler_for(OrderType.JOIN_FLEET))
    with pytest.raises(ValueError):
        registry.register(OrderType.JOIN_FLEET, _make_handler_for(OrderType.JOIN_FLEET))


def test_registry_contains_operator():
    registry = OrderHandlerRegistry()
    registry.register(OrderType.JOIN_FLEET, _make_handler_for(OrderType.JOIN_FLEET))
    assert OrderType.JOIN_FLEET in registry
    assert OrderType.MOVE not in registry


def test_registry_all_registered_returns_frozenset():
    registry = OrderHandlerRegistry()
    registry.register(OrderType.JOIN_FLEET, _make_handler_for(OrderType.JOIN_FLEET))
    registry.register(OrderType.COLONIZE, _make_handler_for(OrderType.COLONIZE))
    keys = registry.all_registered()
    assert isinstance(keys, frozenset)
    assert keys == frozenset({OrderType.JOIN_FLEET, OrderType.COLONIZE})


def test_order_execution_result_default_values():
    result = OrderExecutionResult(success=True)
    assert result.success is True
    assert result.fleet_consumed is False
    assert result.message == ""
    assert result.merged is False
    assert result.cancelled is False
    assert result.colonized is False
    assert result.planet_name is None
    assert result.amount_transferred == 0


def test_base_order_handler_find_ship_matches_by_str_instance_id():
    """DUP-X-1: `_find_ship` is shared on BaseOrderHandler.

    Characterizes the byte-identical behaviour the 5 order handlers
    previously each owned: linear scan of ``fleet.ships`` comparing
    ``str(ship.instance_id) == str(ship_instance_id)``.
    """
    ship_a = MagicMock()
    ship_a.instance_id = 7
    ship_b = MagicMock()
    ship_b.instance_id = "abc"
    fleet = MagicMock()
    fleet.ships = [ship_a, ship_b]

    # int/str coercion: passing "7" matches ship_a whose id is int 7.
    assert BaseOrderHandler._find_ship(fleet, "7") is ship_a
    assert BaseOrderHandler._find_ship(fleet, 7) is ship_a
    assert BaseOrderHandler._find_ship(fleet, "abc") is ship_b
    assert BaseOrderHandler._find_ship(fleet, "missing") is None


def test_find_ship_shared_across_all_order_handlers():
    """All 5 vehicle order handlers resolve `_find_ship` to the base copy."""
    from game.strategy.engine.order_handlers.launch_fighters import (
        LaunchFightersOrderHandler,
    )
    from game.strategy.engine.order_handlers.launch_satellites import (
        LaunchSatellitesOrderHandler,
    )
    from game.strategy.engine.order_handlers.lay_mines import LayMinesOrderHandler
    from game.strategy.engine.order_handlers.recover_fighters import (
        RecoverFightersOrderHandler,
    )
    from game.strategy.engine.order_handlers.recover_satellites import (
        RecoverSatellitesOrderHandler,
    )

    for cls in (
        LaunchFightersOrderHandler,
        LaunchSatellitesOrderHandler,
        LayMinesOrderHandler,
        RecoverFightersOrderHandler,
        RecoverSatellitesOrderHandler,
    ):
        assert cls._find_ship is BaseOrderHandler._find_ship


def test_base_order_handler_emit_event_with_no_bus():
    handler = BaseOrderHandler(event_bus=None)
    # Should be a silent no-op (no AttributeError on `None.log_event`).
    handler._emit_event(
        "ANY_EVENT",
        category="ANY_CATEGORY",
        empire_id=0,
        message="msg",
        extra=1,
    )


def test_base_order_handler_emit_event_with_bus():
    bus = MagicMock()
    handler = BaseOrderHandler(event_bus=bus)
    handler._emit_event(
        "EVT",
        category="CAT",
        empire_id=42,
        message="hello",
        ship_id=7,
    )
    bus.log_event.assert_called_once_with(
        "EVT",
        category="CAT",
        empire_id=42,
        message="hello",
        ship_id=7,
    )
