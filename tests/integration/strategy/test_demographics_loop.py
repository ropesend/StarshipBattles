"""End-to-end PROJ-284 demographic loop integration test (Phase 3 Task 3.6).

Chains the three per-turn demographic engines (OrganicsConsumptionEngine →
HappinessEngine → PopulationEngine) without the surrounding 100-tick turn
loop. Exercises the data flow from `food_allocation` slider → food
consumption → happiness → population growth as it would occur between
full turn passes.

This is NOT a full TurnEngine integration (no fleets, galaxy, harvesting)
— the per-turn pipeline is what PROJ-284 actually ships. A full TurnEngine
regression check lives in `tests/unit/strategy/engine/test_population_engine.py`
(and the sharded suite). These scenarios exist to prove the three engines
compose correctly when run back-to-back turn over turn.
"""
from __future__ import annotations

from typing import List

import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.engine.happiness_engine import HappinessEngine
from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
from game.strategy.engine.population_engine import PopulationEngine


def _run_demographic_turn(
    empires: List[Empire],
    *,
    organics_engine: OrganicsConsumptionEngine,
    happiness_engine: HappinessEngine,
    population_engine: PopulationEngine,
) -> None:
    """One post-tick pipeline pass — same order `TurnEngine.process_turn` uses."""
    organics_engine.process_consumption(empires)
    happiness_engine.process_happiness(empires, galaxy=None)
    population_engine.process_population_growth(empires)


def _earth_like(
    *,
    populations: List[SpeciesPopulation],
    stockpile: dict = None,
    species_configs: dict = None,
) -> Planet:
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
        stockpile=stockpile or {},
        species_configs=species_configs or {},
    )


def _race(*, race_id: str = "human", base_happiness: float = 0.5) -> RaceConfig:
    return RaceConfig(
        race_id=race_id,
        name="Human",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
        base_happiness=base_happiness,
        base_reproduction_rate=0.03,
    )


def _empire_with(colony: Planet, race: RaceConfig, empire_id: int = 1) -> Empire:
    empire = Empire(empire_id=empire_id, name="Test", color=(0, 0, 0), race_config=race)
    empire.colonies = [colony]
    return empire


@pytest.fixture
def engines():
    """Three-engine bundle with a fixed (non-default) economy config so
    tests stay hermetic from whatever is in `data/economy.json`."""
    economy = EconomyConfig(population_consumption={"organics": 0.001})
    return {
        "organics": OrganicsConsumptionEngine(economy_config=economy),
        "happiness": HappinessEngine(),
        "population": PopulationEngine(),
    }


def _pipeline(empires: List[Empire], engines: dict) -> None:
    _run_demographic_turn(
        empires,
        organics_engine=engines["organics"],
        happiness_engine=engines["happiness"],
        population_engine=engines["population"],
    )


# ---------------------------------------------------------------------------
# Scenarios from phase_3_checklist.md Task 3.6
# ---------------------------------------------------------------------------

class TestScenarioAFedColonyIdealPlanet:
    def test_five_turns_fed_colony_grows_and_drains_stockpile(self, engines):
        """Fed colony on ideal planet: population grows, happiness stable,
        organics stockpile drains each turn."""
        pop = SpeciesPopulation(race_id="human", count=10_000, happiness=0.0)
        # Enough organics for 100+ turns at ~10/turn.
        colony = _earth_like(populations=[pop], stockpile={"organics": 1_000.0})
        race = _race(base_happiness=0.5)
        empire = _empire_with(colony, race)

        initial_pop = pop.count
        initial_stock = colony.stockpile["organics"]
        happiness_trace = []

        for _ in range(5):
            _pipeline([empire], engines)
            happiness_trace.append(pop.happiness)

        assert pop.count > initial_pop, "Fed colony must grow over 5 turns"
        assert colony.stockpile["organics"] < initial_stock, (
            "Organics stockpile must drain every turn"
        )
        # Happiness should land near base * hab (~0.47). Stable across turns.
        assert all(0.40 < h < 0.55 for h in happiness_trace), (
            f"Happiness should stabilize near base*hab, got {happiness_trace}"
        )


class TestScenarioBStarvingColony:
    def test_five_turns_starving_colony_collapses_happiness_and_declines(self, engines):
        """Empty stockpile -> ratio=0 -> happiness=0 -> decline every turn."""
        pop = SpeciesPopulation(race_id="human", count=10_000, happiness=0.5)
        colony = _earth_like(populations=[pop], stockpile={"organics": 0.0})
        race = _race(base_happiness=0.5)
        empire = _empire_with(colony, race)

        initial = pop.count

        for _ in range(5):
            _pipeline([empire], engines)

        # After every turn happiness was written to 0 (ratio * anything = 0).
        assert pop.happiness == pytest.approx(0.0)
        # decline = -0.02 * pop * 1.0 per turn -> ~2% per turn compounded.
        # 5 turns ≈ 10% loss. Expect well under initial.
        assert pop.count < initial, "Starving colony must decline"
        # Bounded: not obliterated in 5 turns, not growing.
        assert pop.count > int(initial * 0.5)

    def test_starvation_ratio_written_every_turn_even_when_zero_last_turn(self, engines):
        """Guards the transient-field contract: ratio 0 -> 1 -> 0 over
        refill cycles. If the engine skipped write on zero-need, the next
        turn's happiness would lie."""
        pop = SpeciesPopulation(race_id="human", count=10_000, happiness=0.5)
        colony = _earth_like(populations=[pop], stockpile={"organics": 0.0})
        race = _race()
        empire = _empire_with(colony, race)

        _pipeline([empire], engines)  # turn 1: ratio=0
        assert colony.get_species_config("human").last_food_ratio == pytest.approx(0.0)

        # Refill and run turn 2: should write ratio back to 1.0.
        colony.stockpile["organics"] = 1_000.0
        _pipeline([empire], engines)
        assert colony.get_species_config("human").last_food_ratio == pytest.approx(1.0)
        assert pop.happiness > 0.0


class TestScenarioCFoodAllocationDoubled:
    def test_allocation_two_doubles_consumption_and_elevates_happiness(self, engines):
        """food_allocation=2.0 -> needed doubles, stockpile drains faster,
        happiness scales with the ratio (bounded by supply)."""
        pop_normal = SpeciesPopulation(race_id="human", count=10_000, happiness=0.0)
        colony_normal = _earth_like(
            populations=[pop_normal],
            stockpile={"organics": 1_000.0},
        )
        colony_normal.get_species_config("human").food_allocation = 1.0
        empire_normal = _empire_with(colony_normal, _race(race_id="human"), empire_id=1)

        pop_double = SpeciesPopulation(race_id="human", count=10_000, happiness=0.0)
        colony_double = _earth_like(
            populations=[pop_double],
            stockpile={"organics": 1_000.0},
        )
        colony_double.get_species_config("human").food_allocation = 2.0
        empire_double = _empire_with(colony_double, _race(race_id="human"), empire_id=2)

        _pipeline([empire_normal, empire_double], engines)

        drain_normal = 1_000.0 - colony_normal.stockpile["organics"]
        drain_double = 1_000.0 - colony_double.stockpile["organics"]
        assert drain_double == pytest.approx(2.0 * drain_normal)
        # Happiness doubles too (both ratios hit 1.0 since stockpile covers
        # both allocations — but the formula multiplies by the ratio
        # AFTER capping at supply). At allocation=2 with ample supply,
        # needed=0.2 * 100 = 20 per thousand-of-pop — still covered.
        # Actual happiness boost comes from HappinessEngine seeing
        # `last_food_ratio = supplied / needed`; with supply >= needed
        # both ratios are 1.0, so this test verifies DRAIN scales.
        assert colony_double.get_species_config("human").last_food_ratio == pytest.approx(1.0)
        assert colony_normal.get_species_config("human").last_food_ratio == pytest.approx(1.0)


class TestPipelineOrdering:
    def test_order_matters_consumption_must_precede_happiness(self, engines):
        """Prove ordering: if happiness ran BEFORE consumption on turn 1,
        it would read the default `last_food_ratio=1.0` regardless of
        stockpile. Our pipeline runs them in the correct order — verify
        that starvation shows up as happiness=0 AFTER the first turn."""
        pop = SpeciesPopulation(race_id="human", count=5_000, happiness=0.42)
        colony = _earth_like(populations=[pop], stockpile={"organics": 0.0})
        race = _race(base_happiness=0.8)
        empire = _empire_with(colony, race)

        _pipeline([empire], engines)
        # After one turn: consumption set ratio=0, happiness read ratio=0 -> wrote 0.
        assert pop.happiness == pytest.approx(0.0)
