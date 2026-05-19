"""QA Observation B Phase 8 — planet-issued FMS launch integration.

End-to-end checks that the same order handlers used for fleet-issued
launches also drive planet-issued launches via the
:class:`PlanetStagingYardIssuerAdapter`. The carrier is the planet's
staging yard rather than a ship's bay; the resulting deployed group
appears in ``empire.fleets`` exactly as it would for a fleet launch.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.engine.issuer_adapter import PlanetStagingYardIssuerAdapter
from game.strategy.engine.order_handlers.launch_fighters import (
    LaunchFightersOrderHandler,
)
from game.strategy.engine.order_handlers.launch_satellites import (
    LaunchSatellitesOrderHandler,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fighter_typed(
    design_id: str = "fighter_alpha", hp: int = 80, mass: float = 20.0
) -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={
            "name": design_id,
            "ship_class": "Fighter (Small)",
            "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter",
        },
        vehicle_type="fighter",
        mass=mass,
        current_hp=hp,
    )


def _satellite_typed(
    design_id: str = "sat_alpha", hp: int = 60, mass: float = 15.0
) -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={
            "name": design_id,
            "ship_class": "Satellite (Small)",
            "vehicle_class": "Satellite (Small)",
            "vehicle_type": "Satellite",
        },
        vehicle_type="satellite",
        mass=mass,
        current_hp=hp,
    )


class _StubPlanet:
    """Minimal Planet shape compatible with PlanetStagingYardIssuerAdapter
    and the order handlers' planet branch (Order queue + staging_yard).
    """

    def __init__(self, *, planet_id: int, owner_id: int, location: HexCoord, name: str = "P1") -> None:
        self.id = planet_id
        self.owner_id = owner_id
        self.location = location
        self.global_hex = location
        self.name = name
        # PROJ-449 Phase 3: mirror Planet's ``_staging_yard`` private field —
        # ``PlanetStagingYardIssuerAdapter`` writes to the underscore name,
        # so expose ``staging_yard`` as a property aliasing the same list.
        self._staging_yard: list[dict] = []
        self.max_staging_mass: float = 0.0
        self.orders: list = []

    @property
    def staging_yard(self) -> list[dict]:
        return self._staging_yard

    @staging_yard.setter
    def staging_yard(self, value: list[dict]) -> None:
        self._staging_yard = value

    # IOrderable surface used by order handlers
    def get_current_order(self):
        return self.orders[0] if self.orders else None

    def pop_order(self):
        if self.orders:
            return self.orders.pop(0)
        return None

    def add_order(self, order) -> None:
        self.orders.append(order)

    def add_to_staging_yard(self, item) -> bool:
        # PROJ-450 Phase 4: production substrate is typed. Mass access
        # uses attribute lookup for CarriedVehicle/DropPod, with a dict
        # fallback for any legacy callers.
        if isinstance(item, CarriedVehicle):
            item_mass = float(item.mass)
        elif isinstance(item, dict):
            item_mass = float(item.get("mass", 0.0))
        else:
            item_mass = float(getattr(item, "mass", 0.0))
        if self.max_staging_mass > 0 and (
            sum(_item_mass(i) for i in self.staging_yard) + item_mass
            > self.max_staging_mass
        ):
            return False
        self.staging_yard.append(item)
        return True


def _item_mass(item) -> float:
    if isinstance(item, CarriedVehicle):
        return float(item.mass)
    if isinstance(item, dict):
        return float(item.get("mass", 0.0))
    return float(getattr(item, "mass", 0.0))


def _empire_with(planet: _StubPlanet) -> SimpleNamespace:
    empire = SimpleNamespace(
        id=planet.owner_id, name="E",
        fleets=[], colonies=[planet], deployed_groups=[],
    )
    empire.deployed_groups_of = lambda cls, _e=empire: [
        g for g in _e.deployed_groups if isinstance(g, cls)
    ]
    return empire


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_planet_issued_launch_fighters_creates_fighter_group() -> None:
    """A planet with fighters in its staging yard executes
    LAUNCH_FIGHTERS via the issuer-adapter path, producing a
    fighter_group fleet at the same hex.
    """
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(2, 3)
    planet = _StubPlanet(planet_id=7, owner_id=42, location=hex_c)
    for i in range(3):
        planet.add_to_staging_yard(_fighter_typed(hp=80 - i * 5))
    empire = _empire_with(planet)
    galaxy = SimpleNamespace(current_turn=1)

    planet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "fighter_design_id": "fighter_alpha",
        "count": 3,
        "target_hex": hex_c,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    handler = LaunchFightersOrderHandler()
    result = handler.execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
        galaxy=galaxy,
    )

    assert result.success, result.message
    assert planet.staging_yard == []
    from game.strategy.data.deployed_group import FighterWing
    fgs = empire.deployed_groups_of(FighterWing)
    assert len(fgs) == 1
    fg = fgs[0]
    assert fg.location == hex_c
    assert len(fg.ships) == 3
    # HP preserved into the deployed ShipInstance.
    assert sorted(int(s.current_hp) for s in fg.ships) == [70, 75, 80]


def test_planet_issued_launch_satellites_creates_satellite_group() -> None:
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(1, 1)
    planet = _StubPlanet(planet_id=8, owner_id=12, location=hex_c)
    for _ in range(2):
        planet.add_to_staging_yard(_satellite_typed())
    empire = _empire_with(planet)
    galaxy = SimpleNamespace(current_turn=1)

    planet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "satellite_design_id": "sat_alpha",
        "count": 2,
        "target_hex": hex_c,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    handler = LaunchSatellitesOrderHandler()
    result = handler.execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
        galaxy=galaxy,
    )

    assert result.success, result.message
    assert planet.staging_yard == []
    from game.strategy.data.deployed_group import SatelliteConstellation
    sgs = empire.deployed_groups_of(SatelliteConstellation)
    assert len(sgs) == 1
    assert len(sgs[0].ships) == 2


def test_planet_launch_rejects_when_staging_yard_insufficient() -> None:
    """Order asks for 5 fighters but only 2 are staged -> fail, staging
    yard left intact, order popped (best-effort terminate).
    """
    from game.strategy.data.order_types import Order, OrderType

    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=9, owner_id=3, location=hex_c)
    for _ in range(2):
        planet.add_to_staging_yard(_fighter_typed())
    empire = _empire_with(planet)
    galaxy = SimpleNamespace(current_turn=1)

    planet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "fighter_design_id": "fighter_alpha",
        "count": 5,
        "target_hex": hex_c,
    }))

    issuer = PlanetStagingYardIssuerAdapter(planet)
    result = LaunchFightersOrderHandler().execute_for_issuer(
        issuer=issuer,
        order_owner=planet,
        empire=empire,
        galaxy=galaxy,
    )

    assert not result.success
    # Staging yard fighters returned (since pop_carried/append_carried round-trips
    # leftover items when shortfall is detected).
    assert len(planet.staging_yard) == 2
    # No FighterWing created.
    from game.strategy.data.deployed_group import FighterWing
    assert empire.deployed_groups_of(FighterWing) == []
