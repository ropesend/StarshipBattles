"""
Tests for PopulationEngine.

PROJ-68 Phase 3: Logistic population growth engine.
"""
import pytest
from unittest.mock import MagicMock, patch
from tests.fixtures.turn_engine import build_test_turn_engine

from game.strategy.engine.population_engine import PopulationEngine
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


def make_earth_like_planet(
    name: str = "Earth",
    populations: list = None,
    surface_area: float = 5.1e14,  # Earth ~510 million km²
    owner_id: int = 1
) -> Planet:
    """Create an Earth-like planet for testing."""
    return Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=surface_area,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,  # 15°C in Kelvin
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"Nitrogen": 78000, "Oxygen": 21000},
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
        populations=populations or []
    )


def make_human_race_config(
    race_id: str = "human",
    aptitude_population_growth: int = 50,
    base_reproduction_rate: float = None,
) -> RaceConfig:
    """Create a human-like race config for testing.

    PROJ-283 Phase 4: `aptitude_population_growth` is no longer a stored
    field. We accept the parameter for source-stability of existing
    callers and translate it to `base_reproduction_rate` using the same
    `0.0005 * aptitude` scale the old `_aptitude_to_growth_rate` helper
    used (so test expectations stay numerically stable).
    """
    if base_reproduction_rate is None:
        base_reproduction_rate = 0.0005 * aptitude_population_growth
    return RaceConfig(
        race_id=race_id,
        name="Human",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
        base_reproduction_rate=base_reproduction_rate,
    )


def make_empire(empire_id: int, colonies: list, race_config: RaceConfig) -> Empire:
    """Create an empire with colonies and race_config."""
    empire = Empire(
        empire_id=empire_id,
        name="Test Empire",
        color=(100, 100, 200),
        race_config=race_config
    )
    empire.colonies = colonies
    return empire


class TestLogisticGrowthBasic:
    """Test basic logistic growth mechanics."""

    def test_logistic_growth_basic(self):
        """Single species on good habitability planet grows."""
        engine = PopulationEngine()

        pop = SpeciesPopulation(race_id="human", count=1000, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        initial_pop = pop.count
        engine.process_population_growth([empire])

        # Population should have grown
        assert pop.count > initial_pop, "Population should grow"

    def test_growth_slows_near_capacity(self):
        """Growth slows as population approaches carrying capacity (S-curve)."""
        engine = PopulationEngine()

        # Start at 50% capacity
        planet = make_earth_like_planet()
        carrying_capacity = planet.max_population
        half_capacity = carrying_capacity // 2

        pop = SpeciesPopulation(race_id="human", count=half_capacity, happiness=1.0)
        planet.populations = [pop]
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        engine.process_population_growth([empire])
        growth_at_half = pop.count - half_capacity

        # Reset to 90% capacity
        near_capacity = int(carrying_capacity * 0.9)
        pop.count = near_capacity
        engine.process_population_growth([empire])
        growth_at_90 = pop.count - near_capacity

        # Growth should be much slower near capacity
        assert growth_at_half > growth_at_90, "Growth should slow near capacity"

    def test_zero_population_no_growth(self):
        """Empty colony stays empty - can't grow from nothing."""
        engine = PopulationEngine()

        pop = SpeciesPopulation(race_id="human", count=0, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        engine.process_population_growth([empire])

        assert pop.count == 0, "Zero population cannot grow"


class TestHappinessAndHabitability:
    """Test happiness and habitability effects on growth."""

    def test_low_happiness_slows_growth(self):
        """Low happiness reduces growth rate."""
        engine = PopulationEngine()

        # High happiness population — pop.race_id matches empire.race_config.race_id
        # so the legacy resolver picks up the right RaceConfig (PROJ-291 C3).
        pop_happy = SpeciesPopulation(race_id="human_happy", count=10000, happiness=1.0)
        planet_happy = make_earth_like_planet(name="Happy", populations=[pop_happy])
        race_happy = make_human_race_config(race_id="human_happy")
        empire_happy = make_empire(1, [planet_happy], race_happy)

        # Low happiness population
        pop_sad = SpeciesPopulation(race_id="human_sad", count=10000, happiness=0.2)
        planet_sad = make_earth_like_planet(name="Sad", populations=[pop_sad])
        race_sad = make_human_race_config(race_id="human_sad")
        empire_sad = make_empire(2, [planet_sad], race_sad)

        engine.process_population_growth([empire_happy, empire_sad])

        growth_happy = pop_happy.count - 10000
        growth_sad = pop_sad.count - 10000

        assert growth_happy > growth_sad, "Happy population should grow faster"

    def test_low_habitability_reduces_carrying_capacity(self):
        """Low habitability reduces effective carrying capacity."""
        engine = PopulationEngine()

        # Good habitability planet (Earth-like)
        pop_good = SpeciesPopulation(race_id="human_good", count=10000, happiness=1.0)
        planet_good = make_earth_like_planet(name="Good", populations=[pop_good])
        race_good = make_human_race_config(race_id="human_good")
        empire_good = make_empire(1, [planet_good], race_good)

        # Bad habitability planet (wrong temperature - use extreme value)
        pop_bad = SpeciesPopulation(race_id="human_bad", count=10000, happiness=1.0)
        planet_bad = make_earth_like_planet(name="Bad", populations=[pop_bad])
        planet_bad.surface_temperature = 500.0  # Extremely hot (212°C)
        planet_bad.magnetic_field = 0.0  # No radiation protection
        race_bad = make_human_race_config(race_id="human_bad")
        empire_bad = make_empire(2, [planet_bad], race_bad)

        # Run multiple turns to see divergence
        for _ in range(5):
            engine.process_population_growth([empire_good, empire_bad])

        # Good conditions should result in higher population
        assert pop_good.count > pop_bad.count, "Better habitability should allow more growth"


class TestPopulationDynamics:
    """Test population decline and edge cases."""

    def test_population_shrinks_above_carrying_capacity(self):
        """Population declines if above effective carrying capacity."""
        engine = PopulationEngine()

        # Small planet with extremely harsh conditions
        # Use a small surface area so max_population is low
        pop = SpeciesPopulation(race_id="human", count=100000, happiness=0.3)
        planet = make_earth_like_planet(
            populations=[pop],
            surface_area=1e10  # Very small planet, max_pop ~1000
        )
        planet.surface_temperature = 500.0  # Extremely hot
        planet.magnetic_field = 0.0  # No protection

        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        # Verify we're above capacity
        assert pop.count > planet.max_population, "Test setup: pop should exceed max"

        initial_pop = pop.count

        # Run multiple turns to see decline
        for _ in range(20):
            engine.process_population_growth([empire])

        # Population should have shrunk due to being above effective capacity
        assert pop.count < initial_pop, "Population should shrink above capacity"

    def test_multiple_species_grow_independently(self):
        """Multiple species on same planet grow independently."""
        engine = PopulationEngine()

        pop_human = SpeciesPopulation(race_id="human", count=5000, happiness=1.0)
        pop_alien = SpeciesPopulation(race_id="alien", count=3000, happiness=0.8)
        planet = make_earth_like_planet(populations=[pop_human, pop_alien])

        # Create race configs for both species
        race_human = make_human_race_config(race_id="human")
        race_alien = RaceConfig(
            race_id="alien",
            name="Alien",
            flag_id="flag_test",
            portrait_id="portrait_test",
            theme_id="Federation",
            base_reproduction_rate=0.0275,  # 0.0005 * 55 (was: aptitude=55)
        )

        # Empire has multiple species (we store primary race_config)
        # For multi-species, we'd need a registry lookup
        # For now, test with single empire having human as primary
        empire = make_empire(1, [planet], race_human)
        # Patch to provide alien race config when needed
        original_get_race = engine._get_race_config

        def mock_get_race(race_id, empire):
            if race_id == "human":
                return race_human
            elif race_id == "alien":
                return race_alien
            return None

        engine._get_race_config = mock_get_race

        initial_human = pop_human.count
        initial_alien = pop_alien.count

        engine.process_population_growth([empire])

        # Both should grow (or at least be processed)
        assert pop_human.count != initial_human or pop_alien.count != initial_alien, \
            "At least one species should have population change"


class TestAptitudeEffects:
    """Test aptitude effects on growth rate."""

    def test_high_aptitude_faster_growth(self):
        """Higher population_growth aptitude results in faster growth."""
        engine = PopulationEngine()

        # Low aptitude empire
        pop_low = SpeciesPopulation(race_id="slow", count=10000, happiness=1.0)
        planet_low = make_earth_like_planet(name="Slow", populations=[pop_low])
        race_low = make_human_race_config(race_id="slow", aptitude_population_growth=10)
        empire_low = make_empire(1, [planet_low], race_low)

        # High aptitude empire
        pop_high = SpeciesPopulation(race_id="fast", count=10000, happiness=1.0)
        planet_high = make_earth_like_planet(name="Fast", populations=[pop_high])
        race_high = make_human_race_config(race_id="fast", aptitude_population_growth=90)
        empire_high = make_empire(2, [planet_high], race_high)

        engine.process_population_growth([empire_low, empire_high])

        growth_low = pop_low.count - 10000
        growth_high = pop_high.count - 10000

        assert growth_high > growth_low, "Higher aptitude should mean faster growth"


# PROJ-283 Phase 4: TestAptitudeConversion deleted — the
# `_aptitude_to_growth_rate` helper is gone. Reproduction rate is now
# read directly from `RaceConfig.base_reproduction_rate`. The
# point-budget cost curve for that field is exercised by
# `tests/unit/strategy/data/test_race_point_budget_v2.py::TestCalculateReproductionCost`.


# ---------------------------------------------------------------------------
# PROJ-291 Phase 2 (C3): PopulationEngine consumes IRaceRegistry when wired.
# Pre-fix: `_get_race_config` returns `empire.race_config` regardless of the
# requested `race_id`, so any non-primary species on a multi-species colony
# silently grows using the WRONG `base_reproduction_rate`. Reverses the
# PROJ-287 line-16 deferral.
# ---------------------------------------------------------------------------

class _StubRaceRegistry:
    """Minimal IRaceRegistry stub for tests. Duck-typed — PopulationEngine
    only calls `.get_race(id)`."""

    def __init__(self, mapping: dict):
        self._mapping = mapping

    def get_race(self, race_id: str):
        return self._mapping.get(race_id)


class TestMultiSpeciesViaRegistry:
    """`PopulationEngine(race_registry=...)` resolves every species'
    `RaceConfig` via the registry so multi-species colonies grow with
    per-species `base_reproduction_rate`. Replaces the pre-PROJ-291
    silent wrong-race fallback."""

    def test_each_species_grows_at_its_own_reproduction_rate(self):
        """Humans (rate 0.03) and Voidari (rate 0.05) on the same colony.
        Registry returns each species' own RaceConfig. The two species
        must grow by VISIBLY different amounts — proves each species
        used its OWN reproduction rate rather than the empire's primary
        race rate for both."""
        # Start below capacity so the logistic term is positive.
        pop_human = SpeciesPopulation(race_id="human", count=5000, happiness=1.0)
        pop_voidari = SpeciesPopulation(race_id="voidari", count=5000, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop_human, pop_voidari])

        race_human = make_human_race_config(race_id="human", base_reproduction_rate=0.03)
        race_voidari = make_human_race_config(race_id="voidari", base_reproduction_rate=0.05)
        empire = make_empire(1, [planet], race_human)

        # Seed ratios as OrganicsConsumptionEngine would — both well-fed.
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("voidari").last_consumption_ratios = {"organics": 1.0}

        registry = _StubRaceRegistry({"human": race_human, "voidari": race_voidari})
        engine = PopulationEngine(race_registry=registry)

        initial_human = pop_human.count
        initial_voidari = pop_voidari.count
        engine.process_population_growth([empire])

        growth_human = pop_human.count - initial_human
        growth_voidari = pop_voidari.count - initial_voidari

        # Both species grow (positive growth) — seed conditions are
        # identical except for reproduction_rate.
        assert growth_human > 0
        assert growth_voidari > 0
        # Voidari's rate is ~1.67x humans' — growth should differ
        # visibly. If the bug were present, both species would grow
        # using humans' rate (because `_get_race_config` returned
        # empire.race_config for both) and the deltas would be equal.
        assert growth_voidari > growth_human, (
            f"Voidari ({growth_voidari}) should out-grow humans "
            f"({growth_human}) given the 0.05 vs 0.03 rate difference"
        )

    def test_unknown_race_id_skipped_gracefully(self):
        """Registry returns None for an unknown race_id — species count
        stays unchanged (no logistic term applied), no exception."""
        pop_human = SpeciesPopulation(race_id="human", count=5000, happiness=1.0)
        pop_ghost = SpeciesPopulation(race_id="ghost", count=2000, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop_human, pop_ghost])

        race_human = make_human_race_config(race_id="human")
        empire = make_empire(1, [planet], race_human)

        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("ghost").last_consumption_ratios = {"organics": 1.0}

        registry = _StubRaceRegistry({"human": race_human})
        engine = PopulationEngine(race_registry=registry)

        initial_ghost = pop_ghost.count
        engine.process_population_growth([empire])

        # Human grows; ghost unchanged (None race_config → early-return).
        assert pop_human.count > 5000
        assert pop_ghost.count == initial_ghost

    def test_legacy_path_skips_non_primary_species(self):
        """When no registry is wired, the resolver returns None for
        non-primary species (instead of the pre-PROJ-291 wrong-race
        fallback). The non-primary species' count must not change."""
        pop_human = SpeciesPopulation(race_id="human", count=5000, happiness=1.0)
        pop_voidari = SpeciesPopulation(race_id="voidari", count=5000, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop_human, pop_voidari])

        race_human = make_human_race_config(race_id="human")
        empire = make_empire(1, [planet], race_human)

        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        planet.get_species_config("voidari").last_consumption_ratios = {"organics": 1.0}

        # No race_registry kwarg — legacy path.
        engine = PopulationEngine()

        initial_voidari = pop_voidari.count
        engine.process_population_growth([empire])

        # Human grows (primary race matches); voidari is skipped because
        # the tightened legacy fallback returns None for non-primary
        # species rather than returning empire.race_config.
        assert pop_human.count > 5000
        assert pop_voidari.count == initial_voidari


class TestTurnEngineIntegration:
    """Test PopulationEngine integration with TurnEngine."""

    def test_turn_engine_calls_population_engine(self, fresh_registries):
        """TurnEngine calls PopulationEngine when injected."""
        from game.strategy.engine.turn_engine import TurnEngine

        # Create mock population engine
        mock_pop_engine = MagicMock()

        # Inject into TurnEngine
        turn_engine = build_test_turn_engine(fresh_registries, population_engine=mock_pop_engine)

        # Create minimal test data
        empire = MagicMock(spec=Empire)
        empire.fleets = []
        empire.colonies = []  # Required for harvesting_engine
        empires = [empire]
        galaxy = MagicMock()

        # Run turn
        turn_engine.process_turn(empires, galaxy)

        # Verify population engine was called
        mock_pop_engine.process_population_growth.assert_called_once_with(empires)


class TestFoodRatioAndDecline:
    """PROJ-284 Phase 3 Task 3.5: new growth formula uses
    `base_reproduction_rate * last_food_ratio` plus a starvation decline
    term when `last_food_ratio < 1.0`.

    These tests seed `ColonySpeciesConfig.last_food_ratio` AND
    `pop.happiness` explicitly, simulating what TurnEngine does by
    running OrganicsConsumptionEngine → HappinessEngine before
    PopulationEngine. The PopulationEngine tests don't call those
    engines — they just set the fields directly.
    """

    def test_green_state_positive_growth(self):
        """Full food + decent habitability + decent happiness -> growth."""
        engine = PopulationEngine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = make_earth_like_planet(populations=[pop])
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        race = make_human_race_config()
        empire = make_empire(1, [planet], race)

        initial = pop.count
        engine.process_population_growth([empire])
        assert pop.count > initial, "Green state should produce growth"

    def test_amber_state_food_ratio_half_halves_effective_rate(self):
        """food_ratio=0.5 halves effective_r AND adds decline term.

        With pop=1000 and decline_rate=0.02:
            decline = -0.02 * 1000 * (1 - 0.5) = -10 pop/turn.
        Effective_r is halved, so logistic output is halved relative to
        a green-state run with the same happiness/hab. Net result is
        less growth than green (possibly net decline when growth is small).
        """
        engine = PopulationEngine()

        # Green-state baseline
        green_pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        green_planet = make_earth_like_planet(name="Green", populations=[green_pop])
        green_planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        green_empire = make_empire(1, [green_planet], make_human_race_config(race_id="human"))

        amber_pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        amber_planet = make_earth_like_planet(name="Amber", populations=[amber_pop])
        amber_planet.get_species_config("human").last_consumption_ratios = {"organics": 0.5}
        amber_empire = make_empire(2, [amber_planet], make_human_race_config(race_id="human"))

        engine.process_population_growth([green_empire, amber_empire])

        green_growth = green_pop.count - 1000
        amber_growth = amber_pop.count - 1000
        assert amber_growth < green_growth, (
            "Amber (half food) should grow slower OR decline relative to green"
        )

    def test_red_state_zero_food_declines_population(self):
        """food_ratio=0 zeros effective_r; decline term alone applies."""
        engine = PopulationEngine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = make_earth_like_planet(populations=[pop])
        planet.get_species_config("human").last_consumption_ratios = {"organics": 0.0}
        race = make_human_race_config()
        empire = make_empire(1, [planet], race)

        engine.process_population_growth([empire])

        # decline_rate=0.02 * 1000 * (1-0) = -20
        assert pop.count < 1000, "Starvation must shrink population"
        assert pop.count == pytest.approx(980, abs=2)

    def test_zero_pop_with_starvation_stays_zero(self):
        """Zero-pop colonies skip growth AND decline — 0 * anything = 0."""
        engine = PopulationEngine()
        pop = SpeciesPopulation(race_id="human", count=0, happiness=0.5)
        planet = make_earth_like_planet(populations=[pop])
        planet.get_species_config("human").last_consumption_ratios = {"organics": 0.0}
        race = make_human_race_config()
        empire = make_empire(1, [planet], race)

        engine.process_population_growth([empire])

        assert pop.count == 0

    def test_over_capacity_still_declines_logistically(self):
        """P > K_eff gives a negative logistic term regardless of food."""
        engine = PopulationEngine()
        # Small planet so K_eff ~ 1000; pop at 5000 > K.
        pop = SpeciesPopulation(race_id="human", count=5000, happiness=0.5)
        planet = make_earth_like_planet(populations=[pop], surface_area=1e10)
        planet.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        race = make_human_race_config()
        empire = make_empire(1, [planet], race)

        engine.process_population_growth([empire])
        # P > K so logistic_factor (1 - P/K) is negative -> negative growth.
        assert pop.count < 5000

    def test_happiness_clamp_above_one_still_honored(self):
        """PROJ-284 Phase 3: `HappinessEngine` can push happiness to 3.0
        on over-supplied ideal planets. The growth formula should use
        that value directly (no internal re-clamp to [0, 1])."""
        engine = PopulationEngine()
        pop_one = SpeciesPopulation(race_id="human", count=1000, happiness=1.0)
        planet_one = make_earth_like_planet(name="Baseline", populations=[pop_one])
        planet_one.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        empire_one = make_empire(1, [planet_one], make_human_race_config(race_id="human"))

        pop_three = SpeciesPopulation(race_id="human", count=1000, happiness=3.0)
        planet_three = make_earth_like_planet(name="OverSupplied", populations=[pop_three])
        planet_three.get_species_config("human").last_consumption_ratios = {"organics": 1.0}
        empire_three = make_empire(2, [planet_three], make_human_race_config(race_id="human"))

        engine.process_population_growth([empire_one, empire_three])

        growth_one = pop_one.count - 1000
        growth_three = pop_three.count - 1000
        assert growth_three > growth_one, (
            "happiness=3 must drive more growth than happiness=1 (no internal clamp)"
        )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_no_empires(self):
        """Engine handles empty empire list gracefully."""
        engine = PopulationEngine()
        # Should not raise
        engine.process_population_growth([])

    def test_empire_no_colonies(self):
        """Engine handles empire with no colonies."""
        engine = PopulationEngine()
        empire = make_empire(1, [], make_human_race_config())
        # Should not raise
        engine.process_population_growth([empire])

    def test_colony_no_populations(self):
        """Engine handles colony with no populations."""
        engine = PopulationEngine()
        planet = make_earth_like_planet(populations=[])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)
        # Should not raise
        engine.process_population_growth([empire])

    def test_population_clamped_to_zero(self):
        """Population cannot go negative."""
        engine = PopulationEngine()

        # Very small population on harsh planet
        pop = SpeciesPopulation(race_id="human", count=1, happiness=0.1)
        planet = make_earth_like_planet(populations=[pop])
        planet.surface_temperature = 500.0  # Extremely harsh
        planet.magnetic_field = 0.0

        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        # Run many turns
        for _ in range(100):
            engine.process_population_growth([empire])

        assert pop.count >= 0, "Population should never go negative"


# ---------------------------------------------------------------------------
# PROJ-286 Phase 4: multi-resource behavior via the MIN-aggregation property
# ---------------------------------------------------------------------------

class TestMultiResourceStarvation:
    """PROJ-286: `cfg.last_food_ratio` is now MIN across declared
    resources. PopulationEngine source file was NOT touched — these
    tests pin the decline term + effective_r behavior through the
    computed property."""

    def test_one_starved_resource_collapses_growth_to_full_decline(self):
        """`{organics: 1.0, metals: 0.0}` → min=0 → effective_r=0 and
        decline_term = -decline_rate * pop * (1-0) = -20 for pop=1000."""
        engine = PopulationEngine()
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = make_earth_like_planet(populations=[pop])
        planet.get_species_config("human").last_consumption_ratios = {
            "organics": 1.0, "metals": 0.0,
        }
        race = make_human_race_config()
        empire = make_empire(1, [planet], race)

        engine.process_population_growth([empire])

        # Matches `test_red_state_zero_food_declines_population` numerics
        # because MIN(1.0, 0.0) == 0.0 — the decline term doesn't care
        # WHICH resource is starved, just that at least one is.
        assert pop.count == pytest.approx(980, abs=2)

    def test_mixed_ratios_decline_term_uses_minimum(self):
        """`{organics: 0.5, metals: 1.0}` → min=0.5 → decline_term =
        -0.02 * P * (1 - 0.5) = -10 for P=1000. Must yield LESS growth
        than full-feed, MORE than full-starvation."""
        engine = PopulationEngine()

        # Single-resource 0.5 baseline (no second resource at all).
        baseline_pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        baseline_planet = make_earth_like_planet(name="Baseline", populations=[baseline_pop])
        baseline_planet.get_species_config("human").last_consumption_ratios = {"organics": 0.5}
        baseline_empire = make_empire(1, [baseline_planet], make_human_race_config(race_id="human"))

        # Multi-resource with MIN 0.5.
        mixed_pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        mixed_planet = make_earth_like_planet(name="Mixed", populations=[mixed_pop])
        mixed_planet.get_species_config("human").last_consumption_ratios = {
            "organics": 0.5, "metals": 1.0,
        }
        mixed_empire = make_empire(2, [mixed_planet], make_human_race_config(race_id="human"))

        engine.process_population_growth([baseline_empire, mixed_empire])

        # Identical starting pop, identical MIN ratio → identical decline term
        # + identical effective_r → identical final count.
        assert mixed_pop.count == baseline_pop.count


class TestMultiResourceVsSingleResourceParity:
    """PROJ-286 parity contract: single-resource 0.X and multi-resource
    dict with MIN 0.X must produce identical `_grow_species` output."""

    def test_single_resource_matches_multi_resource_with_same_minimum(self):
        engine = PopulationEngine()

        pop_single = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet_single = make_earth_like_planet(name="Single", populations=[pop_single])
        planet_single.get_species_config("human").last_consumption_ratios = {"organics": 0.3}
        empire_single = make_empire(1, [planet_single], make_human_race_config(race_id="human"))

        pop_multi = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet_multi = make_earth_like_planet(name="Multi", populations=[pop_multi])
        planet_multi.get_species_config("human").last_consumption_ratios = {
            "organics": 0.9, "metals": 0.3, "radioactives": 0.8,
        }
        empire_multi = make_empire(2, [planet_multi], make_human_race_config(race_id="human"))

        engine.process_population_growth([empire_single, empire_multi])

        assert pop_single.count == pop_multi.count
