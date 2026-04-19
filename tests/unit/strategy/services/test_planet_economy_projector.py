"""PROJ-288 Phase 2: PlanetEconomyProjector unit tests.

The projector returns `Dict[resource_id, ResourceProjection(harvest, upkeep, yard, net)]`
for a single planet. Three sub-projections feed each entry:

  harvest  = compute_planet_production(planet, registries) * habitability_mult
  upkeep   = Σ over species: pop.count * cfg.food_allocation * per_pop_rate
             where per_pop_rate comes from EconomyConfig.population_consumption
  yard     = Σ over active queues: build_rate[res] * habitability_mult
             (planetary base queue + shipyard facility queues; empty queues skipped)
  net      = harvest - upkeep - yard

Habitability = `planet_habitability_multiplier(planet, race_registry)` from PROJ-285.
For these tests we keep `populations` empty (or unrelated to harvest/yard) so the
multiplier stays at 1.0 and the math remains hand-verifiable.
"""
from __future__ import annotations

from typing import Optional
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.planet import Planet, PlanetaryFacility, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _planet(
    *,
    name="Earth",
    owner_id: Optional[int] = 1,
    populations=None,
    facilities=None,
    deposits=None,
    construction_queue=None,
    species_configs=None,
) -> Planet:
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
        owner_id=owner_id,
        populations=populations or [],
        facilities=facilities or [],
        deposits=deposits or {},
        construction_queue=construction_queue or [],
        species_configs=species_configs or {},
    )


def _harvester_facility(*, resource_type: str, base_rate: float) -> PlanetaryFacility:
    """Operational facility with a single ResourceHarvester component
    targeting the given resource at the given base rate."""
    return PlanetaryFacility(
        instance_id=f"harv-{resource_type}",
        design_id="extractor",
        name="Extractor",
        design_data={
            "layers": {
                "hull": [
                    {
                        "id": "extractor_core",
                        "abilities": {
                            "ResourceHarvester": {
                                "resource_type": resource_type,
                                "base_harvest_rate": base_rate,
                            }
                        },
                    }
                ]
            }
        },
        is_operational=True,
    )


def _planetary_yard_facility() -> PlanetaryFacility:
    """Operational facility providing the PlanetaryYard ability so the
    planet's BASE construction_queue is recognised by the queue collector."""
    return PlanetaryFacility(
        instance_id="planetary-yard",
        design_id="planetary_yard",
        name="Planetary Yard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "planetary_yard_core", "abilities": {"PlanetaryYard": {}}}
                ]
            }
        },
        is_operational=True,
    )


def _shipyard_facility(*, instance_id: str, queue=None) -> PlanetaryFacility:
    """Operational facility with a SpaceShipyard ability + per-shipyard queue."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="orbital_shipyard",
        name="Orbital Shipyard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": {}}}
                ]
            }
        },
        is_operational=True,
        construction_queue=queue if queue is not None else [],
    )


def _race(race_id: str = "human") -> RaceConfig:
    return RaceConfig(
        race_id=race_id,
        name=race_id.capitalize(),
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


class _StubRegistry:
    """Race-registry double — projector only calls `.get_race(id)`."""
    def __init__(self, races: dict):
        self._races = races

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        return self._races.get(race_id)


def _economy(consumption: dict) -> EconomyConfig:
    return EconomyConfig(population_consumption=consumption)


def _registries():
    """Bare-minimum GameRegistries-shaped stub for the projector. The
    harvest path only needs `.components.get(...)` to be safe to call."""
    reg = MagicMock()
    reg.components = MagicMock()
    reg.components.get = MagicMock(return_value=None)
    return reg


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUncolonizedHarvestOnly:
    """Planet with extractors but no populations, no queues -> harvest only."""

    def test_uncolonized_with_harvesters(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        planet = _planet(
            populations=[],
            facilities=[_harvester_facility(resource_type="metals", base_rate=100.0)],
            deposits={"metals": {"quality": 0.5}},  # quality drops base_rate by half
        )
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),
            race_registry=_StubRegistry({}),
        )

        result = projector.project(planet)

        assert "metals" in result
        proj = result["metals"]
        assert proj.harvest == pytest.approx(50.0)   # 100 * 0.5
        assert proj.upkeep == pytest.approx(0.0)     # no pops
        assert proj.yard == pytest.approx(0.0)       # no queues
        assert proj.net == pytest.approx(50.0)


class TestUpkeepMultiResource:
    """Multi-species fed colony — upkeep per resource sums across species."""

    def test_upkeep_sums_pop_times_allocation_times_rate(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        # Pop A: 1000 humans, allocation 1.0 -> needs 1000 * 1.0 * 0.001 = 1.0 organics,
        #                                             1000 * 1.0 * 0.0005 = 0.5 vapors.
        # Pop B: 500 voidari, allocation 0.5 -> needs 500 * 0.5 * 0.001 = 0.25 organics,
        #                                            500 * 0.5 * 0.0005 = 0.125 vapors.
        cfg_h = ColonySpeciesConfig(food_allocation=1.0)
        cfg_v = ColonySpeciesConfig(food_allocation=0.5)
        planet = _planet(
            populations=[
                SpeciesPopulation(race_id="human", count=1000),
                SpeciesPopulation(race_id="voidari", count=500),
            ],
            species_configs={"human": cfg_h, "voidari": cfg_v},
        )
        registry = _StubRegistry({"human": _race("human"), "voidari": _race("voidari")})
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001, "vapors": 0.0005}),
            race_registry=registry,
        )

        result = projector.project(planet)

        # Habitability ≈ 0.94 for default-prefs humans/voidari on Earth-like.
        # Upkeep is NOT habitability-scaled (only harvest + yard are).
        assert result["organics"].upkeep == pytest.approx(1.0 + 0.25)
        assert result["vapors"].upkeep == pytest.approx(0.5 + 0.125)
        # No harvesters, no queues -> harvest = 0, yard = 0.
        assert result["organics"].harvest == 0.0
        assert result["organics"].yard == 0.0
        # Net is negative (consumption with no income).
        assert result["organics"].net == pytest.approx(-(1.0 + 0.25))


class TestYardDrain:
    """Yard projection sums build_rate across non-empty queues."""

    def test_single_queued_complex_drains_at_planetary_yard_rate(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        # Place a non-empty item on the planet's base queue.
        planet = _planet(
            populations=[],
            facilities=[_planetary_yard_facility()],
            construction_queue=[{"id": "mine_complex", "type": "complex"}],
        )
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),
            race_registry=_StubRegistry({}),
        )

        result = projector.project(planet)

        # planetary_yard default rates (data/production_rates.json) = 2000 per resource.
        # Habitability = 1.0 (no populations).
        for res in ("metals", "organics", "radioactives", "vapors", "exotics"):
            assert result[res].yard == pytest.approx(2000.0), \
                f"{res} expected 2000 yard drain, got {result[res].yard}"

    def test_multi_queue_aggregates_drains(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        # Planetary yard with one item + 2 shipyards each with one item.
        # Base rate 2000 + 30000 + 30000 = 62000 per resource.
        planet = _planet(
            populations=[],
            facilities=[
                _planetary_yard_facility(),
                _shipyard_facility(instance_id="yard-1", queue=[{"id": "ship_a"}]),
                _shipyard_facility(instance_id="yard-2", queue=[{"id": "ship_b"}]),
            ],
            construction_queue=[{"id": "complex_a"}],
        )
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),
            race_registry=_StubRegistry({}),
        )

        result = projector.project(planet)

        for res in ("metals", "organics", "radioactives", "vapors", "exotics"):
            assert result[res].yard == pytest.approx(62000.0), \
                f"{res} expected 62000 (2000 + 30000 + 30000), got {result[res].yard}"

    def test_empty_queue_contributes_zero_drain(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        # Planetary yard exists but nothing queued; shipyard exists with empty queue.
        planet = _planet(
            populations=[],
            facilities=[
                _planetary_yard_facility(),
                _shipyard_facility(instance_id="yard-1", queue=[]),
            ],
            construction_queue=[],  # base queue empty
        )
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),
            race_registry=_StubRegistry({}),
        )

        result = projector.project(planet)

        # No resources should appear at all (no harvest, no upkeep, no yard).
        assert result == {}


class TestNetIsHarvestMinusUpkeepMinusYard:
    """For every resource in the union of the three sub-projections,
    `proj.net == proj.harvest - proj.upkeep - proj.yard`."""

    def test_net_arithmetic_holds_across_all_sources(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        # Construct a planet that has at least one resource with all three sources non-zero.
        cfg = ColonySpeciesConfig(food_allocation=1.0)
        planet = _planet(
            populations=[SpeciesPopulation(race_id="human", count=1000)],
            facilities=[
                _harvester_facility(resource_type="organics", base_rate=10000.0),
                _planetary_yard_facility(),
            ],
            deposits={"organics": {"quality": 0.5}},
            construction_queue=[{"id": "complex_a"}],
            species_configs={"human": cfg},
        )
        registry = _StubRegistry({"human": _race("human")})
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.002}),
            race_registry=registry,
        )

        result = projector.project(planet)

        for res, proj in result.items():
            expected_net = proj.harvest - proj.upkeep - proj.yard
            assert proj.net == pytest.approx(expected_net), \
                f"net invariant violated on {res}: {proj.net} != {expected_net}"


class TestHabitabilityScalesHarvestAndYardOnly:
    """PROJ-285 stacking rule — harvest + yard scale by habitability,
    upkeep does NOT (it depends on demand, not on planet conditions)."""

    def test_hostile_planet_reduces_harvest_and_yard_but_not_upkeep(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        from game.strategy.formulas.colony_output import (
            planet_habitability_multiplier,
        )
        # Hostile (magma) planet to force a low habitability multiplier.
        cfg = ColonySpeciesConfig(food_allocation=1.0)
        planet = Planet(
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
            owner_id=1,
            populations=[SpeciesPopulation(race_id="human", count=1000)],
            facilities=[
                _harvester_facility(resource_type="metals", base_rate=100.0),
                _planetary_yard_facility(),
            ],
            deposits={"metals": {"quality": 1.0}},
            construction_queue=[{"id": "complex_a"}],
            species_configs={"human": cfg},
        )
        registry = _StubRegistry({"human": _race("human")})
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),  # not on planet
            race_registry=registry,
        )

        habitability = planet_habitability_multiplier(planet, registry)
        assert habitability < 0.3  # hostile world

        result = projector.project(planet)

        # metals: harvest scaled by habitability, no upkeep (organics is the
        # only consumption resource and isn't extracted), yard scaled by hab.
        assert result["metals"].harvest == pytest.approx(100.0 * habitability)
        # planetary yard rate 2000 * habitability for metals.
        assert result["metals"].yard == pytest.approx(2000.0 * habitability)


class TestUnownedPlanetReturnsEmpty:
    """`compute_planet_production` already short-circuits on owner_id=None.
    Projector inherits that — no harvest, no yard for an unowned rock."""

    def test_unowned_planet(self):
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )
        planet = _planet(
            owner_id=None,
            facilities=[_harvester_facility(resource_type="metals", base_rate=100.0)],
            deposits={"metals": {"quality": 0.5}},
        )
        projector = PlanetEconomyProjector(
            registries=_registries(),
            economy_config=_economy({"organics": 0.001}),
            race_registry=_StubRegistry({}),
        )

        result = projector.project(planet)

        # No harvest (compute_planet_production short-circuits), no upkeep
        # (no pops), no yard (no queues). Result is empty dict.
        assert result == {}
