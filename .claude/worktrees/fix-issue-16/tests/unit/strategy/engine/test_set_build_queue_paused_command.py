"""Tests for `SetBuildQueuePausedCommand` + handler (FEAT-17).

Mirrors the shape of AddToConstructionQueueCommand handler tests:
resolve entity by id+type, locate the queue owner via queue_id (or default
to the entity itself), then flip its `construction_queue_paused` flag.
"""
from unittest.mock import Mock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet, PlanetaryFacility
from game.strategy.engine.commands import SetBuildQueuePausedCommand
from game.strategy.engine.handlers.construction_queue import (
    SetBuildQueuePausedCommandHandler,
)


def _make_planet() -> Planet:
    return Planet(
        name="Verona I",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        owner_id=0,
        id=42,
    )


def _make_facility(instance_id: str = "yard-1") -> PlanetaryFacility:
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="shipyard",
        name="Shipyard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": {}}}
                ]
            }
        },
        is_operational=True,
    )


def _make_session_for_planet(planet: Planet):
    session = Mock()
    session._get_planet_by_id.return_value = planet
    session._get_fleet_by_id.return_value = None
    return session


def _make_session_for_fleet(fleet: Fleet):
    session = Mock()
    session._get_planet_by_id.return_value = None
    session._get_fleet_by_id.return_value = fleet
    return session


class TestSetBuildQueuePausedForPlanetBase:
    """queue_id=None → toggle the planet's base queue."""

    def test_pause_planet_base_queue(self):
        planet = _make_planet()
        assert planet.construction_queue_paused is False
        session = _make_session_for_planet(planet)
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=42, entity_type="planet", paused=True, queue_id=None
        )

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert planet.construction_queue_paused is True

    def test_unpause_planet_base_queue(self):
        planet = _make_planet()
        planet.construction_queue_paused = True
        session = _make_session_for_planet(planet)
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=42, entity_type="planet", paused=False, queue_id=None
        )

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert planet.construction_queue_paused is False

    def test_pause_planet_base_queue_via_base_queue_id_pattern(self):
        """queue_id 'planet_42_base' resolves to the planet itself."""
        planet = _make_planet()
        session = _make_session_for_planet(planet)
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=42,
            entity_type="planet",
            paused=True,
            queue_id="planet_42_base",
        )

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert planet.construction_queue_paused is True


class TestSetBuildQueuePausedForFacility:
    """queue_id matches a facility instance_id → toggle that facility."""

    def test_pause_facility_queue(self):
        planet = _make_planet()
        f = _make_facility(instance_id="yard-A")
        planet.facilities.append(f)
        assert f.construction_queue_paused is False
        session = _make_session_for_planet(planet)
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=42, entity_type="planet", paused=True, queue_id="yard-A"
        )

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert f.construction_queue_paused is True
        # Planet base flag unchanged
        assert planet.construction_queue_paused is False

    def test_pause_one_of_two_facilities_independently(self):
        planet = _make_planet()
        f1 = _make_facility(instance_id="yard-A")
        f2 = _make_facility(instance_id="yard-B")
        planet.facilities.extend([f1, f2])
        session = _make_session_for_planet(planet)
        handler = SetBuildQueuePausedCommandHandler()

        result = handler.execute(
            session,
            SetBuildQueuePausedCommand(
                entity_id=42, entity_type="planet", paused=True, queue_id="yard-A"
            ),
        )

        assert result.is_valid
        assert f1.construction_queue_paused is True
        assert f2.construction_queue_paused is False


class TestSetBuildQueuePausedForFleet:
    """entity_type='fleet' → toggle the fleet's queue."""

    def test_pause_fleet_queue(self):
        fleet = Fleet(fleet_id=99, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        assert fleet.construction_queue_paused is False
        session = _make_session_for_fleet(fleet)
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=99, entity_type="fleet", paused=True, queue_id=None
        )

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert fleet.construction_queue_paused is True


class TestSetBuildQueuePausedErrors:
    """Failure modes mirror AddToConstructionQueue."""

    def test_unknown_entity_returns_error(self):
        session = Mock()
        session._get_planet_by_id.return_value = None
        session._get_fleet_by_id.return_value = None
        handler = SetBuildQueuePausedCommandHandler()
        cmd = SetBuildQueuePausedCommand(
            entity_id=999, entity_type="planet", paused=True, queue_id=None
        )

        result = handler.execute(session, cmd)

        assert not result.is_valid
