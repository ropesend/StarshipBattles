"""Turn engine maintenance integration tests - cost deduction and scuttling.

PROJ-75 Phase 5: Integration tests for MaintenanceEngine wired into TurnEngine.
Tests verify that process_maintenance() is called during process_turn(),
and that maintenance costs flow correctly and scuttling works end-to-end.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.planet import PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.interfaces.engines import IHarvestingEngine, IPopulationEngine

from tests.unit.strategy.mocks.mock_engines import (
    MockMovementEngine,
    MockProductionEngine,
    MockOrderProcessor,
    MockConflictEngine,
    MockResourceEngine,
    MockMaintenanceEngine,
)


# ===========================================================================
# Inline mocks for engines without existing mock classes
# ===========================================================================

class _MockHarvestingEngine(IHarvestingEngine):
    """Inline mock for harvesting engine."""
    def __init__(self):
        self.calls = []

    def process_harvesting(self, empires):
        self.calls.append(empires)


class _MockPopulationEngine(IPopulationEngine):
    """Inline mock for population engine."""
    def process_population_growth(self, empires):
        pass


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_empire(resources=None, empire_id=0):
    """Create a real Empire with optional starting resources."""
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))
    if resources:
        for res, amount in resources.items():
            empire.resource_pool[res] = amount
    return empire


def _make_facility(resource_cost=None, name="Test Facility", instance_id="fac_1"):
    """Create a facility with given resource costs."""
    cost = resource_cost or {"Metals": 1000}
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="test_complex",
        name=name,
        design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": cost}
                    ]
                }
            }
        },
        is_operational=True,
    )


def _make_colony(facilities=None, name="Test Colony"):
    """Create a mock colony."""
    colony = MagicMock()
    colony.name = name
    colony.id = 1
    colony.facilities = list(facilities) if facilities else []
    return colony


def _make_fully_mocked_engine(maintenance_engine=None):
    """Create TurnEngine with ALL engines injected via DI."""
    mock_maintenance = maintenance_engine or MockMaintenanceEngine()
    engine = TurnEngine(
        movement_engine=MockMovementEngine(),
        production_engine=MockProductionEngine(),
        order_processor=MockOrderProcessor(),
        conflict_engine=MockConflictEngine(),
        resource_engine=MockResourceEngine(),
        harvesting_engine=_MockHarvestingEngine(),
        population_engine=_MockPopulationEngine(),
        maintenance_engine=mock_maintenance,
    )
    return engine, mock_maintenance


def _make_engine_with_real_maintenance():
    """Create TurnEngine with real maintenance but other engines mocked."""
    return TurnEngine(
        movement_engine=MockMovementEngine(),
        production_engine=MockProductionEngine(),
        order_processor=MockOrderProcessor(),
        conflict_engine=MockConflictEngine(),
        resource_engine=MockResourceEngine(),
        harvesting_engine=_MockHarvestingEngine(),
        population_engine=_MockPopulationEngine(),
        # maintenance_engine left as None -> lazily creates real one
    )


# ===========================================================================
# Integration Tests
# ===========================================================================

class TestMaintenanceTurnEngineIntegration:
    """Tests that MaintenanceEngine is properly wired into TurnEngine."""

    def test_maintenance_engine_called_during_process_turn(self):
        """process_turn should call maintenance_engine.process_maintenance."""
        engine, mock_maintenance = _make_fully_mocked_engine()
        empire = _make_empire()
        empire.colonies = []

        engine.process_turn([empire], MagicMock())

        assert mock_maintenance.process_maintenance_called

    def test_maintenance_called_after_harvesting(self):
        """Maintenance should run after harvesting so resources are available."""
        call_order = []

        mock_harvesting = _MockHarvestingEngine()
        original_harvest = mock_harvesting.process_harvesting
        def track_harvesting(empires):
            call_order.append("harvesting")
            return original_harvest(empires)
        mock_harvesting.process_harvesting = track_harvesting

        mock_maintenance = MockMaintenanceEngine()
        original_maintenance = mock_maintenance.process_maintenance
        def track_maintenance(empires):
            call_order.append("maintenance")
            return original_maintenance(empires)
        mock_maintenance.process_maintenance = track_maintenance

        engine = TurnEngine(
            movement_engine=MockMovementEngine(),
            production_engine=MockProductionEngine(),
            order_processor=MockOrderProcessor(),
            conflict_engine=MockConflictEngine(),
            resource_engine=MockResourceEngine(),
            harvesting_engine=mock_harvesting,
            population_engine=_MockPopulationEngine(),
            maintenance_engine=mock_maintenance,
        )

        engine.process_turn([_make_empire()], MagicMock())

        assert call_order.index("harvesting") < call_order.index("maintenance")

    def test_real_maintenance_deducts_facility_costs(self):
        """Real maintenance engine deducts costs when wired into TurnEngine."""
        engine = _make_engine_with_real_maintenance()
        empire = _make_empire({"Metals": 1000.0})
        facility = _make_facility(resource_cost={"Metals": 200})  # 5% = 10
        colony = _make_colony(facilities=[facility])
        empire.colonies = [colony]

        engine.process_turn([empire], MagicMock())

        assert empire.resource_pool["Metals"] == pytest.approx(990.0)

    def test_real_maintenance_scuttles_facility(self):
        """Real maintenance engine scuttles facility when no resources."""
        engine = _make_engine_with_real_maintenance()
        empire = _make_empire({"Metals": 0.0})
        facility = _make_facility(resource_cost={"Metals": 200})
        colony = _make_colony(facilities=[facility])
        empire.colonies = [colony]

        engine.process_turn([empire], MagicMock())

        assert len(colony.facilities) == 0

    def test_maintenance_engine_property_creates_default(self):
        """TurnEngine.maintenance_engine lazily creates MaintenanceEngine."""
        engine = TurnEngine(
            movement_engine=MockMovementEngine(),
            production_engine=MockProductionEngine(),
            order_processor=MockOrderProcessor(),
            conflict_engine=MockConflictEngine(),
            resource_engine=MockResourceEngine(),
        )
        from game.strategy.engine.maintenance_engine import MaintenanceEngine
        assert isinstance(engine.maintenance_engine, MaintenanceEngine)

    def test_maintenance_engine_injectable(self):
        """TurnEngine accepts maintenance_engine via constructor DI."""
        mock_maintenance = MockMaintenanceEngine()
        engine = TurnEngine(
            movement_engine=MockMovementEngine(),
            production_engine=MockProductionEngine(),
            order_processor=MockOrderProcessor(),
            conflict_engine=MockConflictEngine(),
            resource_engine=MockResourceEngine(),
            maintenance_engine=mock_maintenance,
        )
        assert engine.maintenance_engine is mock_maintenance
