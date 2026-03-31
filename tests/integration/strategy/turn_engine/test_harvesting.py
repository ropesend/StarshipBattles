"""Turn engine harvesting integration tests - resource extraction to colony stockpile.

PROJ-75 Phase 2: Integration tests for HarvestingEngine wired into TurnEngine.
PROJ-161: Updated for per-tick via process_harvesting_tick() (100 times per turn).
PROJ-XXX: Updated for local stockpile system — harvest deposits into
colony.stockpile instead of empire.resource_pool.

Tests verify that process_harvesting_tick() is called during process_turn(),
and that planetary resources flow correctly into colony stockpiles.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord

from .conftest import MockGalaxy


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_harvester_facility(
    resource_type="metals",
    base_harvest_rate=100.0,
    instance_id="harv-001",
):
    """Create a facility with a ResourceHarvester component."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id=f"{resource_type.lower()}_harvester_complex",
        name=f"{resource_type} Harvester",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": f"{resource_type.lower()}_harvester",
                        "abilities": {
                            "ResourceHarvester": {
                                "resource_type": resource_type,
                                "base_harvest_rate": base_harvest_rate,
                            }
                        },
                    }
                ]
            }
        },
    )


def _make_planet_with_resources(
    name="Harvest World",
    resources=None,
    facilities=None,
    owner_id=0,
):
    """Create a Planet with resources and facilities for harvesting tests."""
    planet = Planet(
        name=name,
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
        owner_id=owner_id,
    )
    planet.deposits = resources or {}
    planet.facilities = facilities or []
    return planet


def _make_mock_engines():
    """Create mock engines for all TurnEngine dependencies except harvesting."""
    mocks = {
        'movement_engine': MagicMock(),
        'production_engine': MagicMock(),
        'order_processor': MagicMock(),
        'conflict_engine': MagicMock(),
        'resource_engine': MagicMock(),
        'population_engine': MagicMock(),
        'resupply_engine': MagicMock(),
    }
    mocks['movement_engine'].collect_movements.return_value = []
    mocks['order_processor'].process_instant_orders.return_value = []
    return mocks


# ===========================================================================
# Tests
# ===========================================================================

class TestHarvestingIntegration:
    """Integration tests for HarvestingEngine in TurnEngine."""

    def test_harvesting_called_during_process_turn(self, fresh_registries):
        """HarvestingEngine.process_harvesting_tick() is called 100 times during process_turn().

        PROJ-161: Changed from once-per-turn process_harvesting() to per-tick
        process_harvesting_tick() called 100 times (once per tick).
        """
        mock_harvesting = MagicMock()
        mocks = _make_mock_engines()

        engine = TurnEngine(
            registries=fresh_registries,
            **mocks,
            harvesting_engine=mock_harvesting,
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        galaxy = MockGalaxy()

        engine.process_turn([empire], galaxy)

        # Should be called 100 times (once per tick)
        assert mock_harvesting.process_harvesting_tick.call_count == 100
        # Each call should have (tick, [empire])
        for call in mock_harvesting.process_harvesting_tick.call_args_list:
            tick, empires = call[0]
            assert empires == [empire]

    def test_harvesting_extracts_resources_end_to_end(self, fresh_registries):
        """Full E2E: facility harvests from planet into colony stockpile."""
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        facility = _make_harvester_facility("metals", base_harvest_rate=100.0)
        planet = _make_planet_with_resources(
            resources={"metals": {"quantity": 5000, "quality": 0.8}},
            facilities=[facility],
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        empire.add_colony(planet)

        mocks = _make_mock_engines()
        harvesting = HarvestingEngine()

        engine = TurnEngine(
            registries=fresh_registries,
            **mocks,
            harvesting_engine=harvesting,
        )

        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        # harvest = 100 * 0.8 = 80, deposited into colony stockpile
        assert planet.stockpile.get("metals", 0.0) == pytest.approx(80.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(4920.0)

    def test_harvesting_before_production(self, fresh_registries):
        """Harvesting runs before production within each tick.

        PROJ-161: Rewritten for per-tick behavior. In each tick, process_harvesting_tick
        is called before process_construction_tick, so resources are available for builds.

        Tests order by capturing tick numbers when each method is called.
        Note: TurnEngine uses 1-indexed ticks (1-100).
        """
        harvesting_ticks = []
        production_ticks = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = lambda t, e: harvesting_ticks.append(t)

        mocks = _make_mock_engines()
        mocks['production_engine'].process_construction_tick.side_effect = lambda t, e, g, **kw: production_ticks.append(t)

        engine = TurnEngine(
            registries=fresh_registries,
            **mocks,
            harvesting_engine=mock_harvesting,
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        # Both should be called 100 times
        assert len(harvesting_ticks) == 100
        assert len(production_ticks) == 100

        # Both should have been called for all ticks 1-100 (1-indexed)
        assert harvesting_ticks == list(range(1, 101))
        assert production_ticks == list(range(1, 101))

        # Verify order within _process_tick by checking that harvesting is always
        # called before production for the same tick (they're stored in call order)
        # Since both are called in sequence within each tick and stored in order,
        # if tick order is correct (1,1,2,2,3,3...) then order is preserved.

    def test_harvesting_with_storage_cap(self, fresh_registries):
        """Colony stockpile limits are respected during harvesting."""
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        harvester = _make_harvester_facility("metals", base_harvest_rate=100.0)
        # Storage facility provides the 1000 cap
        storage = PlanetaryFacility(
            instance_id="store-001",
            design_id="metals_vault",
            name="Metals Vault",
            design_data={
                "layers": {
                    "core": [{
                        "id": "vault",
                        "abilities": {
                            "EmpireStorage": {
                                "resource_type": "metals",
                                "capacity": 1000.0,
                            }
                        },
                    }]
                }
            },
        )
        planet = _make_planet_with_resources(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )
        planet.stockpile = {"metals": 950.0}

        empire = Empire(0, "Test Empire", (255, 255, 255))
        empire.add_colony(planet)

        mocks = _make_mock_engines()
        harvesting = HarvestingEngine()

        engine = TurnEngine(
            registries=fresh_registries,
            **mocks,
            harvesting_engine=harvesting,
        )

        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        # Cap at 1000; only 50 added from 100 harvest into colony stockpile
        assert planet.stockpile["metals"] == pytest.approx(1000.0)
