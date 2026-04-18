"""Unit tests for `OrganicsConsumptionEngine` (PROJ-284 Phase 2 Task 2.5).

The engine runs once per turn AFTER the 100-tick loop, BEFORE
`PopulationEngine.process_population_growth`. For each colony and each
species on it, it:
    1. Looks up / lazy-creates `ColonySpeciesConfig` via
       `planet.get_species_config(race_id)`.
    2. Computes `needed = pop.count * cfg.food_allocation * food_per_pop_per_turn`.
    3. Drains `min(needed, available)` from `planet.stockpile[food_resource]`.
    4. Writes `cfg.last_food_ratio = supplied / needed` (or 1.0 if needed == 0).

The food resource id is sourced from `EconomyConfig.population_food_resource`
so modders can swap "organics" for any planetary resource in JSON.
"""
from __future__ import annotations

from typing import List

import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _colony(
    *,
    populations: List[SpeciesPopulation],
    stockpile: dict,
    name: str = "Test",
) -> Planet:
    """Minimal Planet with the fields the consumption engine touches."""
    return Planet(
        name=name,
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
        populations=populations,
        stockpile=stockpile,
    )


class _Empire:
    """Bare-minimum Empire duck-type — the engine only reads `colonies`."""
    def __init__(self, colonies: List[Planet]):
        self.colonies = colonies


@pytest.fixture(autouse=True)
def _reset_default_economy_config():
    """Prevent global-config bleed-through between tests."""
    from game.strategy.config import economy_config as mod
    mod.set_default_economy_config(None)
    yield
    mod.set_default_economy_config(None)


@pytest.fixture
def default_engine():
    """Engine reading from the shipped `data/economy.json` defaults."""
    from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
    return OrganicsConsumptionEngine()


# ---------------------------------------------------------------------------
# Scenarios from PROJ-284 phase_2_checklist.md Task 2.5
# ---------------------------------------------------------------------------

class TestOrganicsConsumptionFullSupply:
    def test_full_supply_ratio_is_one_and_stockpile_drained_by_need(self, default_engine):
        """1000 stockpile, 100 pop, allocation 1.0, food_per_pop 0.001
        -> needed=0.1, supplied=0.1, ratio=1.0, stockpile=999.9."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 1000.0})
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(999.9)


class TestOrganicsConsumptionPartialSupply:
    def test_half_supply_ratio_is_half_and_stockpile_fully_drained(self, default_engine):
        """0.05 stockpile, 100 pop -> needed=0.1, supplied=0.05, ratio=0.5, stockpile=0."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 0.05})
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(0.5)
        assert colony.stockpile["organics"] == pytest.approx(0.0)


class TestOrganicsConsumptionEmptyStockpile:
    def test_empty_stockpile_gives_zero_ratio(self, default_engine):
        """Starvation: stockpile 0 -> ratio=0.0 (HappinessEngine reads this)."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 0.0})
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(0.0)
        assert colony.stockpile["organics"] == pytest.approx(0.0)

    def test_missing_resource_key_treated_as_zero(self, default_engine):
        """If `stockpile` dict doesn't even have the food key, treat as 0."""
        pop = SpeciesPopulation(race_id="human", count=50, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={})  # no organics key
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(0.0)


class TestOrganicsConsumptionZeroPopulationEdgeCase:
    def test_zero_population_writes_ratio_one(self, default_engine):
        """Zero-pop edge case: `needed == 0`. Engine explicitly writes
        1.0 so downstream readers (HappinessEngine, PopulationEngine)
        don't see a stale ratio from a previous turn or the
        constructor default."""
        pop = SpeciesPopulation(race_id="human", count=0, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 100.0})
        empire = _Empire([colony])

        # Poison the cached ratio to prove the engine overwrites it.
        cfg = colony.get_species_config("human")
        cfg.last_food_ratio = 0.0
        cfg.last_food_ratio = 0.0

        default_engine.process_consumption([empire])

        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(100.0)  # untouched

    def test_zero_food_allocation_writes_ratio_one(self, default_engine):
        """allocation=0.0 (player starves this species) -> needed=0 ->
        ratio=1.0 (no demand unmet), stockpile untouched."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 100.0})
        # Pre-create config with allocation=0
        cfg = colony.get_species_config("human")
        cfg.food_allocation = 0.0
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(100.0)


class TestOrganicsConsumptionSliderScaling:
    def test_doubled_allocation_doubles_consumption(self, default_engine):
        """allocation=2.0, pop=100 -> needed=0.2 (confirms slider scales
        demand linearly)."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 1000.0})
        cfg = colony.get_species_config("human")
        cfg.food_allocation = 2.0
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(999.8)

    def test_over_allocation_beyond_stockpile_caps_at_available(self, default_engine):
        """allocation=5.0 on a stockpile that can only feed allocation=1.0
        -> supplied = available, ratio = 1/5 = 0.2."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 0.1})
        cfg = colony.get_species_config("human")
        cfg.food_allocation = 5.0
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        assert cfg.last_food_ratio == pytest.approx(0.2)
        assert colony.stockpile["organics"] == pytest.approx(0.0)


class TestOrganicsConsumptionDataDrivenFoodResource:
    def test_injected_custom_economy_config_drains_alternate_resource(self):
        """Swap the food resource to `metals` via DI; engine must drain
        metals, NOT organics. This is the whole point of data-driven
        economy config — modders edit JSON, no code change needed."""
        from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
        custom_cfg = EconomyConfig(
            population_food_resource="metals",
            food_per_pop_per_turn=0.001,
        )
        engine = OrganicsConsumptionEngine(economy_config=custom_cfg)

        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"metals": 1000.0, "organics": 500.0})
        empire = _Empire([colony])

        engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["metals"] == pytest.approx(999.9)
        # Organics untouched — confirms the resource switch.
        assert colony.stockpile["organics"] == pytest.approx(500.0)


class TestOrganicsConsumptionMultipleSpecies:
    def test_multiple_species_have_independent_ratios(self, default_engine):
        """Two species sharing one colony stockpile consume in order;
        each species gets its own `last_food_ratio` reflecting its own
        allocation and any remaining supply after earlier species ate.
        Here `humans` eat first fully; `voidari` face a depleted
        stockpile."""
        human_pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        voidari_pop = SpeciesPopulation(race_id="voidari", count=100, happiness=0.5)
        # Enough for humans (0.1 needed) but only 0.05 left after
        # -> voidari need 0.1 but get 0.05 -> ratio=0.5.
        colony = _colony(
            populations=[human_pop, voidari_pop],
            stockpile={"organics": 0.15},
        )
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        assert colony.get_species_config("human").last_food_ratio == pytest.approx(1.0)
        assert colony.get_species_config("voidari").last_food_ratio == pytest.approx(0.5)
        assert colony.stockpile["organics"] == pytest.approx(0.0)

    def test_multi_species_under_full_supply_all_get_ratio_one(self, default_engine):
        """When both species can be fully fed from the shared stockpile,
        both land at ratio=1.0 regardless of iteration order."""
        colony = _colony(
            populations=[
                SpeciesPopulation(race_id="human", count=100, happiness=0.5),
                SpeciesPopulation(race_id="voidari", count=50, happiness=0.5),
            ],
            stockpile={"organics": 1000.0},
        )
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        assert colony.get_species_config("human").last_food_ratio == pytest.approx(1.0)
        assert colony.get_species_config("voidari").last_food_ratio == pytest.approx(1.0)
        # 0.1 (human) + 0.05 (voidari) = 0.15 consumed.
        assert colony.stockpile["organics"] == pytest.approx(999.85)


class TestOrganicsConsumptionEngineDI:
    def test_default_engine_uses_default_economy_config(self):
        """Constructing without `economy_config` pulls from the module
        singleton (which lazy-loads `data/economy.json`)."""
        from game.strategy.config.economy_config import EconomyConfig, set_default_economy_config
        from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine

        injected = EconomyConfig(
            population_food_resource="metals",
            food_per_pop_per_turn=0.01,
        )
        set_default_economy_config(injected)

        engine = OrganicsConsumptionEngine()

        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"metals": 1000.0})
        empire = _Empire([colony])

        engine.process_consumption([empire])

        assert colony.stockpile["metals"] == pytest.approx(999.0)  # 100 * 0.01 = 1.0 drained
