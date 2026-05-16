"""PROJ-FMS-C Phase 3 — fighter_reboard tests.

Covers ReboardTracker + apply_reboard behavior in isolation. Full
end-to-end coverage of the spec_compiler wiring + simulation_adapter
threading happens in tests/integration/test_fms_c_e2e.py.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.simulation.systems.fighter_reboard import (
    ReboardTracker,
    apply_reboard,
)
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stub_engine_with_launched(launched):
    """Build a minimal engine-like object exposing ``reboard_tracker``."""
    engine = MagicMock()
    tracker = ReboardTracker(battle_id=123)
    for s in launched:
        tracker.track(s)
    engine.reboard_tracker = tracker
    return engine


def _stub_launched_ship(*, alive: bool = True, hp: int = 50, team_id: int = 0):
    """Build a Ship-like stub for the launched-during-battle fighter."""
    ship = MagicMock()
    ship.is_alive = alive
    ship.current_hp = hp
    ship.team_id = team_id
    ship.design_id = "fighter_alpha"
    ship.mass = 20.0
    return ship


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 999):
        self._carrier = carrier
        self._capacity = capacity
        self.loaded = []

    def load_vehicle(self, cv):
        if len(self.loaded) >= self._capacity:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        self.loaded.append(cv)
        return True


def _make_carrier(instance_id: str, capacity: int):
    carrier = ShipInstance(
        instance_id=instance_id,
        design_id="carrier_design",
        name=instance_id,
        owner_id=42,
        design_data={"name": "carrier_design"},
    )
    carrier._cargo_mgr = _StubCargoMgr(carrier, capacity=capacity)
    return carrier


# Patch ShipSerializer.to_dict so we can use the mock launched ships.
@pytest.fixture(autouse=True)
def patch_serializer(monkeypatch):
    def fake_to_dict(ship):
        return {
            "name": "fighter_alpha",
            "ship_class": "Fighter (Small)",
            "design_id": getattr(ship, "design_id", "fighter_alpha"),
            "expected_stats": {"mass": float(getattr(ship, "mass", 20.0))},
        }
    monkeypatch.setattr(
        "game.simulation.entities.ship_serialization.ShipSerializer.to_dict",
        fake_to_dict,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_no_tracker_returns_empty_summary():
    engine = MagicMock()
    engine.reboard_tracker = None
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={},
        empires_by_owner={},
    )
    assert summary == {"reboarded": 0, "overflowed": 0, "discarded": 0}


def test_reboard_one_survivor_onto_friendly_carrier():
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier("carrier_1", capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    survivor = _stub_launched_ship(alive=True, hp=70, team_id=0)
    engine = _stub_engine_with_launched([survivor])

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 1
    assert summary["overflowed"] == 0
    assert summary["discarded"] == 0
    # Carrier got a CarriedVehicle dict.
    assert len(carrier.carried_items) == 1
    assert carrier.carried_items[0]["current_hp"] == 70


def test_dead_fighter_is_discarded():
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier("carrier_1", capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)
    dead = _stub_launched_ship(alive=False, hp=0, team_id=0)
    engine = _stub_engine_with_launched([dead])

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["discarded"] == 1
    assert summary["reboarded"] == 0
    assert len(carrier.carried_items) == 0


def test_overflow_spills_into_new_fighter_group():
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier("carrier_1", capacity=1)  # only 1 slot
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    # Three survivors; only 1 fits.
    survivors = [
        _stub_launched_ship(alive=True, hp=70 - i, team_id=0)
        for i in range(3)
    ]
    engine = _stub_engine_with_launched(survivors)

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 1
    assert summary["overflowed"] == 2
    # The carrier has 1 fighter loaded.
    assert len(carrier.carried_items) == 1
    # A new fighter_group exists at the hex with 2 fighters.
    fgs = [f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "fighter_group"]
    assert len(fgs) == 1
    assert len(fgs[0].ships) == 2
    assert fgs[0].location == hex_c


def test_overflow_merges_into_existing_fighter_group_at_hex():
    """Per decisions.md: overflow merges into a pre-existing
    fighter_group at the same hex (owner match) rather than fragmenting."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier("carrier_1", capacity=0)  # zero capacity, force overflow
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    pre_existing = Fleet(
        fleet_id=200001, owner_id=42, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )

    empire = SimpleNamespace(id=42, fleets=[fleet, pre_existing])

    survivor = _stub_launched_ship(alive=True, hp=70, team_id=0)
    engine = _stub_engine_with_launched([survivor])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 1
    # Pre-existing group grew, no new group minted.
    fgs = [f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "fighter_group"]
    assert len(fgs) == 1
    assert fgs[0] is pre_existing
    assert len(pre_existing.ships) == 1


def test_carrier_destroyed_finds_other_friendly_with_bay_space():
    """A carrier dead at battle end shouldn't accept the reboard; another
    friendly with bay space picks up the slack."""
    hex_c = HexCoord(0, 0)
    dead_carrier = _make_carrier("dead_carrier", capacity=10)
    dead_carrier.is_alive = False  # dead
    backup = _make_carrier("backup", capacity=10)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(dead_carrier)
    fleet.ships.append(backup)

    survivor = _stub_launched_ship(alive=True, hp=80, team_id=0)
    engine = _stub_engine_with_launched([survivor])

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["reboarded"] == 1
    # Backup got the fighter, not the dead carrier.
    assert len(backup.carried_items) == 1
    assert len(dead_carrier.carried_items) == 0
