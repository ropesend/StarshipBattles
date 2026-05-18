"""Per-handler tests for `ColonizeHandler` (PROJ-368 Phase 2).

Drives the handler directly. Mirrors the characterization smoke in
`tests/unit/strategy/engine/test_order_processor_colonize.py` but at the
handler level, with lightweight fixtures.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.colonize import ColonizeHandler
from game.strategy.events.event_types import EventCategory, EventType


def _ship_with_pod(design_id: str, name: str, design_data: dict) -> MagicMock:
    """PROJ-436 Phase 9: build a MagicMock ship with a typed
    ``bay_inventory.pods`` slot. The handler's ``_deploy_drop_pod``
    reads ``ship.bay_inventory.pods`` and writes back via
    ``ship.set_bay_inventory(...)``. The legacy ``carried_items``
    mirror is gone — production code reads the typed slot.
    """
    ship = MagicMock()
    pod = DropPod(
        design_id=design_id,
        design_data=design_data,
        mass=0.0,
        payload={"name": name},
    )
    ship.bay_inventory = BayInventory(bay=[], pods=[pod])

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi

    ship.set_bay_inventory = _set_bay_inventory
    return ship


def _captured_event_bus():
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    return _Bus(), captured


def _fleet_with_order(order, *, location=HexCoord(0, 0)):
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


def test_no_order_returns_uncolonized():
    handler = ColonizeHandler()
    fleet = _fleet_with_order(None)
    result = handler.execute_action_order(fleet, _empire(), MagicMock(), component_registry={})
    assert result.colonized is False
    assert result.success is False


def test_missing_component_registry_logs_and_pops():
    """Q1 resolution: missing component_registry pops the order and returns False."""
    handler = ColonizeHandler()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    result = handler.execute_action_order(
        fleet, empire, MagicMock(),
        component_registry=None,
    )
    assert result.colonized is False
    assert result.success is False
    fleet.pop_order.assert_called_once()


def test_validation_failure_pops_and_returns_false():
    handler = ColonizeHandler()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    galaxy = MagicMock()
    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate:
        mock_validate.return_value = MagicMock(is_valid=False, message="bad")
        result = handler.execute_action_order(fleet, empire, galaxy, component_registry={})
    assert result.colonized is False
    fleet.pop_order.assert_called_once()
    empire.add_colony.assert_not_called()


def test_any_planet_sentinel_resolves_first_unowned():
    """target_planet is None → handler picks the first unowned planet at fleet hex."""
    handler = ColonizeHandler()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, None))
    empire = _empire()

    candidate = _colonizable_planet(planet_id=42, name="Kepler-22b")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [candidate]
    galaxy.get_system_of_planet.return_value = None

    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate, patch(
        "game.strategy.validation.ColonizeValidator.fleet_has_drop_pod",
        return_value=True,
    ), patch(
        "game.strategy.validation.colonize_validator.ColonizeValidator.find_ship_with_drop_pod",
        return_value=(None, None),  # _deploy_drop_pod no-ops
    ):
        mock_validate.return_value = MagicMock(is_valid=True)
        result = handler.execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is True
    assert result.planet_name == "Kepler-22b"
    empire.add_colony.assert_called_once_with(candidate)


def test_no_drop_pod_pops_and_returns_false():
    handler = ColonizeHandler()
    planet = _colonizable_planet()
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()
    galaxy = MagicMock()
    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate, patch(
        "game.strategy.validation.ColonizeValidator.fleet_has_drop_pod",
        return_value=False,
    ):
        mock_validate.return_value = MagicMock(is_valid=True)
        result = handler.execute_action_order(fleet, empire, galaxy, component_registry={})
    assert result.colonized is False
    fleet.pop_order.assert_called_once()
    empire.add_colony.assert_not_called()


def test_happy_path_claims_planet_and_deploys_pod():
    """Successful colonization: empire.add_colony called, pod deployed, event emitted."""
    bus, captured = _captured_event_bus()
    handler = ColonizeHandler(event_bus=bus)

    planet = _colonizable_planet(planet_id=77, name="New Earth")
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()

    galaxy = MagicMock()
    sys_obj = MagicMock()
    sys_obj.name = "Sol"
    galaxy.get_system_of_planet.return_value = sys_obj

    fake_ship = _ship_with_pod(
        design_id="drop_pod_basic",
        name="Test Pod",
        design_data={"initial_stockpile": {"metals": 10}},
    )

    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate, patch(
        "game.strategy.validation.ColonizeValidator.fleet_has_drop_pod",
        return_value=True,
    ), patch(
        "game.strategy.validation.colonize_validator.ColonizeValidator.find_ship_with_drop_pod",
        return_value=(fake_ship, 0),
    ):
        mock_validate.return_value = MagicMock(is_valid=True)
        result = handler.execute_action_order(fleet, empire, galaxy, component_registry={})

    assert result.colonized is True
    assert result.planet_name == "New Earth"
    empire.add_colony.assert_called_once_with(planet)
    # Drop pod removed from ship and facility appended on planet.
    assert fake_ship.bay_inventory.pods == []
    assert len(planet.facilities) == 1
    # initial_stockpile seeded.
    planet.add_to_stockpile.assert_called_once_with("metals", 10.0)


def test_emits_colony_founded_event_payload_exact_match():
    """COLONY_FOUNDED payload includes system_name + local_hex (PROJ-368 invariant)."""
    bus, captured = _captured_event_bus()
    handler = ColonizeHandler(event_bus=bus)

    planet = _colonizable_planet(planet_id=77, name="New Earth")
    planet.location = HexCoord(3, -2)
    fleet = _fleet_with_order(Order(OrderType.COLONIZE, planet))
    empire = _empire()

    galaxy = MagicMock()
    sys_obj = MagicMock()
    sys_obj.name = "Sol"
    galaxy.get_system_of_planet.return_value = sys_obj

    fake_ship = _ship_with_pod(
        design_id="drop_pod_basic",
        name="Test Pod",
        design_data={},
    )

    with patch(
        "game.strategy.validation.ColonizeValidator.validate"
    ) as mock_validate, patch(
        "game.strategy.validation.ColonizeValidator.fleet_has_drop_pod",
        return_value=True,
    ), patch(
        "game.strategy.validation.colonize_validator.ColonizeValidator.find_ship_with_drop_pod",
        return_value=(fake_ship, 0),
    ):
        mock_validate.return_value = MagicMock(is_valid=True)
        handler.execute_action_order(fleet, empire, galaxy, component_registry={})

    founded = [e for e in captured if e[0] == EventType.COLONY_FOUNDED]
    assert len(founded) == 1
    payload = founded[0][1]
    assert payload["category"] == EventCategory.COLONIES
    assert payload["empire_id"] == 0
    assert payload["planet_id"] == 77
    assert payload["planet_name"] == "New Earth"
    assert payload["system_name"] == "Sol"
    assert payload["local_hex"] == [3, -2]
    assert payload["location_hex"] == [0, 0]
