"""Unit tests for PlanetWriteService (PROJ-370 Phase 3)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IPlanetMutator
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.services.planet_write_service import PlanetWriteService


def _make_planet() -> Planet:
    return Planet(
        name="TestWorld",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=1.0,
        radius=1.0,
        surface_area=1.0,
        density=1.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=300.0,
        surface_water=0.5,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )


@pytest.fixture
def planet() -> Planet:
    return _make_planet()


@pytest.fixture
def service() -> PlanetWriteService:
    return PlanetWriteService()


def test_planet_write_service_satisfies_protocol(
    service: PlanetWriteService,
) -> None:
    assert isinstance(service, IPlanetMutator)


# ---- Stockpile ----


def test_set_stockpile_amount(
    service: PlanetWriteService, planet: Planet
) -> None:
    service.set_stockpile_amount(planet, "metals", 250.0)
    assert planet.stockpile["metals"] == 250.0


def test_set_max_stockpile(
    service: PlanetWriteService, planet: Planet
) -> None:
    service.set_max_stockpile(planet, {"metals": 1000.0, "organics": 500.0})
    assert planet.max_stockpile == {"metals": 1000.0, "organics": 500.0}


# ---- Populations ----


def test_add_species_population(
    service: PlanetWriteService, planet: Planet
) -> None:
    pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
    service.add_species_population(planet, pop)
    assert pop in planet.populations


def test_remove_species_population_returns_true_when_present(
    service: PlanetWriteService, planet: Planet
) -> None:
    pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
    planet.populations.append(pop)
    assert service.remove_species_population(planet, pop) is True


def test_remove_species_population_returns_false_when_absent(
    service: PlanetWriteService, planet: Planet
) -> None:
    pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
    assert service.remove_species_population(planet, pop) is False


def test_update_population_count(
    service: PlanetWriteService, planet: Planet
) -> None:
    pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
    planet.populations.append(pop)
    service.update_population_count(planet, "human", 200.0)
    assert pop.count == 200.0


# ---- Facilities ----


def test_add_facility(service: PlanetWriteService, planet: Planet) -> None:
    facility = MagicMock()
    service.add_facility(planet, facility)
    assert facility in planet.facilities


def test_remove_facility(service: PlanetWriteService, planet: Planet) -> None:
    facility = MagicMock()
    planet.facilities.append(facility)
    assert service.remove_facility(planet, facility) is True
    assert facility not in planet.facilities


# ---- Construction queue ----


def test_construction_queue_append_and_pop(
    service: PlanetWriteService, planet: Planet
) -> None:
    item = {"design_id": "factory"}
    service.append_construction_item(planet, item)
    assert planet.construction_queue == [item]
    popped = service.pop_construction_item(planet)
    assert popped == item


# ---- Orders ----


def test_orders_append_pop_clear(
    service: PlanetWriteService, planet: Planet
) -> None:
    o1 = Order(order_type=OrderType.MOVE)
    o2 = Order(order_type=OrderType.MOVE)
    service.append_order(planet, o1)
    service.append_order(planet, o2)
    assert planet.orders == [o1, o2]
    popped = service.pop_order(planet)
    assert popped is o1
    service.clear_orders(planet)
    assert planet.orders == []


# ---- Scalar fields ----


def test_set_owner_id(service: PlanetWriteService, planet: Planet) -> None:
    service.set_owner_id(planet, 1)
    assert planet.owner_id == 1


def test_set_atmosphere(service: PlanetWriteService, planet: Planet) -> None:
    new_atm = {"N2": 78000.0, "O2": 21000.0}
    service.set_atmosphere(planet, new_atm)
    assert planet.atmosphere == new_atm


def test_set_energy(service: PlanetWriteService, planet: Planet) -> None:
    service.set_energy(planet, 50.0)
    assert planet.energy == 50.0


def test_set_energy_capacity_and_generation(
    service: PlanetWriteService, planet: Planet
) -> None:
    service.set_energy_capacity(planet, 1000.0)
    service.set_energy_generation(planet, 50.0)
    assert planet.energy_capacity == 1000.0
    assert planet.energy_generation == 50.0


def test_set_radiation_shielding(
    service: PlanetWriteService, planet: Planet
) -> None:
    service.set_radiation_shielding(planet, 0.5)
    assert planet.radiation_shielding == 0.5
    service.set_radiation_shielding_target(planet, 0.75)
    assert planet.radiation_shielding_target == 0.75
