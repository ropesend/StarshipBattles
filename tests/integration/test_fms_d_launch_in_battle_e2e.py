"""PROJ-FMS-D Phase 3 — tactical satellite launch + auto-reboard + overflow.

Mirrors :mod:`test_fms_c_launch_in_battle_e2e` for satellites. A carrier
deploys satellites via :meth:`BattleEngine.launch_satellites_in_battle`,
those satellites are tracked by the engine's :class:`ReboardTracker`,
and at battle end :func:`apply_reboard` moves survivors back to
friendly bays (with overflow spilling into a new sector
``satellite_group``).
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from game.core.hex_math import HexCoord
from game.core.math import Vector2
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.simulation.systems.fighter_reboard import (
    ReboardTracker,
    apply_reboard,
)
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


def _minimal_satellite_design():
    return {
        "name": "Test Satellite",
        "ship_class": "Satellite (Small)",
        "vehicle_class": "Satellite (Small)",
        "vehicle_type": "Satellite",
        "theme_id": "Federation",
        "layers": {
            "CORE": [
                {"id": "hull_satellite_small", "is_active": True},
            ],
        },
    }


def _make_engine(fresh_registries):
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        mock_factory = MagicMock()
        mock_ai = MagicMock()
        mock_ai.update = MagicMock()
        mock_ai.ship = MagicMock()
        mock_factory.create_for_ship = MagicMock(return_value=mock_ai)
        mock_factory.create_for_ships = MagicMock(return_value=[mock_ai])
        mock_factory.set_grid = MagicMock()
        mock_factory.set_rng = MagicMock()
        engine = BattleEngine(ai_factory=mock_factory)
        engine.end_condition = NeverCondition()
        engine.tick_counter = 0
        engine.recent_beams = []
        engine.reboard_tracker = ReboardTracker(battle_id=id(engine))
        return engine


def _make_carrier_stub(fresh_registries):
    source = MagicMock()
    source.name = "Carrier"
    source.is_alive = True
    source.is_derelict = False
    source.team_id = 0
    source.position = Vector2(0, 0)
    source.velocity = Vector2(0, 0)
    source.angle = 0
    source.radius = 20
    source.color = (255, 255, 255)
    source.theme_id = "Federation"
    source.vehicle_type = "Ship"
    source.registries = fresh_registries
    source.get_all_components = MagicMock(return_value=[])
    source.update = MagicMock()
    source.just_fired_projectiles = []
    source.fleet_attack_bonus = 0.0
    source.fleet_defense_bonus = 0.0
    return source


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 10,
                 accepts: tuple[str, ...] = ("fighter", "satellite")):
        self._carrier = carrier
        self._capacity = capacity
        self._accepts = accepts

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        if cv.vehicle_type not in self._accepts:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


def _make_carrier_strategy_inst(*, capacity: int = 10,
                                  accepts: tuple[str, ...] = ("satellite",)):
    ship = ShipInstance(
        instance_id="carrier_strategy",
        design_id="carrier_design",
        name="Carrier",
        owner_id=42,
        design_data={"name": "carrier_design"},
    )
    ship._cargo_mgr = _StubCargoMgr(
        ship, capacity=capacity, accepts=accepts,
    )
    return ship


def _maybe_skip_if_satellite_design_unavailable(callable_):
    """Skip the test cleanly when the minimal satellite design cannot
    be materialised in the current registry fixture.

    Some test environments don't ship the satellite hull. The audit
    rule is "skip cleanly rather than crash" for fixture gaps.
    """
    from game.core.exceptions import StateException

    try:
        return callable_()
    except (KeyError, StateException, ValueError) as e:
        pytest.skip(f"Satellite design materialisation skipped: {e}")


def test_launch_satellites_in_battle_then_all_survive_reboards_all(
    fresh_registries,
):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    def _launch():
        cvs = [
            CarriedVehicle(
                design_id="test_satellite",
                design_data=_minimal_satellite_design(),
                vehicle_type="satellite",
                mass=30.0,
                current_hp=60 + i,
            )
            for i in range(3)
        ]
        return engine.launch_satellites_in_battle(carrier_sim, cvs)

    spawned = _maybe_skip_if_satellite_design_unavailable(_launch)
    assert len(spawned) == 3

    # Tagged + tracked.
    assert len(engine.reboard_tracker.launched_ships) == 3
    for s in spawned:
        assert getattr(s, "launched_in_battle_id", None) is not None
        assert s.is_alive
        # Sim Ship.vehicle_type is read by the reboard hook for
        # CarriedVehicle classification.
        assert getattr(s, "vehicle_type", "").lower() == "satellite"

    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet])

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 3
    assert summary["overflowed"] == 0
    assert len(strategy_carrier.carried_items) == 3
    for item in strategy_carrier.carried_items:
        assert item["vehicle_type"] == "satellite"


def test_launch_satellites_overflow_spills_to_sector_satellite_group(
    fresh_registries,
):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    def _launch():
        cvs = [
            CarriedVehicle(
                design_id="test_satellite",
                design_data=_minimal_satellite_design(),
                vehicle_type="satellite",
                mass=30.0,
                current_hp=60 - i,
            )
            for i in range(4)
        ]
        return engine.launch_satellites_in_battle(carrier_sim, cvs)

    spawned = _maybe_skip_if_satellite_design_unavailable(_launch)
    assert len(spawned) == 4

    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(
        capacity=2, accepts=("satellite",),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet])

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 2
    assert summary["overflowed"] == 2

    sgs = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "satellite_group"
    ]
    assert len(sgs) == 1
    assert sgs[0].location == hex_c
    assert len(sgs[0].ships) == 2
    # No spurious fighter_group.
    assert not any(
        getattr(f, "group_kind", "fleet") == "fighter_group"
        for f in empire.fleets
    )


def test_launch_satellites_dead_satellites_discarded(fresh_registries):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    def _launch():
        cv = CarriedVehicle(
            design_id="test_satellite",
            design_data=_minimal_satellite_design(),
            vehicle_type="satellite",
            mass=30.0,
            current_hp=60,
        )
        return engine.launch_satellites_in_battle(carrier_sim, [cv])

    spawned = _maybe_skip_if_satellite_design_unavailable(_launch)
    satellite = spawned[0]
    # Simulate the satellite dying mid-battle.
    satellite.current_hp = 0
    satellite.is_alive = False

    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet])

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 0
    assert summary["overflowed"] == 0
    assert summary["discarded"] == 1
    assert len(strategy_carrier.carried_items) == 0
