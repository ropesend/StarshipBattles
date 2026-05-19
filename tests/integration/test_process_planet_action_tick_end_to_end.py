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
        self._staging_yard: list = []
        self.max_staging_mass: float = 0.0
        self.orders: list = []

    @property
    def staging_yard(self) -> list:
        """PROJ-455: backed by ``_staging_yard`` to honour the
        :class:`PlanetStagingYardIssuerAdapter` write contract at
        ``issuer_adapter.py:335`` (``self._planet._staging_yard = remaining``).
        Real :class:`Planet` exposes the same underscore-backed property pair;
        the precedent stub in ``test_fms_planet_lay_mines.py`` skips this
        because its assertions never observe the post-pop yard state.
        """
        return self._staging_yard

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
            sum(_item_mass(i) for i in self._staging_yard) + item_mass
            > self.max_staging_mass
        ):
            return False
        self._staging_yard.append(item)
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
    state. Retained alongside the Phase-2 parametrised test as a
    fast-path debug aid — see decisions.md.
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


# ---------------------------------------------------------------------------
# Phase 2 — Parametrised end-to-end coverage (completion branch + in-progress)
# ---------------------------------------------------------------------------


def _assert_post_dispatch_state(planet, empire, order_type: OrderType) -> None:
    """Per-order-type observable post-condition checks for the
    completion-branch parametrised test.

    Conservative shape: launch / lay orders must empty the staging yard
    and produce exactly one deployed group; recovery orders must empty
    the deployed group(s) of their ships and place the recovered ship
    into the staging yard. Whether the empty group is removed from
    ``empire.deployed_groups`` is handler-policy-defined; the assertions
    only require the ships count = 0 on any remaining groups.
    """
    if order_type is OrderType.LAY_MINES:
        mine_groups = [
            g for g in empire.deployed_groups
            if g.__class__.__name__ == "MineGroup"
        ]
        assert len(mine_groups) == 1, (
            "LAY_MINES should produce exactly one MineGroup; "
            f"got {len(mine_groups)}."
        )
        assert len(planet.staging_yard) == 0, (
            "Mine should have moved out of the staging yard."
        )
    elif order_type in (OrderType.LAUNCH_FIGHTERS, OrderType.LAUNCH_SATELLITES):
        assert len(planet.staging_yard) == 0, (
            f"{order_type.name} should have emptied the staging yard."
        )
        assert len(empire.deployed_groups) == 1, (
            f"{order_type.name} should produce exactly one deployed group; "
            f"got {len(empire.deployed_groups)}."
        )
    elif order_type in (OrderType.RECOVER_FIGHTERS, OrderType.RECOVER_SATELLITES):
        for group in empire.deployed_groups:
            assert len(group.ships) == 0, (
                f"{order_type.name} should empty the deployed group's "
                f"ships; got {len(group.ships)} remaining."
            )
        assert len(planet.staging_yard) >= 1, (
            f"{order_type.name} should have placed the recovered ship "
            f"into the staging yard."
        )
    else:
        pytest.fail(
            f"Unhandled order_type in _assert_post_dispatch_state: "
            f"{order_type!r}"
        )


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
def test_process_planet_action_tick_end_to_end(
    engine_with_fixed_resolver, order_type: OrderType
) -> None:
    """Every planet-FMS order type dispatches cleanly through the full
    engine entry point ``ActionExecutionEngine.process_action_ticks``.

    This is the engine-mediated counterpart of
    ``tests/integration/test_fms_planet_lay_mines.py`` (which drives
    ``_execute_planet_action`` directly). PROJ-455 closes the
    ActionExecutionEngine half of DI-2026-05-18-001 by exercising
    ``_process_planet_action_tick``'s order-progression and
    action-time-resolution logic that the precedent bypassed.
    """
    engine, _processor = engine_with_fixed_resolver

    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
    empire = _build_empire(planet)

    _SCENARIO_BUILDERS[order_type](planet, empire)
    assert planet.get_current_order() is not None
    assert planet.get_current_order().type is order_type

    results = engine.process_action_ticks(
        empires=[empire],
        galaxy=None,
        tick=1,
        component_registry=None,
    )

    assert len(results) == 1, (
        f"Expected exactly one ActionTickResult for the planet's "
        f"{order_type.name} order; got {len(results)}."
    )
    result = results[0]
    assert result.order_type is order_type
    assert result.action_completed is True, (
        f"With _FixedActionTimeResolver(1), tick 1 should complete the "
        f"{order_type.name} action; got action_completed={result.action_completed}."
    )
    assert result.fleet_consumed is False, (
        "Planets are never consumed by an action; only fleet-issuer "
        "paths set fleet_consumed=True."
    )

    assert planet.get_current_order() is None, (
        f"Planet order queue should advance after the engine-mediated "
        f"{order_type.name} dispatch — handler may have raised before "
        f"reaching pop_order(), or returned without popping."
    )

    _assert_post_dispatch_state(planet, empire, order_type)


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
def test_process_planet_action_tick_in_progress_branch(
    order_type: OrderType,
) -> None:
    """One tick with action_time=3 must NOT complete the action.

    Exercises the in-progress return path at
    ``game/strategy/engine/action_execution_engine.py:290-297``: the
    order remains queued, ``execution_progress`` increments to 1,
    ``action_completed`` is False, and the handler is NOT invoked.

    Uses a dedicated `ActionExecutionEngine` constructed inline (with
    `_FixedActionTimeResolver(3)`) rather than the
    ``engine_with_fixed_resolver`` fixture which is wired for
    ``action_time=1`` completion-branch coverage.
    """
    processor = OrderProcessor()
    engine = ActionExecutionEngine(
        order_processor=processor,
        action_time_resolver=_FixedActionTimeResolver(action_time=3),
    )
    hex_c = HexCoord(0, 0)
    planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
    empire = _build_empire(planet)

    _SCENARIO_BUILDERS[order_type](planet, empire)
    assert planet.get_current_order() is not None
    current_order = planet.get_current_order()
    assert current_order.type is order_type

    results = engine.process_action_ticks(
        empires=[empire],
        galaxy=None,
        tick=1,
        component_registry=None,
    )

    assert len(results) == 1
    result = results[0]
    assert result.order_type is order_type
    assert result.action_completed is False, (
        f"With _FixedActionTimeResolver(3) and one tick, {order_type.name} "
        f"should NOT complete; got action_completed={result.action_completed}."
    )
    assert result.execution_progress == 1, (
        f"After one tick the order's execution_progress should be 1; "
        f"got {result.execution_progress}."
    )
    assert result.action_time == 3
    assert result.fleet_consumed is False

    assert planet.get_current_order() is current_order, (
        f"{order_type.name} in-progress: order must remain queued; "
        f"the handler should NOT have been dispatched on this tick."
    )
    assert current_order.execution_progress == 1


def test_planet_fms_e2e_parametrise_matches_registry_view() -> None:
    """Sanity guard: the parametrise list used by the e2e tests above
    must match the live planet-FMS registry view. If a sixth handler is
    added but the parametrise list isn't extended, this test surfaces
    the drift before the next CI run sees an under-covered handler.
    """
    from game.strategy.engine.commands.order_metadata_view import order_metadata

    parametrised = frozenset({
        OrderType.LAY_MINES,
        OrderType.LAUNCH_FIGHTERS,
        OrderType.LAUNCH_SATELLITES,
        OrderType.RECOVER_FIGHTERS,
        OrderType.RECOVER_SATELLITES,
    })
    assert parametrised == order_metadata.planet_fms_action_order_types, (
        "planet_fms_action_order_types drift: the parametrise list in "
        "test_process_planet_action_tick_end_to_end / "
        "test_process_planet_action_tick_in_progress_branch must be "
        "updated to keep coverage exhaustive."
    )
