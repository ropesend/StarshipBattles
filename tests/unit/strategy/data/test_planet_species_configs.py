"""Tests for `Planet.species_configs` (PROJ-284 Phase 1 Task 1.4).

`Planet` gains a `species_configs: Dict[race_id, ColonySpeciesConfig]`
field plus a `get_species_config(race_id)` lazy-create helper.
Round-trip preserves `food_allocation` per-species but resets
`last_food_ratio` (transient).

Note: tests live in their own file (`test_planet_species_configs.py`)
rather than in a generic `test_planet.py` because the existing planet
test suite is split by concern (`test_planet_naming.py`,
`test_planet_stockpile.py`, etc.) — this file follows that convention.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.planet import Planet, PlanetType


def _minimal_planet(**overrides) -> Planet:
    """Build a Planet with the smallest set of valid required fields."""
    defaults = dict(
        name="Test Planet",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.9e24,
        radius=6.3e6,
        surface_area=5.1e14,
        density=5500.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )
    defaults.update(overrides)
    return Planet(**defaults)


class TestSpeciesConfigsField:
    def test_default_empty(self):
        planet = _minimal_planet()
        assert planet.species_configs == {}

    def test_constructor_accepts_explicit_configs(self):
        cfg = ColonySpeciesConfig(food_allocation=2.0)
        planet = _minimal_planet(species_configs={"rossarian": cfg})
        assert planet.species_configs["rossarian"] is cfg


class TestGetSpeciesConfig:
    def test_lazy_creates_default(self):
        """`get_species_config(race_id)` for an unseen race returns a
        default `ColonySpeciesConfig` AND stores it on the planet so the
        next call returns the same instance."""
        planet = _minimal_planet()
        cfg = planet.get_species_config("rossarian")
        assert isinstance(cfg, ColonySpeciesConfig)
        assert cfg.food_allocation == 1.0
        # Stored on planet
        assert "rossarian" in planet.species_configs
        # Same instance returned next time
        assert planet.get_species_config("rossarian") is cfg

    def test_returns_existing_config(self):
        cfg = ColonySpeciesConfig(food_allocation=0.5)
        planet = _minimal_planet(species_configs={"rossarian": cfg})
        assert planet.get_species_config("rossarian") is cfg

    def test_lazy_create_does_not_pollute_other_races(self):
        planet = _minimal_planet()
        planet.get_species_config("rossarian")
        assert list(planet.species_configs.keys()) == ["rossarian"]


def _cfg_with_ratios(food_allocation: float, ratios: dict) -> ColonySpeciesConfig:
    """Build a ColonySpeciesConfig + seed its transient ratio dict.

    PROJ-286: `last_consumption_ratios` is a post-construction-writable
    field; `last_food_ratio` is a read-only computed property. Tests
    that want to exercise the transient-field round-trip path seed the
    dict after construction."""
    cfg = ColonySpeciesConfig(food_allocation=food_allocation)
    cfg.last_consumption_ratios = dict(ratios)
    return cfg


class TestSpeciesConfigsRoundTrip:
    def test_round_trip_preserves_food_allocation(self):
        planet = _minimal_planet()
        planet.species_configs = {
            "rossarian": _cfg_with_ratios(2.5, {"organics": 0.3}),
            "voidari": _cfg_with_ratios(0.5, {"organics": 0.9}),
        }
        restored = Planet.from_dict(planet.to_dict())
        assert restored.species_configs["rossarian"].food_allocation == 2.5
        assert restored.species_configs["voidari"].food_allocation == 0.5

    def test_round_trip_resets_last_consumption_ratios(self):
        """`last_consumption_ratios` is transient — round-trip resets to
        empty dict, which makes `last_food_ratio` revert to 1.0."""
        planet = _minimal_planet()
        planet.species_configs = {
            "rossarian": _cfg_with_ratios(1.0, {"organics": 0.2, "metals": 0.5}),
        }
        restored = Planet.from_dict(planet.to_dict())
        assert restored.species_configs["rossarian"].last_consumption_ratios == {}
        assert restored.species_configs["rossarian"].last_food_ratio == 1.0

    def test_old_save_without_species_configs_loads(self):
        """Backward compatibility: saves from before PROJ-284 lack the
        `species_configs` key. Load with an empty dict (lazy-create on
        first `get_species_config` call)."""
        planet = _minimal_planet()
        data = planet.to_dict()
        del data["species_configs"]
        restored = Planet.from_dict(data)
        assert restored.species_configs == {}
        # Lazy-create still works after load.
        cfg = restored.get_species_config("new_race")
        assert cfg.food_allocation == 1.0

    def test_to_dict_does_not_emit_transient_ratio_fields(self):
        """Sanity: the transient dict doesn't leak into Planet.to_dict()
        either, via ColonySpeciesConfig.to_dict()'s own filter."""
        planet = _minimal_planet()
        planet.species_configs = {
            "rossarian": _cfg_with_ratios(2.0, {"organics": 0.5}),
        }
        emitted = planet.to_dict()["species_configs"]["rossarian"]
        assert emitted == {"food_allocation": 2.0}
        assert "last_consumption_ratios" not in emitted
        assert "last_food_ratio" not in emitted
