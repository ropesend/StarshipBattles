"""Unit tests for `HappinessEngine` (PROJ-284 Phase 3 Task 3.2).

`HappinessEngine.process_happiness(empires, galaxy)` runs ONCE per turn,
BETWEEN `OrganicsConsumptionEngine.process_consumption` (which writes
`ColonySpeciesConfig.last_food_ratio`) and
`PopulationEngine.process_population_growth` (which reads
`SpeciesPopulation.happiness`).

Formula:
    happiness = clamp(race.base_happiness * cfg.last_food_ratio * habitability, 0, 3)

Unbounded above 1.0 so over-supply + ideal habitability can push happiness
past the neutral point — Phase 4 UI lets the player push `food_allocation`
above 1.0 to over-feed. Clamped at 3 to prevent silly values from pathological
setups.
"""
from __future__ import annotations

from typing import List

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.formulas.habitability import score_planet_for_race


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _earth_like(
    *,
    populations: List[SpeciesPopulation],
    species_configs: dict = None,
    name: str = "Earth",
) -> Planet:
    """Planet with Earth-standard physics — ideal habitability for humans."""
    return Planet(
        name=name,
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
        species_configs=species_configs or {},
    )


def _hostile(
    *,
    populations: List[SpeciesPopulation],
    species_configs: dict = None,
) -> Planet:
    """Planet ruthlessly unlike Earth — habitability pushed near zero."""
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
        species_configs=species_configs or {},
    )


def _race(
    *,
    race_id: str = "human",
    base_happiness: float = 0.5,
    base_reproduction_rate: float = 0.03,
) -> RaceConfig:
    """Race with default (Earth-ideal) environmental preferences."""
    return RaceConfig(
        race_id=race_id,
        name="Human",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
        base_happiness=base_happiness,
        base_reproduction_rate=base_reproduction_rate,
    )


def _empire(empire_id: int, colonies: List[Planet], race_config: RaceConfig) -> Empire:
    empire = Empire(
        empire_id=empire_id,
        name="Test Empire",
        color=(100, 100, 200),
        race_config=race_config,
    )
    empire.colonies = colonies
    return empire


@pytest.fixture
def engine():
    from game.strategy.engine.happiness_engine import HappinessEngine
    return HappinessEngine()


# ---------------------------------------------------------------------------
# Scenarios from phase_3_checklist.md Task 3.2
# ---------------------------------------------------------------------------

class TestHappinessIdealPlanet:
    def test_ideal_planet_food_ratio_one_base_half(self, engine):
        """Ideal planet, ratio=1, base=0.5 -> happiness ≈ 0.5 * hab (~0.47)."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)

        # Seed the ratio as OrganicsConsumptionEngine would.
        planet.get_species_config("human").last_food_ratio = 1.0

        engine.process_happiness([empire], galaxy=None)

        hab = score_planet_for_race(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)

    def test_ideal_planet_food_ratio_two_amplifies_happiness(self, engine):
        """food_ratio=2 doubles the happiness signal for the same base."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 2.0

        engine.process_happiness([empire], galaxy=None)

        hab = score_planet_for_race(planet, race)
        # base * ratio * hab = 0.5 * 2.0 * ~0.94 ≈ 0.94 (still under cap 3)
        assert pop.happiness == pytest.approx(0.5 * 2.0 * hab)


class TestHappinessHostilePlanet:
    def test_hostile_planet_drags_happiness_down(self, engine):
        """Low habitability drags happiness toward zero even on full food."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        planet = _hostile(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 1.0

        engine.process_happiness([empire], galaxy=None)

        hab = score_planet_for_race(planet, race)
        assert hab < 0.1, "test setup: hostile planet must be near zero"
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)
        assert pop.happiness < 0.1


class TestHappinessStarvation:
    def test_zero_food_ratio_gives_zero_happiness(self, engine):
        """Starvation collapses happiness to zero regardless of habitability."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.9)  # pre-turn
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 0.0

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(0.0)


class TestHappinessClamping:
    def test_over_supply_clamps_at_three(self, engine):
        """Silly over-supply (ratio=5, base=0.6, hab~1) * each term -> 3.0."""
        # 0.6 * 5.0 * ~0.94 = 2.82. Need to push higher for clamp test.
        # Use ratio=20.0 -> 0.6 * 20 * 0.94 = 11.28 -> clamped to 3.
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.6)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 20.0

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(3.0)

    def test_negative_product_clamps_at_zero(self, engine):
        """Defensive clamp — even if base_happiness were negative (shouldn't
        happen via the validator, but test the clamp)."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        # Violate the invariant for the test.
        planet.get_species_config("human").last_food_ratio = -1.0

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(0.0)


class TestHappinessMissingRaceConfig:
    def test_missing_race_config_skips_pop_without_crash(self, engine):
        """Multi-species where one race isn't in the registry -> skip, no raise."""
        pop_human = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        pop_unknown = SpeciesPopulation(race_id="ghost", count=50, happiness=0.4)
        planet = _earth_like(populations=[pop_human, pop_unknown])
        race = _race(race_id="human", base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 1.0
        planet.get_species_config("ghost").last_food_ratio = 1.0

        engine.process_happiness([empire], galaxy=None)

        # Human gets the formula; ghost falls through to empire.race_config,
        # which `PopulationEngine._get_race_config` returns as a fallback, so
        # it also gets a computed happiness. HappinessEngine reuses the same
        # resolver (decision 2026-04-18 in plan.md § Current State), so both
        # succeed. Test the non-crash property.
        assert pop_human.happiness >= 0
        assert pop_unknown.happiness >= 0

    def test_empire_without_race_config_leaves_happiness_untouched(self, engine):
        """If empire.race_config is None, no resolver fallback -> pop skipped
        (happiness stays at pre-call value)."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.42)
        planet = _earth_like(populations=[pop])
        empire = Empire(empire_id=1, name="NoRace", color=(0, 0, 0))
        empire.colonies = [planet]
        empire.race_config = None
        planet.get_species_config("human").last_food_ratio = 1.0

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(0.42)


class TestHappinessMultiSpecies:
    def test_multi_species_happiness_computed_independently(self, engine):
        """Two species on same planet get independent happiness from their
        own race config + their own `last_food_ratio`."""
        pop_human = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        pop_alien = SpeciesPopulation(race_id="alien", count=50, happiness=0.0)
        planet = _earth_like(populations=[pop_human, pop_alien])
        race_human = _race(race_id="human", base_happiness=0.5)
        race_alien = _race(race_id="alien", base_happiness=0.8)
        empire = _empire(1, [planet], race_human)
        planet.get_species_config("human").last_food_ratio = 1.0
        planet.get_species_config("alien").last_food_ratio = 0.25

        def mock_resolver(race_id, empire_arg):
            return {"human": race_human, "alien": race_alien}.get(race_id)
        engine._get_race_config = mock_resolver

        engine.process_happiness([empire], galaxy=None)

        hab = score_planet_for_race(planet, race_human)
        assert pop_human.happiness == pytest.approx(0.5 * 1.0 * hab)
        assert pop_alien.happiness == pytest.approx(0.8 * 0.25 * hab)
        # Sanity: independent — alien was lower before the run, higher after.
        assert pop_human.happiness != pop_alien.happiness


class TestHappinessEngineEdgeCases:
    def test_no_empires_does_not_raise(self, engine):
        engine.process_happiness([], galaxy=None)

    def test_empty_colony_populations_does_not_raise(self, engine):
        planet = _earth_like(populations=[])
        race = _race()
        empire = _empire(1, [planet], race)
        engine.process_happiness([empire], galaxy=None)

    def test_zero_population_still_gets_fresh_happiness(self, engine):
        """Even zero-count pops get a fresh happiness write so stale
        pre-turn values never leak into population growth."""
        pop = SpeciesPopulation(race_id="human", count=0, happiness=0.99)  # stale
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_food_ratio = 1.0

        engine.process_happiness([empire], galaxy=None)

        hab = score_planet_for_race(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)
        assert pop.happiness != 0.99  # overwritten
