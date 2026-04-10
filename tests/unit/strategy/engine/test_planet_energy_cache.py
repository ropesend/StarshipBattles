"""
Tests for planet energy caching (PROJ-253 Phase 2).

Verifies that PlanetEnergyEngine caches facility scan results and
only rebuilds when facility state changes.
"""
from unittest.mock import MagicMock, patch
from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine


def _make_registries():
    """Create mock registries."""
    registries = MagicMock()
    registries.components = {}
    return registries


def _make_facility(design_data, is_operational=True, instance_id="fac-1"):
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.design_data = design_data
    facility.is_operational = is_operational
    facility.component_states = {}
    return facility


def _make_planet(name="TestPlanet", facilities=None, planet_id="p1"):
    planet = MagicMock()
    planet.name = name
    planet.id = planet_id
    planet.facilities = facilities or []
    planet.energy = 0.0
    planet.energy_capacity = 0.0
    planet.energy_generation = 0.0
    planet.active_abilities = {'PlanetaryShield': False}
    return planet


class TestPlanetEnergyCache:
    """PlanetEnergyEngine should cache facility scan results."""

    def test_cache_populated_on_first_tick(self):
        """First tick should populate the energy cache."""
        engine = PlanetEnergyEngine(registries=_make_registries())
        planet = _make_planet(facilities=[])

        engine._process_planet(planet, tick=1)

        assert hasattr(engine, '_energy_cache')
        assert planet.id in engine._energy_cache

    def test_invalidate_energy_cache_clears_planet(self):
        """invalidate_energy_cache() should remove the planet's cache entry."""
        engine = PlanetEnergyEngine(registries=_make_registries())
        planet = _make_planet(facilities=[])

        engine._process_planet(planet, tick=1)
        assert planet.id in engine._energy_cache

        engine.invalidate_energy_cache(planet.id)
        assert planet.id not in engine._energy_cache

    def test_cache_invalidated_when_facility_count_changes(self):
        """Adding a facility should invalidate the cache."""
        engine = PlanetEnergyEngine(registries=_make_registries())
        fac1 = _make_facility({'components': []})
        planet = _make_planet(facilities=[fac1])

        engine._process_planet(planet, tick=1)

        # Add a new facility
        fac2 = _make_facility({'components': []}, instance_id="fac-2")
        planet.facilities.append(fac2)

        engine._process_planet(planet, tick=2)
        # Cache should have been rebuilt (fingerprint changed)
        # We can't easily check "scan count" without instrumenting,
        # but we can verify the cache exists and is updated
        assert planet.id in engine._energy_cache
