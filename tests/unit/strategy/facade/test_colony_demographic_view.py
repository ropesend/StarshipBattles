"""PROJ-288 Phase 3: ColonyDemographicView + facade accessor tests.

`StrategySessionFacade.get_colony_demographic_view(planet_id)` returns a
single frozen DTO that bundles everything a colony-demographics UI needs
in one read:

  * Per-species lines: race_id, race_name, count, habitability, happiness,
    growth_rate, food_ratio, food_allocation. Ordered largest count first.
  * Per-resource lines: a tuple of `ResourceProjection` from the projector.
  * `total_upkeep` dict — sum of per-species upkeep across the colony,
    used by Treasury / empire-aggregation panels (PROJ-290).

The facade short-circuits to `None` for unowned or missing planets.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _earth(*, planet_id=42, owner_id=1, populations=None,
           species_configs=None, deposits=None, facilities=None,
           construction_queue=None) -> Planet:
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
        id=planet_id,
        owner_id=owner_id,
        populations=populations or [],
        species_configs=species_configs or {},
        deposits=deposits or {},
        facilities=facilities or [],
        construction_queue=construction_queue or [],
    )


def _race(race_id: str, name: str = "") -> RaceConfig:
    return RaceConfig(
        race_id=race_id,
        name=name or race_id.capitalize(),
        race_name=name or race_id.capitalize(),
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


class _StubRegistry:
    def __init__(self, races: dict):
        self._races = races

    def get_race(self, race_id):
        return self._races.get(race_id)


def _facade_for(planet: Planet, *, race_registry, economy: EconomyConfig):
    """Build a StrategySessionFacade with a minimal session that resolves
    only what the colony-demographics path needs."""
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade

    session = MagicMock()
    session.galaxy.systems.values.return_value = []  # planet_index built lazily
    session.registries = MagicMock()
    session.registries.components.get = MagicMock(return_value=None)

    facade = StrategySessionFacade(session)
    # Pre-seed the planet index so `_get_planet_by_id` resolves without
    # depending on the galaxy/system structure.
    facade._planet_index = {planet.id: planet}
    # Pin the facade's race_registry accessor to our stub so the projector
    # + DTO builder both see it without going through CachedRaceRegistry.
    facade._race_registry = race_registry
    # Attach the economy on the facade so the new method can reach it.
    # (Implementation may pull from the session's economy_config — set both.)
    facade._economy_config = economy
    session.economy_config = economy
    return facade


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUnownedReturnsNone:
    def test_uncolonized_planet_returns_none(self):
        planet = _earth(planet_id=1, owner_id=None, populations=[])
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({}),
                             economy=EconomyConfig(population_consumption={}))

        assert facade.economy.colony_demographic_view(1) is None

    def test_missing_planet_returns_none(self):
        # No planet seeded into the index.
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        session = MagicMock()
        session.galaxy.systems.values.return_value = []
        facade = StrategySessionFacade(session)
        facade._planet_index = {}

        assert facade.economy.colony_demographic_view(999) is None


class TestColonizedReturnsView:
    def test_view_has_planet_id_and_name(self):
        planet = _earth(
            planet_id=42,
            owner_id=1,
            populations=[SpeciesPopulation(race_id="human", count=100)],
            species_configs={"human": ColonySpeciesConfig()},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        assert view is not None
        assert view.planet_id == 42
        assert view.planet_name == "Earth"

    def test_species_ordered_largest_first(self):
        planet = _earth(
            populations=[
                SpeciesPopulation(race_id="small", count=50),
                SpeciesPopulation(race_id="big", count=2000),
                SpeciesPopulation(race_id="medium", count=300),
            ],
            species_configs={
                "small": ColonySpeciesConfig(),
                "big": ColonySpeciesConfig(),
                "medium": ColonySpeciesConfig(),
            },
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({
                                 "small": _race("small"),
                                 "big": _race("big"),
                                 "medium": _race("medium"),
                             }),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        race_ids = [s.race_id for s in view.species]
        assert race_ids == ["big", "medium", "small"]

    def test_species_view_has_all_fields_populated(self):
        cfg = ColonySpeciesConfig(food_allocation=0.8)
        cfg.last_consumption_ratios = {"organics": 0.5}
        pop = SpeciesPopulation(race_id="human", count=500, happiness=0.7)
        planet = _earth(populations=[pop], species_configs={"human": cfg})
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human", name="Humans")}),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        assert len(view.species) == 1
        s = view.species[0]
        assert s.race_id == "human"
        assert s.race_name == "Humans"
        assert s.count == 500
        assert 0.0 <= s.habitability <= 1.0
        assert s.happiness == 0.7
        assert s.food_ratio == pytest.approx(0.5)
        assert s.food_allocation == pytest.approx(0.8)
        # growth_rate has the right SIGN — partial food + happiness < 1 is
        # ambiguous, so just sanity-check it is a float in a sane range.
        assert isinstance(s.growth_rate, float)
        assert -1.0 < s.growth_rate < 1.0

    def test_species_with_unknown_race_skipped(self):
        """Save drift / typo: a SpeciesPopulation references a race_id the
        registry can't resolve. The DTO must skip it rather than crash."""
        planet = _earth(
            populations=[
                SpeciesPopulation(race_id="human", count=100),
                SpeciesPopulation(race_id="ghost_race", count=50),
            ],
            species_configs={
                "human": ColonySpeciesConfig(),
                "ghost_race": ColonySpeciesConfig(),
            },
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        race_ids = [s.race_id for s in view.species]
        assert "human" in race_ids
        assert "ghost_race" not in race_ids


class TestFoodSurplusOnDTO:
    """FEAT-19: SpeciesDemographicView carries `food_surplus` (unbounded)
    AND `food_surplus_bonus` (pre-computed per the EconomyConfig
    coefficients). UI consumes both directly so the formatter never
    re-derives the math."""

    def test_default_allocation_one_yields_surplus_one_no_bonus(self):
        """allocation=1.0, full supply → surplus=1.0, bonus=0.0."""
        cfg = ColonySpeciesConfig(food_allocation=1.0)
        cfg.last_consumption_ratios = {"organics": 1.0}
        planet = _earth(
            populations=[SpeciesPopulation(race_id="human", count=100)],
            species_configs={"human": cfg},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(
                                 population_consumption={"organics": 0.001},
                                 surplus_food_bonus_per_x=0.20,
                                 surplus_food_bonus_cap=0.20,
                             ))

        view = facade.economy.colony_demographic_view(42)
        s = view.species[0]

        assert s.food_surplus == pytest.approx(1.0)
        assert s.food_surplus_bonus == pytest.approx(0.0)

    def test_allocation_one_thirty_five_yields_partial_bonus(self):
        """FEAT-19 repro: allocation=1.35 + full supply → surplus=1.35,
        bonus = min(0.20, 0.20 × 0.35) = 0.07."""
        cfg = ColonySpeciesConfig(food_allocation=1.35)
        cfg.last_consumption_ratios = {"organics": 1.0}
        planet = _earth(
            populations=[SpeciesPopulation(race_id="human", count=100)],
            species_configs={"human": cfg},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(
                                 population_consumption={"organics": 0.001},
                                 surplus_food_bonus_per_x=0.20,
                                 surplus_food_bonus_cap=0.20,
                             ))

        view = facade.economy.colony_demographic_view(42)
        s = view.species[0]

        assert s.food_surplus == pytest.approx(1.35)
        assert s.food_surplus_bonus == pytest.approx(0.07)

    def test_allocation_two_hits_cap(self):
        """allocation=2.0 → surplus=2.0, raw bonus 0.20 = cap → 0.20."""
        cfg = ColonySpeciesConfig(food_allocation=2.0)
        cfg.last_consumption_ratios = {"organics": 1.0}
        planet = _earth(
            populations=[SpeciesPopulation(race_id="human", count=100)],
            species_configs={"human": cfg},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(
                                 population_consumption={"organics": 0.001},
                                 surplus_food_bonus_per_x=0.20,
                                 surplus_food_bonus_cap=0.20,
                             ))

        view = facade.economy.colony_demographic_view(42)
        s = view.species[0]

        assert s.food_surplus == pytest.approx(2.0)
        assert s.food_surplus_bonus == pytest.approx(0.20)


class TestResourceProjections:
    def test_projections_include_consumption_resources(self):
        cfg = ColonySpeciesConfig(food_allocation=1.0)
        planet = _earth(
            populations=[SpeciesPopulation(race_id="human", count=1000)],
            species_configs={"human": cfg},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(population_consumption={
                                 "organics": 0.001,
                                 "vapors": 0.0005,
                             }))

        view = facade.economy.colony_demographic_view(42)

        rids = {p.resource_id for p in view.resource_projections}
        assert "organics" in rids
        assert "vapors" in rids

    def test_total_upkeep_sums_across_species(self):
        cfg_a = ColonySpeciesConfig(food_allocation=1.0)
        cfg_b = ColonySpeciesConfig(food_allocation=0.5)
        planet = _earth(
            populations=[
                SpeciesPopulation(race_id="human", count=1000),
                SpeciesPopulation(race_id="voidari", count=500),
            ],
            species_configs={"human": cfg_a, "voidari": cfg_b},
        )
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({
                                 "human": _race("human"),
                                 "voidari": _race("voidari"),
                             }),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        # human: 1000 * 1.0 * 0.001 = 1.0
        # voidari: 500 * 0.5 * 0.001 = 0.25
        # total: 1.25
        assert view.total_upkeep["organics"] == pytest.approx(1.25)


class TestFrozenness:
    def test_view_is_frozen_dataclass(self):
        from game.strategy.facade.dto.colony_demographic_view import (
            ColonyDemographicView,
        )
        planet = _earth(populations=[SpeciesPopulation(race_id="human", count=100)],
                        species_configs={"human": ColonySpeciesConfig()})
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
            view.planet_id = 999  # type: ignore[misc]

    def test_species_view_is_frozen_dataclass(self):
        planet = _earth(populations=[SpeciesPopulation(race_id="human", count=100)],
                        species_configs={"human": ColonySpeciesConfig()})
        facade = _facade_for(planet,
                             race_registry=_StubRegistry({"human": _race("human")}),
                             economy=EconomyConfig(population_consumption={"organics": 0.001}))

        view = facade.economy.colony_demographic_view(42)

        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
            view.species[0].count = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PROJ-292 m4 + m5: DTO invariants enforced in __post_init__
# ---------------------------------------------------------------------------

class TestTotalUpkeepReadOnly:
    """PROJ-292 m4: `total_upkeep` must be a read-only Mapping. Even
    though the DTO is frozen, callers could previously mutate the
    underlying dict — wrap in MappingProxyType in __post_init__."""

    def test_total_upkeep_rejects_item_assignment(self):
        from game.strategy.facade.dto.colony_demographic_view import (
            ColonyDemographicView,
        )
        view = ColonyDemographicView(
            planet_id=1,
            planet_name="Earth",
            species=(),
            resource_projections=(),
            total_upkeep={"organics": 5.0, "metals": 0.5},
        )
        with pytest.raises(TypeError):
            view.total_upkeep["organics"] = 999.0  # type: ignore[index]

    def test_total_upkeep_preserves_values(self):
        """Wrapping must preserve the original entries for consumers
        (read-only doesn't mean empty)."""
        from game.strategy.facade.dto.colony_demographic_view import (
            ColonyDemographicView,
        )
        view = ColonyDemographicView(
            planet_id=1,
            planet_name="Earth",
            species=(),
            resource_projections=(),
            total_upkeep={"organics": 5.0, "metals": 0.5},
        )
        assert view.total_upkeep["organics"] == 5.0
        assert view.total_upkeep["metals"] == 0.5


class TestSpeciesSortedInDTOConstructor:
    """PROJ-292 m5: the DTO must enforce largest-count-first ordering
    regardless of the caller's input order. Previously relied on facade
    pre-sort — now the DTO's __post_init__ guarantees it."""

    def test_species_sorted_largest_first_when_constructed_ascending(self):
        from game.strategy.facade.dto.colony_demographic_view import (
            ColonyDemographicView,
            SpeciesDemographicView,
        )

        def _sv(race_id: str, count: int) -> SpeciesDemographicView:
            return SpeciesDemographicView(
                race_id=race_id,
                race_name=race_id.title(),
                count=count,
                habitability=1.0,
                happiness=0.5,
                growth_rate=0.01,
                food_ratio=1.0,
                food_allocation=1.0,
                food_surplus=1.0,
                food_surplus_bonus=0.0,
            )

        # Caller passes in ASCENDING order; DTO must re-sort.
        species_ascending = (
            _sv("small", 100),
            _sv("medium", 500),
            _sv("big", 10_000),
        )
        view = ColonyDemographicView(
            planet_id=1,
            planet_name="Earth",
            species=species_ascending,
            resource_projections=(),
            total_upkeep={},
        )
        assert [s.race_id for s in view.species] == ["big", "medium", "small"]

    def test_species_sort_is_stable_on_equal_counts(self):
        from game.strategy.facade.dto.colony_demographic_view import (
            ColonyDemographicView,
            SpeciesDemographicView,
        )

        def _sv(race_id: str, count: int) -> SpeciesDemographicView:
            return SpeciesDemographicView(
                race_id=race_id,
                race_name=race_id.title(),
                count=count,
                habitability=1.0,
                happiness=0.5,
                growth_rate=0.01,
                food_ratio=1.0,
                food_allocation=1.0,
                food_surplus=1.0,
                food_surplus_bonus=0.0,
            )

        # Two species with equal counts; their relative order should be
        # preserved by Python's stable sort.
        view = ColonyDemographicView(
            planet_id=1,
            planet_name="Earth",
            species=(_sv("alpha", 500), _sv("beta", 500), _sv("big", 1000)),
            resource_projections=(),
            total_upkeep={},
        )
        assert [s.race_id for s in view.species] == ["big", "alpha", "beta"]
