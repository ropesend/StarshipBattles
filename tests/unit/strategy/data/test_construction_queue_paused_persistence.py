"""FEAT-17 — `construction_queue_paused` flag round-trips through save/load.

Each yard-owning entity (Planet, PlanetaryFacility, Fleet) carries its own
flag. PlanetaryFacility round-trips are covered alongside other facility
serialization in `test_facility_construction_queue.py`; this file covers
Planet (base queue) and Fleet (space-yard queue), plus the legacy-save
compatibility default.

PROJ-322 Task 1.9 (S04-CAT4-001): Planet and Fleet variants collapsed
into a parametrized fixture-factory; the four method shapes (default,
set True, set False, legacy save) are now parametrized cases.
"""

import pytest

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


def _make_real_fleet() -> Fleet:
    return Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5.0)


_ENTITY_FACTORIES = {
    "planet": (_make_planet, Planet),
    "fleet": (_make_real_fleet, Fleet),
}


@pytest.fixture(params=list(_ENTITY_FACTORIES.keys()))
def entity_factory(request):
    """(entity_factory_callable, entity_class) pair for Planet / Fleet."""
    return _ENTITY_FACTORIES[request.param]


class TestConstructionQueuePausedPersistence:
    """Round-trip coverage for the FEAT-17 `construction_queue_paused`
    flag on every yard-owning entity. Parametrized over Planet and Fleet
    in PROJ-322 Task 1.9 (S04-CAT4-001)."""

    def test_defaults_paused_to_false(self, entity_factory):
        make, _ = entity_factory
        entity = make()
        assert entity.construction_queue_paused is False

    def test_paused_round_trips(self, entity_factory):
        make, cls = entity_factory
        entity = make()
        entity.construction_queue_paused = True

        data = entity.to_dict()
        assert data["construction_queue_paused"] is True

        restored = cls.from_dict(data)
        assert restored.construction_queue_paused is True

    def test_unpaused_round_trips(self, entity_factory):
        make, cls = entity_factory
        entity = make()
        entity.construction_queue_paused = False

        data = entity.to_dict()
        restored = cls.from_dict(data)
        assert restored.construction_queue_paused is False

    def test_legacy_save_defaults_to_false(self, entity_factory):
        """Save written before FEAT-17 must load with paused=False."""
        make, cls = entity_factory
        entity = make()
        data = entity.to_dict()
        # Strip the FEAT-17 key to simulate an old save
        data.pop("construction_queue_paused", None)
        restored = cls.from_dict(data)
        assert restored.construction_queue_paused is False
