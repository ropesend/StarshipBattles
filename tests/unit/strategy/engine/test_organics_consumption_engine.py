"""Unit tests for `OrganicsConsumptionEngine` (PROJ-284 Phase 2 Task 2.5
+ PROJ-286 Phase 3).

The engine runs once per turn AFTER the 100-tick loop, BEFORE
`PopulationEngine.process_population_growth`. For each colony and each
species on it, it:
    1. Looks up / lazy-creates `ColonySpeciesConfig` via
       `planet.get_species_config(race_id)`.
    2. Clears `cfg.last_consumption_ratios` (overwrite, never append).
    3. For each `(resource_id, per_pop_rate)` in
       `EconomyConfig.population_consumption.items()`:
        a. `needed = pop.count * cfg.food_allocation * per_pop_rate`
        b. Drains `min(needed, available)` from `planet.stockpile[resource_id]`.
        c. Writes `cfg.last_consumption_ratios[resource_id] = supplied / needed`
           (or 1.0 if needed == 0).

Downstream `HappinessEngine` + `PopulationEngine` read
`cfg.last_food_ratio` which returns `min(last_consumption_ratios.values())`
— the colony is "as well-fed as its worst-supplied resource" (Liebig).

PROJ-284 tests here use a single-resource `{"organics": 0.001}` config
via the `default_engine` fixture so that existing assertions on a single
stockpile drain + ratio keep their semantics. PROJ-286 adds the
`TestMultiResourceConsumption` block for the 3-resource path.
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
        _stockpile=stockpile,
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
    """Single-resource (organics-only) engine preserving PROJ-284 test
    semantics. PROJ-286 tests that need the 3-resource shape use the
    `three_resource_engine` fixture instead."""
    from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
    cfg = EconomyConfig(population_consumption={"organics": 0.001})
    return OrganicsConsumptionEngine(economy_config=cfg)


@pytest.fixture
def three_resource_engine():
    """PROJ-286: the shipped `data/economy.json` declares three
    resources. This fixture wires the same values explicitly so tests
    assert against a stable baseline independent of future tuning."""
    from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
    cfg = EconomyConfig(population_consumption={
        "organics": 0.001,
        "metals": 0.0001,
        "radioactives": 0.00001,
    })
    return OrganicsConsumptionEngine(economy_config=cfg)


# ---------------------------------------------------------------------------
# PROJ-284 scenarios — preserved under single-resource fixture
# ---------------------------------------------------------------------------

class TestOrganicsConsumptionFullSupply:
    def test_full_supply_ratio_is_one_and_stockpile_drained_by_need(self, default_engine):
        """1000 stockpile, 100 pop, allocation 1.0, food_per_pop 0.001
        -> needed=0.1, supplied=0.1, ratio=1.0, _stockpile=999.9."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 1000.0})
        empire = _Empire([colony])

        default_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(999.9)


class TestOrganicsConsumptionPartialSupply:
    def test_half_supply_ratio_is_half_and_stockpile_fully_drained(self, default_engine):
        """0.05 stockpile, 100 pop -> needed=0.1, supplied=0.05, ratio=0.5, _stockpile=0."""
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
        don't see a stale ratio from a previous turn."""
        pop = SpeciesPopulation(race_id="human", count=0, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"organics": 100.0})
        empire = _Empire([colony])

        # Poison the cached ratios to prove the engine overwrites them.
        cfg = colony.get_species_config("human")
        cfg.last_consumption_ratios = {"organics": 0.0, "stale_key": 0.0}

        default_engine.process_consumption([empire])

        assert cfg.last_food_ratio == pytest.approx(1.0)
        assert colony.stockpile["organics"] == pytest.approx(100.0)  # untouched
        # Stale key from before the turn is gone — engine clears every turn.
        assert "stale_key" not in cfg.last_consumption_ratios

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
        """Swap the upkeep dict to `metals` via DI; engine must drain
        metals, NOT organics. This is the whole point of data-driven
        economy config — modders edit JSON, no code change needed."""
        from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
        custom_cfg = EconomyConfig(population_consumption={"metals": 0.001})
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
        allocation and any remaining supply after earlier species ate."""
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
        from game.strategy.config.economy_config import set_default_economy_config
        from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine

        injected = EconomyConfig(population_consumption={"metals": 0.01})
        set_default_economy_config(injected)

        engine = OrganicsConsumptionEngine()

        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={"metals": 1000.0})
        empire = _Empire([colony])

        engine.process_consumption([empire])

        assert colony.stockpile["metals"] == pytest.approx(999.0)  # 100 * 0.01 = 1.0 drained


# ---------------------------------------------------------------------------
# PROJ-286 scenarios — multi-resource consumption
# ---------------------------------------------------------------------------

class TestMultiResourceConsumption:
    """The real PROJ-286 shape: population drains every resource declared
    in `EconomyConfig.population_consumption` per turn."""

    def test_three_resource_config_drains_all_three_per_turn(self, three_resource_engine):
        """Stockpile preseeded with all three — each drained by
        `pop * allocation * per_pop_rate`, each per-resource ratio is
        1.0, aggregate `last_food_ratio` is 1.0."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={
            "organics": 100.0,
            "metals": 100.0,
            "radioactives": 100.0,
        })
        empire = _Empire([colony])

        three_resource_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        # 100 pop * 1.0 allocation * rate
        assert colony.stockpile["organics"] == pytest.approx(100.0 - 100 * 0.001)
        assert colony.stockpile["metals"] == pytest.approx(100.0 - 100 * 0.0001)
        assert colony.stockpile["radioactives"] == pytest.approx(100.0 - 100 * 0.00001)
        assert cfg.last_consumption_ratios == {
            "organics": pytest.approx(1.0),
            "metals": pytest.approx(1.0),
            "radioactives": pytest.approx(1.0),
        }
        assert cfg.last_food_ratio == pytest.approx(1.0)

    def test_one_resource_missing_drops_aggregate_to_zero(self, three_resource_engine):
        """Organics + radioactives fully supplied, metals stockpile
        absent → metals ratio = 0, aggregate via MIN = 0. Species is
        starving even though two of three resources are full."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={
            "organics": 100.0,
            "radioactives": 100.0,
            # metals missing
        })
        empire = _Empire([colony])

        three_resource_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_consumption_ratios["organics"] == pytest.approx(1.0)
        assert cfg.last_consumption_ratios["metals"] == pytest.approx(0.0)
        assert cfg.last_consumption_ratios["radioactives"] == pytest.approx(1.0)
        assert cfg.last_food_ratio == pytest.approx(0.0)

    def test_last_consumption_ratios_overwritten_every_turn(self, three_resource_engine):
        """Bogus pre-seeded keys from an earlier config are removed; the
        dict reflects ONLY the current `economy.population_consumption`."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={
            "organics": 100.0,
            "metals": 100.0,
            "radioactives": 100.0,
        })
        cfg = colony.get_species_config("human")
        # Stale keys from a previous different config.
        cfg.last_consumption_ratios = {"food_paste": 0.5, "water": 0.2}
        empire = _Empire([colony])

        three_resource_engine.process_consumption([empire])

        assert set(cfg.last_consumption_ratios.keys()) == {"organics", "metals", "radioactives"}
        assert "food_paste" not in cfg.last_consumption_ratios
        assert "water" not in cfg.last_consumption_ratios

    def test_zero_population_writes_one_per_declared_resource(self, three_resource_engine):
        """Zero pop → needed=0 for each resource → each per-resource
        ratio = 1.0 → aggregate 1.0. `last_consumption_ratios` still has
        an entry for every declared resource so the dict isn't empty
        (MIN over non-empty dict of 1.0 values = 1.0)."""
        pop = SpeciesPopulation(race_id="human", count=0, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={
            "organics": 100.0,
            "metals": 100.0,
            "radioactives": 100.0,
        })
        empire = _Empire([colony])

        three_resource_engine.process_consumption([empire])

        cfg = colony.get_species_config("human")
        assert cfg.last_consumption_ratios == {
            "organics": 1.0, "metals": 1.0, "radioactives": 1.0,
        }
        assert cfg.last_food_ratio == pytest.approx(1.0)
        # Stockpiles untouched.
        assert colony.stockpile["organics"] == pytest.approx(100.0)
        assert colony.stockpile["metals"] == pytest.approx(100.0)
        assert colony.stockpile["radioactives"] == pytest.approx(100.0)

    def test_zero_allocation_writes_one_per_declared_resource(self, three_resource_engine):
        """Same as zero-pop: allocation=0 makes needed=0 for every
        resource → every per-resource ratio = 1.0."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        colony = _colony(populations=[pop], stockpile={
            "organics": 100.0,
            "metals": 100.0,
            "radioactives": 100.0,
        })
        cfg = colony.get_species_config("human")
        cfg.food_allocation = 0.0
        empire = _Empire([colony])

        three_resource_engine.process_consumption([empire])

        assert cfg.last_consumption_ratios == {
            "organics": 1.0, "metals": 1.0, "radioactives": 1.0,
        }
        assert cfg.last_food_ratio == pytest.approx(1.0)
