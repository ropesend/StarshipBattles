"""Per-handler tests for `SelfDestructHandler` (PROJ-368 Phase 2).

Drives the handler directly. Pins SHIPS_SELF_DESTRUCTED event payload
and the SG-003 empty-fleet cleanup contract.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.self_destruct import SelfDestructHandler
from game.strategy.events.event_types import EventCategory, EventType


def _captured_event_bus():
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    return _Bus(), captured


def _ship(ship_id: str, name: str = "TestShip"):
    s = MagicMock()
    s.id = ship_id
    s.name = name
    return s


def _fleet(ships: list, fleet_id: int = 1):
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = HexCoord(2, 3)
    fleet.ships = list(ships)

    def _remove_ship(s):
        fleet.ships.remove(s)
    fleet.remove_ship = MagicMock(side_effect=_remove_ship)
    fleet.pop_order = MagicMock()
    return fleet


def _empire():
    emp = MagicMock()
    emp.id = 0
    emp.remove_fleet = MagicMock()
    return emp


def test_no_order_returns_failure():
    handler = SelfDestructHandler()
    fleet = MagicMock(spec=Fleet)
    fleet.get_current_order.return_value = None
    result = handler.execute_action_order(fleet, _empire(), MagicMock())
    assert result.success is False


def test_empty_ship_id_list_pops_and_returns_failure():
    handler = SelfDestructHandler()
    s1 = _ship("a", "Alpha")
    fleet = _fleet([s1])
    fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, [])
    result = handler.execute_action_order(fleet, _empire(), MagicMock())
    assert result.success is False
    fleet.pop_order.assert_called_once()


def test_target_not_a_list_pops_and_returns_failure():
    handler = SelfDestructHandler()
    fleet = _fleet([_ship("a")])
    fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, "not_a_list")
    result = handler.execute_action_order(fleet, _empire(), MagicMock())
    assert result.success is False
    fleet.pop_order.assert_called_once()


def test_happy_path_removes_specified_ships():
    handler = SelfDestructHandler()
    a = _ship("a", "Alpha")
    b = _ship("b", "Bravo")
    c = _ship("c", "Charlie")
    fleet = _fleet([a, b, c])
    empire = _empire()
    fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, ["a", "c"])
    result = handler.execute_action_order(fleet, empire, MagicMock())
    assert result.success is True
    assert result.fleet_consumed is False  # b survives
    # a and c removed; b remains.
    assert fleet.ships == [b]
    # Empty-fleet cleanup NOT triggered.
    empire.remove_fleet.assert_not_called()


def test_fleet_emptied_triggers_empire_remove_fleet():
    """SG-003: emptying the fleet via self-destruct removes it from the empire."""
    handler = SelfDestructHandler()
    a = _ship("a", "Alpha")
    fleet = _fleet([a])
    empire = _empire()
    fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, ["a"])
    result = handler.execute_action_order(fleet, empire, MagicMock())
    assert result.success is True
    assert result.fleet_consumed is True
    assert fleet.ships == []
    empire.remove_fleet.assert_called_once()


def test_emits_ships_self_destructed_event_payload_exact_match():
    bus, captured = _captured_event_bus()
    handler = SelfDestructHandler(event_bus=bus)
    a = _ship("a", "Alpha")
    b = _ship("b", "Bravo")
    fleet = _fleet([a, b], fleet_id=7)
    empire = _empire()
    fleet.get_current_order.return_value = Order(OrderType.SELF_DESTRUCT, ["a"])
    handler.execute_action_order(fleet, empire, MagicMock())
    events = [e for e in captured if e[0] == EventType.SHIPS_SELF_DESTRUCTED]
    assert len(events) == 1
    payload = events[0][1]
    assert payload == {
        "category": EventCategory.SUPERWEAPONS,
        "empire_id": 0,
        "message": "1 ships self-destructed",
        "fleet_id": 7,
        "ship_count": 1,
        "ship_names": ["Alpha"],
        "location_hex": [2, 3],
    }
