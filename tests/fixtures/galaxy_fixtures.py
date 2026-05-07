"""Galaxy stub factory for unit tests (PROJ-378).

Constructs a minimal post-PROJ-372 ``Galaxy`` whose ``_state``,
``_registry`` and ``_spatial`` are wired but whose heavy ``__init__``
dependencies (``NameRegistry``, ``StarImageRegistry``, ``StarGenerator``,
``PlanetImageRegistry``, ``PlanetGenerator``, ``StormGenerator``,
``GalaxyWarpGenerator``, ``GalaxySystemGenerator``,
``GalaxyPathfindingService``) are skipped — saving ~33 ms per call and
removing the disk I/O dependency that ``Galaxy(radius=...)`` would
otherwise drag into a unit test.

This is the canonical implementation. ``tests/unit/strategy/data/conftest.py``
exposes a thin ``galaxy_stub`` ``@pytest.fixture`` wrapper for unit tests
that prefer fixture injection.

Safe to call on a stubbed galaxy:
  * ``galaxy.unregister_planet(...)`` / ``galaxy.register_planet(...)`` and
    other methods that delegate to ``_registry``.
  * ``galaxy.get_all_fleets_in_system(...)`` and other methods that
    delegate to ``_spatial``.
  * ``galaxy.remove_warp_link(...)`` and other methods that read
    ``_state`` directly.
  * Property reads/writes (``galaxy.radius``, ``galaxy.systems[k] = v``,
    ``galaxy.name_map[k] = v``, etc.).

NOT safe to call on a stubbed galaxy (use real ``Galaxy(radius=...)``):
  * ``galaxy.generate_systems(...)``, ``galaxy.generate_planets(...)``,
    ``galaxy.generate_warp_lanes(...)`` — depend on generators that the
    stub does not wire.
  * Any method that reads ``galaxy.naming``, ``galaxy.star_generator``,
    ``galaxy.planet_generator``, ``galaxy.storm_generator``,
    ``galaxy._warp_gen``, ``galaxy._sys_gen`` or ``galaxy._pathfinder``.
"""
from __future__ import annotations

from game.strategy.data.galaxy import Galaxy
from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry
from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex
from game.strategy.data.galaxy_state import GalaxyState


def make_galaxy_stub(radius: int = 100) -> Galaxy:
    """Return a minimal post-PROJ-372 ``Galaxy`` for unit-test setup."""
    galaxy = Galaxy.__new__(Galaxy)
    galaxy._state = GalaxyState(radius=radius)
    galaxy._registry = GalaxyEntityRegistry(galaxy._state)
    galaxy._spatial = GalaxySpatialIndex(galaxy._state)
    return galaxy
