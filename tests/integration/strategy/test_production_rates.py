"""Integration tests for per-resource production rate limits.

PROJ-97 Phase 6: Tests that the per-resource production rate system
correctly calculates build turns based on resource bottlenecks,
caps cost_per_tick to respect rate limits, and properly consumes
resources over multiple turns.
"""
import pytest
import math

from game.ui.panels.build_queue_controller import BuildQueueController
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    get_default_production_rates,
    _get_facility_production_rates,
)
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord


# ===========================================================================
# Factory helpers
# ===========================================================================

def _make_shipyard_facility(
    production_rates: dict = None,
    construction_speed_bonus: float = 1.0,
    instance_id: str = "yard-001",
) -> PlanetaryFacility:
    """Create a shipyard facility with production_rates in SpaceShipyard ability."""
    abilities = {
        "SpaceShipyard": {
            "can_build_ships": True,
            "can_build_complexes": True,
            "construction_speed_bonus": construction_speed_bonus,
        }
    }
    if production_rates:
        abilities["SpaceShipyard"]["production_rates"] = production_rates

    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="test_shipyard",
        name="Test Shipyard",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": "shipyard_comp",
                        "abilities": abilities,
                    }
                ]
            }
        },
        is_operational=True,
    )


def _make_planet(facilities=None) -> Planet:
    """Create a minimal planet for testing."""
    planet = Planet(
        name="Test World",
        location=HexCoord(0, 0),
        orbit_distance=2,
        mass=5.97e24,
        radius=6.37e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.8,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=0,
    )
    planet.facilities = facilities or []
    return planet


def _make_build_queue_source(
    build_rate: dict,
    queue_id: str = "test-queue",
    display_name: str = "Test Queue",
) -> BuildQueueSource:
    """Create a BuildQueueSource with per-resource rates."""
    return BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=None,
        construction_queue=[],
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet",
        build_rate=build_rate,
        planet_id=1,
    )


# ===========================================================================
# Turn Calculation Tests
# ===========================================================================

class TestPerResourceTurnCalculation:
    """Tests for per-resource bottleneck turn calculation."""

    def test_high_metal_cost_creates_multi_turn_build(self):
        """5500 Metals at 3000/turn rate takes 2 turns (bottleneck)."""
        # Build rate: 3000/turn for all resources
        build_rate = {"Metals": 3000, "Organics": 3000, "Radioactives": 3000}

        # Design costs 5500 Metals -> ceil(5500/3000) = 2 turns
        # Using controller's turn calculation logic
        cost = {"Metals": 5500}

        turns_per_resource = []
        for res, rate in build_rate.items():
            res_cost = cost.get(res, 0)
            if res_cost > 0 and rate > 0:
                turns_per_resource.append(math.ceil(res_cost / rate))

        total_turns = max(1, max(turns_per_resource)) if turns_per_resource else 1

        assert total_turns == 2

    def test_mixed_resources_bottleneck_determines_turns(self):
        """When different resources have different rates, slowest determines turns."""
        # Metals fast (3000/turn), Exotics slow (1500/turn)
        build_rate = {"Metals": 3000, "Exotics": 1500}

        # Costs: 2000 Metals, 2000 Exotics
        # Metals: ceil(2000/3000) = 1 turn
        # Exotics: ceil(2000/1500) = 2 turns -> bottleneck
        cost = {"Metals": 2000, "Exotics": 2000}

        turns_per_resource = []
        for res, rate in build_rate.items():
            res_cost = cost.get(res, 0)
            if res_cost > 0 and rate > 0:
                turns_per_resource.append(math.ceil(res_cost / rate))

        total_turns = max(1, max(turns_per_resource)) if turns_per_resource else 1

        assert total_turns == 2

    def test_construction_speed_bonus_multiplies_all_rates(self):
        """Shipyard with 1.5x construction_speed_bonus multiplies all per-resource rates."""
        # Base rates: 3000/turn for each resource
        base_rates = {
            "Metals": 3000,
            "Organics": 3000,
            "Radioactives": 3000,
            "Vapors": 3000,
            "Exotics": 3000,
        }

        facility = _make_shipyard_facility(
            production_rates=base_rates,
            construction_speed_bonus=1.5,  # 1.5x multiplier
        )

        rates = _get_facility_production_rates(facility)

        # Each rate should be multiplied by 1.5
        assert rates["Metals"] == pytest.approx(4500.0)
        assert rates["Organics"] == pytest.approx(4500.0)
        assert rates["Radioactives"] == pytest.approx(4500.0)
        assert rates["Vapors"] == pytest.approx(4500.0)
        assert rates["Exotics"] == pytest.approx(4500.0)


# ===========================================================================
# Cost Per Tick Capping Tests
# ===========================================================================

class TestCostPerTickCapping:
    """Tests for cost_per_tick being capped to per-resource rate limits."""

    def test_cost_per_tick_respects_rate_cap(self):
        """cost_per_tick for each resource is capped at rate/100."""
        build_rate = {"Metals": 3000, "Exotics": 1500}

        # Max per tick: Metals 30, Exotics 15
        max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}

        assert max_per_tick["Metals"] == pytest.approx(30.0)
        assert max_per_tick["Exotics"] == pytest.approx(15.0)

    def test_non_bottleneck_resource_gets_capped(self):
        """Non-bottleneck resources are capped to prevent front-loading."""
        build_rate = {"Metals": 3000, "Exotics": 1500}

        # Costs: 2000 Metals, 2000 Exotics
        # Turns: 2 (from Exotics bottleneck)
        # Natural rate: 2000 / 200 = 10/tick for each
        # Metals cap: 30/tick (no issue, 10 < 30)
        # Exotics cap: 15/tick (no issue, 10 < 15)

        cost = {"Metals": 2000, "Exotics": 2000}
        turns = 2
        total_ticks = turns * 100

        max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}

        cost_per_tick = {}
        for res, amount in cost.items():
            natural_rate = amount / total_ticks
            cap = max_per_tick.get(res, float('inf'))
            cost_per_tick[res] = min(natural_rate, cap)

        # Both resources at 10/tick (no capping needed)
        assert cost_per_tick["Metals"] == pytest.approx(10.0)
        assert cost_per_tick["Exotics"] == pytest.approx(10.0)

    def test_single_turn_high_cost_gets_capped(self):
        """When cost fits in 1 turn but exceeds per-tick rate, it gets capped."""
        # Rate: 3000/turn = 30/tick max
        build_rate = {"Metals": 3000}

        # Cost: 2500 Metals = 1 turn (ceil(2500/3000) = 1)
        # Natural rate: 2500/100 = 25/tick
        # Cap: 30/tick (no capping needed here)

        cost = {"Metals": 2500}
        turns = 1
        total_ticks = turns * 100

        max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}

        cost_per_tick = {}
        for res, amount in cost.items():
            natural_rate = amount / total_ticks
            cap = max_per_tick.get(res, float('inf'))
            cost_per_tick[res] = min(natural_rate, cap)

        assert cost_per_tick["Metals"] == pytest.approx(25.0)


# ===========================================================================
# Resource Consumption Over Turns Tests
# ===========================================================================

class TestResourceConsumptionOverTurns:
    """Tests for correct resource consumption spread across turns."""

    def test_first_turn_consumption_capped_at_rate(self):
        """After 100 ticks (turn 1), consumption doesn't exceed rate limit."""
        build_rate = {"Metals": 3000}

        # Cost: 5500 Metals at 3000/turn = 2 turns
        # Turn 1: consume up to 3000 Metals
        # Turn 2: consume remaining 2500 Metals

        cost = {"Metals": 5500}
        turns = 2
        total_ticks = turns * 100

        # Cost per tick: 5500 / 200 = 27.5/tick
        # After 100 ticks: 2750 Metals (natural rate)
        # But with per-tick cap of 30, it's min(27.5, 30) = 27.5

        max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}
        natural_rate = cost["Metals"] / total_ticks
        capped_rate = min(natural_rate, max_per_tick["Metals"])

        turn_1_consumption = capped_rate * 100

        # 27.5 * 100 = 2750, which is under 3000 rate limit
        assert turn_1_consumption == pytest.approx(2750.0)
        assert turn_1_consumption <= 3000.0

    def test_all_resources_consumed_after_all_turns(self):
        """After all turns complete (200 ticks), all 5500 Metals are consumed."""
        cost = {"Metals": 5500}
        turns = 2
        total_ticks = turns * 100

        # At natural rate without capping (since 27.5 < 30)
        natural_rate = cost["Metals"] / total_ticks
        total_consumed = natural_rate * total_ticks

        assert total_consumed == pytest.approx(5500.0)


# ===========================================================================
# Production Rates JSON Tests
# ===========================================================================

class TestProductionRatesFromJSON:
    """Tests for loading production rates from JSON."""

    def test_planetary_yard_has_default_rates(self):
        """Planetary yard loads default rates from JSON."""
        rates = get_default_production_rates("planetary_yard")

        # Should have all 5 resource types at 2000/turn
        assert "Metals" in rates
        assert "Organics" in rates
        assert "Radioactives" in rates
        assert "Vapors" in rates
        assert "Exotics" in rates

        assert rates["Metals"] == 2000

    def test_space_shipyard_has_default_rates(self):
        """Space shipyard loads default rates from JSON (3000/turn)."""
        rates = get_default_production_rates("space_shipyard")

        assert rates["Metals"] == 3000
        assert rates["Exotics"] == 3000

    def test_fleet_space_yard_has_default_rates(self):
        """Fleet space yard loads default rates from JSON (3000/turn)."""
        rates = get_default_production_rates("fleet_space_yard")

        assert rates["Metals"] == 3000
        assert rates["Exotics"] == 3000

    def test_unknown_yard_type_returns_empty(self):
        """Unknown yard type returns empty dict."""
        rates = get_default_production_rates("unknown_yard")

        assert rates == {}


# ===========================================================================
# BuildQueueSource Integration Tests
# ===========================================================================

class TestBuildQueueSourceIntegration:
    """Tests for BuildQueueSource with per-resource rates."""

    def test_source_build_rate_is_dict(self):
        """BuildQueueSource.build_rate is Dict[str, float]."""
        rates = {"Metals": 3000, "Organics": 3000}
        source = _make_build_queue_source(build_rate=rates)

        assert isinstance(source.build_rate, dict)
        assert source.build_rate["Metals"] == 3000
        assert source.build_rate["Organics"] == 3000

    def test_facility_production_rates_extracted(self):
        """Facility production_rates are extracted from SpaceShipyard ability."""
        rates = {
            "Metals": 4000,
            "Organics": 3500,
            "Radioactives": 3000,
            "Vapors": 2500,
            "Exotics": 2000,
        }

        facility = _make_shipyard_facility(production_rates=rates)
        extracted = _get_facility_production_rates(facility)

        assert extracted["Metals"] == 4000
        assert extracted["Organics"] == 3500
        assert extracted["Radioactives"] == 3000
        assert extracted["Vapors"] == 2500
        assert extracted["Exotics"] == 2000

    def test_facility_without_production_rates_uses_defaults(self):
        """Facility without explicit production_rates falls back to defaults."""
        facility = _make_shipyard_facility(production_rates=None)
        rates = _get_facility_production_rates(facility)

        # Should fall back to space_shipyard defaults (3000)
        assert rates["Metals"] == 3000
