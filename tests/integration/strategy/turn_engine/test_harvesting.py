"""Turn engine harvesting integration tests - resource extraction to empire pool.

PROJ-75 Phase 2: Integration tests for HarvestingEngine wired into TurnEngine.
Tests verify that process_harvesting() is called during process_turn(),
and that planetary resources flow correctly into empire pools.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord

from .conftest import MockGalaxy


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_harvester_facility(
    resource_type="Metals",
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
    planet.resources = resources or {}
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

    def test_harvesting_called_during_process_turn(self):
        """HarvestingEngine.process_harvesting() is called during process_turn()."""
        mock_harvesting = MagicMock()
        mocks = _make_mock_engines()

        engine = TurnEngine(
            **mocks,
            harvesting_engine=mock_harvesting,
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        galaxy = MockGalaxy()

        engine.process_turn([empire], galaxy)

        mock_harvesting.process_harvesting.assert_called_once_with([empire])

    def test_harvesting_extracts_resources_end_to_end(self):
        """Full E2E: facility harvests from planet into empire pool."""
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        facility = _make_harvester_facility("Metals", base_harvest_rate=100.0)
        planet = _make_planet_with_resources(
            resources={"Metals": {"quantity": 5000, "quality": 0.8}},
            facilities=[facility],
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        empire.add_colony(planet)

        mocks = _make_mock_engines()
        harvesting = HarvestingEngine()

        engine = TurnEngine(
            **mocks,
            harvesting_engine=harvesting,
        )

        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        # harvest = 100 * 0.8 = 80
        assert empire.resource_pool.get("Metals", 0.0) == pytest.approx(80.0)
        assert planet.resources["Metals"]["quantity"] == pytest.approx(4920.0)

    def test_harvesting_before_production(self):
        """Harvesting runs before production, so resources are available for builds."""
        call_order = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting.side_effect = lambda e: call_order.append("harvesting")

        mocks = _make_mock_engines()
        mocks['production_engine'].process_production.side_effect = lambda *a, **kw: call_order.append("production")

        engine = TurnEngine(
            **mocks,
            harvesting_engine=mock_harvesting,
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        assert call_order.index("harvesting") < call_order.index("production")

    def test_harvesting_with_storage_cap(self):
        """Empire storage limits are respected during harvesting."""
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        harvester = _make_harvester_facility("Metals", base_harvest_rate=100.0)
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
                                "resource_type": "Metals",
                                "capacity": 1000.0,
                            }
                        },
                    }]
                }
            },
        )
        planet = _make_planet_with_resources(
            resources={"Metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )

        empire = Empire(0, "Test Empire", (255, 255, 255))
        empire.add_colony(planet)
        empire.resource_pool = {"Metals": 950.0}

        mocks = _make_mock_engines()
        harvesting = HarvestingEngine()

        engine = TurnEngine(
            **mocks,
            harvesting_engine=harvesting,
        )

        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        # Cap at 1000; only 50 added from 100 harvest
        assert empire.resource_pool["Metals"] == pytest.approx(1000.0)
