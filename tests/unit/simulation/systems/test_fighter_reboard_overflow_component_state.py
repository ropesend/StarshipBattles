"""PROJ-FMS-D audit Fix 1 — overflow path preserves per-component damage state.

The PROJ-FMS-C audit-fix pass added component_states preservation for the
reboard-onto-carrier path (`_ship_to_carried_vehicle` captures
`ship.components` -> `CarriedVehicle.component_states`, and
`LaunchFightersOrderHandler` restores them at strategic launch).

BUT the overflow path in :func:`fighter_reboard._build_overflow_ship_instance`
was still lossy: it constructed a fresh :class:`ShipInstance` from only
``design_data + current_hp`` and never reapplied ``cv.component_states``.
Effect: any fighter or satellite that overflows into a new sector group at
battle end silently lost its per-component damage state.

This module pins the missing round trip for both vehicle types.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.core.component_state import ComponentState
from game.core.hex_math import HexCoord
from game.strategy.data.deployed_group import FighterWing, SatelliteConstellation
from game.simulation.systems.fighter_reboard import (
    ReboardTracker,
    apply_reboard,
)
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _damaged_components() -> dict[str, ComponentState]:
    return {
        "comp_hull#0": ComponentState(
            component_id="comp_hull", instance_index=0,
            current_hp=30.0, max_hp=100.0,
        ),
        "comp_engine#0": ComponentState(
            component_id="comp_engine", instance_index=0,
            current_hp=15.0, max_hp=80.0,
            is_active=False,
        ),
    }


def _stub_launched_ship(
    *,
    vehicle_type: str,
    design_id: str,
    hp: int = 50,
    components: dict[str, ComponentState] | None = None,
) -> MagicMock:
    ship = MagicMock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.current_hp = hp
    ship.team_id = 0
    ship.design_id = design_id
    ship.mass = 20.0 if vehicle_type == "Fighter" else 30.0
    ship.vehicle_type = vehicle_type
    ship.components = components if components is not None else {}
    ship.name = f"{design_id} 1"
    return ship


@pytest.fixture(autouse=True)
def patch_serializer(monkeypatch):
    def fake_to_dict(ship):
        return {
            "name": getattr(ship, "design_id", "unknown"),
            "design_id": getattr(ship, "design_id", "unknown"),
            "expected_stats": {"mass": float(getattr(ship, "mass", 20.0))},
        }
    monkeypatch.setattr(
        "game.simulation.entities.ship_serialization.ShipSerializer.to_dict",
        fake_to_dict,
    )


def _make_carrier(capacity: int = 0) -> ShipInstance:
    """Zero-capacity carrier so launched survivors always overflow."""
    inst = ShipInstance(
        instance_id="carrier_1",
        design_id="carrier_design",
        name="Carrier",
        owner_id=42,
        design_data={"name": "carrier_design"},
    )

    class _CargoMgr:
        def load_vehicle(self, cv):
            return False

    inst._cargo_mgr = _CargoMgr()
    return inst


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_fighter_overflow_preserves_component_states():
    """Fighter overflow ShipInstance carries cv.component_states forward."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(capacity=0)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)

    damaged = _damaged_components()
    fighter = _stub_launched_ship(
        vehicle_type="Fighter", design_id="fighter_alpha",
        hp=70, components=damaged,
    )
    tracker = ReboardTracker(battle_id=99)
    tracker.track(fighter)
    engine = MagicMock()
    engine.reboard_tracker = tracker

    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 1
    assert summary["reboarded"] == 0

    fgs = [g for g in empire.deployed_groups if isinstance(g, FighterWing)]
    assert len(fgs) == 1
    overflow_ship = fgs[0].ships[0]
    # PROJ-FMS-D audit Fix 1: the overflow ShipInstance must carry forward
    # the per-component damage state from the launched fighter.
    assert overflow_ship.components, (
        "Audit Fix 1: overflow ShipInstance must reapply "
        "cv.component_states; the strategic-recovery path does this via "
        "LaunchFightersOrderHandler, the overflow path must match."
    )
    assert set(overflow_ship.components.keys()) == set(damaged.keys())
    assert overflow_ship.components["comp_hull#0"].current_hp == 30.0
    assert overflow_ship.components["comp_engine#0"].current_hp == 15.0
    assert overflow_ship.components["comp_engine#0"].is_active is False


def test_satellite_overflow_preserves_component_states():
    """Satellite overflow ShipInstance carries cv.component_states forward."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(capacity=0)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)

    damaged = _damaged_components()
    satellite = _stub_launched_ship(
        vehicle_type="Satellite", design_id="sat_alpha",
        hp=60, components=damaged,
    )
    tracker = ReboardTracker(battle_id=99)
    tracker.track(satellite)
    engine = MagicMock()
    engine.reboard_tracker = tracker

    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 1
    sgs = [g for g in empire.deployed_groups if isinstance(g, SatelliteConstellation)]
    assert len(sgs) == 1
    overflow_ship = sgs[0].ships[0]
    # Same contract for satellites.
    assert overflow_ship.components, (
        "Audit Fix 1: satellite overflow ShipInstance must reapply "
        "cv.component_states."
    )
    assert overflow_ship.components["comp_hull#0"].current_hp == 30.0
    assert overflow_ship.components["comp_engine#0"].current_hp == 15.0


def test_overflow_no_components_is_fine():
    """A ship with no per-component state still overflows (no crash)."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(capacity=0)
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)

    fighter = _stub_launched_ship(
        vehicle_type="Fighter", design_id="fighter_alpha",
        hp=70, components={},
    )
    tracker = ReboardTracker(battle_id=99)
    tracker.track(fighter)
    engine = MagicMock()
    engine.reboard_tracker = tracker

    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])
    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )
    assert summary["overflowed"] == 1
    fgs = [g for g in empire.deployed_groups if isinstance(g, FighterWing)]
    overflow_ship = fgs[0].ships[0]
    # Empty components dict is fine; what matters is no crash + HP carried.
    assert overflow_ship.current_hp == 70
