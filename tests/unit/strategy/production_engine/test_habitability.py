"""PROJ-285 Phase 3 Task 3.2: habitability multiplier hook on ProductionEngine.

Separate file so the existing production-engine test suite (tick_consumption,
spawning, resource_costs) stays MagicMock-based and unchanged.

Hook behavior:
- `ProductionEngine(registries, race_registry=None)` — `None` means no
  habitability scaling (pre-PROJ-285 call pattern). Existing tests use
  this path.
- When `race_registry` is injected AND the queue owner is a Planet with
  populations, the per-turn cached habitability multiplier scales the
  per-tick resource consumption. Low habitability -> slow production.
- Fleet queues (no planet) are NOT habitability-scaled — fleet yards
  operate in space, no habitability context.
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
from game.strategy.engine.production_engine import ProductionEngine


def _registries() -> GameRegistries:
    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={},
        resource_catalog=ResourceCatalog([]),
    )


def _planetary_yard() -> PlanetaryFacility:
    return PlanetaryFacility(
        instance_id="yard",
        design_id="hub",
        name="Hub",
        design_data={
            "layers": {"CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]},
        },
        is_operational=True,
    )


def _planet(*, populations=None, stockpile=None, name: str = "Earth") -> Planet:
    p = Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24, radius=6.371e6, surface_area=5.1e14, density=5515.0,
        surface_gravity=9.81, surface_pressure=101325.0,
        surface_temperature=288.0, surface_water=0.71,
        tectonic_activity=0.3, magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL,
        deposits={},
        populations=populations or [],
        facilities=[_planetary_yard()],
        stockpile=dict(stockpile) if stockpile else {},
        max_stockpile={"metals": 1e9, "organics": 1e9},
    )
    # Wire the dict methods production_engine expects on a "colony" — Planet
    # already exposes has_stockpile / consume_from_stockpile from its API.
    return p


def _human() -> RaceConfig:
    return RaceConfig(
        race_id="human", name="Human",
        flag_id="f", portrait_id="p", theme_id="Federation",
    )


class _StubRegistry:
    def __init__(self, races):
        self._races = races

    def get_race(self, rid) -> Optional[RaceConfig]:
        return self._races.get(rid)


class TestProductionHabitabilityDI:
    def test_engine_accepts_race_registry_kwarg(self):
        """`ProductionEngine(registries=..., race_registry=...)` must not raise."""
        reg = _StubRegistry({"human": _human()})
        engine = ProductionEngine(registries=_registries(), race_registry=reg)
        assert engine is not None

    def test_legacy_constructor_still_works(self):
        """Pre-PROJ-285 `ProductionEngine(registries=...)` call pattern
        must remain valid — no race_registry kwarg is effectively
        race_registry=None."""
        engine = ProductionEngine(registries=_registries())
        assert engine is not None

    def test_set_current_turn_available(self):
        """TurnEngine invokes this to key the per-turn cache."""
        engine = ProductionEngine(registries=_registries())
        engine.set_current_turn(5)
        assert engine._current_turn == 5


class TestProductionHabitabilityScaling:
    def test_hostile_colony_consumes_resources_slower(self):
        """Fixed-amount test: with race_registry injected, the tick
        consumption on a hostile planet should be less than on an ideal
        planet for the same queued item.

        This exercises `_process_queue_tick_dynamic` end-to-end, so
        we build a minimal real Planet + queue item and compare
        stockpile drain after one tick."""
        reg = _StubRegistry({"human": _human()})
        engine = ProductionEngine(registries=_registries(), race_registry=reg)
        engine.set_current_turn(1)

        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        ideal = _planet(populations=[pop], stockpile={"metals": 10000.0}, name="Ideal")
        hostile = _planet(populations=[pop], stockpile={"metals": 10000.0}, name="Hostile")
        # Make hostile actually hostile.
        hostile.surface_gravity = 25.0
        hostile.surface_temperature = 500.0
        hostile.surface_water = 0.0
        hostile.tectonic_activity = 0.9
        hostile.magnetic_field = 0.0
        hostile.atmosphere = {}
        hostile.planet_type = PlanetType.MAGMA

        # One queued item with explicit cost tracking.
        queue_item = {
            "design_id": "Test",
            "type": "complex",
            "turns_remaining": 10,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {},
        }
        ideal.construction_queue = [dict(queue_item)]
        hostile.construction_queue = [dict(queue_item)]

        production_rate = {"metals": 100.0}  # 100/turn -> 1/tick baseline

        # Process one tick on each.
        empire_ideal = Empire(empire_id=1, name="A", color=(0, 0, 0))
        empire_ideal.colonies = [ideal]
        empire_hostile = Empire(empire_id=2, name="B", color=(0, 0, 0))
        empire_hostile.colonies = [hostile]

        engine._process_queue_tick_dynamic(
            ideal.construction_queue, empire_ideal, 1, MagicMock(),
            production_rate, colony_or_fleet=ideal, is_complex_only=True,
        )
        engine._process_queue_tick_dynamic(
            hostile.construction_queue, empire_hostile, 1, MagicMock(),
            production_rate, colony_or_fleet=hostile, is_complex_only=True,
        )

        ideal_drain = 10000.0 - ideal.stockpile["metals"]
        hostile_drain = 10000.0 - hostile.stockpile["metals"]
        assert ideal_drain > 0
        assert hostile_drain > 0
        # Hostile should consume <5% of ideal (habitability ~0.002 vs ~0.94).
        assert hostile_drain < ideal_drain * 0.05, (
            f"hostile {hostile_drain} should be < 5% of ideal {ideal_drain}"
        )

    def test_uncolonized_planet_runs_at_full_rate(self):
        """Automated production site with no population -> multiplier=1.0
        -> same drain as a race_registry=None legacy run."""
        reg = _StubRegistry({"human": _human()})
        engine_with_reg = ProductionEngine(registries=_registries(), race_registry=reg)
        engine_with_reg.set_current_turn(1)

        engine_no_reg = ProductionEngine(registries=_registries())

        p_with = _planet(populations=[], stockpile={"metals": 10000.0})
        p_no = _planet(populations=[], stockpile={"metals": 10000.0})

        item = {
            "design_id": "Test", "type": "complex", "turns_remaining": 10,
            "total_cost": {"metals": 100.0}, "resources_consumed": {},
        }
        p_with.construction_queue = [dict(item)]
        p_no.construction_queue = [dict(item)]

        rate = {"metals": 100.0}
        empire = Empire(empire_id=1, name="A", color=(0, 0, 0))

        engine_with_reg._process_queue_tick_dynamic(
            p_with.construction_queue, empire, 1, MagicMock(),
            rate, colony_or_fleet=p_with, is_complex_only=True,
        )
        engine_no_reg._process_queue_tick_dynamic(
            p_no.construction_queue, empire, 1, MagicMock(),
            rate, colony_or_fleet=p_no, is_complex_only=True,
        )

        # Both empty -> multiplier=1.0 -> identical drain.
        drain_with = 10000.0 - p_with.stockpile["metals"]
        drain_no = 10000.0 - p_no.stockpile["metals"]
        assert drain_with == pytest.approx(drain_no)


class TestProductionFleetPath:
    def test_fleet_queue_not_habitability_scaled(self):
        """Fleet queues (no planet reference) must NOT apply habitability
        scaling — the `_get_habitability_mult` helper returns 1.0 for
        any object that lacks `get_cached_habitability_multiplier`.

        Tested directly on the helper rather than through the full
        `_process_queue_tick_dynamic` pipeline because Fleet
        affordability checking (`has_cargo_resources` etc) is orthogonal
        to the habitability hook and pulling it into this test just
        obscures the contract under test."""
        from game.strategy.data.fleet import Fleet

        reg = _StubRegistry({"human": _human()})
        engine = ProductionEngine(registries=_registries(), race_registry=reg)

        fleet = MagicMock(spec=Fleet)
        # spec=Fleet -> MagicMock only exposes attributes that exist on
        # the real Fleet class. `get_cached_habitability_multiplier` is
        # NOT on Fleet, so accessing it raises AttributeError, and
        # `getattr(fleet, "get_cached_habitability_multiplier", None)`
        # returns None -> hook returns 1.0.
        mult = engine._get_habitability_mult(fleet)
        assert mult == 1.0

    def test_planet_without_race_registry_not_scaled(self):
        """If `race_registry=None` (legacy call pattern), the hook
        short-circuits to 1.0 even for a real Planet — preserves
        pre-PROJ-285 behavior for existing callers."""
        engine = ProductionEngine(registries=_registries())  # no race_registry
        planet = _planet(
            populations=[SpeciesPopulation(race_id="human", count=100, happiness=0.5)],
        )
        mult = engine._get_habitability_mult(planet)
        assert mult == 1.0


class TestProductionCacheShared:
    def test_harvest_and_production_share_planet_cache(self, monkeypatch):
        """The per-turn cache lives on Planet — both engines hitting the
        same planet in the same turn should trigger exactly one
        `planet_habitability_multiplier` computation."""
        import game.strategy.formulas.colony_output as co_mod

        call_count = {"n": 0}
        real_helper = co_mod.planet_habitability_multiplier

        def counting(planet, registry):
            call_count["n"] += 1
            return real_helper(planet, registry)

        monkeypatch.setattr(co_mod, "planet_habitability_multiplier", counting)

        reg = _StubRegistry({"human": _human()})
        prod_engine = ProductionEngine(registries=_registries(), race_registry=reg)
        prod_engine.set_current_turn(1)

        from game.strategy.engine.harvesting_engine import HarvestingEngine
        harv_engine = HarvestingEngine(registries=_registries(), race_registry=reg)
        harv_engine.set_current_turn(1)

        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _planet(populations=[pop], stockpile={"metals": 10000.0})
        planet.deposits = {"metals": {"quantity": 1e8, "quality": 1.0}}

        item = {
            "design_id": "T", "type": "complex", "turns_remaining": 10,
            "total_cost": {"metals": 100.0}, "resources_consumed": {},
        }
        planet.construction_queue = [dict(item)]
        empire = Empire(empire_id=1, name="A", color=(0, 0, 0))
        empire.colonies = [planet]

        prod_engine._process_queue_tick_dynamic(
            planet.construction_queue, empire, 1, MagicMock(),
            {"metals": 100.0}, colony_or_fleet=planet, is_complex_only=True,
        )
        harv_engine.process_harvesting_tick(tick=1, empires=[empire])

        # Both engines computed multiplier for planet on same turn — cache
        # should give exactly ONE underlying call.
        assert call_count["n"] == 1
