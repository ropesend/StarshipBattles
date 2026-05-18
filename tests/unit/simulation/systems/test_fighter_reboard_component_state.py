"""PROJ-FMS-C audit Fix 2 — per-component damage state through reboard.

The strategic launch/recovery path already preserves
:attr:`ShipInstance.components` end-to-end:
``LaunchFightersOrderHandler`` reapplies them at deploy, and
``RecoverFightersOrderHandler`` captures them on the recovered
``CarriedVehicle``. But the in-battle launch/reboard loop was lossy:

  - :func:`game.simulation.systems.fighter_reboard._ship_to_carried_vehicle`
    did NOT capture ``ship.components``.
  - :func:`game.simulation.systems.attack_processor._spawn_from_carried_vehicle`
    only restored ``current_hp``, ignoring ``component_states``.

This file pins the missing round trip: damage component state on a
launched fighter; reboard via :func:`apply_reboard`; the reboarded
:class:`CarriedVehicle` carries the same component state.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from game.core.component_state import ComponentState
from game.core.hex_math import HexCoord
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


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 999):
        self._carrier = carrier
        self._capacity = capacity

    def load_vehicle(self, cv: CarriedVehicle) -> bool:
        # PROJ-436 Phase 9: load through the typed BayInventory.bay slot.
        if len(self._carrier.bay_inventory.bay) >= self._capacity:
            return False
        self._carrier.bay_inventory.bay.append(cv)
        return True


def _make_carrier_inst() -> ShipInstance:
    inst = ShipInstance(
        instance_id="carrier_1",
        design_id="carrier_design",
        name="Carrier",
        owner_id=42,
        design_data={"name": "carrier_design"},
    )
    inst._cargo_mgr = _StubCargoMgr(inst)
    return inst


def _make_launched_fighter_with_damaged_components() -> Any:
    """Sim-Ship-like stub: fighter has full component_states on the sim side."""
    ship = MagicMock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.current_hp = 60
    ship.team_id = 0
    ship.design_id = "fighter_alpha"
    ship.mass = 20.0
    # Simulated per-component damage state on the launched fighter.
    # `_ship_to_carried_vehicle` must thread this onto the CarriedVehicle.
    ship.components = {
        "comp_hull": ComponentState(
            component_id="comp_hull", instance_index=0,
            current_hp=30, max_hp=100,
        ),
        "comp_engine": ComponentState(
            component_id="comp_engine", instance_index=0,
            current_hp=80, max_hp=80,
        ),
    }
    # ``ship_serialization.to_dict`` is patched at call site via design_data.
    ship.name = "Carrier Wing 1"
    return ship


# ---------------------------------------------------------------------------
# Tests (failing pre-fix; passing post-fix).
# ---------------------------------------------------------------------------


def test_reboard_captures_component_states_into_carried_vehicle(monkeypatch):
    """Damaged components on a launched fighter survive the reboard hook.

    PROJ-FMS-C audit Fix 2: ``_ship_to_carried_vehicle`` must read
    ``ship.components`` (the sim-side damage state) into the resulting
    ``CarriedVehicle.component_states`` field. Strategic recovery already
    does the equivalent in ``RecoverFightersOrderHandler``; the in-battle
    reboard hook must match.
    """
    # Patch ShipSerializer.to_dict so the reboard helper doesn't have to
    # run the real serializer on a stub ship.
    from game.simulation.entities import ship_serialization

    def fake_to_dict(ship):
        return {
            "name": ship.design_id,
            "design_id": ship.design_id,
            "expected_stats": {"mass": ship.mass},
        }

    monkeypatch.setattr(ship_serialization.ShipSerializer, "to_dict", fake_to_dict)

    fighter = _make_launched_fighter_with_damaged_components()

    # Wire it through apply_reboard with a carrier that can receive it.
    engine = MagicMock()
    tracker = ReboardTracker(battle_id=999)
    tracker.track(fighter)
    engine.reboard_tracker = tracker

    carrier_inst = _make_carrier_inst()
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=HexCoord(0, 0), speed=5.0
    )
    fleet.ships.append(carrier_inst)
    empire = SimpleNamespace(id=42, fleets=[fleet], deployed_groups=[])

    summary = apply_reboard(
        engine=engine,
        participating_fleets_by_owner={42: [fleet]},
        empires_by_owner={42: empire},
    )

    assert summary["reboarded"] == 1
    # PROJ-431 Phase 1f: carried inventory lives in the typed
    # ``bay_inventory.bay`` slot; ``carried_items`` is the legacy
    # dict-list projection.
    assert len(carrier_inst.bay_inventory.bay) == 1
    loaded = carrier_inst.bay_inventory.bay[0]
    assert isinstance(loaded, CarriedVehicle)
    assert loaded.component_states is not None, (
        "Fix 2: the reboard helper must capture ship.components into "
        "CarriedVehicle.component_states."
    )
    assert set(loaded.component_states.keys()) == {"comp_hull", "comp_engine"}
    assert loaded.component_states["comp_hull"].current_hp == 30
    assert loaded.component_states["comp_engine"].current_hp == 80


def test_spawn_from_carried_vehicle_restores_component_states(
    monkeypatch, fresh_registries
):
    """The reverse direction: launching from a CarriedVehicle restores damage state.

    PROJ-FMS-C audit Fix 2: ``_spawn_from_carried_vehicle`` must apply
    ``CarriedVehicle.component_states`` to the spawned ``Ship.components``
    after :meth:`ShipSerializer.from_dict`. Mirrors the symmetric step
    in :class:`LaunchFightersOrderHandler` (strategic launch).
    """
    from game.simulation.systems import attack_processor

    cv = CarriedVehicle(
        design_id="test_fighter",
        design_data={
            "name": "Test Fighter",
            "vehicle_type": "Fighter",
            "layers": {"CORE": [{"id": "hull_fighter_small"}]},
        },
        vehicle_type="fighter",
        mass=20.0,
        current_hp=50,
        component_states={
            "comp_hull": ComponentState(
                component_id="comp_hull", instance_index=0,
                current_hp=40, max_hp=100,
            ),
        },
    )

    source = MagicMock()
    source.registries = fresh_registries
    source.color = (255, 255, 255)
    source.theme_id = "Federation"
    source.angle = 0
    source.team_id = 0

    spawned = MagicMock()
    spawned.components = {}
    spawned.current_hp = 0

    def fake_from_dict(design_data, registries=None):
        return spawned

    monkeypatch.setattr(
        "game.simulation.entities.ship_serialization.ShipSerializer.from_dict",
        fake_from_dict,
    )

    new_ship = attack_processor._spawn_from_carried_vehicle(
        engine=MagicMock(),
        source_ship=source,
        carried_payload=cv,
        new_name="Wing 1",
        spawn_pos=type(source.color)([0.0, 0.0]) if False else SimpleNamespace(x=0.0, y=0.0),
    )

    assert new_ship is spawned
    # Restored damage state.
    assert new_ship.components, (
        "Fix 2: spawned ship must carry the component_states from "
        "CarriedVehicle so per-component damage state survives the launch."
    )
    assert "comp_hull" in new_ship.components
    assert new_ship.components["comp_hull"].current_hp == 40


def test_round_trip_through_in_battle_reboard_preserves_damage(monkeypatch):
    """End-to-end round trip: damage in battle → reboard → re-launch → same HP.

    Pins the contract codex's audit asked for: per-component damage
    state must survive damage → reboard → re-launch through the
    in-battle path, matching how the strategic launch/recovery path
    already behaves.
    """
    from game.simulation.entities import ship_serialization
    from game.simulation.systems.fighter_reboard import _ship_to_carried_vehicle

    def fake_to_dict(ship):
        return {
            "name": "fighter_alpha",
            "design_id": "fighter_alpha",
            "expected_stats": {"mass": 20.0},
        }

    monkeypatch.setattr(
        ship_serialization.ShipSerializer, "to_dict", fake_to_dict,
    )

    damaged_fighter = _make_launched_fighter_with_damaged_components()
    # Reboard.
    cv = _ship_to_carried_vehicle(damaged_fighter)
    assert cv is not None
    assert cv.component_states is not None
    assert cv.component_states["comp_hull"].current_hp == 30

    # Re-launch from the carried vehicle.
    from game.simulation.systems import attack_processor

    spawned = MagicMock()
    spawned.components = {}
    spawned.current_hp = 0
    monkeypatch.setattr(
        "game.simulation.entities.ship_serialization.ShipSerializer.from_dict",
        lambda design_data, registries=None: spawned,
    )

    source = MagicMock()
    source.registries = None
    source.color = (255, 255, 255)
    source.theme_id = "Federation"
    source.angle = 0
    source.team_id = 0

    relaunched = attack_processor._spawn_from_carried_vehicle(
        engine=MagicMock(),
        source_ship=source,
        carried_payload=cv,
        new_name="Wing 2",
        spawn_pos=SimpleNamespace(x=0.0, y=0.0),
    )
    assert relaunched.components["comp_hull"].current_hp == 30
    assert relaunched.components["comp_engine"].current_hp == 80
