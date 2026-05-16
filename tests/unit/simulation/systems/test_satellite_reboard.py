"""PROJ-FMS-D Phase 2 — satellite reboard tests.

Pins the generalised :func:`apply_reboard` behavior for satellites:
- A surviving in-battle-launched Satellite ship reboards onto a friendly
  bay (with the bay-type filter forced via the cargo manager stub).
- Overflow spills into a ``satellite_group``, not a ``fighter_group``.
- Pre-existing same-empire ``satellite_group`` at the hex catches the
  overflow (merge policy mirrors fighters).
- Mixed-type batches: a fighter + a satellite produce one
  ``fighter_group`` and one ``satellite_group`` overflow respectively.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.simulation.systems.fighter_reboard import (
    ReboardTracker,
    apply_reboard,
)
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


class _StubCargoMgr:
    """Cargo manager stub that gates on the CarriedVehicle's vehicle_type."""

    def __init__(self, carrier, *, capacity: int = 999,
                 accepts: tuple[str, ...] = ("fighter", "satellite")):
        self._carrier = carrier
        self._capacity = capacity
        self._accepts = accepts
        self.loaded: List[Any] = []

    def load_vehicle(self, cv) -> bool:
        if len(self.loaded) >= self._capacity:
            return False
        if cv.vehicle_type not in self._accepts:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        self.loaded.append(cv)
        return True


def _make_carrier(
    instance_id: str, capacity: int,
    accepts: tuple[str, ...] = ("fighter", "satellite"),
) -> ShipInstance:
    carrier = ShipInstance(
        instance_id=instance_id,
        design_id="carrier_design",
        name=instance_id,
        owner_id=42,
        design_data={"name": "carrier_design"},
    )
    carrier._cargo_mgr = _StubCargoMgr(
        carrier, capacity=capacity, accepts=accepts,
    )
    return carrier


def _stub_launched_ship(
    *, alive: bool = True, hp: int = 50, team_id: int = 0,
    vehicle_type: str = "Satellite",
    design_id: str = "sat_alpha",
) -> MagicMock:
    ship = MagicMock()
    ship.is_alive = alive
    ship.current_hp = hp
    ship.team_id = team_id
    ship.design_id = design_id
    ship.mass = 30.0
    ship.vehicle_type = vehicle_type
    return ship


@pytest.fixture(autouse=True)
def patch_serializer(monkeypatch):
    def fake_to_dict(ship):
        return {
            "name": getattr(ship, "design_id", "sat_alpha"),
            "design_id": getattr(ship, "design_id", "sat_alpha"),
            "expected_stats": {"mass": float(getattr(ship, "mass", 30.0))},
        }
    monkeypatch.setattr(
        "game.simulation.entities.ship_serialization.ShipSerializer.to_dict",
        fake_to_dict,
    )


def _stub_engine_with_launched(launched: List[Any]):
    engine = MagicMock()
    tracker = ReboardTracker(battle_id=123)
    for s in launched:
        tracker.track(s)
    engine.reboard_tracker = tracker
    return engine


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_satellite_reboards_into_universal_bay():
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", capacity=5, accepts=("fighter", "satellite"),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    survivor = _stub_launched_ship(alive=True, hp=60, vehicle_type="Satellite")
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
    # The stored CarriedVehicle dict declares satellite vehicle_type.
    assert carrier.carried_items[0]["vehicle_type"] == "satellite"


def test_satellite_overflows_into_new_satellite_group():
    hex_c = HexCoord(0, 0)
    # Carrier has zero satellite capacity -> overflow.
    carrier = _make_carrier(
        "carrier_1", capacity=0, accepts=("fighter", "satellite"),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    survivors = [
        _stub_launched_ship(alive=True, hp=60 - i, vehicle_type="Satellite")
        for i in range(2)
    ]
    engine = _stub_engine_with_launched(survivors)

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 2
    sat_groups = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "satellite_group"
    ]
    assert len(sat_groups) == 1
    assert len(sat_groups[0].ships) == 2
    # 300000+ id namespace.
    assert sat_groups[0].id >= 300000
    # No spurious fighter_group.
    assert not any(
        getattr(f, "group_kind", "fleet") == "fighter_group"
        for f in empire.fleets
    )


def test_satellite_overflow_merges_into_existing_satellite_group():
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", capacity=0, accepts=("fighter", "satellite"),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    pre_existing = Fleet(
        fleet_id=300001, owner_id=42, location=hex_c, speed=0.0,
        group_kind="satellite_group",
    )

    empire = SimpleNamespace(id=42, fleets=[fleet, pre_existing])
    survivor = _stub_launched_ship(alive=True, hp=70, vehicle_type="Satellite")
    engine = _stub_engine_with_launched([survivor])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 1
    sat_groups = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "satellite_group"
    ]
    assert len(sat_groups) == 1
    assert sat_groups[0] is pre_existing
    assert len(pre_existing.ships) == 1


def test_mixed_fighter_satellite_batch_uses_correct_overflow_kinds():
    """One fighter + one satellite overflow → fighter_group + satellite_group."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", capacity=0, accepts=("fighter", "satellite"),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    fighter = _stub_launched_ship(
        alive=True, hp=50, vehicle_type="Fighter", design_id="fighter_alpha",
    )
    satellite = _stub_launched_ship(
        alive=True, hp=60, vehicle_type="Satellite", design_id="sat_alpha",
    )
    engine = _stub_engine_with_launched([fighter, satellite])

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 2
    fgs = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "fighter_group"
    ]
    sgs = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "satellite_group"
    ]
    assert len(fgs) == 1
    assert len(sgs) == 1
    assert len(fgs[0].ships) == 1
    assert len(sgs[0].ships) == 1


def test_satellite_only_bay_rejects_fighter_overflow():
    """A satellite-only bay refuses fighter CVs; fighter overflows even if
    space exists for satellites."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", capacity=5, accepts=("satellite",),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    fighter = _stub_launched_ship(
        alive=True, hp=50, vehicle_type="Fighter", design_id="fighter_alpha",
    )
    engine = _stub_engine_with_launched([fighter])

    empire = SimpleNamespace(id=42, fleets=[fleet])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    # Bay rejects fighters; overflows into fighter_group.
    assert summary["overflowed"] == 1
    assert summary["reboarded"] == 0
    fgs = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "fighter_group"
    ]
    assert len(fgs) == 1
