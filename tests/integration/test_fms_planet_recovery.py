"""QA Observation B Phase 8 — planet-issued FMS recovery integration.

Verifies that the same order handlers used for fleet-issued recovery
also drive planet-issued recovery via the
:class:`PlanetStagingYardIssuerAdapter`. Recovered fighters /
satellites land in the planet's staging yard with HP preserved, and
the source deployed group is consumed (or shrunk) as normal.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import FighterWing, SatelliteConstellation
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.issuer_adapter import PlanetStagingYardIssuerAdapter
from game.strategy.engine.order_handlers.recover_fighters import (
    RecoverFightersOrderHandler,
)
from game.strategy.engine.order_handlers.recover_satellites import (
    RecoverSatellitesOrderHandler,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _StubPlanet:
    def __init__(self, *, planet_id: int, owner_id: int, location: HexCoord, name: str = "P") -> None:
        self.id = planet_id
        self.owner_id = owner_id
        self.location = location
        self.global_hex = location
        self.name = name
        self.staging_yard: list[dict] = []
        self.max_staging_mass: float = 0.0
        self.orders: list = []

    def get_current_order(self):
        return self.orders[0] if self.orders else None

    def pop_order(self):
        if self.orders:
            return self.orders.pop(0)
        return None

    def add_order(self, order) -> None:
        self.orders.append(order)

    def add_to_staging_yard(self, item) -> bool:
        # PROJ-450 Phase 1: mirror Planet.add_to_staging_yard's typed
        # normalisation — accept dict / CarriedVehicle / DropPod and
        # store as a dict on the legacy substrate.
        if isinstance(item, DropPod):
            item_dict = dict(item.payload)
            item_dict["design_id"] = item.design_id
            item_dict["design_data"] = item.design_data
            item_dict["mass"] = float(item.mass)
        elif isinstance(item, CarriedVehicle):
            item_dict = item.to_dict()
        else:
            item_dict = item
        item_mass = item_dict.get("mass", 0.0)
        if self.max_staging_mass > 0 and (
            sum(i.get("mass", 0.0) for i in self.staging_yard) + item_mass
            > self.max_staging_mass
        ):
            return False
        self.staging_yard.append(item_dict)
        return True


def _fighter_ship(instance_id: str, owner_id: int, hp: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="fighter_alpha",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "fighter_alpha", "mass": 20.0},
        current_hp=hp,
    )


def _satellite_ship(instance_id: str, owner_id: int, hp: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="sat_alpha",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "sat_alpha", "mass": 15.0},
        current_hp=hp,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_planet_issued_recover_fighters_drains_fighter_group_into_staging() -> None:
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=1, owner_id=42, location=hex_c)

    fg = FighterWing(group_id=200001, owner_id=42, location=hex_c)
    fg.ships.extend(_fighter_ship(f"f_{i}", 42, hp=70 + i) for i in range(3))
    empire = SimpleNamespace(id=42, name="E", fleets=[], deployed_groups=[fg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    planet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "fighter_group_id": fg.id,
        "count": None,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    result = RecoverFightersOrderHandler().execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
    )

    assert result.success, result.message
    # Group fully drained -> removed from empire.fleets.
    assert fg not in empire.deployed_groups
    assert len(planet.staging_yard) == 3
    # HP preserved on the staged items.
    assert sorted(int(item["current_hp"]) for item in planet.staging_yard) == [70, 71, 72]


def test_planet_issued_recover_satellites_drains_into_staging() -> None:
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(1, 2)
    planet = _StubPlanet(planet_id=2, owner_id=7, location=hex_c)

    sg = SatelliteConstellation(group_id=210001, owner_id=7, location=hex_c)
    sg.ships.extend(_satellite_ship(f"s_{i}", 7, hp=55 + i) for i in range(2))
    empire = SimpleNamespace(id=7, name="E", fleets=[], deployed_groups=[sg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    planet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "satellite_group_id": sg.id,
        "count": None,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    result = RecoverSatellitesOrderHandler().execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
    )

    assert result.success, result.message
    assert sg not in empire.deployed_groups
    assert len(planet.staging_yard) == 2
    assert sorted(int(item["current_hp"]) for item in planet.staging_yard) == [55, 56]


def test_planet_recovery_partial_when_staging_capacity_caps() -> None:
    """``max_staging_mass`` < total fighter mass -> partial recovery,
    surplus stays with the fighter_group.
    """
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(3, 3)
    planet = _StubPlanet(planet_id=4, owner_id=11, location=hex_c)
    # Each fighter is 20 mass. Cap to fit exactly 2.
    planet.max_staging_mass = 40.0

    fg = FighterWing(group_id=220001, owner_id=11, location=hex_c)
    fg.ships.extend(_fighter_ship(f"f_{i}", 11, hp=80) for i in range(5))
    empire = SimpleNamespace(id=11, name="E", fleets=[], deployed_groups=[fg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    planet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "fighter_group_id": fg.id,
        "count": None,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    result = RecoverFightersOrderHandler().execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
    )

    assert result.success, result.message
    assert len(planet.staging_yard) == 2
    # Group still present with remaining ships.
    assert fg in empire.deployed_groups
    assert len(fg.ships) == 3
