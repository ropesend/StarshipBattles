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
from game.strategy.formulas.habitability import calculate_habitability


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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)

    def test_ideal_planet_food_ratio_two_amplifies_happiness(self, engine):
        """food_ratio=2 doubles the happiness signal for the same base.

        FEAT-19 note: ratio=2.0 with default allocation=1.0 yields
        `last_food_surplus = 1.0 * 2.0 = 2.0`, so the additive surplus
        bonus also triggers (capped at +0.20 per shipped defaults)."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_consumption_ratios = {"organics": 2.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        # base * ratio * hab + capped bonus = 0.5 * 2.0 * ~0.94 + 0.20.
        assert pop.happiness == pytest.approx(0.5 * 2.0 * hab + 0.20)


class TestHappinessHostilePlanet:
    def test_hostile_planet_drags_happiness_down(self, engine):
        """Low habitability drags happiness toward zero even on full food."""
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        planet = _hostile(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 0.0}

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(0.0)


class TestHappinessSurplusBonus:
    """FEAT-19: when `cfg.last_food_surplus > 1.0`, an additive bonus
    `min(cap, per_x × (surplus - 1.0))` is added before the [0, 3]
    clamp. Defaults: per_x=0.20, cap=0.20 (data-driven via EconomyConfig)."""

    def _make_engine(self, *, per_x: float = 0.20, cap: float = 0.20):
        """HappinessEngine wired with an explicit EconomyConfig so the
        bonus coefficients are pinned per-test instead of relying on the
        module-level default."""
        from game.strategy.config.economy_config import EconomyConfig
        from game.strategy.engine.happiness_engine import HappinessEngine
        cfg = EconomyConfig(
            population_consumption={"organics": 0.001},
            surplus_food_bonus_per_x=per_x,
            surplus_food_bonus_cap=cap,
        )
        return HappinessEngine(economy_config=cfg)

    def test_surplus_one_no_bonus(self):
        """allocation=1.0, ratio=1.0 → surplus=1.0 → no bonus, falls back
        to legacy formula `base × ratio × hab`."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 1.0
        cfg.last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)

    def test_surplus_partial_below_cap(self):
        """FEAT-19 QA-screenshot repro: allocation=1.35, ratio=1.0 →
        surplus=1.35, bonus = min(0.20, 0.20 × 0.35) = 0.07."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 1.35
        cfg.last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        expected = 0.5 * 1.0 * hab + 0.07
        assert pop.happiness == pytest.approx(expected)

    def test_surplus_at_cap(self):
        """allocation=2.0, ratio=1.0 → surplus=2.0, bonus = min(0.20, 0.20)
        = 0.20 (cap reached exactly)."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 2.0
        cfg.last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab + 0.20)

    def test_surplus_above_cap_clamps(self):
        """allocation=5.0 → surplus=5.0, raw bonus would be 0.80, but
        cap=0.20 caps it at 0.20."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 5.0
        cfg.last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab + 0.20)

    def test_starving_at_high_alloc_no_bonus(self):
        """allocation=2.0 but only 50% supply → surplus=1.0 → no bonus.
        Boundary case: surplus must be STRICTLY > 1.0 to trigger the
        bonus, otherwise an unmet-demand colony would silently get a
        boost it didn't earn."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 2.0
        cfg.last_consumption_ratios = {"organics": 0.5}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        # Base term uses last_food_ratio=0.5, no bonus added.
        assert pop.happiness == pytest.approx(0.5 * 0.5 * hab)

    def test_starving_well_below_one_no_bonus(self):
        """allocation=2.0, supply=25% → surplus=0.5 → no bonus, base
        happiness already reduced via last_food_ratio=0.25."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 2.0
        cfg.last_consumption_ratios = {"organics": 0.25}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 0.25 * hab)

    def test_multi_resource_min_drives_surplus(self):
        """allocation=2.0, organics=1.0 metals=0.6 → MIN ratio=0.6 →
        surplus = 2.0 × 0.6 = 1.2 → bonus = min(0.20, 0.20 × 0.2) = 0.04.
        Liebig's Law on the surplus side mirrors the base formula."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 2.0
        cfg.last_consumption_ratios = {"organics": 1.0, "metals": 0.6}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        # base × MIN ratio × hab + bonus(0.04)
        assert pop.happiness == pytest.approx(0.5 * 0.6 * hab + 0.04)

    def test_bonus_data_driven_via_economy_config(self):
        """Inject explicit `surplus_food_bonus_per_x=0.50` and
        `surplus_food_bonus_cap=0.30` — bonus must use injected coefs,
        not the defaults. Pins the data-driven contract."""
        engine = self._make_engine(per_x=0.50, cap=0.30)
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 1.4  # surplus = 1.4
        cfg.last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        # bonus = min(0.30, 0.50 × 0.4) = min(0.30, 0.20) = 0.20
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab + 0.20)

    def test_clamp_at_three_includes_bonus(self):
        """Bonus participates in the existing [0, 3] clamp — bonus does
        not bypass it. Use a surplus that pushes the pre-clamp sum past 3."""
        engine = self._make_engine()
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=1.0)
        empire = _empire(1, [planet], race)
        cfg = planet.get_species_config("human")
        cfg.food_allocation = 2.0  # surplus 2.0 → bonus 0.20
        # Manually push base term high — engine wouldn't normally write
        # ratio=10 but the property reads whatever the dict holds.
        cfg.last_consumption_ratios = {"organics": 10.0}

        engine.process_happiness([empire], galaxy=None)

        # base 1.0 × 10.0 × ~0.94 = 9.4, +0.20 = 9.6, clamped to 3.0.
        assert pop.happiness == pytest.approx(3.0)


class TestHappinessClamping:
    def test_over_supply_clamps_at_three(self, engine):
        """Silly over-supply (ratio=5, base=0.6, hab~1) * each term -> 3.0."""
        # 0.6 * 5.0 * ~0.94 = 2.82. Need to push higher for clamp test.
        # Use ratio=20.0 -> 0.6 * 20 * 0.94 = 11.28 -> clamped to 3.
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.6)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_consumption_ratios = {"organics": 20.0}

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
        planet.get_species_config("human").last_consumption_ratios = {"organics": -1.0}

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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("ghost").last_consumption_ratios = {"organics": 1.0}

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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}

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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("alien").last_consumption_ratios = {"organics": 0.25}

        def mock_resolver(race_id, empire_arg):
            return {"human": race_human, "alien": race_alien}.get(race_id)
        engine._get_race_config = mock_resolver

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race_human)
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
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 1.0 * hab)
        assert pop.happiness != 0.99  # overwritten


# ---------------------------------------------------------------------------
# PROJ-286 Phase 4: multi-resource behavior via the MIN-aggregation property
# ---------------------------------------------------------------------------

class TestMultiResourceStarvation:
    """PROJ-286: `cfg.last_food_ratio` is now MIN across declared
    resources. HappinessEngine + PopulationEngine source files were NOT
    touched — these tests pin that behavior through the computed property."""

    def test_one_starved_resource_collapses_happiness_to_zero(self, engine):
        """Full organics but no metals → aggregate ratio = 0 → happiness
        formula multiplies by 0 → happiness = 0 regardless of
        habitability or base_happiness."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.9)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_consumption_ratios = {
            "organics": 1.0, "metals": 0.0,
        }

        engine.process_happiness([empire], galaxy=None)

        assert pop.happiness == pytest.approx(0.0)

    def test_mixed_ratios_happiness_uses_minimum(self, engine):
        """`{organics: 0.5, metals: 0.8, radioactives: 1.0}` → min=0.5 →
        happiness = base * 0.5 * hab. Proves the property feeds the same
        formula HappinessEngine has always used — no engine rewrite."""
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet = _earth_like(populations=[pop])
        race = _race(base_happiness=0.5)
        empire = _empire(1, [planet], race)
        planet.get_species_config("human").last_consumption_ratios = {
            "organics": 0.5, "metals": 0.8, "radioactives": 1.0,
        }

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race)
        assert pop.happiness == pytest.approx(0.5 * 0.5 * hab)


class TestMultiResourceVsSingleResourceParity:
    """PROJ-286 parity contract: a single-resource ratio X and a
    multi-resource dict whose MIN is X must produce identical happiness.
    Pins the aggregation semantic so a future refactor (e.g. swapping
    MIN for WEIGHTED) doesn't silently break downstream formulas."""

    def test_single_resource_matches_multi_resource_with_same_minimum(self, engine):
        """`{organics: 0.4}` and `{organics: 0.9, metals: 0.4}` have the
        same MIN (0.4) so happiness must match bit-for-bit."""
        pop_single = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet_single = _earth_like(name="Single", populations=[pop_single])
        race = _race(base_happiness=0.5)
        empire_single = _empire(1, [planet_single], race)
        planet_single.get_species_config("human").last_consumption_ratios = {"organics": 0.4}

        pop_multi = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        planet_multi = _earth_like(name="Multi", populations=[pop_multi])
        empire_multi = _empire(2, [planet_multi], race)
        planet_multi.get_species_config("human").last_consumption_ratios = {
            "organics": 0.9, "metals": 0.4,
        }

        engine.process_happiness([empire_single, empire_multi], galaxy=None)

        assert pop_single.happiness == pytest.approx(pop_multi.happiness)


# ---------------------------------------------------------------------------
# PROJ-291 Phase 2 (C3): HappinessEngine consumes IRaceRegistry when wired.
# Pre-fix: `_get_race_config` returns `empire.race_config` regardless of the
# requested `race_id`, so any non-primary species on a multi-species colony
# silently computes happiness with the WRONG `base_happiness`. Reverses the
# PROJ-287 line-16 deferral.
# ---------------------------------------------------------------------------

class _StubRaceRegistry:
    """Minimal IRaceRegistry stub for tests. Duck-typed — no Protocol
    inheritance needed because HappinessEngine only calls `.get_race(id)`."""

    def __init__(self, mapping: dict):
        self._mapping = mapping

    def get_race(self, race_id: str):
        return self._mapping.get(race_id)


class TestMultiSpeciesViaRegistry:
    """`HappinessEngine(race_registry=...)` resolves every species'
    `RaceConfig` via the registry so multi-species colonies compute
    per-species happiness with the correct `base_happiness`. Replaces
    the pre-PROJ-291 silent wrong-race fallback."""

    def test_two_species_use_their_own_base_happiness(self):
        """Humans + Voidari on the same colony. Registry returns each
        species' own RaceConfig. Each pop's happiness must reflect its
        OWN base_happiness, not the empire's primary race."""
        from game.strategy.engine.happiness_engine import HappinessEngine

        pop_human = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        pop_voidari = SpeciesPopulation(race_id="voidari", count=500, happiness=0.0)
        planet = _earth_like(populations=[pop_human, pop_voidari])

        race_human = _race(race_id="human", base_happiness=0.5)
        race_voidari = _race(race_id="voidari", base_happiness=0.8)
        empire = _empire(1, [planet], race_human)

        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("voidari").last_consumption_ratios = {"organics": 1.0}

        registry = _StubRaceRegistry({"human": race_human, "voidari": race_voidari})
        engine = HappinessEngine(race_registry=registry)

        engine.process_happiness([empire], galaxy=None)

        hab_human = calculate_habitability(planet, race_human)
        hab_voidari = calculate_habitability(planet, race_voidari)
        assert pop_human.happiness == pytest.approx(0.5 * 1.0 * hab_human)
        assert pop_voidari.happiness == pytest.approx(0.8 * 1.0 * hab_voidari)
        # Sanity: the two values MUST differ — proves the registry
        # resolved each species independently rather than reusing
        # empire.race_config for both.
        assert pop_human.happiness != pop_voidari.happiness

    def test_unknown_race_id_skipped_gracefully(self):
        """When the registry returns None for a race_id, the species is
        skipped (happiness unchanged from pre-call value) — no exception
        raised, no silent fallback to the wrong race."""
        from game.strategy.engine.happiness_engine import HappinessEngine

        pop_human = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        pop_ghost = SpeciesPopulation(race_id="ghost", count=500, happiness=0.42)
        planet = _earth_like(populations=[pop_human, pop_ghost])

        race_human = _race(race_id="human", base_happiness=0.5)
        empire = _empire(1, [planet], race_human)

        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("ghost").last_consumption_ratios = {"organics": 1.0}

        # Registry knows humans but not ghosts.
        registry = _StubRaceRegistry({"human": race_human})
        engine = HappinessEngine(race_registry=registry)

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race_human)
        assert pop_human.happiness == pytest.approx(0.5 * 1.0 * hab)
        # Unknown race pre-call happiness is preserved.
        assert pop_ghost.happiness == pytest.approx(0.42)

    def test_legacy_path_returns_none_for_non_primary_species(self):
        """When no registry is wired (legacy callers) AND the requested
        race_id doesn't match the empire's primary race, the resolver
        returns None and the species is gracefully skipped — instead of
        the pre-PROJ-291 silent-wrong-race fallback.

        Primary race (humans) updates; secondary race (voidari) stays at
        its pre-call value because the legacy fallback no longer returns
        the empire's race_config when the race_id doesn't match."""
        from game.strategy.engine.happiness_engine import HappinessEngine

        pop_human = SpeciesPopulation(race_id="human", count=1000, happiness=0.0)
        pop_voidari = SpeciesPopulation(race_id="voidari", count=500, happiness=0.77)
        planet = _earth_like(populations=[pop_human, pop_voidari])

        race_human = _race(race_id="human", base_happiness=0.5)
        empire = _empire(1, [planet], race_human)

        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("voidari").last_consumption_ratios = {"organics": 1.0}

        # No race_registry kwarg — legacy path.
        engine = HappinessEngine()

        engine.process_happiness([empire], galaxy=None)

        hab = calculate_habitability(planet, race_human)
        assert pop_human.happiness == pytest.approx(0.5 * 1.0 * hab)
        # Voidari is NOT updated — the tightened legacy fallback returns
        # None for non-primary species instead of returning the empire's
        # primary race_config (the pre-PROJ-291 bug).
        assert pop_voidari.happiness == pytest.approx(0.77)
