"""Unit tests for `planet_habitability_multiplier` (PROJ-285 Phase 1 Task 1.3).

The helper returns the population-weighted mean habitability across all
species on a planet:

    multiplier = Σ (pop.count * score_planet_for_race(planet, race_for(pop))) / Σ pop.count

Uncolonized planets (no populations) return 1.0 — a lifeless extractor
base pays no habitability penalty. Species with missing race_config
entries are skipped (population excluded from both numerator AND
denominator), so a colony of one known race + one unknown race
multiplies at the known race's value.
"""
from __future__ import annotations

from typing import List, Optional
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _earth_like(populations: List[SpeciesPopulation]) -> Planet:
    """Earth-standard physics — an Earth-default-prefs race scores ~0.94 here."""
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
        populations=populations,
    )


def _hostile(populations: List[SpeciesPopulation]) -> Planet:
    """Magma world — Earth-default-prefs race scores ~0.002 here."""
    return Planet(
        name="Hostile",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=25.0,
        surface_pressure=101325.0,
        surface_temperature=500.0,
        surface_water=0.0,
        tectonic_activity=0.9,
        magnetic_field=0.0,
        atmosphere={},
        planet_type=PlanetType.MAGMA,
        populations=populations,
    )


def _race(race_id: str = "human") -> RaceConfig:
    """Default-prefs race. `__post_init__` backfills all 17 FACTOR_REGISTRY
    entries with Earth-standard setpoints, so an Earth-like planet scores
    high and a magma planet scores low."""
    return RaceConfig(
        race_id=race_id,
        name=race_id.capitalize(),
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


class _StubRegistry:
    """Minimal race-registry double — the helper only calls `.get_race(id)`."""
    def __init__(self, races: dict):
        self._races = races

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        return self._races.get(race_id)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUncolonized:
    def test_empty_populations_returns_one(self):
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[])
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(planet, registry) == 1.0

    def test_populations_all_zero_count_returns_one(self):
        """A planet where every species has count=0 is functionally uncolonized."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=0, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=0, happiness=0.5),
        ])
        registry = _StubRegistry({"human": _race("human"), "alien": _race("alien")})
        assert planet_habitability_multiplier(planet, registry) == 1.0


class TestSingleSpecies:
    def test_ideal_planet_yields_high_multiplier(self):
        """Earth-default-prefs race on an Earth-like planet -> habitability
        score around 0.94 (verified by `score_planet_for_race` elsewhere)."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        registry = _StubRegistry({"human": _race("human")})
        mult = planet_habitability_multiplier(planet, registry)
        assert mult > 0.9, f"Ideal planet should score >0.9, got {mult}"
        assert mult <= 1.0

    def test_hostile_planet_yields_low_multiplier(self):
        """Magma world -> habitability near zero."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _hostile(populations=[pop])
        registry = _StubRegistry({"human": _race("human")})
        mult = planet_habitability_multiplier(planet, registry)
        assert mult < 0.3, f"Hostile planet should score <0.3, got {mult}"
        assert mult >= 0.0


class TestPopulationWeighted:
    def test_weighted_average_of_two_species(self):
        """Helper uses real habitability scores — construct a scenario where
        70% of population scores ~1.0 and 30% scores ~0 via stub registry
        (species with missing race_config contribute 0 via skip, OR we pin
        the math using two real races with known outputs). Here we use two
        identical races (hab≈0.94) weighted 70/30 — the weighted average
        must equal that same ~0.94 regardless of weights when inputs match."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=300, happiness=0.5),
        ])
        registry = _StubRegistry({"human": _race("human"), "alien": _race("alien")})
        mult = planet_habitability_multiplier(planet, registry)
        # Both races have identical prefs -> same score -> weighted avg == that score.
        # Sanity: in [0.9, 1.0] range.
        assert 0.9 < mult <= 1.0

    def test_weighted_average_monkey_patched_scores(self, monkeypatch):
        """Pin the arithmetic: patch `score_planet_for_race` to return
        fixed values per race so we can assert the weighted-sum math
        directly without depending on `FACTOR_REGISTRY` tuning."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=300, happiness=0.5),
        ])
        race_human = _race("human")
        race_alien = _race("alien")
        registry = _StubRegistry({"human": race_human, "alien": race_alien})

        def fake_score(planet_arg, race_config):
            if race_config is race_human:
                return 1.0
            if race_config is race_alien:
                return 0.2
            return 0.0

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # 0.7 * 1.0 + 0.3 * 0.2 = 0.76
        assert mult == pytest.approx(0.76)


class TestZeroCountSpeciesExcluded:
    def test_zero_count_species_excluded_from_weight(self, monkeypatch):
        """A species with `count=0` doesn't count in the numerator OR
        denominator. Weighted average reduces to the remaining species."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
            SpeciesPopulation(race_id="ghost", count=0, happiness=0.5),
        ])
        race_human = _race("human")
        race_ghost = _race("ghost")
        registry = _StubRegistry({"human": race_human, "ghost": race_ghost})

        def fake_score(planet_arg, race_config):
            if race_config is race_human:
                return 0.5
            return 0.0  # ghost would score 0, but it's zero-count -> skipped

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # Only human contributes: weighted avg = 0.5.
        assert mult == pytest.approx(0.5)


class TestMissingRaceConfig:
    def test_missing_race_excluded_from_both_numerator_and_denominator(self, monkeypatch):
        """Species whose race_id isn't in the registry are skipped entirely
        — their count does NOT inflate the denominator (would drag the
        multiplier down unfairly). Design decision documented in the helper
        docstring."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="unknown", count=300, happiness=0.5),
        ])
        race_human = _race("human")
        registry = _StubRegistry({"human": race_human})  # "unknown" absent

        def fake_score(planet_arg, race_config):
            return 0.8

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # Only human counts: 700 * 0.8 / 700 = 0.8.
        assert mult == pytest.approx(0.8)

    def test_all_races_missing_returns_one(self):
        """If every species on the planet has an unknown race_id, the
        weighted sum collapses to zero population -> fall back to 1.0
        (treat as uncolonized for multiplier purposes)."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="ghost_a", count=500, happiness=0.5),
            SpeciesPopulation(race_id="ghost_b", count=500, happiness=0.5),
        ])
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(planet, registry) == 1.0


class TestResilience:
    def test_planet_without_populations_attr_returns_one(self):
        """Defensive: if a planet-like object lacks `populations` entirely
        (e.g., a malformed save or a non-Planet object passed by mistake),
        return 1.0 rather than raising."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        bare = MagicMock(spec=[])  # no `populations` attr
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(bare, registry) == 1.0

    def test_registry_raising_does_not_propagate(self, monkeypatch):
        """A registry that raises on `get_race` should cause the species
        to be skipped (same as missing), not blow up the pipeline."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
        ])

        class ExplodingRegistry:
            def get_race(self, race_id):
                raise RuntimeError("disk corrupt")

        # Should NOT raise.
        mult = planet_habitability_multiplier(planet, ExplodingRegistry())
        assert mult == 1.0  # Species skipped -> no populations counted -> default.
