"""Turn engine maintenance integration tests - cost deduction and scuttling.

PROJ-75 Phase 5: Integration tests for MaintenanceEngine wired into TurnEngine.
PROJ-161: Updated for per-tick via process_maintenance_tick() (100 times per turn).

Tests verify that process_maintenance_tick() is called during process_turn(),
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
    """Inline mock for harvesting engine (PROJ-161: per-tick only)."""
    def __init__(self):
        self.tick_calls = []

    def process_harvesting_tick(self, tick, empires):
        self.tick_calls.append((tick, empires))


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
        """process_turn should call maintenance_engine.process_maintenance_tick 100 times.

        PROJ-161: Changed from once-per-turn process_maintenance() to per-tick
        process_maintenance_tick() called 100 times (once per tick).
        """
        engine, mock_maintenance = _make_fully_mocked_engine()
        empire = _make_empire()
        empire.colonies = []

        engine.process_turn([empire], MagicMock())

        # Should be called 100 times (once per tick)
        assert mock_maintenance.process_maintenance_tick_called
        assert len(mock_maintenance.process_maintenance_tick_calls) == 100

    def test_maintenance_called_after_harvesting(self):
        """Maintenance should run after harvesting within each tick so resources are available.

        PROJ-161: Rewritten for per-tick behavior. In each tick, process_harvesting_tick
        is called before process_maintenance_tick, so resources are available for maintenance.

        Note: TurnEngine uses 1-indexed ticks (1-100).
        """
        call_order = []

        # Create tracking mock for harvesting
        class TrackingHarvestingEngine(_MockHarvestingEngine):
            def process_harvesting_tick(self, tick, empires):
                call_order.append(("harvesting", tick))
                return super().process_harvesting_tick(tick, empires)

        # Create tracking mock for maintenance
        class TrackingMaintenanceEngine(MockMaintenanceEngine):
            def process_maintenance_tick(self, tick, empires):
                call_order.append(("maintenance", tick))
                return super().process_maintenance_tick(tick, empires)

        mock_harvesting = TrackingHarvestingEngine()
        mock_maintenance = TrackingMaintenanceEngine()

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

        # Verify harvesting happens before maintenance within each tick
        harvesting_calls = [c for c in call_order if c[0] == "harvesting"]
        maintenance_calls = [c for c in call_order if c[0] == "maintenance"]

        assert len(harvesting_calls) == 100
        assert len(maintenance_calls) == 100

        # For each tick (1-100), harvesting should come before maintenance in call_order
        for tick in range(1, 101):
            harvest_idx = call_order.index(("harvesting", tick))
            maint_idx = call_order.index(("maintenance", tick))
            assert harvest_idx < maint_idx, f"Tick {tick}: harvesting should precede maintenance"

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
