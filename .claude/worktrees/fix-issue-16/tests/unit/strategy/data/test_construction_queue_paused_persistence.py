"""FEAT-17 — `construction_queue_paused` flag round-trips through save/load.

Each yard-owning entity (Planet, PlanetaryFacility, Fleet) carries its own
flag. PlanetaryFacility round-trips are covered alongside other facility
serialization in `test_facility_construction_queue.py`; this file covers
Planet (base queue) and Fleet (space-yard queue), plus the legacy-save
compatibility default.
"""

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet


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
    )


class TestPlanetConstructionQueuePausedPersistence:
    """Planet.construction_queue_paused round-trips."""

    def test_planet_defaults_paused_to_false(self):
        planet = _make_planet()
        assert planet.construction_queue_paused is False

    def test_planet_paused_round_trips(self):
        planet = _make_planet()
        planet.construction_queue_paused = True

        data = planet.to_dict()
        assert data["construction_queue_paused"] is True

        restored = Planet.from_dict(data)
        assert restored.construction_queue_paused is True

    def test_planet_unpaused_round_trips(self):
        planet = _make_planet()
        planet.construction_queue_paused = False

        data = planet.to_dict()
        restored = Planet.from_dict(data)
        assert restored.construction_queue_paused is False

    def test_legacy_planet_save_defaults_to_false(self):
        """Save written before FEAT-17 must load with paused=False."""
        planet = _make_planet()
        data = planet.to_dict()
        # Strip the FEAT-17 key to simulate an old save
        data.pop("construction_queue_paused", None)
        restored = Planet.from_dict(data)
        assert restored.construction_queue_paused is False


class TestFleetConstructionQueuePausedPersistence:
    """Fleet.construction_queue_paused round-trips."""

    def test_fleet_defaults_paused_to_false(self):
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        assert fleet.construction_queue_paused is False

    def test_fleet_paused_round_trips(self):
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        fleet.construction_queue_paused = True

        data = fleet.to_dict()
        assert data["construction_queue_paused"] is True

        restored = Fleet.from_dict(data)
        assert restored.construction_queue_paused is True

    def test_fleet_unpaused_round_trips(self):
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        fleet.construction_queue_paused = False

        data = fleet.to_dict()
        restored = Fleet.from_dict(data)
        assert restored.construction_queue_paused is False

    def test_legacy_fleet_save_defaults_to_false(self):
        """Save written before FEAT-17 must load with paused=False."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)
        data = fleet.to_dict()
        data.pop("construction_queue_paused", None)
        restored = Fleet.from_dict(data)
        assert restored.construction_queue_paused is False
