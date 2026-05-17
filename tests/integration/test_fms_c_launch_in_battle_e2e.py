"""PROJ-FMS-C Phase 4 — tactical launch + auto-reboard + overflow.

Covers the mid-battle launch flow: a carrier deploys fighters via
``BattleEngine.launch_fighters_in_battle``, those fighters are tracked
by the engine's ``ReboardTracker``, and at battle end
``apply_reboard`` moves survivors back to friendly bays (with overflow
spilling into a new sector fighter_group).
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from game.core.constants import AttackType
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_fighter_design():
    return {
        "name": "Test Fighter",
        "ship_class": "Fighter (Small)",
        "vehicle_class": "Fighter (Small)",
        "vehicle_type": "Fighter",
        "theme_id": "Federation",
        "layers": {
            "CORE": [
                {"id": "hull_fighter_small", "is_active": True},
                {"id": "fighter_cockpit", "is_active": True},
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
        # PROJ-FMS-C Phase 3: install a tracker the way the spec
        # compiler would.
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
    source.registries = fresh_registries
    source.get_all_components = MagicMock(return_value=[])
    source.update = MagicMock()
    source.just_fired_projectiles = []
    source.fleet_attack_bonus = 0.0
    source.fleet_defense_bonus = 0.0
    return source


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 10):
        self._carrier = carrier
        self._capacity = capacity

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


def _make_carrier_strategy_inst(*, capacity: int = 10):
    ship = ShipInstance(
        instance_id="carrier_strategy",
        design_id="carrier_design",
        name="Carrier",
        owner_id=42,
        design_data={"name": "carrier_design"},
    )
    ship._cargo_mgr = _StubCargoMgr(ship, capacity=capacity)
    return ship


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_launch_in_battle_then_all_survive_reboards_all(fresh_registries):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    # Launch 3 fighters mid-battle.
    cvs = [
        CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=70 + i,
        )
        for i in range(3)
    ]
    spawned = engine.launch_fighters_in_battle(carrier_sim, cvs)
    assert len(spawned) == 3

    # Tagged + tracked.
    assert len(engine.reboard_tracker.launched_ships) == 3
    for s in spawned:
        assert getattr(s, "launched_in_battle_id", None) is not None
        assert s.is_alive

    # Strategy fleet with the carrier — surface for apply_reboard.
    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    # Reboard.
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 3
    assert summary["overflowed"] == 0
    assert len(strategy_carrier.carried_items) == 3


def test_launch_in_battle_overflow_spills_to_sector_group(fresh_registries):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    # Launch 4; only 2 bay slots free at reboard time.
    cvs = [
        CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=80 - i,
        )
        for i in range(4)
    ]
    spawned = engine.launch_fighters_in_battle(carrier_sim, cvs)
    assert len(spawned) == 4

    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(capacity=2)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 2
    assert summary["overflowed"] == 2

    # New fighter_group exists at the sector with 2 fighters.
    fgs = [f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "fighter_group"]
    assert len(fgs) == 1
    assert fgs[0].location == hex_c
    assert len(fgs[0].ships) == 2


def test_launch_in_battle_dead_fighters_discarded(fresh_registries):
    engine = _make_engine(fresh_registries)
    carrier_sim = _make_carrier_stub(fresh_registries)
    engine.ships = [carrier_sim]
    engine.ai_controllers = []

    cv = CarriedVehicle(
        design_id="test_fighter",
        design_data=_minimal_fighter_design(),
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )
    spawned = engine.launch_fighters_in_battle(carrier_sim, [cv])
    fighter = spawned[0]

    # Simulate the fighter dying mid-battle.
    fighter.current_hp = 0
    fighter.is_alive = False

    hex_c = HexCoord(0, 0)
    strategy_carrier = _make_carrier_strategy_inst(capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(strategy_carrier)
    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 0
    assert summary["overflowed"] == 0
    assert summary["discarded"] == 1
    assert len(strategy_carrier.carried_items) == 0
