"""Tests for the polymorphic IIssuerAdapter (QA Observation B).

Both adapter shapes must round-trip ``pop_carried``/``append_carried``
identically over the same item dicts so the order handlers can treat
fleet- and planet-issued FMS actions uniformly.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.engine.issuer_adapter import (
    FleetShipIssuerAdapter,
    PlanetStagingYardIssuerAdapter,
)


# --------------------------------------------------------------------- helpers


def _mine_dict(design_id: str = "mine_warhead_small", mass: float = 5.0) -> dict:
    return {
        "design_id": design_id,
        "design_data": {"name": design_id},
        "vehicle_type": "mine",
        "mass": mass,
        "current_hp": 30,
    }


def _fighter_dict(design_id: str = "scout_fighter", mass: float = 10.0) -> dict:
    return {
        "design_id": design_id,
        "design_data": {"name": design_id},
        "vehicle_type": "fighter",
        "mass": mass,
        "current_hp": 100,
    }


class _StubShip:
    def __init__(self) -> None:
        self.instance_id = "carrier_1"
        self.design_id = "stub"
        self.owner_id = 42
        self.name = "Carrier"
        self.design_data = {}
        self.current_hp = 100
        self.carried_items: list[dict] = []
        self.is_alive = True
        self.is_derelict = False
        self._cargo_mgr = None  # filled in tests as needed


def _make_fleet(carrier: _StubShip, hex_c: HexCoord) -> Fleet:
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        display_name="Test Fleet", group_kind="fleet",
    )
    fleet.ships.append(carrier)
    return fleet


def _make_planet(
    name: str = "TestPlanet", max_staging: float = 0.0, owner_id: int = 42,
) -> Planet:
    p = Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5510.0,
        surface_gravity=9.8,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )
    p.owner_id = owner_id
    p.max_staging_mass = max_staging
    p.id = 99
    return p


# --------------------------------------------------------------------- fleet adapter


def test_fleet_adapter_location_owner_label():
    carrier = _StubShip()
    hex_c = HexCoord(3, -2)
    fleet = _make_fleet(carrier, hex_c)
    a = FleetShipIssuerAdapter(fleet, carrier)
    assert a.location == hex_c
    assert a.owner_id == 42
    assert "Test Fleet" in a.display_label


def test_fleet_adapter_pop_carried_filters_by_type_and_design():
    carrier = _StubShip()
    carrier.carried_items = [
        _mine_dict("mine_a"),
        _mine_dict("mine_b"),
        _fighter_dict(),
        _mine_dict("mine_a"),
    ]
    fleet = _make_fleet(carrier, HexCoord(0, 0))
    a = FleetShipIssuerAdapter(fleet, carrier)

    popped = a.pop_carried("mine", "mine_a", count=2)
    assert len(popped) == 2
    assert all(p["design_id"] == "mine_a" for p in popped)
    # remaining: 1 mine_b + 1 fighter
    assert len(carrier.carried_items) == 2


def test_fleet_adapter_pop_all_when_count_none():
    carrier = _StubShip()
    carrier.carried_items = [_mine_dict(), _mine_dict(), _fighter_dict()]
    fleet = _make_fleet(carrier, HexCoord(0, 0))
    a = FleetShipIssuerAdapter(fleet, carrier)

    popped = a.pop_carried("mine", None, count=None)
    assert len(popped) == 2
    # leaves the fighter alone
    assert len(carrier.carried_items) == 1
    assert carrier.carried_items[0]["vehicle_type"] == "fighter"


def test_fleet_adapter_count_carried():
    carrier = _StubShip()
    carrier.carried_items = [_mine_dict(), _mine_dict("mine_b"), _fighter_dict()]
    fleet = _make_fleet(carrier, HexCoord(0, 0))
    a = FleetShipIssuerAdapter(fleet, carrier)
    assert a.count_carried("mine", None) == 2
    assert a.count_carried("mine", "mine_b") == 1
    assert a.count_carried("fighter", None) == 1
    assert a.count_carried("satellite", None) == 0


def test_fleet_adapter_append_carried_roundtrip():
    carrier = _StubShip()
    fleet = _make_fleet(carrier, HexCoord(0, 0))
    a = FleetShipIssuerAdapter(fleet, carrier)
    items = [_mine_dict(), _mine_dict()]
    n = a.append_carried(items)
    assert n == 2
    assert len(carrier.carried_items) == 2


# --------------------------------------------------------------------- planet adapter


def test_planet_adapter_location_owner_label():
    p = _make_planet(name="Foo", owner_id=42)
    a = PlanetStagingYardIssuerAdapter(p)
    assert a.location == HexCoord(0, 0)
    assert a.owner_id == 42
    assert "Foo" in a.display_label


def test_planet_adapter_pop_carried_from_staging_yard():
    p = _make_planet()
    p.staging_yard = [_mine_dict(), _mine_dict("mine_b"), _fighter_dict()]
    a = PlanetStagingYardIssuerAdapter(p)

    popped = a.pop_carried("mine", None, count=None)
    assert len(popped) == 2
    assert len(p.staging_yard) == 1
    assert p.staging_yard[0]["vehicle_type"] == "fighter"


def test_planet_adapter_pop_carried_specific_design():
    p = _make_planet()
    p.staging_yard = [_mine_dict("mine_a"), _mine_dict("mine_b"), _mine_dict("mine_a")]
    a = PlanetStagingYardIssuerAdapter(p)

    popped = a.pop_carried("mine", "mine_a", count=1)
    assert len(popped) == 1
    assert popped[0]["design_id"] == "mine_a"
    assert len(p.staging_yard) == 2  # 1 of each design remains


def test_planet_adapter_count_carried():
    p = _make_planet()
    p.staging_yard = [_mine_dict(), _mine_dict("mine_b"), _fighter_dict()]
    a = PlanetStagingYardIssuerAdapter(p)
    assert a.count_carried("mine", None) == 2
    assert a.count_carried("fighter", None) == 1


def test_planet_adapter_append_respects_max_staging_mass():
    p = _make_planet(max_staging=12.0)  # caps at 12 — 2 mines @ 5 = 10 ok, 3rd overflows
    a = PlanetStagingYardIssuerAdapter(p)
    items = [_mine_dict(mass=5.0), _mine_dict(mass=5.0), _mine_dict(mass=5.0)]
    n = a.append_carried(items)
    assert n == 2  # 3rd would push to 15 > 12
    assert len(p.staging_yard) == 2


def test_planet_adapter_append_no_cap_when_zero():
    p = _make_planet(max_staging=0.0)
    a = PlanetStagingYardIssuerAdapter(p)
    items = [_mine_dict(mass=100.0) for _ in range(5)]
    assert a.append_carried(items) == 5


def test_planet_adapter_append_recovered_via_to_dict():
    p = _make_planet(max_staging=100.0)
    a = PlanetStagingYardIssuerAdapter(p)
    cv = CarriedVehicle(
        design_id="scout_fighter",
        design_data={"name": "scout"},
        vehicle_type="fighter",
        mass=10.0,
        current_hp=80,
    )
    assert a.append_recovered(cv) is True
    assert len(p.staging_yard) == 1
    assert p.staging_yard[0]["design_id"] == "scout_fighter"


def test_planet_adapter_append_recovered_respects_cap():
    p = _make_planet(max_staging=5.0)
    p.staging_yard = [_mine_dict(mass=5.0)]
    a = PlanetStagingYardIssuerAdapter(p)
    cv = CarriedVehicle(
        design_id="scout_fighter",
        design_data={},
        vehicle_type="fighter",
        mass=10.0,
        current_hp=80,
    )
    # adding cv (mass 10) would exceed cap of 5
    assert a.append_recovered(cv) is False
    assert len(p.staging_yard) == 1


# --------------------------------------------------------------------- protocol


def test_both_adapters_satisfy_protocol():
    from game.strategy.engine.issuer_adapter import IIssuerAdapter

    carrier = _StubShip()
    fleet = _make_fleet(carrier, HexCoord(0, 0))
    fleet_a = FleetShipIssuerAdapter(fleet, carrier)
    planet_a = PlanetStagingYardIssuerAdapter(_make_planet())
    assert isinstance(fleet_a, IIssuerAdapter)
    assert isinstance(planet_a, IIssuerAdapter)
