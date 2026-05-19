"""PROJ-455 Phase 1+2 — Planet-FMS end-to-end engine-mediated coverage.

DI-2026-05-18-001 (ActionExecutionEngine half) closure: drive the full
``ActionExecutionEngine.process_action_ticks`` chain for the planet
branch — `process_action_ticks → _process_planet_action_tick →
ActionTimeResolver.resolve_action_time → _execute_planet_action →
OrderProcessor.get_handler → handler.execute_for_issuer` — rather than
the precedent's direct `_execute_planet_action` shortcut.

The companion test at ``tests/integration/test_fms_planet_lay_mines.py``
(PROJ-445 Phase 1) drives ``ActionExecutionEngine._execute_planet_action``
directly, covering only the handler-dispatch leaf of the chain. This
file extends coverage upstream through ``process_action_ticks`` so the
full order-progression / action-time-resolution / dispatch chain has at
least one parametrised behavioural test.

Strategy:
- Reuse the ``_StubPlanet`` shape from the precedent (verified
  compatible with ``PlanetStagingYardIssuerAdapter`` and every planet
  branch of every planet-FMS order handler).
- Inject a deterministic ``_FixedActionTimeResolver`` so the order
  completes on the first tick — keeps the end-to-end test deterministic
  and independent of the static resolver's component-registry-driven
  behaviour.
- Drive ``engine.process_action_ticks(empires=[empire], galaxy=None,
  tick=1, component_registry=None)`` and assert on the returned
  ``ActionTickResult`` list plus the planet's post-tick state.
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


class _FixedActionTimeResolver:
    """Test double for ``ActionTimeResolver``.

    Returns a constant ``action_time`` so the order completes on the
    first tick (when constructed with the default ``action_time=1``).
    Keeps the end-to-end test deterministic — the static resolver's
    component-registry-driven behaviour is out of scope for this test
    file.
    """

    def __init__(self, action_time: int = 1) -> None:
        self._action_time = action_time

    def resolve_action_time(self, _issuer, _order, _component_registry) -> int:
        return self._action_time


class _StubPlanet:
    """Minimal Planet shape compatible with PlanetStagingYardIssuerAdapter
    and the planet branch of every planet-FMS order handler.

    Mirrors the precedent at tests/integration/test_fms_planet_lay_mines.py
    (PROJ-450 Phase 4 typed-substrate shape).
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
def engine_with_fixed_resolver() -> tuple[ActionExecutionEngine, OrderProcessor]:
    """Engine fixture with a deterministic ``action_time=1`` resolver.

    The fixed resolver guarantees one-tick completion regardless of
    component_registry state, making the end-to-end assertion
    `action_completed is True` deterministic.
    """
    processor = OrderProcessor()
    engine = ActionExecutionEngine(
        order_processor=processor,
        action_time_resolver=_FixedActionTimeResolver(action_time=1),
    )
    return engine, processor


def _build_empire(planet: _StubPlanet) -> SimpleNamespace:
    empire = SimpleNamespace(
        id=planet.owner_id,
        name="E",
        fleets=[],
        colonies=[planet],
        deployed_groups=[],
    )
    empire.deployed_groups_of = lambda cls, _e=empire: [
        g for g in _e.deployed_groups if isinstance(g, cls)
    ]
    return empire


def test_lay_mines_e2e_smoke(engine_with_fixed_resolver) -> None:
    """Smoke test: LAY_MINES dispatches end-to-end through
    ``process_action_ticks``.

    Drives the full engine entry point (not the
    ``_execute_planet_action`` shortcut the precedent uses) and asserts
    on the returned ``ActionTickResult`` list plus post-tick planet
    state.
    """
    engine, _processor = engine_with_fixed_resolver

    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
    empire = _build_empire(planet)

    _build_lay_mines_scenario(planet, empire)
    assert planet.get_current_order() is not None
    assert planet.get_current_order().type is OrderType.LAY_MINES

    results = engine.process_action_ticks(
        empires=[empire],
        galaxy=None,
        tick=1,
        component_registry=None,
    )

    assert len(results) == 1
    assert results[0].order_type is OrderType.LAY_MINES
    assert results[0].action_completed is True
    assert planet.get_current_order() is None, (
        "Planet order queue should advance after the engine-mediated "
        "LAY_MINES dispatch."
    )
