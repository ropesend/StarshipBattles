"""Tests for `Planet.get_cached_habitability_multiplier` (PROJ-285 Phase 1 Task 1.4).

The cache avoids recomputing the population-weighted habitability
multiplier once per tick per colony per resource. Populations only
change at turn boundaries (population growth runs after the 100-tick
loop), so a per-turn cache key is sufficient.

Contract:
- First call for a given turn computes via `planet_habitability_multiplier`
  and stores the result.
- Subsequent calls at the same turn return the stored value without
  re-invoking the helper.
- Calls at a new turn recompute.
- The cache MUST NOT serialize — `to_dict`/`from_dict` excludes both
  `_cached_habitability_multiplier` and `_cached_multiplier_turn` so
  saves stay canonical.

File named `test_planet_habitability_cache.py` to follow the project's
convention of splitting planet tests by concern
(`test_planet_stockpile.py`, `test_planet_species_configs.py`, ...)
rather than growing a monolithic `test_planet.py`.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation


def _earth_like(populations=None) -> Planet:
    return Planet(
        name="Earth",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL,
        populations=populations or [],
    )


class TestCacheBasic:
    def test_first_call_computes_and_stores(self, monkeypatch):
        import game.strategy.formulas.colony_output as co_mod

        fake_helper = MagicMock(return_value=0.7)
        # The Planet method late-imports from `colony_output`; patch
        # there so the binding resolves to our stub.
        monkeypatch.setattr(
            co_mod, "planet_habitability_multiplier", fake_helper,
        )

        planet = _earth_like()
        registry = MagicMock()
        result = planet.get_cached_habitability_multiplier(registry, turn=5)

        assert result == 0.7
        fake_helper.assert_called_once_with(planet, registry)

    def test_same_turn_second_call_uses_cache(self, monkeypatch):
        """The helper is invoked once; the second call reads the cached
        value without recomputing."""
        import game.strategy.formulas.colony_output as co_mod

        fake_helper = MagicMock(return_value=0.5)
        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", fake_helper)

        planet = _earth_like()
        registry = MagicMock()
        planet.get_cached_habitability_multiplier(registry, turn=5)
        planet.get_cached_habitability_multiplier(registry, turn=5)
        planet.get_cached_habitability_multiplier(registry, turn=5)

        fake_helper.assert_called_once()

    def test_new_turn_recomputes(self, monkeypatch):
        import game.strategy.formulas.colony_output as co_mod

        fake_helper = MagicMock(side_effect=[0.5, 0.4])
        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", fake_helper)

        planet = _earth_like()
        registry = MagicMock()
        first = planet.get_cached_habitability_multiplier(registry, turn=5)
        second = planet.get_cached_habitability_multiplier(registry, turn=6)

        assert first == 0.5
        assert second == 0.4
        assert fake_helper.call_count == 2


class TestCacheNotSerialized:
    def test_to_dict_does_not_emit_cache_fields(self, monkeypatch):
        """`to_dict` must NOT include either cache field, regardless of
        whether the cache has been populated."""
        import game.strategy.formulas.colony_output as co_mod
        monkeypatch.setattr(
            co_mod, "planet_habitability_multiplier",
            MagicMock(return_value=0.42),
        )

        planet = _earth_like()
        # Warm the cache.
        planet.get_cached_habitability_multiplier(MagicMock(), turn=3)

        data = planet.to_dict()
        assert "_cached_habitability_multiplier" not in data
        assert "_cached_multiplier_turn" not in data

    def test_from_dict_does_not_hydrate_cache_fields(self, monkeypatch):
        """Round-trip resets the cache so post-load state is authoritative."""
        import game.strategy.formulas.colony_output as co_mod

        counter = MagicMock(return_value=0.9)
        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", counter)

        planet = _earth_like()
        planet.get_cached_habitability_multiplier(MagicMock(), turn=7)
        assert counter.call_count == 1

        # Round-trip: the cache must be cold afterward.
        restored = Planet.from_dict(planet.to_dict())
        # Even at the SAME turn=7 that we already computed for, the
        # restored planet recomputes because `from_dict` doesn't carry
        # the cache.
        restored.get_cached_habitability_multiplier(MagicMock(), turn=7)
        assert counter.call_count == 2

    def test_cache_fields_initialize_to_sentinel(self):
        """Fresh Planet has a None value and turn=-1 so the first
        `get_cached_habitability_multiplier` call at any turn recomputes."""
        planet = _earth_like()
        assert planet._cached_habitability_multiplier is None
        assert planet._cached_multiplier_turn == -1


class TestCacheBypassEqual:
    def test_cache_does_not_affect_planet_equality(self, monkeypatch):
        """Two planets with identical identity-defining fields but
        different cache state must still compare equal — equality is
        based on name + location + orbit_distance (see
        `Planet.__eq__`)."""
        import game.strategy.formulas.colony_output as co_mod
        monkeypatch.setattr(
            co_mod, "planet_habitability_multiplier",
            MagicMock(return_value=0.5),
        )
        a = _earth_like()
        b = _earth_like()
        a.get_cached_habitability_multiplier(MagicMock(), turn=1)
        assert a == b  # Cache state ignored.
