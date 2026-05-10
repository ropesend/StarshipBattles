"""Tests for OrdersWindow two-stage construction (PROJ-328 Phase A
Task A.3).

Covers:

* Stage-1 cheap state survives bypass_init.
* OrderDescriber pure-data behaviour for each OrderType branch.
* MockOrdersUiBuilder populates rows.

Live-pygame integration (the auto-refresh in update(), button layout,
etc.) is covered by tests/unit/ui/screens/test_fleet_orders_refresh.py.
Hotkey dispatch is covered by tests/unit/ui/screens/test_sub_window_
hotkeys.py.

PROJ-322 Task 5.16 (Orders portion) closed by this migration.
"""

from unittest.mock import MagicMock
import pygame

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import Order, OrderType
from game.ui.screens.orders_window import (
    EDITABLE_ORDER_TYPES,
    OrderDescriber,
    OrderRowDescription,
    OrdersWindow,
)
from tests.fixtures.orders_ui_builder import (
    MockOrdersUiBuilder,
    NullOrdersUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _make_entity(orders=None, *, name="Test Fleet", entity_id=42):
    """Build a minimal IOrderable stand-in."""
    entity = MagicMock(name=name)
    entity.id = entity_id
    entity.name = name
    entity.orders = list(orders or [])
    # Some BUILD-order branches read entity.construction_queue.
    entity.construction_queue = []
    return entity


def _make_window(entity, *, ui_builder=None, **kwargs):
    if ui_builder is None:
        ui_builder = MockOrdersUiBuilder()
    with bypass_init(OrdersWindow):
        return OrdersWindow(
            pygame.Rect(0, 0, 400, 500),
            MagicMock(name="ui_manager"),
            entity,
            window_manager=None,
            ui_builder=ui_builder,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# OrderDescriber — pure data, no bypass needed.
# ---------------------------------------------------------------------------


class TestOrderDescriber:
    def test_move_with_hex_coord(self):
        order = Order(OrderType.MOVE, target=HexCoord(3, 4))
        text = OrderDescriber().describe(order, _make_entity())
        assert text == "MOVE (3, 4)"

    def test_move_with_other_target(self):
        target = MagicMock(__str__=lambda self: "target_obj")
        order = Order(OrderType.MOVE, target=target)
        text = OrderDescriber().describe(order, _make_entity())
        assert text.startswith("MOVE ")

    def test_transfer_load(self):
        order = Order(OrderType.TRANSFER, target={'direction': 'load'})
        assert OrderDescriber().describe(order, _make_entity()) == "load cargo"

    def test_transfer_unload(self):
        order = Order(OrderType.TRANSFER, target={'direction': 'unload'})
        assert OrderDescriber().describe(order, _make_entity()) == "drop cargo"

    def test_load_population_always_load(self):
        order = Order(OrderType.LOAD_POPULATION, target={'direction': 'unload'})
        # LOAD_POPULATION ignores direction and always says "load cargo".
        assert OrderDescriber().describe(order, _make_entity()) == "load cargo"

    def test_unload_population_always_drop(self):
        order = Order(OrderType.UNLOAD_POPULATION, target={'direction': 'load'})
        assert OrderDescriber().describe(order, _make_entity()) == "drop cargo"

    def test_transfer_with_non_dict_target(self):
        order = Order(OrderType.TRANSFER, target="some_target")
        assert OrderDescriber().describe(order, _make_entity()) == "TRANSFER"

    def test_build_with_construction_queue(self):
        order = Order(OrderType.BUILD, target=None)
        entity = _make_entity()
        entity.construction_queue = [{}, {}, {}]
        assert OrderDescriber().describe(order, entity) == "BUILDING (3 items)"

    def test_activate_ability(self):
        order = Order(OrderType.ACTIVATE_ABILITY,
                      target={'ability_name': 'shields'})
        assert OrderDescriber().describe(order, _make_entity()) == "ACTIVATE SHIELDS"

    def test_deactivate_ability(self):
        order = Order(OrderType.DEACTIVATE_ABILITY,
                      target={'ability_name': 'cloak'})
        assert OrderDescriber().describe(order, _make_entity()) == "DEACTIVATE CLOAK"


class TestOrderDescriberDescribeAll:
    def test_describes_each_order_with_index(self):
        orders = [
            Order(OrderType.MOVE, target=HexCoord(1, 1)),
            Order(OrderType.TRANSFER, target={'direction': 'load'}),
        ]
        entity = _make_entity(orders=orders)
        rows = OrderDescriber().describe_all(entity)

        assert len(rows) == 2
        assert rows[0].index == 0
        assert rows[0].text == "MOVE (1, 1)"
        assert rows[0].is_editable is True  # MOVE is editable
        assert rows[1].index == 1
        assert rows[1].text == "load cargo"

    def test_marks_non_editable_orders(self):
        orders = [Order(OrderType.JOIN_FLEET, target=MagicMock(id=99))]
        # JOIN_FLEET isn't in EDITABLE_ORDER_TYPES.
        entity = _make_entity(orders=orders)
        rows = OrderDescriber().describe_all(entity)
        assert rows[0].is_editable is False
        assert OrderType.JOIN_FLEET not in EDITABLE_ORDER_TYPES


# ---------------------------------------------------------------------------
# Two-stage construction.
# ---------------------------------------------------------------------------


class TestOrdersWindowConstruction:
    def test_stage1_state_survives_bypass(self):
        entity = _make_entity()
        callback = MagicMock()
        window = _make_window(entity, clear_orders_callback=callback)

        assert window.entity is entity
        assert window._clear_orders_callback is callback
        assert window._window_init_bypassed is True

    def test_default_describer_is_real(self):
        window = _make_window(_make_entity())
        assert isinstance(window._order_describer, OrderDescriber)

    def test_null_builder_leaves_widget_slots_unset(self):
        window = _make_window(_make_entity(), ui_builder=NullOrdersUiBuilder())
        assert window.list_container is None
        assert window.btn_clear is None
        assert window.rows == []

    def test_mock_builder_populates_rows_from_describer(self):
        orders = [Order(OrderType.MOVE, target=HexCoord(1, 2))]
        entity = _make_entity(orders=orders)
        window = _make_window(entity)

        assert window.list_container is not None
        assert window.btn_clear is not None
        assert len(window.rows) == 1
        # Editable MOVE order gets the edit button.
        assert 'edit' in window.rows[0]
        # Description back-pointer is populated.
        desc = window.rows[0]['description']
        assert isinstance(desc, OrderRowDescription)
        assert desc.text == "MOVE (1, 2)"

    def test_get_order_description_shim_delegates_to_describer(self):
        """Backwards-compat shim for callers that used to read
        screen._get_order_description directly."""
        entity = _make_entity()
        window = _make_window(entity)
        order = Order(OrderType.MOVE, target=HexCoord(7, 8))
        assert window._get_order_description(order) == "MOVE (7, 8)"
