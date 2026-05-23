"""PROJ-333 Phase 1: OrderProcessor COLONIZE characterization.

Pins COLONIZE happy/unhappy paths and the drop-pod deploy contract:
no order, validation failure, "Any" planet sentinel resolution,
missing drop pod, successful colonize+pop+deploy, initial_stockpile
seeding from drop-pod design_data, COLONY_FOUNDED event payload,
execute_action_order routing, and the missing-component_registry
error path.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.events.event_types import EventType


def _wire_bay(ship: MagicMock, pod_dicts: list) -> None:
    """PROJ-436 Phase 9: wire a MagicMock ship's typed bay_inventory
    from a list of legacy pod dicts. The legacy ``carried_items``
    mirror is gone — production code reads the typed pods slot.
    """
    ship.bay_inventory = BayInventory(
        bay=[],
        pods=[
            DropPod(
                design_id=str(d.get("design_id", "")),
                design_data=dict(d.get("design_data", {})),
                mass=float(d.get("mass", 0.0)),
                payload={
                    k: v for k, v in d.items()
                    if k not in {"design_id", "design_data", "mass"}
                },
            )
            for d in pod_dicts
        ],
    )

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi

    ship.set_bay_inventory = _set_bay_inventory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _captured_event_bus():
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    return _Bus(), captured


def _fleet_with_order(order: Order, *, location: HexCoord = HexCoord(0, 0)):
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = location
    fleet.get_current_order.return_value = order
    fleet.pop_order = MagicMock()
    fleet.ships = []
    return fleet


def _empire(name: str = "Test Empire"):
    emp = MagicMock()
    emp.id = 0
    emp.name = name
    emp.add_colony = MagicMock()
    emp.race_config = None
    return emp


def _colonizable_planet(planet_id: int = 99, name: str = "Eden") -> MagicMock:
    planet = MagicMock()
    planet.id = planet_id
    planet.name = name
    planet.owner_id = None
    planet.location = HexCoord(0, 0)
    planet.facilities = []
    planet.add_to_stockpile = MagicMock()
    return planet


# ---------------------------------------------------------------------------
# process_colonize: early-exit / validation paths
# ---------------------------------------------------------------------------


def test_process_colonize_returns_false_when_no_current_order():
    """No order → returns OrderExecutionResult(colonized=False)."""
    proc = OrderProcessor()
    fleet = _fleet_with_order(None)
    result = proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, _empire(), MagicMock(), component_registry={})
    assert result.colonized is False


def test_process_colonize_returns_false_when_validation_fails():
    """Validator failure → colonized=False, order popped, no add_colony call."""
    proc = OrderProcessor()
    planet = _colonizable_planet()
    order = Order(OrderType.COLONIZE, planet)
    fleet = _fleet_with_order(order)
    empire = _empire()

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = []  # ensure validator fails

    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate:
        mock_validate.return_value = MagicMock(is_valid=False, message="bad")
        result = proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is False
    fleet.pop_order.assert_called_once()
    empire.add_colony.assert_not_called()


def test_process_colonize_resolves_any_planet_picks_first_unowned():
    """`order.target = None` (Any sentinel) picks first unowned at hex."""
    proc = OrderProcessor()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, None))
    empire = _empire()

    owned = _colonizable_planet(planet_id=1, name="Mars")
    owned.owner_id = 7  # taken
    free1 = _colonizable_planet(planet_id=2, name="Free1")
    free2 = _colonizable_planet(planet_id=3, name="Free2")

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [owned, free1, free2]
    galaxy.get_system_of_planet.return_value = None

    # Make a drop pod present so we don't trip the no-pod branch.
    pod_ship = MagicMock()
    _wire_bay(pod_ship, [
        {"vehicle_type": "drop_pod", "design_id": "pod1", "name": "Pod"}
    ])
    fleet.ships = [pod_ship]

    with patch(
        "game.strategy.validation.ColonizeValidator.validate",
        return_value=MagicMock(is_valid=True),
    ):
        result = proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is True
    empire.add_colony.assert_called_once_with(free1)


def test_process_colonize_returns_false_when_no_drop_pod_in_fleet():
    """Validator passes but fleet has no drop pod → colonized=False, popped."""
    proc = OrderProcessor()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = None

    empty_ship = MagicMock()
    _wire_bay(empty_ship, [])
    fleet.ships = [empty_ship]  # no pod

    with patch(
        "game.strategy.validation.ColonizeValidator.validate",
        return_value=MagicMock(is_valid=True),
    ):
        result = proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is False
    fleet.pop_order.assert_called_once()
    empire.add_colony.assert_not_called()


# ---------------------------------------------------------------------------
# Successful colonize: add_colony, pop, drop-pod deploy, stockpile seed
# ---------------------------------------------------------------------------


def test_process_colonize_adds_colony_pops_order_and_deploys_pod():
    """Happy path: empire.add_colony, fleet.pop_order, drop pod removed from ship."""
    proc = OrderProcessor()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = None

    pod_item = {"vehicle_type": "drop_pod", "design_id": "pod1",
                "name": "PrimePod", "design_data": {}}
    pod_ship = MagicMock()
    _wire_bay(pod_ship, [pod_item])
    fleet.ships = [pod_ship]

    with patch(
        "game.strategy.validation.ColonizeValidator.validate",
        return_value=MagicMock(is_valid=True),
    ):
        result = proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is True
    empire.add_colony.assert_called_once_with(planet)
    fleet.pop_order.assert_called_once()
    assert pod_ship.bay_inventory.pods == []  # pod consumed
    assert len(planet.facilities) == 1   # pod deployed as facility


def test_process_colonize_seeds_stockpile_from_design_initial_stockpile():
    """`design_data['initial_stockpile']` flows through `planet.add_to_stockpile`."""
    proc = OrderProcessor()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = None

    pod_ship = MagicMock()
    _wire_bay(pod_ship, [{
        "vehicle_type": "drop_pod",
        "design_id": "seed_pod",
        "name": "SeedPod",
        "design_data": {"initial_stockpile": {"metals": 50.0, "organics": 25.0}},
    }])
    fleet.ships = [pod_ship]

    with patch(
        "game.strategy.validation.ColonizeValidator.validate",
        return_value=MagicMock(is_valid=True),
    ):
        proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    # PROJ-480 Task 4.10: per-key assertion. Adding a new resource to
    # the colony-pod payload should not break this test — it only fails
    # if the historically-tracked metals/organics amounts drift.
    add_calls = {c.args[0]: c.args[1] for c in planet.add_to_stockpile.call_args_list}
    assert add_calls.get("metals") == 50.0
    assert add_calls.get("organics") == 25.0


# ---------------------------------------------------------------------------
# COLONY_FOUNDED event emission
# ---------------------------------------------------------------------------


def test_process_colonize_logs_colony_founded_event_with_system_and_local_hex():
    """Successful colonize emits COLONY_FOUNDED with system_name + local_hex."""
    bus, captured = _captured_event_bus()
    proc = OrderProcessor(event_bus=bus)
    planet = _colonizable_planet(name="Avalon")
    planet.location = HexCoord(2, 1)

    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet),
                              location=HexCoord(5, 5))
    empire = _empire(name="Empire-A")

    fake_system = MagicMock()
    fake_system.name = "Avalon System"
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = fake_system

    pod_ship = MagicMock()
    _wire_bay(pod_ship, [
        {"vehicle_type": "drop_pod", "design_id": "pod", "name": "Pod"},
    ])
    fleet.ships = [pod_ship]

    with patch(
        "game.strategy.validation.ColonizeValidator.validate",
        return_value=MagicMock(is_valid=True),
    ):
        proc.get_handler(OrderType.COLONIZE).execute_action_order(fleet, empire, galaxy, component_registry={})

    founded = [e for e in captured if e[0] == EventType.COLONY_FOUNDED]
    assert len(founded) == 1
    payload = founded[0][1]
    assert payload["planet_id"] == planet.id
    assert payload["system_name"] == "Avalon System"
    assert payload["local_hex"] == [2, 1]
    assert payload["location_hex"] == [5, 5]


# ---------------------------------------------------------------------------
# execute_action_order routing for COLONIZE
# ---------------------------------------------------------------------------


def test_execute_action_order_routes_colonize_with_component_registry():
    """COLONIZE order with non-None registry → ColonizeHandler is invoked.

    PROJ-368 Phase 4: execute_action_order is a registry lookup. The
    routing-test now patches the registered ColonizeHandler instead of
    the legacy process_colonize delegate.
    """
    proc = OrderProcessor()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, _colonizable_planet()))
    galaxy = MagicMock()

    handler = proc._handler_registry.get(OrderType.COLONIZE)
    with patch.object(handler, "execute_action_order") as mock_exec:
        mock_exec.return_value = MagicMock(
            success=True, fleet_consumed=False, colonized=True, planet_name="X",
        )
        proc.execute_action_order(fleet, _empire(), galaxy,
                                  component_registry={"any": "thing"})

    mock_exec.assert_called_once()


def test_execute_action_order_logs_error_and_pops_when_colonize_missing_registry(caplog):
    """COLONIZE with `component_registry=None` → ColonizeHandler logs + pops, returns False.

    PROJ-368 Phase 4: the missing-component_registry branch lives inside
    ColonizeHandler.execute_action_order (Q1: log+pop+False preserved).
    """
    proc = OrderProcessor()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, _colonizable_planet()))

    import logging
    with caplog.at_level(logging.ERROR):
        result = proc.execute_action_order(
            fleet, _empire(), MagicMock(), component_registry=None,
        )

    assert result is False
    fleet.pop_order.assert_called_once()
    assert "requires component_registry" in caplog.text


# ---------------------------------------------------------------------------
# _deploy_drop_pod fallback: no pod found → warning + early return
# ---------------------------------------------------------------------------


def test_deploy_drop_pod_warns_and_returns_when_no_pod_found(caplog):
    """`_deploy_drop_pod` logs a warning and exits when no pod available."""
    proc = OrderProcessor()
    fleet = MagicMock()
    empty_ship = MagicMock()
    _wire_bay(empty_ship, [])
    fleet.ships = [empty_ship]
    planet = _colonizable_planet()

    import logging
    with caplog.at_level(logging.WARNING):
        proc._handler_registry.get(OrderType.COLONIZE)._deploy_drop_pod(fleet, planet)

    assert "No drop pod found" in caplog.text
    assert planet.facilities == []
