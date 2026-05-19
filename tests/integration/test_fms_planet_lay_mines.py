"""PROJ-445 Phase 1 (F-B-022 + F-B-001) — planet-FMS engine-mediated dispatch.

Parametrised across the five planet-FMS order types so that any new
planet-FMS handler added without the unified 5-kwarg
``execute_for_issuer`` signature is caught here before it reaches
production.

The bug this test was authored to catch (F-B-001):
``LayMinesOrderHandler.execute_for_issuer`` was missing the
``registries`` kwarg that
:meth:`ActionExecutionEngine._execute_planet_action` unconditionally
passes since PROJ-438 Phase 6 removed the ``try / except TypeError``
fallback. Any planet-issued ``OrderType.LAY_MINES`` therefore raised
``TypeError`` at dispatch. The fix mirrors :mod:`recover_fighters`'
accept-and-ignore shape; this test parametrises across all five
planet-FMS order types so the same drift caught here next time will
fail for any handler, not just LayMines.

Strategy: drive each order through
:meth:`ActionExecutionEngine._execute_planet_action` (which calls
``handler.execute_for_issuer(..., registries=...)`` exactly once with
the unified signature) and assert:

- no exception escapes,
- the order queue is advanced (handler reached and popped the order).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import FighterWing, SatelliteConstellation
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.action_execution_engine import ActionExecutionEngine
from game.strategy.engine.order_processor import OrderProcessor


class _StubPlanet:
    """Minimal Planet shape compatible with PlanetStagingYardIssuerAdapter
    and the planet branch of every planet-FMS order handler.
    """

    def __init__(
        self,
        *,
        planet_id: int,
        owner_id: int,
        location: HexCoord,
        name: str = "P1",
    ) -> None:
        self.id = planet_id
        self.owner_id = owner_id
        self.location = location
        self.global_hex = location
        self.name = name
        self.staging_yard: list = []
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
        # PROJ-450 Phase 4: production substrate is typed. Mass access
        # uses attribute lookup for CarriedVehicle/DropPod, with a dict
        # fallback for any legacy callers.
        if isinstance(item, (CarriedVehicle,)):
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


def _mine_typed(design_id: str = "mine_alpha") -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={"name": design_id},
        vehicle_type="mine",
        mass=5.0,
        current_hp=30,
    )


def _fighter_typed(design_id: str = "fighter_alpha") -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={"name": design_id, "vehicle_class": "Fighter (Small)"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )


def _satellite_typed(design_id: str = "sat_alpha") -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={"name": design_id, "vehicle_class": "Satellite (Small)"},
        vehicle_type="satellite",
        mass=15.0,
        current_hp=60,
    )


def _fighter_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="fighter_alpha",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "fighter_alpha", "mass": 20.0},
        current_hp=80,
    )


def _satellite_ship(instance_id: str, owner_id: int) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="sat_alpha",
        name=instance_id,
        owner_id=owner_id,
        design_data={"name": "sat_alpha", "mass": 15.0},
        current_hp=60,
    )


def _build_lay_mines_scenario(planet: _StubPlanet, empire: SimpleNamespace) -> None:
    planet.add_to_staging_yard(_mine_typed())
    planet.add_order(
        Order(
            OrderType.LAY_MINES,
            target={
                "mine_design_id": "mine_alpha",
                "count": 1,
                "target_hex": planet.location,
            },
        )
    )


def _build_launch_fighters_scenario(
    planet: _StubPlanet, empire: SimpleNamespace
) -> None:
    planet.add_to_staging_yard(_fighter_typed())
    planet.add_order(
        Order(
            OrderType.LAUNCH_FIGHTERS,
            target={
                "fighter_design_id": "fighter_alpha",
                "count": 1,
                "target_hex": planet.location,
            },
        )
    )


def _build_launch_satellites_scenario(
    planet: _StubPlanet, empire: SimpleNamespace
) -> None:
    planet.add_to_staging_yard(_satellite_typed())
    planet.add_order(
        Order(
            OrderType.LAUNCH_SATELLITES,
            target={
                "satellite_design_id": "sat_alpha",
                "count": 1,
                "target_hex": planet.location,
            },
        )
    )


def _build_recover_fighters_scenario(
    planet: _StubPlanet, empire: SimpleNamespace
) -> None:
    fg = FighterWing(group_id=300001, owner_id=planet.owner_id, location=planet.location)
    fg.ships.append(_fighter_ship("f_0", planet.owner_id))
    empire.deployed_groups.append(fg)
    planet.add_order(
        Order(
            OrderType.RECOVER_FIGHTERS,
            target={"fighter_group_id": fg.id, "count": None},
        )
    )


def _build_recover_satellites_scenario(
    planet: _StubPlanet, empire: SimpleNamespace
) -> None:
    sg = SatelliteConstellation(
        group_id=310001, owner_id=planet.owner_id, location=planet.location
    )
    sg.ships.append(_satellite_ship("s_0", planet.owner_id))
    empire.deployed_groups.append(sg)
    planet.add_order(
        Order(
            OrderType.RECOVER_SATELLITES,
            target={"satellite_group_id": sg.id, "count": None},
        )
    )


_SCENARIO_BUILDERS = {
    OrderType.LAY_MINES: _build_lay_mines_scenario,
    OrderType.LAUNCH_FIGHTERS: _build_launch_fighters_scenario,
    OrderType.LAUNCH_SATELLITES: _build_launch_satellites_scenario,
    OrderType.RECOVER_FIGHTERS: _build_recover_fighters_scenario,
    OrderType.RECOVER_SATELLITES: _build_recover_satellites_scenario,
}


@pytest.fixture
def engine_and_processor() -> tuple[ActionExecutionEngine, OrderProcessor]:
    processor = OrderProcessor()
    engine = ActionExecutionEngine(order_processor=processor)
    return engine, processor


@pytest.mark.parametrize(
    "order_type",
    [
        OrderType.LAY_MINES,
        OrderType.LAUNCH_FIGHTERS,
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_FIGHTERS,
        OrderType.RECOVER_SATELLITES,
    ],
)
def test_planet_issued_fms_dispatches_through_engine(
    engine_and_processor, order_type: OrderType
) -> None:
    """Every planet-FMS order type must dispatch cleanly through
    ``ActionExecutionEngine._execute_planet_action``.

    The engine call site passes the unified 5-kwarg signature
    (``issuer``, ``order_owner``, ``empire``, ``galaxy``, ``registries``)
    to ``handler.execute_for_issuer``. Any handler missing one of the
    trailing kwargs raises ``TypeError`` at dispatch — F-B-001 was
    exactly this drift on ``LayMinesOrderHandler``.
    """
    engine, _processor = engine_and_processor

    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
    empire = SimpleNamespace(
        id=7,
        name="E",
        fleets=[],
        colonies=[planet],
        deployed_groups=[],
    )
    empire.deployed_groups_of = lambda cls, _e=empire: [
        g for g in _e.deployed_groups if isinstance(g, cls)
    ]

    _SCENARIO_BUILDERS[order_type](planet, empire)
    assert planet.get_current_order() is not None
    assert planet.get_current_order().type is order_type

    engine._execute_planet_action(planet, empire, component_registry=None)

    assert planet.get_current_order() is None, (
        f"Planet order queue should advance after {order_type.name} "
        f"dispatch — handler may have raised before reaching pop_order(), "
        f"or returned without popping."
    )


def test_planet_fms_order_types_match_registry_view() -> None:
    """Sanity guard: the parametrize list above must match the live
    planet-FMS registry view. If a sixth handler is added but the
    parametrise list isn't extended, this test surfaces the drift."""
    from game.strategy.engine.commands.order_metadata_view import order_metadata

    parametrised = frozenset({
        OrderType.LAY_MINES,
        OrderType.LAUNCH_FIGHTERS,
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_FIGHTERS,
        OrderType.RECOVER_SATELLITES,
    })
    assert parametrised == order_metadata.planet_fms_action_order_types, (
        "planet_fms_action_order_types drift: parametrise list above "
        "must be updated to keep coverage exhaustive."
    )
