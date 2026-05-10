"""Registry-completeness gate (PROJ-368 Phase 4 Task 4.10).

Asserts every `OrderType` value handled by `OrderProcessor` has a
registered handler in the default registry. Failing this test BLOCKS
Phase 4 sign-off because the deletion-and-switchover commit cannot be
merged with stragglers or unrouted OrderTypes.
"""
from __future__ import annotations

from game.strategy.data.order_types import (
    ACTION_ORDER_TYPES,
    PLANET_ACTION_ORDER_TYPES,
    OrderType,
)
from game.strategy.engine.order_handlers.registry_factory import (
    create_default_order_handler_registry,
)
from game.strategy.engine.superweapon_order_processor import (
    SuperweaponOrderProcessor,
)


def test_every_action_order_type_has_a_handler():
    """ACTION_ORDER_TYPES (minus planet-only) plus JOIN_FLEET must all be registered."""
    registry = create_default_order_handler_registry(
        event_bus=None,
        superweapon_processor=SuperweaponOrderProcessor(),
    )
    expected = (ACTION_ORDER_TYPES - PLANET_ACTION_ORDER_TYPES) | {OrderType.JOIN_FLEET}
    registered = registry.all_registered()
    missing = expected - registered
    assert not missing, f"OrderTypes missing handlers: {missing}"


def test_join_fleet_handler_registered():
    registry = create_default_order_handler_registry(event_bus=None)
    assert OrderType.JOIN_FLEET in registry


def test_colonize_handler_registered():
    registry = create_default_order_handler_registry(event_bus=None)
    assert OrderType.COLONIZE in registry


def test_self_destruct_handler_registered():
    registry = create_default_order_handler_registry(event_bus=None)
    assert OrderType.SELF_DESTRUCT in registry


def test_transfer_family_registered():
    registry = create_default_order_handler_registry(event_bus=None)
    assert OrderType.TRANSFER in registry
    assert OrderType.LOAD_POPULATION in registry
    assert OrderType.UNLOAD_POPULATION in registry


def test_transfer_family_shares_one_handler_instance():
    """Single TransferHandler instance, three OrderType keys."""
    registry = create_default_order_handler_registry(event_bus=None)
    h_t = registry.get(OrderType.TRANSFER)
    h_l = registry.get(OrderType.LOAD_POPULATION)
    h_u = registry.get(OrderType.UNLOAD_POPULATION)
    assert h_t is h_l is h_u


def test_all_5_spec_driven_superweapons_registered():
    registry = create_default_order_handler_registry(event_bus=None)
    for order_type in (
        OrderType.IMPLODE_PLANET,
        OrderType.STELLERATE_STAR,
        OrderType.OPEN_WARP_POINT,
        OrderType.CLOSE_WARP_POINT,
        OrderType.CREATE_DYSON_SPHERE,
    ):
        assert order_type in registry, f"{order_type.name} missing handler"


def test_planet_action_orders_NOT_registered():
    """ACTIVATE_ABILITY and DEACTIVATE_ABILITY are handled elsewhere."""
    registry = create_default_order_handler_registry(event_bus=None)
    assert OrderType.ACTIVATE_ABILITY not in registry
    assert OrderType.DEACTIVATE_ABILITY not in registry
