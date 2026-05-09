"""PROJ-333 Phase 1: OrderProcessor TRANSFER characterization.

Pins TRANSFER routing for planet + fleet targets across cargo types
(drop_pod, passengers, resources), the BUG-70 LOAD_POPULATION
auto-resolve at fleet hex, the silent galaxy.empires fallback (and
the secondary owner-empire scan), and the staging-yard reverse
iteration semantics for drop pods.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import SpeciesPopulation
from game.strategy.engine.order_processor import OrderProcessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fleet(fleet_id: int = 1, location: HexCoord = HexCoord(0, 0)):
    f = MagicMock(spec=Fleet)
    f.id = fleet_id
    f.location = location
    f.ships = []
    f.pop_order = MagicMock()
    return f


def _planet(planet_id: int = 1, name: str = "P", *, owner_id: int = 0):
    p = MagicMock()
    p.id = planet_id
    p.name = name
    p.owner_id = owner_id
    p.populations = []
    p.facilities = []
    p.staging_yard = []
    p.planet_type = "continental"  # for is_planet protocol
    return p


def _empire(empire_id: int = 0):
    e = MagicMock()
    e.id = empire_id
    e.fleets = []
    e.race_config = MagicMock(race_id="humans")
    return e


def _ok_validation():
    v = MagicMock()
    v.is_valid = True
    return v


# ---------------------------------------------------------------------------
# process_transfer: invalid params
# ---------------------------------------------------------------------------


def test_process_transfer_returns_false_when_target_not_dict():
    """Transfer order with non-dict target → success=False, popped."""
    proc = OrderProcessor()
    order = Order(OrderType.TRANSFER, "not_a_dict")
    fleet = _fleet()
    fleet.get_current_order.return_value = order

    result = proc.process_transfer(fleet, _empire(), MagicMock())
    assert result.success is False
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# BUG-70: LOAD_POPULATION auto-resolves colony at fleet hex
# ---------------------------------------------------------------------------


def test_process_transfer_load_population_auto_resolves_colony_at_fleet_hex():
    """Bare LOAD_POPULATION with no planet_id resolves owned colony at hex."""
    proc = OrderProcessor()
    fleet = _fleet(location=HexCoord(2, 3))
    empire = _empire()

    colony = _planet(planet_id=5, name="Home", owner_id=empire.id)
    pop = SpeciesPopulation(race_id="humans", count=10, happiness=0.5)
    colony.populations = [pop]
    colony.total_population = 10

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [colony]

    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()

    # PROJ-393 (LEG-04-004): species_id is now required for passenger LOAD;
    # the colony has a single "humans" population so we name it explicitly.
    params = {"direction": "load", "cargo_type": "passengers", "amount": 5,
              "species_id": "humans"}
    fleet.get_current_order.return_value = Order(OrderType.LOAD_POPULATION, params)

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(fleet, empire, galaxy)

    assert result.success is True
    assert pop.count == 5
    fleet.resources.load_cargo_to_fleet.assert_called_with("passengers", 5)


def test_process_transfer_load_population_no_colony_returns_success_skipped():
    """LOAD_POPULATION at hex with no owned colony → success(skipped) + pop."""
    proc = OrderProcessor()
    fleet = _fleet(location=HexCoord(0, 0))
    fleet.get_current_order.return_value = Order(
        OrderType.LOAD_POPULATION,
        {"direction": "load", "cargo_type": "passengers", "amount": 0},
    )

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = []  # nothing here

    result = proc.process_transfer(fleet, _empire(), galaxy)

    assert result.success is True
    assert "skipped" in result.message
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# Target fleet lookup: galaxy.empires + owner-empire fallback
# ---------------------------------------------------------------------------


def test_process_transfer_target_fleet_lookup_searches_galaxy_empires():
    """`target_fleet_id` first searches `galaxy.empires` for a match."""
    proc = OrderProcessor()
    src = _fleet(fleet_id=1)
    target_fleet = _fleet(fleet_id=42)

    other_empire = MagicMock()
    other_empire.fleets = [target_fleet]
    galaxy = MagicMock()
    galaxy.empires = [other_empire]

    src.resources.get_fleet_cargo_current.return_value = 0
    src.resources.unload_cargo_from_fleet = MagicMock(return_value=0)
    target_fleet.resources.get_fleet_cargo_current.return_value = 0
    target_fleet.resources.get_fleet_cargo_capacity.return_value = 100

    src.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "unload", "cargo_type": "metals", "amount": 0,
         "target_fleet_id": 42},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(src, _empire(), galaxy)

    assert result.success is True


def test_process_transfer_target_fleet_falls_back_to_owner_empire_when_galaxy_lacks_empires_attr():
    """Galaxy without `empires` attr → falls through to owner empire scan."""
    proc = OrderProcessor()
    src = _fleet(fleet_id=1)
    target = _fleet(fleet_id=99)

    owner = _empire()
    owner.fleets = [target]

    # Plain object → no .empires attribute, so getattr default ([]) hits.
    galaxy = object()

    src.resources.get_fleet_cargo_current.return_value = 0
    src.resources.unload_cargo_from_fleet = MagicMock(return_value=0)
    target.resources.get_fleet_cargo_current.return_value = 0
    target.resources.get_fleet_cargo_capacity.return_value = 100

    src.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "unload", "cargo_type": "metals", "amount": 0,
         "target_fleet_id": 99},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(src, owner, galaxy)

    assert result.success is True


# ---------------------------------------------------------------------------
# drop_pod skips location check
# ---------------------------------------------------------------------------


def test_process_transfer_drop_pod_skips_location_check():
    """`cargo_type='drop_pod'` passes `skip_location_check=True` to the validator."""
    proc = OrderProcessor()
    fleet = _fleet()
    target_planet = _planet()
    target_planet.staging_yard = []

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = target_planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "load", "cargo_type": "drop_pod", "amount": 0,
         "planet_id": target_planet.id},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ) as mock_v:
        proc.process_transfer(fleet, _empire(), galaxy)

    assert mock_v.call_args.kwargs["skip_location_check"] is True


# ---------------------------------------------------------------------------
# Passenger load: capping by population + species_id targeting
# ---------------------------------------------------------------------------


def test_process_transfer_load_passengers_caps_by_population_count():
    """Load amount caps by the colony's species count (not just cargo space)."""
    proc = OrderProcessor()
    fleet = _fleet()
    empire = _empire()
    planet = _planet(owner_id=empire.id)
    pop = SpeciesPopulation(race_id="humans", count=3, happiness=0.5)
    planet.populations = [pop]
    planet.total_population = 3

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        # PROJ-393 (LEG-04-004): species_id is now required for passenger LOAD.
        {"direction": "load", "cargo_type": "passengers", "amount": 50,
         "planet_id": planet.id, "species_id": "humans"},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(fleet, empire, galaxy)

    assert result.amount_transferred == 3
    assert pop.count == 0
    fleet.resources.load_cargo_to_fleet.assert_called_with("passengers", 3)


def test_process_transfer_load_passengers_with_species_id_targets_specific_species():
    """`species_id` selects the matching species; non-matching are untouched."""
    proc = OrderProcessor()
    fleet = _fleet()
    empire = _empire()
    planet = _planet(owner_id=empire.id)
    humans = SpeciesPopulation(race_id="humans", count=5, happiness=0.5)
    drones = SpeciesPopulation(race_id="drones", count=10, happiness=0.5)
    planet.populations = [humans, drones]
    planet.total_population = 15

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "load", "cargo_type": "passengers", "amount": 4,
         "planet_id": planet.id, "species_id": "drones"},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(fleet, empire, galaxy)

    assert result.amount_transferred == 4
    assert humans.count == 5  # untouched
    assert drones.count == 6


def test_process_transfer_unload_passengers_creates_new_species_population_when_absent():
    """Unloading a species not yet on the planet appends a new SpeciesPopulation."""
    proc = OrderProcessor()
    fleet = _fleet()
    empire = _empire()
    planet = _planet(owner_id=empire.id)
    planet.populations = []  # empty colony

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.resources.get_fleet_cargo_current.return_value = 7
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=7)
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "unload", "cargo_type": "passengers", "amount": 7,
         "planet_id": planet.id, "species_id": "newcomers"},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        proc.process_transfer(fleet, empire, galaxy)

    assert len(planet.populations) == 1
    assert planet.populations[0].race_id == "newcomers"
    assert planet.populations[0].count == 7


# ---------------------------------------------------------------------------
# Resource cargo load: capped by stockpile
# ---------------------------------------------------------------------------


def test_process_transfer_load_resource_caps_by_planet_stockpile():
    """Load amount capped by `int(round(planet.get_stockpile(...)))`."""
    proc = OrderProcessor()
    fleet = _fleet()
    empire = _empire()
    planet = _planet(owner_id=empire.id)
    planet.get_stockpile = MagicMock(return_value=2.4)  # → int(round(2.4)) = 2
    planet.consume_from_stockpile = MagicMock()

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "load", "cargo_type": "metals", "amount": 50,
         "planet_id": planet.id},
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = proc.process_transfer(fleet, empire, galaxy)

    assert result.amount_transferred == 2
    fleet.resources.load_cargo_to_fleet.assert_called_with("metals", 2)
    planet.consume_from_stockpile.assert_called_with("metals", 2.0)


# ---------------------------------------------------------------------------
# Drop pod load/unload: staging yard iteration
# ---------------------------------------------------------------------------


def test_load_pod_from_staging_yard_iterates_in_reverse():
    """Pod load iterates staging yard in reverse (LIFO) per design.md surprise #3."""
    proc = OrderProcessor()
    fleet = _fleet()
    ship = MagicMock()
    ship.name = "Carrier"
    ship.get_pod_storage_capacity = MagicMock(return_value=10)
    ship.get_pod_storage_used = MagicMock(return_value=0)
    ship.can_carry_pod = MagicMock(return_value=True)
    ship.carried_items = []
    fleet.ships = [ship]

    planet = _planet()
    pod_a = {"name": "PodA", "mass": 1.0}
    pod_b = {"name": "PodB", "mass": 1.0}
    pod_c = {"name": "PodC", "mass": 1.0}
    planet.staging_yard = [pod_a, pod_b, pod_c]

    def _remove(idx):
        return planet.staging_yard.pop(idx)
    planet.remove_from_staging_yard = MagicMock(side_effect=_remove)

    loaded = proc._handler_registry.get(OrderType.TRANSFER)._dispatch_drop_pod_load(fleet, planet, None, 1)

    assert loaded == 1
    # Reverse iteration: the LAST pod (PodC) was loaded first.
    assert ship.carried_items == [pod_c]
    assert planet.staging_yard == [pod_a, pod_b]


def test_unload_pod_to_staging_yard_returns_count_unloaded():
    """Pod unload returns the count actually moved, removing items from ship."""
    proc = OrderProcessor()
    fleet = _fleet()
    ship = MagicMock()
    pod_x = {"name": "PodX"}
    pod_y = {"name": "PodY"}
    ship.carried_items = [pod_x, pod_y]
    fleet.ships = [ship]

    planet = _planet()
    planet.add_to_staging_yard = MagicMock(return_value=True)

    count = proc._handler_registry.get(OrderType.TRANSFER)._dispatch_drop_pod_unload(fleet, planet, None, 2)

    assert count == 2
    assert ship.carried_items == []
    assert planet.add_to_staging_yard.call_count == 2
