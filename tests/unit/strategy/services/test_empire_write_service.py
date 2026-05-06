"""Unit tests for EmpireWriteService (PROJ-370 Phase 4)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IEmpireMutator
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.services.empire_write_service import EmpireWriteService


def _make_empire(empire_id: int = 0) -> Empire:
    return Empire(
        empire_id=empire_id, name=f"E{empire_id}", color=(255, 0, 0),
    )


def _make_planet() -> Planet:
    return Planet(
        name="X",
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
def service() -> EmpireWriteService:
    return EmpireWriteService()


def test_empire_write_service_satisfies_protocol(
    service: EmpireWriteService,
) -> None:
    assert isinstance(service, IEmpireMutator)


def test_add_colony_assigns_owner_id(service: EmpireWriteService) -> None:
    empire = _make_empire(0)
    planet = _make_planet()
    service.add_colony(empire, planet)
    assert planet in empire.colonies
    assert planet.owner_id == 0


def test_remove_colony_returns_true_when_present(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    planet = _make_planet()
    empire.add_colony(planet)
    assert service.remove_colony(empire, planet) is True
    assert planet not in empire.colonies


def test_remove_colony_returns_false_when_absent(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    planet = _make_planet()
    assert service.remove_colony(empire, planet) is False


def test_clear_colonies_empties_list(service: EmpireWriteService) -> None:
    empire = _make_empire(0)
    empire.add_colony(_make_planet())
    empire.add_colony(_make_planet())
    service.clear_colonies(empire)
    assert empire.colonies == []


def test_add_fleet_sets_owner(service: EmpireWriteService) -> None:
    empire = _make_empire(2)
    fleet = Fleet(fleet_id=1, owner_id=99, location=HexCoord(0, 0))
    service.add_fleet(empire, fleet)
    assert fleet in empire.fleets
    assert fleet.owner_id == 2


def test_remove_fleet_returns_true_when_present(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    empire.add_fleet(fleet)
    assert service.remove_fleet(empire, fleet) is True


def test_remove_fleet_returns_false_when_absent(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    assert service.remove_fleet(empire, fleet) is False


def test_set_max_storage_amount(service: EmpireWriteService) -> None:
    empire = _make_empire(0)
    service.set_max_storage_amount(empire, "metals", 1000.0)
    assert empire.max_storage["metals"] == 1000.0


def test_replace_max_storage_clears_then_repopulates(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    empire.max_storage["old"] = 50.0
    service.replace_max_storage(empire, {"metals": 1000.0, "organics": 500.0})
    assert empire.max_storage == {"metals": 1000.0, "organics": 500.0}


def test_add_built_design(service: EmpireWriteService) -> None:
    empire = _make_empire(0)
    service.add_built_design(empire, "scout")
    assert "scout" in empire.built_ship_designs


def test_prune_empty_fleets_removes_only_empty(
    service: EmpireWriteService,
) -> None:
    empire = _make_empire(0)
    empty_fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    full_fleet = Fleet(fleet_id=2, owner_id=0, location=HexCoord(0, 0))
    full_fleet.ships.append(MagicMock(is_combat_capable=lambda: True))
    empire.add_fleet(empty_fleet)
    empire.add_fleet(full_fleet)
    removed = service.prune_empty_fleets(
        {0: empire},
        {0: [empty_fleet, full_fleet]},
    )
    assert removed == [empty_fleet.id]
    assert empty_fleet not in empire.fleets
    assert full_fleet in empire.fleets
