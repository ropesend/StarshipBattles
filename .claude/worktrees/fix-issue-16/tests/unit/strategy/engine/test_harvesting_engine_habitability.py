"""PROJ-285 Phase 2 Task 2.2: habitability multiplier hook on HarvestingEngine.

Dedicated test file so existing `test_harvesting_engine.py` (824 lines,
MagicMock-based) stays unchanged. The new behavior:

    harvest = base_rate * size_multiplier * booster_mult * quality * habitability_mult * tick_fraction

`habitability_mult` is resolved via
`colony.get_cached_habitability_multiplier(race_registry, current_turn)`.
When the engine is constructed WITHOUT `race_registry` (the pre-PROJ-285
call pattern that legacy tests use), the multiplier defaults to 1.0 and
all existing test expectations continue to hold.
"""
from __future__ import annotations

from typing import Optional
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.core.registry import GameRegistries
from game.core.resources import ResourceCatalog
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.engine.harvesting_engine import HarvestingEngine


def _registries() -> GameRegistries:
    """Minimal registries — harvesting engine only needs the components dict
    for registry-lookup paths, which these inline-ability tests don't exercise."""
    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={},
        resource_catalog=ResourceCatalog([]),
    )


def _harvester_facility(base_rate: float = 100.0) -> PlanetaryFacility:
    """Complex with one metals harvester. Inline ability; no registry lookup needed."""
    return PlanetaryFacility(
        instance_id="harv-001",
        design_id="harv_design",
        name="Extractor",
        design_data={
            "layers": {
                "CORE": [
                    {
                        "id": "metals_harvester",
                        "abilities": {
                            "ResourceHarvester": {
                                "resource_type": "metals",
                                "base_harvest_rate": base_rate,
                            }
                        },
                    }
                ],
            }
        },
    )


def _earth_like(
    *,
    populations=None,
    facilities=None,
    stockpile=None,
    max_stockpile=None,
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
        deposits={"metals": {"quantity": 1_000_000.0, "quality": 1.0}},
        populations=populations or [],
        facilities=facilities or [_harvester_facility()],
        stockpile=stockpile or {},
        max_stockpile=max_stockpile or {"metals": 1e9},
    )


def _hostile(**kwargs) -> Planet:
    """Magma world — Earth-prefs race scores ~0.002."""
    planet = _earth_like(**kwargs)
    planet.name = "Hostile"
    planet.surface_gravity = 25.0
    planet.surface_temperature = 500.0
    planet.surface_water = 0.0
    planet.tectonic_activity = 0.9
    planet.magnetic_field = 0.0
    planet.atmosphere = {}
    planet.planet_type = PlanetType.MAGMA
    return planet


def _empire(colony: Planet, empire_id: int = 1) -> Empire:
    empire = Empire(empire_id=empire_id, name="Test", color=(0, 0, 0))
    empire.colonies = [colony]
    return empire


class _StubRegistry:
    def __init__(self, races: dict):
        self._races = races

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        return self._races.get(race_id)


def _human_race() -> RaceConfig:
    return RaceConfig(
        race_id="human",
        name="Human",
        flag_id="flag",
        portrait_id="portrait",
        theme_id="Federation",
    )


# ---------------------------------------------------------------------------
# Backward compatibility: no race_registry injected -> multiplier = 1.0
# ---------------------------------------------------------------------------

class TestHabitabilityHookBackwardCompat:
    def test_no_race_registry_preserves_legacy_behavior(self):
        """The pre-PROJ-285 `HarvestingEngine(registries=...)` call
        pattern must still work: no race_registry means no habitability
        scaling, harvest amount is the legacy formula."""
        engine = HarvestingEngine(registries=_registries())
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        empire = _empire(planet)

        engine.process_harvesting_tick(tick=1, empires=[empire])

        # base_rate=100, quality=1, tick_fraction=0.01 -> 1.0/tick
        assert planet.stockpile["metals"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# New behavior: race_registry injected -> habitability applies
# ---------------------------------------------------------------------------

class TestHabitabilityHookApplied:
    def test_ideal_planet_habitability_close_to_one(self):
        """With a race injected, ideal planet yields close-to-full harvest."""
        race_registry = _StubRegistry({"human": _human_race()})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        empire = _empire(planet)

        engine.process_harvesting_tick(tick=1, empires=[empire])

        # habitability ~0.94 on Earth-like for Earth-prefs race.
        # 1.0 * habitability ≈ 0.94/tick.
        assert planet.stockpile["metals"] == pytest.approx(0.94, abs=0.05)

    def test_hostile_planet_multiplier_suppresses_harvest(self):
        """Magma world -> habitability near zero -> harvest essentially blocked."""
        race_registry = _StubRegistry({"human": _human_race()})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _hostile(populations=[pop])
        empire = _empire(planet)

        engine.process_harvesting_tick(tick=1, empires=[empire])

        # habitability ~0.002 -> harvest << 0.01
        assert planet.stockpile.get("metals", 0.0) < 0.05

    def test_uncolonized_planet_full_rate(self):
        """No populations -> `planet_habitability_multiplier` returns 1.0
        -> automated extractor runs at full rate. Same as the
        race_registry=None legacy path, reached via a different branch."""
        race_registry = _StubRegistry({"human": _human_race()})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        planet = _hostile(populations=[])  # hostile but uncolonized
        empire = _empire(planet)

        engine.process_harvesting_tick(tick=1, empires=[empire])

        # Hostile planet but no population -> multiplier=1.0 -> full harvest.
        assert planet.stockpile["metals"] == pytest.approx(1.0)

    def test_multi_species_population_weighted(self, monkeypatch):
        """Pin the math: patch `score_planet_for_race` so the weighted
        mean is deterministic. 70/30 split with scores 1.0 / 0.5 yields
        0.85 multiplier -> 0.85 * 1.0/tick = 0.85/tick harvest."""
        import game.strategy.formulas.colony_output as co_mod

        race_a = RaceConfig(
            race_id="a", name="A", flag_id="f", portrait_id="p", theme_id="Federation",
        )
        race_b = RaceConfig(
            race_id="b", name="B", flag_id="f", portrait_id="p", theme_id="Federation",
        )

        def fake_score(planet_arg, rc):
            return 1.0 if rc is race_a else 0.5

        monkeypatch.setattr(co_mod, "score_planet_for_race", fake_score)

        race_registry = _StubRegistry({"a": race_a, "b": race_b})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="a", count=700, happiness=0.5),
            SpeciesPopulation(race_id="b", count=300, happiness=0.5),
        ])
        empire = _empire(planet)

        engine.process_harvesting_tick(tick=1, empires=[empire])

        # multiplier = (700*1 + 300*0.5) / 1000 = 0.85
        # harvest = base*quality*mult*tick_fraction = 100*1*0.85*0.01 = 0.85
        assert planet.stockpile["metals"] == pytest.approx(0.85)


class TestHabitabilityHookCaching:
    def test_multiple_ticks_share_one_cache_computation(self, monkeypatch):
        """Across 100 ticks of one turn, `planet_habitability_multiplier`
        runs ONCE per colony per turn (the cache check on Planet).
        This is the whole point of the cache — avoid O(ticks × colonies)
        habitability recomputation."""
        import game.strategy.formulas.colony_output as co_mod

        call_count = {"n": 0}

        def counting_helper(planet, registry):
            call_count["n"] += 1
            return 0.5

        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", counting_helper)

        race_registry = _StubRegistry({"human": _human_race()})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        engine.set_current_turn(1)
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        empire = _empire(planet)

        # Run all 100 ticks of a turn.
        for tick in range(1, 101):
            engine.process_harvesting_tick(tick=tick, empires=[empire])

        assert call_count["n"] == 1, (
            f"Expected 1 habitability computation across 100 ticks; got {call_count['n']}"
        )

    def test_new_turn_triggers_recompute(self, monkeypatch):
        """`engine.set_current_turn(new)` invalidates the cache key — the
        first tick of the new turn recomputes."""
        import game.strategy.formulas.colony_output as co_mod

        call_count = {"n": 0}

        def counting_helper(planet, registry):
            call_count["n"] += 1
            return 0.5

        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", counting_helper)

        race_registry = _StubRegistry({"human": _human_race()})
        engine = HarvestingEngine(
            registries=_registries(),
            race_registry=race_registry,
        )
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        empire = _empire(planet)

        engine.set_current_turn(1)
        engine.process_harvesting_tick(tick=1, empires=[empire])
        engine.process_harvesting_tick(tick=2, empires=[empire])
        assert call_count["n"] == 1

        engine.set_current_turn(2)
        engine.process_harvesting_tick(tick=1, empires=[empire])
        assert call_count["n"] == 2
