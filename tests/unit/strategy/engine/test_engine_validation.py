"""
Tests for sub-engine per-tick input validation.

PROJ-251 Phase 6: Validates that engines raise ValidationException
with clear messages when preconditions are violated.
"""
import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException


# ---------------------------------------------------------------------------
# Helper to create a mock empire with configurable fleets/colonies
# ---------------------------------------------------------------------------

def _empire(fleets=None, colonies=None):
    e = MagicMock()
    e.id = 0
    e.fleets = fleets or []
    e.colonies = colonies or []
    e.resource_pool = {}
    return e


def _fleet(location=MagicMock(), ships=None, orders=None):
    f = MagicMock()
    f.id = "fleet-1"
    f.location = location
    f.ships = ships if ships is not None else []
    f.orders = orders if orders is not None else []
    return f


# ---------------------------------------------------------------------------
# Engine 1: HarvestingEngine
# ---------------------------------------------------------------------------

class TestHarvestingEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.harvesting_engine import HarvestingEngine
        engine = HarvestingEngine(registries=fresh_registries)
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self, fresh_registries):
        from game.strategy.engine.harvesting_engine import HarvestingEngine
        engine = HarvestingEngine(registries=fresh_registries)
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 2: ConsumableManagementEngine
# ---------------------------------------------------------------------------

class TestConsumableManagementEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
        engine = ConsumableManagementEngine(registries=fresh_registries)
        engine._validate_tick_inputs([_empire(fleets=[_fleet()])])

    def test_fleet_none_ships_raises(self, fresh_registries):
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
        engine = ConsumableManagementEngine(registries=fresh_registries)
        fleet = _fleet()
        fleet.ships = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(fleets=[fleet])])


# ---------------------------------------------------------------------------
# Engine 3: ResupplyEngine
# ---------------------------------------------------------------------------

class TestResupplyEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.resupply_engine import ResupplyEngine
        engine = ResupplyEngine(registries=fresh_registries)
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self, fresh_registries):
        from game.strategy.engine.resupply_engine import ResupplyEngine
        engine = ResupplyEngine(registries=fresh_registries)
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 4: PlanetEnergyEngine
# ---------------------------------------------------------------------------

class TestPlanetEnergyEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
        engine = PlanetEnergyEngine(registries=fresh_registries)
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self, fresh_registries):
        from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
        engine = PlanetEnergyEngine(registries=fresh_registries)
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 5: ProductionEngine
# ---------------------------------------------------------------------------

class TestProductionEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.production_engine import ProductionEngine
        engine = ProductionEngine(registries=fresh_registries)
        engine._validate_tick_inputs([_empire()])

    def test_resource_pool_none_raises(self, fresh_registries):
        from game.strategy.engine.production_engine import ProductionEngine
        engine = ProductionEngine(registries=fresh_registries)
        emp = _empire()
        emp.resource_pool = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([emp])


# ---------------------------------------------------------------------------
# Engine 6: EnvironmentalHazardEngine
# ---------------------------------------------------------------------------

class TestEnvironmentalHazardEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
        engine = EnvironmentalHazardEngine()
        engine._validate_tick_inputs([_empire()])

    def test_fleet_none_location_raises(self):
        from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
        engine = EnvironmentalHazardEngine()
        fleet = _fleet()
        fleet.location = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(fleets=[fleet])])


# ---------------------------------------------------------------------------
# Engine 7: OrderProcessor
# ---------------------------------------------------------------------------

class TestOrderProcessorValidation:

    def test_valid_empires_pass(self):
        from game.strategy.data.order_types import OrderType
        from game.strategy.engine.order_processor import OrderProcessor
        engine = OrderProcessor()
        # PROJ-368 Phase 4: _validate_tick_inputs lives on JoinFleetHandler.
        engine._handler_registry.get(OrderType.JOIN_FLEET)._validate_tick_inputs(
            [_empire(fleets=[_fleet()])]
        )

    def test_fleet_none_orders_raises(self):
        from game.strategy.data.order_types import OrderType
        from game.strategy.engine.order_processor import OrderProcessor
        engine = OrderProcessor()
        fleet = _fleet()
        fleet.orders = None
        with pytest.raises(ValidationException):
            engine._handler_registry.get(OrderType.JOIN_FLEET)._validate_tick_inputs(
                [_empire(fleets=[fleet])]
            )


# ---------------------------------------------------------------------------
# Engine 8: ActionExecutionEngine
# ---------------------------------------------------------------------------

class TestActionExecutionEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine
        engine = ActionExecutionEngine(order_processor=MagicMock())
        engine._validate_tick_inputs([_empire()])

    def test_fleet_none_location_raises(self):
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine
        engine = ActionExecutionEngine(order_processor=MagicMock())
        fleet = _fleet()
        fleet.location = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(fleets=[fleet])])


# ---------------------------------------------------------------------------
# Engine 9: PlanetActionEngine
# ---------------------------------------------------------------------------

class TestPlanetActionEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.planet_action_engine import PlanetActionEngine
        engine = PlanetActionEngine()
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self):
        from game.strategy.engine.planet_action_engine import PlanetActionEngine
        engine = PlanetActionEngine()
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 10: ComponentActivationEngine
# ---------------------------------------------------------------------------

class TestComponentActivationEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.component_activation_engine import ComponentActivationEngine
        engine = ComponentActivationEngine()
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self):
        from game.strategy.engine.component_activation_engine import ComponentActivationEngine
        engine = ComponentActivationEngine()
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 11: FleetMovementEngine
# ---------------------------------------------------------------------------

class TestFleetMovementEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        engine = FleetMovementEngine()
        engine._validate_tick_inputs([_empire()])

    def test_fleet_none_location_raises(self):
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        engine = FleetMovementEngine()
        fleet = _fleet()
        fleet.location = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(fleets=[fleet])])


# ---------------------------------------------------------------------------
# Engine 12: ConflictResolutionEngine
# ---------------------------------------------------------------------------

class TestConflictResolutionEngineValidation:

    def test_valid_empires_pass(self, fresh_registries):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        engine = ConflictResolutionEngine(battle_resolver=MagicMock(), registries=fresh_registries)
        engine._validate_tick_inputs([_empire()])

    def test_fleet_none_location_raises(self, fresh_registries):
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        engine = ConflictResolutionEngine(battle_resolver=MagicMock(), registries=fresh_registries)
        fleet = _fleet()
        fleet.location = None
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(fleets=[fleet])])


# ---------------------------------------------------------------------------
# Engine 13: PopulationEngine
# ---------------------------------------------------------------------------

class TestPopulationEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.population_engine import PopulationEngine
        engine = PopulationEngine()
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self):
        from game.strategy.engine.population_engine import PopulationEngine
        engine = PopulationEngine()
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


# ---------------------------------------------------------------------------
# Engine 14: QualityEngine + AtmosphereEngine
# ---------------------------------------------------------------------------

class TestQualityEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self):
        from game.strategy.engine.quality_engine import QualityEngine
        engine = QualityEngine()
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])


class TestAtmosphereEngineValidation:

    def test_valid_empires_pass(self):
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine
        engine = AtmosphereEngine()
        engine._validate_tick_inputs([_empire()])

    def test_colony_none_raises(self):
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine
        engine = AtmosphereEngine()
        with pytest.raises(ValidationException):
            engine._validate_tick_inputs([_empire(colonies=[None])])
